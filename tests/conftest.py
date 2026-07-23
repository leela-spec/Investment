"""Shared fixtures: a fully-populated warehouse at the seed anchor, built
offline from synthetic fixtures with an isolated archive."""

from __future__ import annotations

import datetime as dt

import pytest

import ipos.etl.base as etl_base
from ipos.aggregate.contradictions import evaluate as evaluate_contradictions
from ipos.aggregate.modules import aggregate
from ipos.config.load import load_registry
from ipos.etl.fixtures import SEED_ANCHOR, generate_series
from ipos.etl.pull import pull_all
from ipos.transforms.run import build_canonical, compute
from ipos.warehouse.db import connect, init_db


def _fixture_connector(entry, source, start, end):
    """Return deterministic synthetic data — NO network, NO archive."""
    return generate_series(entry)


FAKE_CONNECTORS = {
    "fred": _fixture_connector,
    "stooq": _fixture_connector,
    "manual_csv": _fixture_connector,
}


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Safety net: any accidental live HTTP call in a test fails immediately
    instead of hanging on a proxy timeout (enforces the no-live-calls rule)."""
    def _blocked(*a, **k):
        raise AssertionError("network access attempted in a test")
    monkeypatch.setattr("requests.get", _blocked)
    monkeypatch.setattr("requests.Session.request", _blocked)


@pytest.fixture
def as_of():
    return SEED_ANCHOR


@pytest.fixture
def populated_db(tmp_path, monkeypatch):
    """Return a path to a warehouse with the full pipeline run at SEED_ANCHOR,
    built entirely from fixtures (no live calls)."""
    monkeypatch.setattr(etl_base, "ARCHIVE_ROOT", tmp_path / "archive")
    reg = load_registry()
    db = tmp_path / "w.duckdb"
    init_db(reg, db)
    with connect(db) as con:
        pull_all(con, reg, as_of=SEED_ANCHOR, ingested_at=dt.datetime(2026, 7, 18, 8, 0, 0),
                 connectors=FAKE_CONNECTORS)
        build_canonical(con, SEED_ANCHOR)
        compute(con, reg, SEED_ANCHOR)
        aggregate(con, reg, SEED_ANCHOR)
        evaluate_contradictions(con, SEED_ANCHOR)
    return db, reg
