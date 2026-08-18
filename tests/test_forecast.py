"""Forecast-log tests (01_DECISION_ANALYSIS.md amendment 2026-07-29, item 17).

These test a discipline rather than a feature. The log is only evidence if a
call cannot be rewritten after the fact and its goalposts cannot drift, so those
two properties get the most direct tests here.
"""

from __future__ import annotations

import datetime as dt

import pytest

from ipos.forecast import (
    brier,
    load_targets,
    record,
    resolve,
    tilt_to_probability,
)
from ipos.warehouse.db import connect


def _rows(con):
    return con.execute(
        "SELECT as_of_date, stance_dim, horizon_weeks, benchmark_series, direction, "
        "tilt, probability, baseline_value, hurdle, resolve_on, criterion, "
        "scoring_version FROM log_forecast ORDER BY stance_dim, horizon_weeks"
    ).fetchall()


def test_targets_config_is_coherent():
    """Every target must name a direction and justify itself, and no dimension
    may be both forecast and excluded."""
    cfg = load_targets()
    targets, excluded = cfg["targets"], cfg["excluded"]
    assert not (set(targets) & set(excluded)), "a dimension is both forecast and excluded"
    for dim, spec in targets.items():
        assert spec["direction"] in (1, -1), dim
        assert spec["series"], dim
        # the direction is the easiest thing to get backwards and the most
        # damaging (it would score a right call as wrong), so it must be argued
        assert len(spec.get("note", "")) > 40, f"{dim} has no reasoning for its direction"
    for dim, why in excluded.items():
        assert len(why) > 40, f"{dim} is excluded without a reason"
    assert cfg["horizons_weeks"] == [4, 13, 26]


def test_probability_is_capped_both_ways():
    """A Brier score punishes overconfidence hard, so the mapping must never
    emit a near-certainty no matter how extreme the tilt."""
    span = load_targets()["probability_span"]
    assert tilt_to_probability(0.0, span) == 0.5
    assert tilt_to_probability(1.0, span) == pytest.approx(0.8)
    assert tilt_to_probability(-1.0, span) == pytest.approx(0.2)
    # out-of-range input is clamped, not extrapolated
    assert tilt_to_probability(5.0, span) == pytest.approx(0.8)
    assert tilt_to_probability(-5.0, span) == pytest.approx(0.2)
    # monotonic
    probs = [tilt_to_probability(t / 10, span) for t in range(-10, 11)]
    assert probs == sorted(probs)


def test_record_writes_calls_for_strong_tilts_only(populated_db, as_of):
    db, reg = populated_db
    with connect(db) as con:
        cfg = load_targets()
        summary = record(con, as_of, reg.defaults.scoring_version)
        rows = _rows(con)

    assert summary["written"] == len(rows)
    tilt_by_dim = {r[1]: r[5] for r in rows}
    for dim, tilt in tilt_by_dim.items():
        assert abs(tilt) >= cfg["min_abs_tilt"], (
            f"{dim} logged a non-call at tilt {tilt}; weak tilts must be skipped "
            "or they pad the record with trivially calibrated coin-flips"
        )
    # only dimensions declared falsifiable, never the excluded macro readings
    assert set(tilt_by_dim) <= set(cfg["targets"])
    assert not (set(tilt_by_dim) & set(cfg["excluded"]))
    # every logged call carries a full, frozen resolution rule
    for r in rows:
        aod, dim, horizon, series, direction, tilt, prob, base, hurdle, res_on, crit, sv = r
        assert res_on == aod + dt.timedelta(weeks=horizon)
        assert direction in (1, -1)
        assert 0.2 <= prob <= 0.8
        assert series in crit and sv == "1.0"


def test_a_logged_call_can_never_be_rewritten(populated_db, as_of):
    """The core honesty property. The pipeline is idempotent and re-runnable, so
    without ON CONFLICT DO NOTHING a re-run after a weights change would let the
    system quietly retro-fit its own track record."""
    db, reg = populated_db
    with connect(db) as con:
        record(con, as_of, reg.defaults.scoring_version)
        before = _rows(con)

        # simulate the operator changing their mind and re-running the week
        con.execute(
            "UPDATE agg_module SET stance_value = -stance_value WHERE as_of_date = ?",
            [as_of],
        )
        record(con, as_of, "9.9")
        after = _rows(con)

    assert after == before, "a re-run overwrote calls that had already been made"


