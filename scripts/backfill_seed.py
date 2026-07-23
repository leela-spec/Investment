#!/usr/bin/env python
"""Thin wrapper around ``ipos.backfill`` so the seed step is runnable as a
plain script (``python scripts/backfill_seed.py``) as well as via the
``ipos-backfill`` entry point.

RUN EARLY on a networked machine with a FRED key: FRED's ICE BofA OAS series
carry only a rolling 3-year window, so archiving now is the only way to keep
older OAS history. Nothing else in Phase 1 is time-sensitive.
"""

from __future__ import annotations

import sys

from ipos.backfill import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
