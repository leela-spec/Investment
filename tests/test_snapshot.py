"""Snapshot & report tests (C6 Definition of Done): schema-valid snapshot,
byte-identical on re-run (determinism), and a report that renders with no LLM."""

from __future__ import annotations

import datetime as dt

from ipos.export.report import render_report, write_report
from ipos.export.snapshot import build_snapshot, validate, write_snapshot
from ipos.warehouse.db import connect


def _build(populated_db, as_of):
    db, reg = populated_db
    with connect(db, read_only=True) as con:
        return build_snapshot(con, reg, as_of)


def test_snapshot_schema_valid(populated_db, as_of):
    snap = _build(populated_db, as_of)
    validate(snap)  # raises on invalid
    assert snap["as_of"] == as_of.isoformat()
    assert len(snap["indicators"]) == 22
    assert len(snap["modules"]) == 8
    assert 0 <= snap["overall"]["risk_budget"] <= 100


def test_snapshot_deterministic_bytes(populated_db, as_of, tmp_path):
    snap1 = _build(populated_db, as_of)
    snap2 = _build(populated_db, as_of)
    p1 = write_snapshot(snap1, as_of, tmp_path / "a")
    p2 = write_snapshot(snap2, as_of, tmp_path / "b")
    b1 = open(p1["snapshot"], "rb").read()
    b2 = open(p2["snapshot"], "rb").read()
    assert b1 == b2  # byte-identical
    m1 = open(p1["snapshot_min"], "rb").read()
    m2 = open(p2["snapshot_min"], "rb").read()
    assert m1 == m2


def test_earlier_weeks_synthetic_flag_does_not_taint_this_week(populated_db, as_of):
    # 2026-07-26 regression: a PRIOR week's legitimate --seed-offline run
    # (synthetic-vintage fact_weekly rows) must not permanently flag every
    # later, genuinely real week's snapshot as synthetic too.
    db, reg = populated_db
    with connect(db) as con:
        con.execute(
            "INSERT OR REPLACE INTO fact_weekly "
            "(series_id, as_of_date, value, vintage_id, obs_date, ingested_at) "
            "VALUES ('SPX', ?, 100.0, 'synthetic@SPX@prior-week', ?, ?)",
            [as_of - dt.timedelta(weeks=1), as_of - dt.timedelta(weeks=1), dt.datetime(2026, 1, 1)],
        )
    snap = _build(populated_db, as_of)
    assert snap["flags"]["synthetic_data"] is False


def test_snapshot_exports_level_percentile_and_z(populated_db, as_of):
    """`fact_feature.pctile_156w` / `z_104w` were computed and stored since Phase 1
    but never reached the snapshot, so no renderer could show where a reading sat
    in its own history (2026-07-29 audit)."""
    snap = _build(populated_db, as_of)
    by_id = {i["id"]: i for i in snap["indicators"]}
    for ind in snap["indicators"]:
        assert "pctile_156w" in ind and "z_104w" in ind and "history_weeks" in ind
    assert 0 <= by_id["SPX"]["pctile_156w"] <= 100
    assert by_id["SPX"]["history_weeks"] > 0
    # The level percentile is NOT direction-adjusted, and must not be confused
    # with the score. HY_OAS is an inverted indicator, so a HIGH spread level
    # must produce a LOW score -- if these ever move together, something has
    # started treating the percentile as the score.
    hy = by_id["HY_OAS"]
    assert hy["pctile_156w"] > 60 and hy["score"] < 40


def test_budget_attribution_contributions_sum_to_the_delta(populated_db, as_of):
    """The reconciliation guard for the contribution decomposition.

    The per-module contributions are only honest if they add up to the reported
    change in the base budget. If this drifts, the panel is asserting an
    explanation it cannot support and must be pulled, not patched.
    """
    db, reg = populated_db
    # The golden fixture only writes the aggregate layer for one week, so build a
    # prior week by hand to exercise the populated path.
    prev = as_of - dt.timedelta(weeks=1)
    with connect(db) as con:
        row = con.execute(
            "SELECT risk_budget_0_100, confidence_0_100, regime_label, risk_scaler, "
            "regime_confidence, policy_json, params_json FROM agg_regime WHERE as_of_date = ?",
            [as_of],
        ).fetchone()
        con.execute(
            "INSERT OR REPLACE INTO agg_regime (as_of_date, risk_budget_0_100, "
            "confidence_0_100, regime_label, risk_scaler, regime_confidence, "
            "policy_json, params_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [prev, *row],
        )
        for mid, dim, score, conf, stance in con.execute(
            "SELECT module_id, stance_dim, module_score, module_confidence, stance_value "
            "FROM agg_module WHERE as_of_date = ?", [as_of],
        ).fetchall():
            con.execute(
                "INSERT OR REPLACE INTO agg_module (as_of_date, module_id, stance_dim, "
                "module_score, module_confidence, stance_value, params_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                # nudge one module so the delta is non-zero and signed
                [prev, mid, dim, score - (4.0 if mid == "Credit" else 0.0), conf, stance, None],
            )

    snap = _build(populated_db, as_of)
    attr = snap["budget_attribution"]
    assert attr["prev_as_of"] == prev.isoformat()
    total = sum(c["contribution"] for c in attr["contributions"])
    assert abs(total - attr["delta"]) < 1e-3, (
        f"contributions sum to {total} but delta is {attr['delta']}"
    )
    assert abs(attr["base_to"] - attr["base_from"] - attr["delta"]) < 1e-3
    # Credit was moved up by 4 points, so it must be the dominant contributor
    assert attr["contributions"][0]["module"] == "Credit"
    assert attr["contributions"][0]["contribution"] > 0


