"""ETL tests (C2 Definition of Done): happy path archives + loads, a dead
primary source falls back to the next, and a fully offline pull replays the
archive and marks the result stale — with zero unhandled exceptions. All
connectors here are fakes; there are no live network calls."""

from __future__ import annotations

import datetime as dt

import pandas as pd
import pytest

from ipos.config.models import RegistryEntry, Source
from ipos.etl import base
from ipos.etl.base import archive_latest, run_fallback


@pytest.fixture(autouse=True)
def _isolate_archive(tmp_path, monkeypatch):
    monkeypatch.setattr(base, "ARCHIVE_ROOT", tmp_path / "archive")


def _entry(sources):
    return RegistryEntry(
        series_id="TST", name="test", asset_class="Rates",
        sources=sources, higher_is_better=True, scoring_method="percentile",
        module_id="RatesLiquidity",
    )


def _good_df():
    return pd.DataFrame(
        {"obs_date": [dt.date(2026, 7, 10), dt.date(2026, 7, 17)], "value": [1.0, 2.0]}
    )


def test_happy_path_archives_and_returns():
    entry = _entry([Source(type="fred", locator="X")])
    conns = {"fred": lambda e, s, a, b: _good_df()}
    res = run_fallback(entry, conns, pull_date=dt.date(2026, 7, 17))
    assert res.ok and not res.from_archive and not res.stale
    assert res.source_type == "fred"
    # archived verbatim before transform
    assert archive_latest("fred", "TST") is not None


def test_falls_back_to_next_source():
    entry = _entry([Source(type="fred", locator="X"), Source(type="stooq", locator="Y")])

    def dead(e, s, a, b):
        raise ConnectionError("primary down")

    conns = {"fred": dead, "stooq": lambda e, s, a, b: _good_df()}
    res = run_fallback(entry, conns, pull_date=dt.date(2026, 7, 17))
    assert res.ok and res.source_type == "stooq"
    assert any("fred" in a and "err" in a for a in res.attempts)


def test_offline_replays_archive_and_marks_stale():
    entry = _entry([Source(type="fred", locator="X")])
    # first, a successful pull to populate the archive
    run_fallback(entry, {"fred": lambda e, s, a, b: _good_df()},
                 pull_date=dt.date(2026, 7, 17))

    # now every source is dead -> replay archive, stale
    def dead(e, s, a, b):
        raise ConnectionError("offline")

    res = run_fallback(entry, {"fred": dead}, pull_date=dt.date(2026, 7, 24))
    assert res.ok and res.from_archive and res.stale
    assert res.error  # records why the live pull failed


def test_total_failure_no_exception():
    entry = _entry([Source(type="fred", locator="X")])

    def dead(e, s, a, b):
        raise ConnectionError("offline")

    # no archive exists for this fresh series -> empty, errored, but no raise
    res = run_fallback(entry, {"fred": dead}, pull_date=dt.date(2026, 7, 24))
    assert not res.ok and res.stale and res.error
