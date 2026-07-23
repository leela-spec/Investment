"""Manual-CSV connector — the inbox for anything unautomatable (e.g. a broker
export, or a hand-downloaded series). Matches ``data/inbox/<locator glob>``;
expects columns date,value (case-insensitive). Processed files are left in
place (archiving handles provenance)."""

from __future__ import annotations

import datetime as dt

import pandas as pd

from ipos.config.load import REPO_ROOT
from ipos.config.models import RegistryEntry, Source

INBOX = REPO_ROOT / "data" / "inbox"


def pull(
    entry: RegistryEntry,
    source: Source,
    start: dt.date | None,
    end: dt.date | None,
) -> pd.DataFrame:
    matches = sorted(INBOX.glob(source.locator))
    if not matches:
        raise FileNotFoundError(f"no inbox file matching {source.locator}")
    latest = matches[-1]
    raw = pd.read_csv(latest)
    cols = {c.lower(): c for c in raw.columns}
    if "date" not in cols or "value" not in cols:
        raise RuntimeError(f"{latest.name}: need date,value columns; got {list(raw.columns)}")
    df = raw.rename(columns={cols["date"]: "obs_date", cols["value"]: "value"})
    return df[["obs_date", "value"]]
