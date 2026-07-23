#!/usr/bin/env python
"""Regenerate the committed golden snapshot (C9 regression harness).

Run this ONLY when you have intentionally changed scoring/aggregation/
contradictions/snapshot output — and bump `scoring_version` in
`configs/scoring_defaults.yaml` in the same change so year-over-year
comparability is preserved (see risk #3 in 01_DECISION_ANALYSIS.md).

    uv run python scripts/update_golden.py

The golden is built from deterministic synthetic fixtures, so it is a pure
logic-regression guard (independent of live data).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ipos.golden import GOLDEN_PATH, build_golden_min


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        content = build_golden_min(Path(d))
    GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN_PATH.write_text(content, encoding="utf-8")
    print(f"wrote golden snapshot ({len(content)} bytes) -> {GOLDEN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
