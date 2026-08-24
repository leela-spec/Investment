"""IPOS Backtesting & Simulation Engine.

Computes, over historical weekly data:

1. **Regime classification accuracy** — walk-forward re-classification of the
   benchmark using the SAME close-only classifier as production
   (``ipos.aggregate.regime.classify_history``), scored against an ex-post
   realized-regime label (forward-looking volatility/direction decomposition).
2. **Risk-budget drawdown suppression** — a weekly-rebalanced synthetic
   exposure of ``risk_budget = base * regime.risk_scaler`` applied to the
   benchmark's forward weekly returns, vs the unscaled static benchmark.
   Reports max drawdown, vol, and drawdown suppression.
3. **Risk-adjusted return comparison** — Sharpe / Sortino / Calmar of the
   regime-scaled strategy against the static buy-and-hold benchmark.

DESIGN CONTRACT:
  * Deterministic: pure functions of the input price series; no wall-clock.
  * Reuses the production classifier — no re-implementation drift.
  * The advisor tilt overlay (optional) consumes
    ``ipos.advisor.rule_engine.advise`` when per-week AdvisorStates are given,
    but the core metrics run on prices alone so they are always computable.
  * No live trading semantics; this is decision-support analytics only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ipos.aggregate.regime import classify_history


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RegimeAccuracyReport:
    n_weeks_evaluated: int
    hits: int
    misses: int
    ambiguous: int          # realized label not classifiable (mixed evidence)
    accuracy_pct: float
    confusion: dict[str, dict[str, int]] = field(default_factory=dict)
    by_regime_recall: dict[str, float] = field(default_factory=dict)


@dataclass
class StrategyMetrics:
    total_return_pct: float
    ann_return_pct: float
    ann_vol_pct: float
    sharpe: float
    sortino: float
    calmar: float
    max_drawdown_pct: float
    n_weeks: int


@dataclass
class DrawdownSuppressionReport:
    static_max_dd_pct: float
    scaled_max_dd_pct: float
    suppression_pct: float            # relative reduction in max drawdown
    static_worst_week_pct: float
    scaled_worst_week_pct: float
    avg_risk_budget: float            # mean scaler actually applied 0-1
    time_in_market_pct: float         # weeks with budget > 0


@dataclass
class BacktestReport:
    benchmark: str
    start: str
    end: str
    regime_accuracy: RegimeAccuracyReport
    static_metrics: StrategyMetrics
    scaled_metrics: StrategyMetrics
    drawdown_suppression: DrawdownSuppressionReport
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Realized (ex-post) regime labeling — the evaluation target
# ---------------------------------------------------------------------------

def realized_regime(closes: np.ndarray, i: int, horizon: int = 8,
                    trend_thr: float = 0.03, vol_split: float = 1.25) -> str | None:
    """Label what the market DID over ``horizon`` weeks after week ``i``
    (uses only data up to i+horizon; caller guarantees availability).

    TRENDY  : |net move| >= trend_thr and vol not accelerating
    MOMENTUM: |net move| >= trend_thr and vol accelerating >= vol_split
    CHOPPY  : small net move (< trend_thr/2) with high two-sided variance
    UNCERTAIN: everything else / mixed evidence -> None (ambiguous)
    """
    seg = closes[i + 1: i + 1 + horizon]
    if len(seg) < horizon // 2:
        return None
    rets = np.diff(np.concatenate([[closes[i]], seg]))
    gross = float(np.sum(np.abs(rets)))
    net = float(abs(seg[-1] - closes[i]))
    er = net / gross if gross > 0 else 0.0
    half = len(rets) // 2
    v1 = float(np.mean(np.abs(rets[:half]))) if half else 0.0
    v2 = float(np.mean(np.abs(rets[half:]))) if half else v1
    accel = v2 / v1 if v1 > 0 else 1.0
    directional = net >= trend_thr * closes[i]
    if directional and accel >= vol_split:
        return "MOMENTUM"
    if directional and er >= 0.4:
        return "TRENDY"
    if net < trend_thr / 2 * closes[i] and er <= 0.35:
        return "CHOPPY"
    return None                      # ambiguous


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _weekly_returns(closes: np.ndarray) -> np.ndarray:
    return np.diff(closes) / closes[:-1]


def _max_drawdown(returns: np.ndarray) -> float:
    equity = np.cumprod(1.0 + returns)
    peak = np.maximum.accumulate(equity)
    dd = equity / peak - 1.0
    return float(dd.min()) if len(dd) else 0.0


def compute_metrics(returns: np.ndarray, rf_weekly: float = 0.0) -> StrategyMetrics:
    """Annualized metrics from a weekly return vector (52 weeks/year)."""
    n = len(returns)
    if n == 0:
        return StrategyMetrics(0, 0, 0, 0, 0, 0, 0, 0)
    equity = float(np.prod(1.0 + returns))
    ann_ret = equity ** (52.0 / n) - 1.0 if equity > 0 else -1.0
    vol = float(np.std(returns, ddof=1)) * math.sqrt(52.0) if n > 1 else 0.0
    excess = returns - rf_weekly
    downside = excess[excess < 0]
    dvol = float(np.std(downside, ddof=1)) * math.sqrt(52.0) if len(downside) > 1 else 0.0
    mdd = _max_drawdown(returns)
    sharpe = float(np.mean(excess)) * 52.0 / vol if vol > 0 else 0.0
    sortino = float(np.mean(excess)) * 52.0 / dvol if dvol > 0 else 0.0
    calmar = ann_ret / abs(mdd) if mdd < 0 else 0.0
    return StrategyMetrics(
        total_return_pct=round((equity - 1.0) * 100, 4),
        ann_return_pct=round(ann_ret * 100, 4),
        ann_vol_pct=round(vol * 100, 4),
        sharpe=round(sharpe, 4),
        sortino=round(sortino, 4),
        calmar=round(calmar, 4),
        max_drawdown_pct=round(mdd * 100, 4),
        n_weeks=n,
    )


# ---------------------------------------------------------------------------
# Core simulations
# ---------------------------------------------------------------------------

def regime_accuracy_walk_forward(
    closes: list[float],
    highs: list[float] | None = None,
    lows: list[float] | None = None,
    min_history: int = 24,
    horizon: int = 8,
) -> RegimeAccuracyReport:
    """Re-run the production classifier at every week t (using only data <= t),
    then compare its label to the realized regime over t+1..t+horizon."""
    p = np.asarray(closes, dtype=float)
    h = np.asarray(highs, dtype=float) if highs is not None else None
    l = np.asarray(lows, dtype=float) if lows is not None else None
    confusion: dict[str, dict[str, int]] = {}
    hits = misses = ambiguous = 0
    for t in range(min_history, len(p) - horizon):
        pred = classify_history(list(p[:t + 1]),
                                list(h[:t + 1]) if h is not None else None,
                                list(l[:t + 1]) if l is not None else None).label
        actual = realized_regime(p, t, horizon=horizon)
        if actual is None:
            ambiguous += 1
            continue
        slot = confusion.setdefault(pred, {})
        slot[actual] = slot.get(actual, 0) + 1
        if pred == actual:
            hits += 1
        else:
            misses += 1
    evaluated = hits + misses
    recall: dict[str, float] = {}
    for pred, slot in confusion.items():
        tot = sum(slot.values())
        if tot:
            recall[pred] = round(slot.get(pred, 0) / tot * 100, 2)
    return RegimeAccuracyReport(
        n_weeks_evaluated=evaluated,
        hits=hits,
        misses=misses,
        ambiguous=ambiguous,
        accuracy_pct=round(hits / evaluated * 100, 2) if evaluated else 0.0,
        confusion={k: dict(v) for k, v in sorted(confusion.items())},
        by_regime_recall=recall,
    )


def risk_budget_series(closes: list[float],
                       highs: list[float] | None = None,
                       lows: list[float] | None = None,
                       min_history: int = 16,
                       floor: float = 0.15) -> tuple[np.ndarray, list[str]]:
    """Walk-forward regime risk budgets: budget[t] applied to the return from
    t -> t+1 (no look-ahead: the classifier only sees data <= t).
    Budgets are floored at ``floor`` (never fully flat — the framework is a
    risk *budget*, not an on/off switch)."""
    p = np.asarray(closes, dtype=float)
    h = np.asarray(highs, dtype=float) if highs is not None else None
    l = np.asarray(lows, dtype=float) if lows is not None else None
    budgets = np.ones(len(p))
    labels: list[str] = ["UNCERTAIN"] * len(p)
    for t in range(len(p)):
        if t + 1 < min_history:
            budgets[t] = floor
            labels[t] = "UNCERTAIN"
            continue
        res = classify_history(list(p[:t + 1]),
                               list(h[:t + 1]) if h is not None else None,
                               list(l[:t + 1]) if l is not None else None)
        budgets[t] = max(floor, res.risk_scaler)
        labels[t] = res.label
    return budgets, labels


def simulate_scaled(returns: np.ndarray, budgets: np.ndarray) -> np.ndarray:
    """Apply weekly risk budgets to returns (aligned: budget[t] on ret[t])."""
    n = min(len(returns), len(budgets))
    return returns[:n] * budgets[:n]


def run_backtest(
    dates: list[str],
    closes: list[float],
    highs: list[float] | None = None,
    lows: list[float] | None = None,
    benchmark: str = "SPX",
    horizon: int = 8,
    floor: float = 0.15,
    rf_weekly: float = 0.0,
) -> BacktestReport:
    """Full report: regime accuracy + drawdown suppression + risk-adjusted
    comparison vs the static benchmark."""
    assert len(dates) == len(closes), "dates/closes length mismatch"
    p = np.asarray(closes, dtype=float)
    rets = _weekly_returns(p)

    acc = regime_accuracy_walk_forward(closes, highs, lows, horizon=horizon)

    budgets, _ = risk_budget_series(closes, highs, lows, floor=floor)
    scaled = simulate_scaled(rets, budgets[1:])       # budget known at t applies to t->t+1

    static_m = compute_metrics(rets, rf_weekly)
    scaled_m = compute_metrics(scaled, rf_weekly)

    static_dd = abs(static_m.max_drawdown_pct)
    scaled_dd = abs(scaled_m.max_drawdown_pct)
    suppression = round((static_dd - scaled_dd) / static_dd * 100, 2) if static_dd > 0 else 0.0

    dd_report = DrawdownSuppressionReport(
        static_max_dd_pct=static_m.max_drawdown_pct,
        scaled_max_dd_pct=scaled_m.max_drawdown_pct,
        suppression_pct=suppression,
        static_worst_week_pct=round(float(rets.min()) * 100, 4) if len(rets) else 0.0,
        scaled_worst_week_pct=round(float(scaled.min()) * 100, 4) if len(scaled) else 0.0,
        avg_risk_budget=round(float(np.mean(budgets[1:len(scaled) + 1])), 4) if len(scaled) else 0.0,
        time_in_market_pct=round(float(np.mean(budgets[1:len(scaled) + 1] > floor + 1e-9) * 100), 2)
        if len(scaled) else 0.0,
    )

    notes = [
        "Walk-forward: classifier at week t uses ONLY data <= t (no look-ahead).",
        f"Realized-label horizon: {horizon} weeks; ambiguous windows excluded "
        f"({acc.ambiguous} of {acc.n_weeks_evaluated + acc.ambiguous}).",
        f"Risk budget floored at {floor:.0%}; scaler source: "
        "ipos.aggregate.regime.RISK_SCALER (production values).",
        "Decision-support analytics only — no execution/trading semantics.",
    ]

    return BacktestReport(
        benchmark=benchmark,
        start=dates[0],
        end=dates[-1],
        regime_accuracy=acc,
        static_metrics=static_m,
        scaled_metrics=scaled_m,
        drawdown_suppression=dd_report,
        notes=notes,
    )


def format_report(r: BacktestReport) -> str:
    lines = [
        f"IPOS BACKTEST — {r.benchmark}  {r.start} .. {r.end}",
        "",
        "Regime classification (walk-forward):",
        f"  evaluated={r.regime_accuracy.n_weeks_evaluated}  "
        f"hits={r.regime_accuracy.hits}  misses={r.regime_accuracy.misses}  "
        f"ambiguous={r.regime_accuracy.ambiguous}",
        f"  accuracy={r.regime_accuracy.accuracy_pct}%",
        f"  recall by predicted regime: {r.regime_accuracy.by_regime_recall}",
        "",
        "Static benchmark:",
        _fmt_metrics(r.static_metrics, "  "),
        "Regime-scaled strategy:",
        _fmt_metrics(r.scaled_metrics, "  "),
        "",
        "Drawdown suppression:",
        f"  static maxDD={r.drawdown_suppression.static_max_dd_pct}%  "
        f"scaled maxDD={r.drawdown_suppression.scaled_max_dd_pct}%  "
        f"suppression={r.drawdown_suppression.suppression_pct}%",
        f"  worst week: static {r.drawdown_suppression.static_worst_week_pct}% "
        f"vs scaled {r.drawdown_suppression.scaled_worst_week_pct}%",
        f"  avg risk budget={r.drawdown_suppression.avg_risk_budget}  "
        f"time above floor={r.drawdown_suppression.time_in_market_pct}%",
        "",
        "Notes:",
    ]
    lines += [f"  - {n}" for n in r.notes]
    return "\n".join(lines)


def _fmt_metrics(m: StrategyMetrics, pad: str = "") -> str:
    return (f"{pad}totRet={m.total_return_pct}% annRet={m.ann_return_pct}% "
            f"vol={m.ann_vol_pct}% sharpe={m.sharpe} sortino={m.sortino} "
            f"calmar={m.calmar} maxDD={m.max_drawdown_pct}% ({m.n_weeks}w)")


__all__ = [
    "run_backtest", "regime_accuracy_walk_forward", "risk_budget_series",
    "simulate_scaled", "compute_metrics", "realized_regime",
    "BacktestReport", "RegimeAccuracyReport", "StrategyMetrics",
    "DrawdownSuppressionReport", "format_report",
]