def test_budget_attribution_omitted_without_a_prior_week(populated_db, as_of):
    """No prior aggregate row must omit the section rather than invent a baseline
    -- the aggregate tables are only as deep as `ipos-replay` has rebuilt them."""
    snap = _build(populated_db, as_of)
    assert "budget_attribution" not in snap


def test_regime_block_explains_itself(populated_db, as_of):
    snap = _build(populated_db, as_of)
    regime = snap["regime"]
    assert regime["base_risk_budget"] is not None
    # headline == base x scaler, which is what the report's bridge asserts
    assert abs(regime["base_risk_budget"] * regime["risk_scaler"]
               - snap["overall"]["risk_budget"]) < 0.01
    assert "overlap_index" in regime["features"]
    assert regime["features"]["atr_source"] in ("ohlc", "close")
    # the dead duplicate is gone; the live one remains
    assert "risk_scaler" not in snap["overall"]


def test_contradiction_recurrence_counts_repeat_weeks(populated_db, as_of):
    """"Fired once" and "fired 3 weeks running" are different situations; the
    single-week query this replaced could not distinguish them."""
    db, reg = populated_db
    with connect(db) as con:
        cid = con.execute(
            "SELECT contradiction_id FROM log_contradiction WHERE as_of_date = ? LIMIT 1",
            [as_of],
        ).fetchone()[0]
        for back in (1, 2):
            con.execute(
                "INSERT OR REPLACE INTO log_contradiction (as_of_date, contradiction_id, "
                "severity, summary, details_json) VALUES (?, ?, 'low', 'repeat', NULL)",
                [as_of - dt.timedelta(weeks=back), cid],
            )
    snap = _build(populated_db, as_of)
    hit = next(c for c in snap["contradictions"] if c["id"] == cid)
    assert hit["weeks_fired"] == 3
    assert hit["weeks_observed"] == 3


def test_breadth_reports_spread_not_just_the_average(populated_db, as_of):
    snap = _build(populated_db, as_of)
    b = snap["breadth"]
    assert b["n_scored"] == len(snap["indicators"])
    assert 0 <= b["pct_above_50"] <= 100
    assert b["n_above_50"] == sum(1 for i in snap["indicators"] if i["score"] > 50)


def test_markdown_overall_bullets_do_not_collapse_onto_one_line(populated_db, as_of):
    """Jinja's `trim_blocks` eats the newline after a block tag, so a line ENDING
    in a conditional silently swallows the next bullet. This bit the Policy /
    Degraded bullets on 2026-07-27 and the Risk-budget / Breadth bullets on
    2026-07-29 -- each time invisibly, because the markdown still parsed."""
    md = render_report(_build(populated_db, as_of))
    bullets = [ln for ln in md.splitlines() if ln.startswith("- **")]
    labels = ["Risk budget", "Confidence", "Breadth", "Regime"]
    for label in labels:
        matching = [b for b in bullets if b.startswith(f"- **{label}:")]
        assert len(matching) == 1, f"{label!r} bullet missing or duplicated: {bullets}"
        # exactly one bullet's worth of content -- no second "- **" glued on
        assert matching[0].count("- **") == 1, f"bullets collapsed: {matching[0]!r}"


def test_markdown_never_prints_a_bare_python_none(populated_db, as_of):
    """`regime_features.range_overlap` is legitimately None on close-only data;
    a raw "None" in the report reads as a value rather than an absence."""
    md = render_report(_build(populated_db, as_of))
    assert "= None" not in md
    assert "| None |" not in md


def test_report_renders_without_llm(populated_db, as_of, tmp_path):
    snap = _build(populated_db, as_of)
    md = render_report(snap)
    assert "IPOS Weekly Report" in md
    assert "Risk budget" in md
    # deterministic
    assert render_report(snap) == md
    path = write_report(snap, as_of, tmp_path)
    assert path.endswith("report.md")
