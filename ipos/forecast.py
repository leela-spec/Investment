"""Forecast log: write down this week's calls so they can be scored later.

The point of this module is a discipline, not a feature. A Brier score or a
reliability diagram only counts as evidence about the system if the forecast was
recorded BEFORE its outcome window opened — dated, quantified, with a fixed
horizon and an unambiguous resolution rule. That property cannot be recovered
retroactively, which is why the logging ships now and the report section does
not (01_DECISION_ANALYSIS.md amendment 2026-07-29, item 17).

Three properties make the log trustworthy rather than decorative:

1. **Append-only in behaviour.** Inserts use ON CONFLICT DO NOTHING, so
   re-running a past week — the pipeline is idempotent and re-runnable — can
   never rewrite a call already made. Changing a weight and re-running does not
   let the system retro-fit its own record.
2. **Frozen goalposts.** ``baseline_value`` and ``hurdle`` are copied into the
   row, not looked up at resolution time. This project has twice had stored
   history move underneath it (the 2026-07-27 synthetic purge shifted 24 of 26
   weeks of Credit scores), and a claim whose target moves with the warehouse is
   not a claim.
3. **Mechanical resolution.** ``resolve`` needs exactly one new number: the
   benchmark's value on ``resolve_on``. No judgement, no discretion.

No wall clock anywhere: everything derives from ``as_of`` and stored data, so
the weekly run stays deterministic.
"""

from __future__ import annotations

import datetime as dt
import statistics

import duckdb
import yaml

from ipos.config.load import CONFIG_DIR

TARGETS_PATH = CONFIG_DIR / "forecast_targets.yaml"

#: Trailing window used to compute the hurdle (the benchmark's typical move over
#: the horizon). Matches the 156-week percentile lookback in
#: configs/scoring_defaults.yaml so the forecast rests on the same span of
#: history the score itself was ranked against.
HURDLE_LOOKBACK_WEEKS = 156

#: A hurdle needs enough horizon-length observations to be a median rather than
#: an anecdote. Below this the dimension is skipped for that horizon and the
#: reason is reported, instead of logging a claim against a made-up target.
MIN_HURDLE_SAMPLES = 12