def test_hurdle_and_baseline_are_frozen_against_history_changing(populated_db, as_of):
    """This project has twice had stored history move underneath it (the
    2026-07-27 synthetic purge shifted 24 of 26 weeks of Credit scores). A claim
    whose target moves with the warehouse is not a claim, so the goalposts are
    copied into the row rather than looked up at resolution time."""
    db, reg = populated_db
    with connect(db) as con:
        record(con, as_of, reg.defaults.scoring_version)
        frozen = {(r[1], r[2]): (r[7], r[8]) for r in _rows(con)}

        # rewrite the benchmark's entire past — the kind of thing a backfill or a
        # purge does — leaving the current week alone
        con.execute(
            "UPDATE fact_weekly SET value = value * 2 WHERE series_id = 'SPX' "
            "AND as_of_date < ?", [as_of],
        )
        after = {(r[1], r[2]): (r[7], r[8]) for r in _rows(con)}

    assert after == frozen, "rewriting history moved the goalposts of a logged call"


def test_calls_are_not_resolvable_before_their_horizon_completes(populated_db, as_of):
    db, reg = populated_db
    with connect(db) as con:
        record(con, as_of, reg.defaults.scoring_version)
        # nothing has had time to resolve as of the week it was written
        assert resolve(con, as_of) == []
        assert brier(resolve(con, as_of)) is None, (
            "brier() must return None on an empty set rather than a flattering "
            "small-sample number"
        )


def test_resolution_is_mechanical_and_direction_aware(populated_db, as_of):
    """Proves the frozen criterion can actually be settled, and that an INVERTED
    target scores correctly -- getting direction backwards would mark a right
    call wrong, which is worse than not scoring at all."""
    db, reg = populated_db
    horizon = 4
    with connect(db) as con:
        record(con, as_of, reg.defaults.scoring_version)
        rows = con.execute(
            "SELECT stance_dim, benchmark_series, direction, baseline_value, hurdle "
            "FROM log_forecast WHERE horizon_weeks = ?", [horizon],
        ).fetchall()
        assert rows, "no calls at this horizon to resolve"

        resolve_on = as_of + dt.timedelta(weeks=horizon)
        # Plant an outcome that CLEARS each hurdle in the claimed direction, so
        # every call must resolve to 1 regardless of its sign.
        for _dim, series, direction, baseline, hurdle in rows:
            winning = baseline + direction * (abs(hurdle) + 1.0)
            con.execute(
                "INSERT OR REPLACE INTO fact_weekly (series_id, as_of_date, value, "
                "vintage_id, obs_date, ingested_at) VALUES (?, ?, ?, 'test', ?, ?)",
                [series, resolve_on, winning, resolve_on, dt.datetime(2026, 1, 1)],
            )

        resolved = resolve(con, resolve_on)

    assert len(resolved) == len(rows)
    assert all(r["outcome"] == 1 for r in resolved), (
        f"a call that beat its hurdle in the claimed direction scored 0: "
        f"{[(r['stance_dim'], r['margin']) for r in resolved if r['outcome'] == 0]}"
    )

    score = brier(resolved)
    assert score["n"] == len(rows)
    # the baselines that make the number interpretable must be reported with it
    assert "always_50" in score and "base_rate" in score
    assert score["scoring_versions"] == ["1.0"]


def test_brier_punishes_confident_wrongness_asymmetrically():
    """The property that makes this worth doing at all."""
    confident_right = brier([{"probability": 0.9, "outcome": 1, "scoring_version": "1.0"}])
    confident_wrong = brier([{"probability": 0.9, "outcome": 0, "scoring_version": "1.0"}])
    assert confident_right["brier"] == pytest.approx(0.01)
    assert confident_wrong["brier"] == pytest.approx(0.81)


def test_weekly_run_logs_forecasts_as_its_own_stage(populated_db, as_of):
    """The stage must appear in run_log like every other pipeline stage, so the
    record has an audit trail of when it was written. (Exports go to the isolated
    dir from conftest's autouse ``_no_operator_exports``.)"""
    from ipos.run import run_weekly

    db, reg = populated_db
    res = run_weekly(as_of=as_of, db_path=db, registry=reg, seed_offline=True)
    assert "forecast" in res.stages
    with connect(db, read_only=True) as con:
        stages = [r[0] for r in con.execute(
            "SELECT stage FROM run_log WHERE as_of_date = ?", [as_of]
        ).fetchall()]
        assert "forecast" in stages
        assert con.execute("SELECT count(*) FROM log_forecast").fetchone()[0] > 0
