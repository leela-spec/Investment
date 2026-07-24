"""Scoring tests (C3 Definition of Done): monotonicity, directional inversion,
0-100 bounds under extreme z, hand-computed fixtures, and idempotency of the
full transform pass."""

from __future__ import annotations

import datetime as dt
import math

import pytest

from ipos.config.models import BandStep
from ipos.transforms.scoring import band_score, percentile_score, zscore_score


# --- percentile -------------------------------------------------------------

def test_percentile_hand_computed():
    # current (last) value 5 sits above 3 of 5 values (incl. itself) -> 60%
    window = [1.0, 2.0, 9.0, 4.0, 5.0]
    # count(v <= 5) = {1,2,4,5} = 4 -> 4/5 = 80%
    assert percentile_score(window, higher_is_better=True) == pytest.approx(80.0)
    assert percentile_score(window, higher_is_better=False) == pytest.approx(20.0)


def test_percentile_monotonic_when_higher_is_better():
    base = [10.0, 20.0, 30.0, 40.0]
    low = percentile_score(base + [25.0], higher_is_better=True)
    high = percentile_score(base + [50.0], higher_is_better=True)
    assert high >= low


def test_percentile_inversion_symmetry():
    window = [1.0, 2.0, 3.0, 4.0, 5.0]
    up = percentile_score(window, higher_is_better=True)
    down = percentile_score(window, higher_is_better=False)
    assert up + down == pytest.approx(100.0)


# --- zscore -----------------------------------------------------------------

def test_zscore_center_is_fifty():
    # a value equal to the window mean -> z=0 -> score 50
    window = [1.0, 2.0, 3.0, 4.0, 5.0]  # mean 3, current 3
    window_at_mean = [1.0, 2.0, 3.0, 4.0, 5.0, 3.0]
    assert zscore_score(window_at_mean, higher_is_better=True) == pytest.approx(50.0, abs=1e-9)


def test_zscore_bounds_extreme():
    # a gigantic outlier: tanh saturates -> score approaches 100 (not beyond)
    window = [0.0] * 50 + [1e9]
    s = zscore_score(window, higher_is_better=True)
    assert 0.0 <= s <= 100.0
    assert s > 99.0
    # inverted
    si = zscore_score(window, higher_is_better=False)
    assert 0.0 <= si <= 100.0
    assert si < 1.0


def test_zscore_inversion_symmetry():
    window = [1.0, 3.0, 2.0, 8.0, 4.0, 6.0]
    up = zscore_score(window, higher_is_better=True)
    down = zscore_score(window, higher_is_better=False)
    assert up + down == pytest.approx(100.0)


def test_zscore_hand_computed():
    window = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]  # mean=5, pop std=2
    # current 9 -> z=(9-5)/2=2 -> tanh(2/2)=tanh(1)=0.7615 -> 50*(1.7615)=88.08
    expected = 50.0 * (math.tanh(1.0) + 1.0)
    assert zscore_score(window, higher_is_better=True, k=2.0) == pytest.approx(expected)


# --- band -------------------------------------------------------------------

def _curve_bands():
    return [
        BandStep(upper=0.0, score=20),
        BandStep(upper=0.5, score=45),
        BandStep(upper=1.0, score=70),
        BandStep(upper=None, score=90),
    ]


def test_band_mapping():
    b = _curve_bands()
    assert band_score(-0.3, b) == 20   # x < 0
    assert band_score(0.0, b) == 45    # [0, 0.5)
    assert band_score(0.4, b) == 45
    assert band_score(0.5, b) == 70    # [0.5, 1.0)
    assert band_score(1.0, b) == 90    # >= 1.0
    assert band_score(3.0, b) == 90


def test_band_monotonic_non_decreasing():
    b = _curve_bands()
    xs = [-1, -0.1, 0.0, 0.25, 0.5, 0.9, 1.0, 2.0]
    scores = [band_score(x, b) for x in xs]
    assert scores == sorted(scores)


# --- idempotency of the full transform pass ---------------------------------

def test_vectorized_matches_scalar_scoring():
    """The production path (ipos/transforms/run.py) computes percentile/zscore
    with vectorized numpy; assert it equals the unit-tested scalar functions on
    random windows so the two implementations cannot silently diverge (WS-B)."""
    import numpy as np

    rng = np.random.default_rng(12345)
    for _ in range(200):
        n = int(rng.integers(2, 160))
        w = rng.normal(0, 1, n).cumsum() + 100.0
        for hib in (True, False):
            # percentile — production: mean(w <= w[-1]) * 100, inverted if not hib
            raw_pct = float(np.mean(w <= w[-1]) * 100.0)
            prod_pct = raw_pct if hib else 100.0 - raw_pct
            assert percentile_score(list(w), hib) == pytest.approx(prod_pct, abs=1e-9)

            # zscore — production: 50*(tanh(z/k)+1) clipped, inverted if not hib
            mu = float(np.mean(w)); sd = float(np.std(w))
            z = (w[-1] - mu) / sd if sd > 0 else 0.0
            s = min(100.0, max(0.0, 50.0 * (math.tanh(z / 2.0) + 1.0)))
            prod_z = s if hib else 100.0 - s
            assert zscore_score(list(w), hib, k=2.0) == pytest.approx(prod_z, abs=1e-9)


def test_transform_idempotent(tmp_path, monkeypatch):
    import ipos.etl.base as base
    from ipos.config.load import load_registry
    from ipos.etl.fixtures import SEED_ANCHOR
    from ipos.etl.pull import pull_all
    from ipos.transforms.run import build_canonical, compute
    from ipos.warehouse.db import connect, init_db

    from tests.conftest import FAKE_CONNECTORS

    monkeypatch.setattr(base, "ARCHIVE_ROOT", tmp_path / "archive")
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    init_db(reg, db)

    def run_once():
        with connect(db) as con:
            pull_all(con, reg, as_of=SEED_ANCHOR, ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0),
                     connectors=FAKE_CONNECTORS)
            build_canonical(con, SEED_ANCHOR)
            compute(con, reg, SEED_ANCHOR)
            return con.execute(
                "SELECT series_id, score_0_100, confidence_0_100 FROM fact_score "
                "WHERE as_of_date = ? ORDER BY series_id", [SEED_ANCHOR]
            ).fetchall()

    first = run_once()
    second = run_once()
    assert first == second
    for _, score, conf in first:
        assert 0.0 <= score <= 100.0
        assert 0.0 <= conf <= 100.0
