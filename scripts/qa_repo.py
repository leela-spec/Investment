#!/usr/bin/env python3
"""IPOS Playbook Repo QA

Runs local integrity + referential tests to ensure your repo is internally consistent.

Usage:
  python scripts/qa_repo.py

Exit codes:
  0 = all required tests passed
  2 = one or more required tests failed
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from glob import glob
from typing import Any, Dict, List, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANIFEST = os.path.join(REPO_ROOT, "MANIFEST.json")
PROCESS = os.path.join(REPO_ROOT, "03_extract", "process.jsonl")
INDICATORS = os.path.join(REPO_ROOT, "03_extract", "indicators.jsonl")
RULES = os.path.join(REPO_ROOT, "03_extract", "rules.jsonl")
MODULES_DIR = os.path.join(REPO_ROOT, "04_playbook", "modules")

MAX_PDF_PAGES_DEFAULT = 231  # change if you update the PDF


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                raise ValueError(f"Invalid JSON on {path}:{i}: {e}")
    return rows


def assert_unique_ids(rows: List[Dict[str, Any]], file_label: str) -> Tuple[bool, str]:
    ids = [r.get("id") for r in rows]
    c = Counter(ids)
    dups = [k for k, v in c.items() if v > 1]
    missing = [i for i in ids if not i]
    if missing:
        return False, f"{file_label}: missing 'id' on {len(missing)} rows"
    if dups:
        return False, f"{file_label}: duplicate ids: {dups[:10]}" + ("..." if len(dups) > 10 else "")
    return True, f"{file_label}: unique ids OK ({len(ids)})"


def parse_front_matter(md_text: str) -> Dict[str, str]:
    # very small parser: expects --- ... --- at top
    if not md_text.startswith("---"):
        return {}
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = parts[1].strip()
    out: Dict[str, str] = {}
    for line in fm.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def extract_backticked_vars(text: str) -> set[str]:
    return set(re.findall(r"`([a-zA-Z0-9_]+)`", text))


def extract_page_numbers(page_refs: List[str]) -> List[int]:
    nums: List[int] = []
    for pr in page_refs:
        m = re.match(r"p(\d+)", str(pr).strip())
        if m:
            nums.append(int(m.group(1)))
    return nums


def main() -> int:
    failures: List[str] = []
    warnings: List[str] = []

    # ---- existence
    for p in [MANIFEST, PROCESS, INDICATORS, RULES, MODULES_DIR]:
        if not os.path.exists(p):
            failures.append(f"Missing required path: {p}")

    if failures:
        print("\n".join(failures))
        return 2

    # ---- load manifest + data
    manifest = json.load(open(MANIFEST, "r", encoding="utf-8"))
    proc = read_jsonl(PROCESS)
    ind = read_jsonl(INDICATORS)
    rules = read_jsonl(RULES)
    modules = sorted(glob(os.path.join(MODULES_DIR, "*.md")))

    # ---- Test 01: counts match manifest
    expected = manifest.get("counts", {})
    actual = {
        "03_extract/process.jsonl": len(proc),
        "03_extract/indicators.jsonl": len(ind),
        "03_extract/rules.jsonl": len(rules),
        "04_playbook/modules": len(modules),
    }
    for k, v in expected.items():
        if actual.get(k) != v:
            failures.append(f"Count mismatch for {k}: expected {v}, got {actual.get(k)}")
    if not any("Count mismatch" in f for f in failures):
        print("PASS: manifest counts match actual files")

    # ---- Test 02: unique ids
    for rows, label in [(proc, "process.jsonl"), (ind, "indicators.jsonl"), (rules, "rules.jsonl")]:
        ok, msg = assert_unique_ids(rows, label)
        if not ok:
            failures.append(msg)
        else:
            print(f"PASS: {msg}")

    # ---- Test 03: module_id matches filename
    for mpath in modules:
        fname = os.path.basename(mpath).replace(".md", "")
        txt = open(mpath, "r", encoding="utf-8").read()
        fm = parse_front_matter(txt)
        mid = fm.get("module_id")
        if mid != fname:
            failures.append(f"Module id mismatch: {mpath} has module_id={mid} (expected {fname})")
    if not any("Module id mismatch" in f for f in failures):
        print(f"PASS: module_id matches filenames ({len(modules)})")

    # ---- Test 04: modules reference only known tech_* indicators
    ind_ids = {r["id"] for r in ind}
    for mpath in modules:
        txt = open(mpath, "r", encoding="utf-8").read()
        vars_ = {v for v in extract_backticked_vars(txt) if v.startswith("tech_")}
        missing = sorted([v for v in vars_ if v not in ind_ids])
        if missing:
            failures.append(f"{os.path.basename(mpath)} references unknown indicators: {missing}")
    if not any("references unknown indicators" in f for f in failures):
        print("PASS: all tech_* references in modules exist in indicators.jsonl")

    # ---- Test 05: page_refs within PDF bounds
    max_pages = MAX_PDF_PAGES_DEFAULT
    for rows, label in [(proc, "process"), (ind, "indicators"), (rules, "rules")]:
        for row in rows:
            nums = extract_page_numbers(row.get("page_refs", []))
            for n in nums:
                if not (1 <= n <= max_pages):
                    failures.append(f"{label}:{row.get('id')} has out-of-range page ref p{n} (max {max_pages})")
    if not any("out-of-range page ref" in f for f in failures):
        print(f"PASS: all page_refs within 1..{max_pages}")

    # ---- Test 06: composite indicator policy smoke test
    def row_str(r: Dict[str, Any]) -> str:
        return json.dumps(r, ensure_ascii=False).lower()

    bad_terms = ["fear", "greed", "goersch trend", "fear & greed"]
    bad = []
    for r in ind:
        s = row_str(r)
        if any(t in s for t in bad_terms):
            bad.append(r["id"])
    if bad:
        warnings.append(f"Composite-policy check: indicators mention composite/proprietary terms: {bad}")
    else:
        print("PASS: composite-policy smoke test")

    # ---- Test 07: missing modules referenced in rules (informational)
    module_ids = {os.path.basename(p).replace(".md", "") for p in modules}
    applies = set()
    for r in rules:
        for a in r.get("applies_to", []):
            applies.add(a)

    likely_modules = sorted([
        a for a in applies
        if a.isupper()
        and a not in module_ids
        and a not in {"TREND_HIERARCHY", "TREND_STRUCTURE"}
    ])
    if likely_modules:
        warnings.append("Rules reference module/concept names without module files yet: " + ", ".join(likely_modules))

    # ---- Test 08: needs_verification report (informational)
    nv = [r["id"] for r in rules if r.get("needs_verification") is True]
    if nv:
        warnings.append(f"{len(nv)} rules marked needs_verification=true. Example: {nv[:10]}")

    # ---- report
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f" - {f}")
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f" - {w}")

    if failures:
        return 2
    print("\nALL REQUIRED TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
