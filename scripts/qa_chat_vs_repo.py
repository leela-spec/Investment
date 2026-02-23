#!/usr/bin/env python3
"""Chat vs Repo Coverage QA (optional)

Goal:
- If you save a local chat transcript file (markdown),
  this script extracts JSONL lines that were generated in chat
  and checks that every extracted 'id' exists in the repo JSONLs.

Usage:
  python scripts/qa_chat_vs_repo.py logs/chat_transcript.md

Exit codes:
  0 = all chat ids found in repo
  3 = some chat ids missing in repo
"""

from __future__ import annotations

import json
import os
import sys
from typing import Set

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROCESS = os.path.join(REPO_ROOT, "03_extract", "process.jsonl")
INDICATORS = os.path.join(REPO_ROOT, "03_extract", "indicators.jsonl")
RULES = os.path.join(REPO_ROOT, "03_extract", "rules.jsonl")


def read_jsonl_ids(path: str) -> Set[str]:
    ids: Set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "id" in obj:
                ids.add(str(obj["id"]))
    return ids


def extract_chat_ids(chat_path: str) -> Set[str]:
    ids: Set[str] = set()
    with open(chat_path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not (s.startswith("{") and '"id"' in s):
                continue
            try:
                obj = json.loads(s)
                if isinstance(obj, dict) and "id" in obj:
                    ids.add(str(obj["id"]))
            except Exception:
                continue
    return ids


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/qa_chat_vs_repo.py logs/chat_transcript.md")
        return 1

    chat_path = sys.argv[1]
    if not os.path.exists(chat_path):
        print(f"Chat transcript not found: {chat_path}")
        return 1

    repo_ids = set()
    repo_ids |= read_jsonl_ids(PROCESS)
    repo_ids |= read_jsonl_ids(INDICATORS)
    repo_ids |= read_jsonl_ids(RULES)

    chat_ids = extract_chat_ids(chat_path)
    missing = sorted([i for i in chat_ids if i not in repo_ids])

    print(f"Chat ids found: {len(chat_ids)}")
    print(f"Repo ids found: {len(repo_ids)}")

    if missing:
        print("\nMISSING ids (present in chat transcript but not in repo):")
        for m in missing[:50]:
            print(" -", m)
        if len(missing) > 50:
            print(f" ... and {len(missing)-50} more")
        return 3

    print("\nALL CHAT IDS FOUND IN REPO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
