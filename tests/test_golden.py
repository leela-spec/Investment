"""Golden-snapshot regression (C9). Rebuilds the snapshot from deterministic
fixtures via the same code path used to generate the committed golden, and
asserts byte-identical output. A diff means scoring/aggregation/contradictions/
snapshot logic changed — intended changes are landed by running
`scripts/update_golden.py` (with a `scoring_version` bump)."""

from __future__ import annotations

from ipos.golden import GOLDEN_PATH, build_golden_min


def test_snapshot_matches_golden(tmp_path):
    assert GOLDEN_PATH.exists(), "run scripts/update_golden.py to create the golden"
    expected = GOLDEN_PATH.read_text(encoding="utf-8")
    actual = build_golden_min(tmp_path)
    assert actual == expected, (
        "snapshot output drifted from the committed golden. If this change is "
        "intentional, run `uv run python scripts/update_golden.py` and bump "
        "scoring_version in configs/scoring_defaults.yaml."
    )
