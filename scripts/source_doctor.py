from pathlib import Path
import yaml

def check_sources():
    repo_root = Path(r"C:\GitDev\Investment")
    active_path = repo_root / "configs" / "registry.yaml"

    with open(active_path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    indicators = doc.get("indicators", [])
    print(f"Checking data feed health for {len(indicators)} indicators...")

    counts = {"fred": 0, "stooq": 0, "yahoo": 0, "ustreasury": 0, "manual_csv": 0}
    single_sourced = []

    for ind in indicators:
        sources = ind.get("sources", [])
        for s in sources:
            stype = s.get("type")
            if stype in counts:
                counts[stype] += 1
        if len(sources) <= 1:
            single_sourced.append(ind["series_id"])

    print("\nSource Coverage Summary:")
    for k, v in counts.items():
        print(f"  - {k.upper()}: {v} connectors wired")

    print(f"\nSingle-sourced series ({len(single_sourced)} total):")
    print("  " + ", ".join(single_sourced[:15]))
    if len(single_sourced) > 15:
        print(f"  ... and {len(single_sourced) - 15} more.")

if __name__ == "__main__":
    check_sources()
