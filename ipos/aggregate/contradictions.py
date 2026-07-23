"""Contradictions engine (rank-3 feature; C4 decision 5).

Config-driven predicates in ``configs/contradictions.yaml`` are evaluated over
the week's module scores, indicator scores, and regime label. Each hit is
written to ``log_contradiction`` with the triggering values captured
automatically (by walking the predicate for ``module(...)`` / ``indicator(...)``
references). This is the Blueprint's "no traffic lights" differentiator: it
surfaces *disagreement*, not a single colour.

Predicate DSL is a tiny, safe expression language evaluated with Python's
``ast`` module — NO ``eval``. Only comparisons, boolean/unary ops, numeric
literals, and a whitelist of helper calls are permitted.
"""

from __future__ import annotations

import ast
import datetime as dt
import json
import math
from dataclasses import dataclass
from pathlib import Path

import duckdb
import yaml

from ipos.config.load import REPO_ROOT

CONTRADICTIONS_YAML = REPO_ROOT / "configs" / "contradictions.yaml"

_ALLOWED_FUNCS = {"module", "module_conf", "module_spread", "indicator", "regime", "abs", "min", "max"}
_SEVERITIES = {"low", "med", "high"}


class ContradictionConfigError(ValueError):
    pass


@dataclass
class Predicate:
    id: str
    when: str
    severity: str
    summary: str
    tree: ast.Expression


# --- safe evaluator ---------------------------------------------------------

_ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not,
    ast.Compare, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq,
    ast.Call, ast.Name, ast.Load, ast.Constant,
)


def _validate_ast(node: ast.AST) -> None:
    for child in ast.walk(node):
        if not isinstance(child, _ALLOWED_NODES):
            raise ContradictionConfigError(
                f"disallowed expression element: {type(child).__name__}"
            )
        if isinstance(child, ast.Call):
            if not isinstance(child.func, ast.Name) or child.func.id not in _ALLOWED_FUNCS:
                raise ContradictionConfigError(
                    f"only calls to {sorted(_ALLOWED_FUNCS)} are allowed"
                )
        if isinstance(child, ast.Name) and child.id not in _ALLOWED_FUNCS:
            raise ContradictionConfigError(f"unknown name: {child.id}")


def _compile(expr: str) -> ast.Expression:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ContradictionConfigError(f"cannot parse predicate {expr!r}: {exc}") from exc
    _validate_ast(tree)
    return tree


def _eval(node: ast.AST, funcs: dict):
    if isinstance(node, ast.Expression):
        return _eval(node.body, funcs)
    if isinstance(node, ast.BoolOp):
        vals = [_eval(v, funcs) for v in node.values]
        return all(vals) if isinstance(node.op, ast.And) else any(vals)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _eval(node.operand, funcs)
    if isinstance(node, ast.Compare):
        left = _eval(node.left, funcs)
        for op, comp in zip(node.ops, node.comparators):
            right = _eval(comp, funcs)
            if left is None or right is None:  # missing data => predicate can't fire
                return False
            if not _cmp(op, left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.Call):
        args = [_eval(a, funcs) for a in node.args]
        return funcs[node.func.id](*args)
    if isinstance(node, ast.Constant):
        return node.value
    raise ContradictionConfigError(f"unexpected node {type(node).__name__}")


def _cmp(op, a, b) -> bool:
    if isinstance(op, ast.Lt):
        return a < b
    if isinstance(op, ast.LtE):
        return a <= b
    if isinstance(op, ast.Gt):
        return a > b
    if isinstance(op, ast.GtE):
        return a >= b
    if isinstance(op, ast.Eq):
        return a == b
    if isinstance(op, ast.NotEq):
        return a != b
    raise ContradictionConfigError(f"unsupported comparator {type(op).__name__}")


# --- config loading ---------------------------------------------------------

def load_predicates(path: Path | None = None) -> list[Predicate]:
    p = path or CONTRADICTIONS_YAML
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    preds: list[Predicate] = []
    seen: set[str] = set()
    for row in data.get("contradictions", []):
        pid = row["id"]
        if pid in seen:
            raise ContradictionConfigError(f"duplicate contradiction id: {pid}")
        seen.add(pid)
        sev = row["severity"]
        if sev not in _SEVERITIES:
            raise ContradictionConfigError(f"{pid}: severity must be one of {_SEVERITIES}")
        tree = _compile(row["when"])
        preds.append(Predicate(id=pid, when=row["when"], severity=sev,
                               summary=row["summary"], tree=tree))
    return preds


# --- context ----------------------------------------------------------------