def load_targets(path=None) -> dict:
    """Load configs/forecast_targets.yaml (which dimensions are falsifiable)."""
    with open(path or TARGETS_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def tilt_to_probability(tilt: float, span: float) -> float:
    """Map a [-1,+1] tilt monotonically onto a capped probability.

    Capped at 0.5 ± span (0.20..0.80 by default) on purpose. The Brier score
    punishes overconfidence asymmetrically, and nothing in this system justifies
    a claim stronger than 4-to-1 — so it is not permitted to make one."""
    return round(0.5 + span * max(-1.0, min(1.0, float(tilt))), 6)


def _weekly_series(con: duckdb.DuckDBPyConnection, series_id: str, upto: dt.date):
    """Ordered (week, value) for one series up to and including ``upto``."""
    return con.execute(
        "SELECT as_of_date, value FROM fact_weekly WHERE series_id = ? "
        "AND as_of_date <= ? ORDER BY as_of_date",
        [series_id, upto],
    ).fetchall()


def _hurdle(history, horizon: int) -> float | None:
    """Median change in the benchmark over ``horizon`` weeks, across the trailing
    window. This is the bar the claim must beat.

    Using the benchmark's own typical move — rather than simply "did it rise" —
    keeps the base rate near 50%. Equities rise over most 13-week windows, so
    "SPX goes up" would score well with no skill at all and make the resulting
    Brier number uninterpretable."""
    values = [v for _wk, v in history[-(HURDLE_LOOKBACK_WEEKS + horizon):]]
    changes = [values[i] - values[i - horizon] for i in range(horizon, len(values))]
    if len(changes) < MIN_HURDLE_SAMPLES:
        return None
    return round(statistics.median(changes), 6)


def record(
    con: duckdb.DuckDBPyConnection,
    as_of: dt.date,
    scoring_version: str,
    targets: dict | None = None,
) -> dict:
    """Write this week's falsifiable calls into ``log_forecast``.

    Returns a summary for the run log. Never raises on a missing benchmark or
    thin history — it skips that call and says so, because a run must not fail
    over its own bookkeeping."""
    cfg = targets if targets is not None else load_targets()
    span = float(cfg.get("probability_span", 0.30))
    min_tilt = float(cfg.get("min_abs_tilt", 0.2))
    horizons = list(cfg.get("horizons_weeks") or [4, 13, 26])
    target_map = cfg.get("targets") or {}

    tilts = dict(con.execute(
        "SELECT stance_dim, stance_value FROM agg_module WHERE as_of_date = ?",
        [as_of],
    ).fetchall())

    written = 0
    skipped: list[str] = []
    for dim in sorted(target_map):
        tilt = tilts.get(dim)
        if tilt is None:
            skipped.append(f"{dim}: no stance value this week")
            continue
        if abs(float(tilt)) < min_tilt:
            # Not a call. Logging it would pad the record with trivially
            # well-calibrated near-coin-flips and flatter the eventual score.
            skipped.append(f"{dim}: |tilt| {abs(float(tilt)):.2f} < {min_tilt}")
            continue

        spec = target_map[dim]
        series_id = spec["series"]
        direction = int(spec["direction"])
        history = _weekly_series(con, series_id, as_of)
        if not history or history[-1][0] != as_of:
            skipped.append(f"{dim}: no {series_id} value at {as_of}")
            continue
        baseline = float(history[-1][1])
        probability = tilt_to_probability(float(tilt), span)

        for horizon in horizons:
            hurdle = _hurdle(history, horizon)
            if hurdle is None:
                skipped.append(f"{dim}/{horizon}w: too little {series_id} history for a hurdle")
                continue
            resolve_on = as_of + dt.timedelta(weeks=horizon)
            rises = "rises" if direction > 0 else "falls"
            criterion = (
                f"{series_id} {rises} by more than {abs(hurdle):.6g} "
                f"(its median {horizon}w move) from {baseline:.6g} "
                f"between {as_of} and {resolve_on}"
            )
            con.execute(
                """
                INSERT INTO log_forecast
                  (as_of_date, stance_dim, horizon_weeks, benchmark_series, direction,
                   tilt, probability, baseline_value, hurdle, resolve_on, criterion,
                   scoring_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT DO NOTHING
                """,
                [as_of, dim, horizon, series_id, direction, round(float(tilt), 6),
                 probability, round(baseline, 6), hurdle, resolve_on, criterion,
                 scoring_version],
            )
            written += 1

    return {"written": written, "skipped": skipped,
            "dims": sorted({d for d in target_map if d in tilts})}


def resolve(con: duckdb.DuckDBPyConnection, upto: dt.date) -> list[dict]:
    """Settle every logged call whose horizon has completed by ``upto``.

    Pure computation over stored data — nothing is written, so this is safe to
    call at any time and cannot corrupt the record it reads. Exists now, ahead
    of any display, to prove the recorded criteria are actually resolvable: a
    frozen rule nobody has ever settled is a rule that might not work.

    Returns one dict per resolved call with ``outcome`` (1/0) and the realised
    move, ready for a Brier score: ``mean((probability - outcome) ** 2)``.
    """
    rows = con.execute(
        """
        SELECT f.as_of_date, f.stance_dim, f.horizon_weeks, f.benchmark_series,
               f.direction, f.tilt, f.probability, f.baseline_value, f.hurdle,
               f.resolve_on, f.scoring_version, w.value
        FROM log_forecast f
        JOIN fact_weekly w
          ON w.series_id = f.benchmark_series AND w.as_of_date = f.resolve_on
        WHERE f.resolve_on <= ?
        ORDER BY f.as_of_date, f.stance_dim, f.horizon_weeks
        """,
        [upto],
    ).fetchall()

    out = []
    for (aod, dim, horizon, series_id, direction, tilt, prob,
         baseline, hurdle, resolve_on, sv, final) in rows:
        realized = float(final) - float(baseline)
        # Did it beat its own typical move, in the direction claimed?
        margin = (realized - float(hurdle)) * int(direction)
        out.append({
            "as_of": aod, "stance_dim": dim, "horizon_weeks": horizon,
            "benchmark_series": series_id, "tilt": tilt, "probability": prob,
            "realized_change": round(realized, 6), "hurdle": hurdle,
            "margin": round(margin, 6),
            "outcome": 1 if margin > 0 else 0,
            "resolve_on": resolve_on, "scoring_version": sv,
        })
    return out


def brier(resolved: list[dict]) -> dict | None:
    """Brier score over resolved calls, beside the two baselines that make it
    interpretable.

    Reporting the score alone would be meaningless — 0.24 is good or terrible
    depending on the base rate. ``always_50`` is the no-information forecaster
    (a fixed 0.25); ``base_rate`` is the forecaster that always predicts the
    observed frequency, which is the real bar to clear. Returns None rather than
    a flattering small-sample number when there is nothing to say."""
    if not resolved:
        return None
    n = len(resolved)
    outcomes = [r["outcome"] for r in resolved]
    rate = sum(outcomes) / n
    return {
        "n": n,
        "brier": round(sum((r["probability"] - r["outcome"]) ** 2 for r in resolved) / n, 6),
        "always_50": round(sum((0.5 - o) ** 2 for o in outcomes) / n, 6),
        "base_rate": round(sum((rate - o) ** 2 for o in outcomes) / n, 6),
        "observed_rate": round(rate, 6),
        # scoring_version segmentation matters: calls made under different
        # methods are not comparable, so pooling across a bump is a bug.
        "scoring_versions": sorted({r["scoring_version"] for r in resolved}),
    }
