#!/usr/bin/env python
"""Provenance helper between the frozen extraction layer (03_extract) and the
ops registry (configs/registry.yaml).

The extraction JSONL is upstream knowledge; the runtime never reads it. The
registry is *seeded* from it and keeps an ``extract_ref`` back-pointer for
auditability to PDF page level. This script:

  1. verifies every ``extract_ref`` in the registry resolves to a real id in
     03_extract/indicators.jsonl (provenance integrity — fails loudly if not);
  2. lists extraction indicators not yet in the registry as expansion
     candidates (Phase 3 pool), so widening 20 -> 60 stays evidence-driven.

It does not modify the registry; it reports. (Editing the registry is a
deliberate, reviewed act — see the indicator-expansion protocol in C1.)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRACT = REPO_ROOT / "03_extract" / "indicators.jsonl"
REGISTRY = REPO_ROOT / "configs" / "registry.yaml"


def _extract_ids() -> set[str]:
    ids = set()
    for line in EXTRACT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            ids.add(json.loads(line)["id"])
    return ids


def main(argv: list[str] | None = None) -> int:
    extract_ids = _extract_ids()
    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    indicators = reg.get("indicators", [])

    refs = {i["series_id"]: i.get("extract_ref") for i in indicators}
    with_ref = {s: r for s, r in refs.items() if r}
    without_ref = sorted(s for s, r in refs.items() if not r)

    # 1) provenance integrity
    dangling = sorted(
        f"{s} -> {r}" for s, r in with_ref.items() if r not in extract_ids
    )
    print(f"registry: {len(indicators)} indicators, "
          f"{len(with_ref)} with extract_ref, {len(without_ref)} without")
    if dangling:
        print("DANGLING extract_ref (not found in 03_extract/indicators.jsonl):")
        for d in dangling:
            print(f"  {d}")
    else:
        print("provenance: OK — all extract_ref back-pointers resolve")

    if without_ref:
        print(f"no extract_ref yet ({len(without_ref)}): {', '.join(without_ref)}")

    # 2) expansion candidates (in extraction, not in registry)
    mapped = {r for r in with_ref.values()}
    candidates = sorted(extract_ids - mapped)
    print(f"\nexpansion candidates in 03_extract not yet mapped ({len(candidates)}):")
    for c in candidates:
        print(f"  {c}")

    return 1 if dangling else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