def _build_context(con: duckdb.DuckDBPyConnection, as_of: dt.date) -> dict:
    modules = dict(con.execute(
        "SELECT module_id, module_score FROM agg_module WHERE as_of_date = ?", [as_of]
    ).fetchall())
    module_confs = dict(con.execute(
        "SELECT module_id, module_confidence FROM agg_module WHERE as_of_date = ?", [as_of]
    ).fetchall())
    indicators = dict(con.execute(
        "SELECT series_id, score_0_100 FROM fact_score WHERE as_of_date = ?", [as_of]
    ).fetchall())
    spreads: dict[str, float] = {}
    rows = con.execute(
        """
        SELECT d.module_id, max(s.score_0_100) - min(s.score_0_100)
        FROM fact_score s JOIN dim_series d USING (series_id)
        WHERE s.as_of_date = ? AND d.enabled
        GROUP BY d.module_id
        """,
        [as_of],
    ).fetchall()
    for mid, spread in rows:
        spreads[mid] = spread
    regime_row = con.execute(
        "SELECT regime_label FROM agg_regime WHERE as_of_date = ?", [as_of]
    ).fetchone()
    regime_label = regime_row[0] if regime_row else None

    def _get(d, key):
        # missing this week => None => predicate can't fire (fail-degraded).
        return float(d[key]) if key in d else None

    return {
        "module": lambda k: _get(modules, k),
        "module_conf": lambda k: _get(module_confs, k),
        "module_spread": lambda k: _get(spreads, k),
        "indicator": lambda k: _get(indicators, k),
        "regime": lambda: regime_label,
        "abs": abs, "min": min, "max": max,
    }


def _references(preds: list[Predicate]) -> dict[str, set[str]]:
    """Collect the module/indicator ids each predicate references, for
    typo-checking against the registry at run time."""
    out: dict[str, set[str]] = {"module": set(), "indicator": set()}
    for pred in preds:
        for node in ast.walk(pred.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if node.func.id in ("module", "module_conf", "module_spread"):
                        out["module"].add(arg.value)
                    elif node.func.id == "indicator":
                        out["indicator"].add(arg.value)
    return out


def _validate_references(
    con: duckdb.DuckDBPyConnection, preds: list[Predicate]
) -> None:
    known_modules = {r[0] for r in con.execute("SELECT DISTINCT module_id FROM dim_series").fetchall()}
    known_series = {r[0] for r in con.execute("SELECT series_id FROM dim_series").fetchall()}
    refs = _references(preds)
    bad_mods = refs["module"] - known_modules
    bad_series = refs["indicator"] - known_series
    if bad_mods:
        raise ContradictionConfigError(f"predicates reference unknown module(s): {sorted(bad_mods)}")
    if bad_series:
        raise ContradictionConfigError(f"predicates reference unknown series: {sorted(bad_series)}")


def _captured_values(tree: ast.Expression, funcs: dict) -> dict:
    """Evaluate every module()/indicator()/module_*() reference in the predicate
    so the log records exactly which numbers triggered it."""
    out: dict[str, float] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn = node.func.id
            if fn in ("module", "module_conf", "module_spread", "indicator") and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant):
                    try:
                        out[f"{fn}({arg.value})"] = round(float(funcs[fn](arg.value)), 4)
                    except Exception:
                        pass
    return dict(sorted(out.items()))


# --- engine -----------------------------------------------------------------

def evaluate(
    con: duckdb.DuckDBPyConnection, as_of: dt.date, path: Path | None = None
) -> list[dict]:
    """Evaluate all predicates for the week, write hits to log_contradiction,
    and return them (deterministic order: severity high>med>low, then id)."""
    preds = load_predicates(path)
    _validate_references(con, preds)
    ctx = _build_context(con, as_of)

    hits: list[dict] = []
    for pred in preds:
        try:
            fired = bool(_eval(pred.tree, ctx))
        except ContradictionConfigError:
            raise
        if fired:
            hits.append({
                "id": pred.id,
                "severity": pred.severity,
                "summary": pred.summary,
                "details": _captured_values(pred.tree, ctx),
            })

    sev_rank = {"high": 0, "med": 1, "low": 2}
    hits.sort(key=lambda h: (sev_rank[h["severity"]], h["id"]))

    con.execute("DELETE FROM log_contradiction WHERE as_of_date = ?", [as_of])
    for h in hits:
        con.execute(
            """
            INSERT OR REPLACE INTO log_contradiction
              (as_of_date, contradiction_id, severity, summary, details_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            [as_of, h["id"], h["severity"], h["summary"],
             json.dumps(h["details"], sort_keys=True)],
        )
    return hits
