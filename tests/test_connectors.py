"""Keyless connector tests (WS-A): parse recorded payloads, no live calls.
The autouse _no_network fixture (conftest) blocks accidental HTTP."""

from __future__ import annotations

import datetime as dt

from ipos.config.models import RegistryEntry, Source
from ipos.etl import dbnomics, ustreasury


def _entry():
    return RegistryEntry(
        series_id="X", name="x", asset_class="Rates",
        sources=[Source(type="dbnomics", locator="FRED/T10Y2Y")],
        higher_is_better=True, scoring_method="zscore", module_id="RatesLiquidity",
    )


def test_dbnomics_parses_period_value(monkeypatch):
    class Resp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self):
            return {"series": {"docs": [{
                "period": ["2026-07-03", "2026-07-10", "2026-07-17"],
                "value": [0.40, "NA", 0.55],
            }]}}
    monkeypatch.setattr(dbnomics.requests, "get", lambda *a, **k: Resp())
    df = dbnomics.pull(_entry(), Source(type="dbnomics", locator="FRED/T10Y2Y"),
                       None, dt.date(2026, 7, 17))
    assert list(df["value"]) == [0.40, 0.55]      # NA dropped
    assert str(df["obs_date"].iloc[0]) == "2026-07-03"


def test_dbnomics_full_locator(monkeypatch):
    captured = {}
    class Resp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"series": {"docs": [{"period": ["2026-07-17"], "value": [1.0]}]}}
    def fake_get(url, params=None, **k):
        captured["ids"] = params["series_ids"]
        return Resp()
    monkeypatch.setattr(dbnomics.requests, "get", fake_get)
    dbnomics.pull(_entry(), Source(type="dbnomics", locator="OECD/MEI/USA.X"), None, None)
    assert captured["ids"] == "OECD/MEI/USA.X"


def test_ustreasury_parses_tenor(monkeypatch):
    csv = "Date,3 Mo,2 Yr,10 Yr,30 Yr\n07/17/2026,5.10,4.20,4.30,4.50\n07/10/2026,5.11,4.22,4.33,4.55\n"
    class Resp:
        status_code = 200
        text = csv
    monkeypatch.setattr(ustreasury.requests, "get", lambda *a, **k: Resp())
    e = RegistryEntry(series_id="DGS10", name="10y", asset_class="Rates",
                      sources=[Source(type="ustreasury", locator="BC_10YEAR")],
                      higher_is_better=False, scoring_method="zscore", module_id="RatesLiquidity")
    df = ustreasury.pull(e, Source(type="ustreasury", locator="BC_10YEAR"),
                         dt.date(2026, 1, 1), dt.date(2026, 7, 17))
    assert set(df["value"]) == {4.30, 4.33}
    assert list(df.columns) == ["obs_date", "value"]


def test_registry_multisource_no_single_critical():
    from ipos.config.load import load_registry
    reg = load_registry()
    assert not [e.series_id for e in reg.active() if e.critical and len(e.sources) < 2]
    # every FRED entry now has a keyless dbnomics fallback
    for e in reg.active():
        types = [s.type for s in e.sources]
        if "fred" in types:
            assert "dbnomics" in types, f"{e.series_id} lacks keyless fallback"
