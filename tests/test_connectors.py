"""Keyless connector tests (WS-A): parse recorded payloads, no live calls.
The autouse _no_network fixture (conftest) blocks accidental HTTP."""

from __future__ import annotations

import datetime as dt

from ipos.config.models import RegistryEntry, Source
from ipos.etl import dbnomics, ustreasury, yahoo


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


def _yahoo_chart(timestamps, opens, highs, lows, closes):
    return {"chart": {"result": [{
        "timestamp": timestamps,
        "indicators": {"quote": [{
            "open": opens, "high": highs, "low": lows, "close": closes,
        }]},
    }]}}


def test_yahoo_parses_close(monkeypatch):
    class Resp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self):
            return _yahoo_chart(
                [1752710400, 1752796800],  # 2025-07-17, 2025-07-18 UTC noon
                [1.0, 1.0], [1.0, 1.0], [1.0, 1.0], [100.0, None],
            )
    monkeypatch.setattr(yahoo.requests, "get", lambda *a, **k: Resp())
    df = yahoo.pull(_entry(), Source(type="yahoo", locator="^GSPC"), None, None)
    assert list(df["value"]) == [100.0]  # the None close is dropped


def test_yahoo_no_result_raises(monkeypatch):
    class Resp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"chart": {"result": []}}
    monkeypatch.setattr(yahoo.requests, "get", lambda *a, **k: Resp())
    try:
        yahoo.pull(_entry(), Source(type="yahoo", locator="^GSPC"), None, None)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass


def test_yahoo_pull_ohlc(monkeypatch):
    class Resp:
        status_code = 200
        def raise_for_status(self): pass
        def json(self):
            return _yahoo_chart(
                [1752710400], [99.0], [102.0], [98.0], [100.0],
            )
    monkeypatch.setattr(yahoo.requests, "get", lambda *a, **k: Resp())
    df = yahoo.pull_ohlc(_entry(), Source(type="yahoo", locator="^GSPC"), None, None)
    assert list(df.columns) == ["obs_date", "open", "high", "low", "close"]
    assert df.iloc[0]["high"] == 102.0 and df.iloc[0]["low"] == 98.0


# Source types that need no API key. The point of the rule below is that losing
# the FRED key (or FRED itself) must not take the whole pipeline down.
KEYLESS_TYPES = {"dbnomics", "stooq", "yahoo", "ustreasury", "manual_csv"}

# FRED series with NO free keyless alternative, each with the reason. This list
# replaced a blanket "every FRED entry has a dbnomics fallback" assertion, which
# passed only because the registry listed dbnomics legs that stopped working:
# FRED left DBnomics entirely (verified 2026-07-27, 93 providers, no FRED), so
# 15 such legs were dead and were removed. Keeping the exceptions explicit means
# a genuinely single-sourced series is visible in review rather than hidden
# behind a fallback that cannot fire.
NO_FREE_ALTERNATIVE = {
    "NFCI": "Chicago Fed proprietary composite; published via FRED only",
    "WALCL": "Fed H.4.1 balance sheet; no keyless machine feed wired",
    "WRESBAL": "same H.4.1 release as WALCL",
    "ICSA": "DOL claims; no keyless feed wired (DOL has one, not yet built)",
    "UMCSENT": "U. Michigan survey, licensed distribution",
    "DTWEXBGS": "Fed broad trade-weighted USD — the ICE dollar index (DXY) is a "
                "DIFFERENT index (120.5 vs 101.4 same day), so it is not a substitute",
    "DFF": "effective fed funds; NY Fed publishes EFFR keyless, connector not built",
}


def test_registry_multisource_no_single_critical():
    from ipos.config.load import load_registry
    reg = load_registry()
    assert not [e.series_id for e in reg.active() if e.critical and len(e.sources) < 2]


def test_every_fred_series_has_a_keyless_fallback_or_a_stated_reason():
    """Losing the FRED key must not be fatal. Any FRED-backed series without a
    keyless leg has to be listed in NO_FREE_ALTERNATIVE with a reason."""
    from ipos.config.load import load_registry

    reg = load_registry()
    unprotected = []
    for e in reg.active():
        types = {s.type for s in e.sources}
        if "fred" not in types:
            continue
        if types & KEYLESS_TYPES:
            continue
        if e.series_id in NO_FREE_ALTERNATIVE:
            continue
        unprotected.append(e.series_id)
    assert not unprotected, (
        "these FRED series have no keyless fallback and no stated reason — add a "
        f"real second source, or document why none exists: {unprotected}"
    )


def test_no_free_alternative_list_stays_honest():
    """The exception list must not rot: every entry must still be a real FRED
    series that still lacks a keyless leg. If someone wires a fallback, the
    entry has to be removed so the list keeps meaning something."""
    from ipos.config.load import load_registry

    reg = load_registry()
    by_id = {e.series_id: e for e in reg.active()}
    stale = []
    for sid in NO_FREE_ALTERNATIVE:
        entry = by_id.get(sid)
        if entry is None:
            stale.append(f"{sid} (no longer in the registry)")
        elif {s.type for s in entry.sources} & KEYLESS_TYPES:
            stale.append(f"{sid} (now HAS a keyless fallback — drop it from the list)")
    assert not stale, f"NO_FREE_ALTERNATIVE is out of date: {stale}"
