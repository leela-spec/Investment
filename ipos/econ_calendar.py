"""Free economic-event calendar (WS-D).

Deterministic from ``configs/calendar.yaml`` schedule rules + the ``as_of``
date — no scraping, no API key, no wall-clock. Surfaces the macro events in the
current and next week for "why now" context in the snapshot and report. This is
the lighter alternative the user chose over a news pipeline.
"""

from __future__ import annotations

import calendar as _stdcal
import datetime as dt
from pathlib import Path

import yaml

from ipos.config.load import REPO_ROOT

CALENDAR_YAML = REPO_ROOT / "configs" / "calendar.yaml"


def _first_business_day(year: int, month: int) -> dt.date:
    d = dt.date(year, month, 1)
    while d.weekday() >= 5:  # Sat/Sun -> next
        d += dt.timedelta(days=1)
    return d


def _matches(d: dt.date, rule: dict) -> bool:
    kind = rule.get("type")
    if kind == "nth_weekday":
        return d.weekday() == rule["weekday"] and (d.day - 1) // 7 == rule["n"] - 1
    if kind == "first_business_day":
        return d == _first_business_day(d.year, d.month)
    if kind == "day_of_month":
        return d.day == rule["day"]
    if kind == "dates":
        return d.isoformat() in set(rule.get("dates", []))
    return False


def events_for(as_of: dt.date, path: Path | None = None) -> list[dict]:
    """Return macro events in the week ending ``as_of`` (Friday) and, if
    configured, the following week. Deterministic; sorted by date."""
    p = path or CALENDAR_YAML
    if not p.exists():
        return []
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    win = cfg.get("window", {})
    this_days = int(win.get("this_week_days", 5))
    include_next = bool(win.get("include_next_week", True))

    start = as_of - dt.timedelta(days=this_days - 1)     # Mon..Fri(as_of)
    end = as_of + dt.timedelta(days=7) if include_next else as_of

    out: list[dict] = []
    n_days = (end - start).days + 1
    for i in range(n_days):
        d = start + dt.timedelta(days=i)
        for ev in cfg.get("events", []):
            if _matches(d, ev["rule"]):
                out.append({
                    "name": ev["name"],
                    "category": ev.get("category"),
                    "date": d.isoformat(),
                    "when": "this_week" if d <= as_of else "next_week",
                    "approximate": bool(ev["rule"].get("approximate", False)),
                })
    out.sort(key=lambda e: (e["date"], e["name"]))
    return out
