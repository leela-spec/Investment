"""
promote_registry.py - Safely promotes validated series from registry_120.yaml into registry.yaml.
"""
import os
import sys
from pathlib import Path
import yaml

def promote_candidate_registry(dry_run=True, target_count=60):
    repo_root = Path(__file__).resolve().parent.parent
    configs_dir = repo_root / "configs"
    active_path = configs_dir / "registry.yaml"
    cand_path = configs_dir / "registry_120.yaml"

    if not cand_path.exists():
        print(f"Error: Candidate registry not found at {cand_path}")
        return 1

    with open(active_path, "r", encoding="utf-8") as f:
        active_doc = yaml.safe_load(f)

    with open(cand_path, "r", encoding="utf-8") as f:
        cand_doc = yaml.safe_load(f)

    active_inds = active_doc.get("indicators", [])
    cand_inds = cand_doc.get("indicators", [])

    existing_ids = {ind["series_id"] for ind in active_inds}
    print(f"Current active indicators: {len(active_inds)}")
    print(f"Candidate pool indicators: {len(cand_inds)}")

    promoted = []
    for cand in cand_inds:
        sid = cand["series_id"]
        if sid not in existing_ids:
            promoted.append(cand)
            if len(active_inds) + len(promoted) >= target_count:
                break

    print(f"Identified {len(promoted)} high-priority indicators for promotion.")
    for p in promoted[:10]:
        print(f"  + {p['series_id']}: {p.get('name', 'N/A')} [{p.get('asset_class', 'N/A')}]")
    if len(promoted) > 10:
        print(f"  ... and {len(promoted) - 10} more.")

    if not dry_run:
        active_doc["indicators"].extend(promoted)
        with open(active_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(active_doc, f, sort_keys=False)
        print(f"SUCCESS: Active registry updated to {len(active_doc['indicators'])} indicators.")
    else:
        print("DRY RUN COMPLETE: Pass --apply to write changes.")
    return 0

if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    promote_candidate_registry(dry_run=dry)
