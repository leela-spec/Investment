"""Economic calendar tests (WS-D): schedule rules are deterministic and fire on
the right dates; the window covers this + next week; no network."""

from __future__ import annotations

import datetime as dt

from ipos.econ_calendar import _first_business_day, _matches, events_for


def test_nth_weekday_first_friday():
    # July 2026: Fridays are 3,10,17,24,31 -> 1st Friday = 3rd
    assert _matches(dt.date(2026, 7, 3), {"type": "nth_weekday", "n": 1, "weekday": 4})
    assert not _matches(dt.date(2026, 7, 10), {"type": "nth_weekday", "n": 1, "weekday": 4})
    # 3rd Friday (OPEX) = 17th
    assert _matches(dt.date(2026, 7, 17), {"type": "nth_weekday", "n": 3, "weekday": 4})


def test_first_business_day():
    # 1 July 2026 is a Wednesday -> first business day
    assert _first_business_day(2026, 7) == dt.date(2026, 7, 1)
    # 1 Aug 2026 is a Saturday -> first business day is Mon 3 Aug
    assert _first_business_day(2026, 8) == dt.date(2026, 8, 3)


def test_dates_rule():
    r = {"type": "dates", "dates": ["2026-07-29"]}
    assert _matches(dt.date(2026, 7, 29), r)
    assert not _matches(dt.date(2026, 7, 28), r)


def test_events_for_seed_week_is_deterministic():
    as_of = dt.date(2026, 7, 17)  # a Friday
    a = events_for(as_of)
    b = events_for(as_of)
    assert a == b
    names = {e["name"] for e in a}
    # OPEX (3rd Friday = 17th) lands in this week
    assert "Options Expiry (monthly OPEX)" in names
    for e in a:
        assert e["when"] in ("this_week", "next_week")
        assert dt.date.fromisoformat(e["date"]) <= as_of + dt.timedelta(days=7)
