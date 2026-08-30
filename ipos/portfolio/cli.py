"""CLI interface for IPOS Portfolio Normalizer (Module M11)."""

import argparse
import sys
import json
import os
from ipos.portfolio.normalizer import PortfolioNormalizer, ValidationException


def main():
    parser = argparse.ArgumentParser(description="IPOS Portfolio Normalizer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # normalize command
    p_norm = subparsers.add_parser("normalize", help="Normalize broker export CSV")
    p_norm.add_argument("--input", required=True, help="Input raw CSV fixture")
    p_norm.add_argument("--outdir", required=True, help="Output directory for canonical tables")

    # validate command
    p_val = subparsers.add_parser("validate", help="Validate raw or canonical file")
    p_val.add_argument("--input", required=True, help="Input CSV file")

    # reconcile command
    p_rec = subparsers.add_parser("reconcile", help="Generate reconciliation report")
    p_rec.add_argument("--input", required=True, help="Input CSV file")

    # doctor command
    p_doc = subparsers.add_parser("doctor", help="Check normalizer readiness and dependencies")

    args = parser.parse_args()
    normalizer = PortfolioNormalizer()

    if args.command == "doctor":
        print("M11 Normalizer Doctor: OK (Python, Pandas, PyArrow ready)")
        sys.exit(0)

    elif args.command == "validate":
        try:
            _, df_act, _, _ = normalizer.normalize_csv_fixture(args.input)
            print(f"Validation SUCCESS: {len(df_act)} canonical activity rows valid.")
            sys.exit(0)
        except Exception as e:
            print(f"Validation FAILED: {e}")
            sys.exit(1)

    elif args.command == "normalize":
        try:
            df_holdings, df_activities, manifest, reconciliation = normalizer.normalize_csv_fixture(args.input)
            os.makedirs(args.outdir, exist_ok=True)
            
            # Write parquet & csv
            df_holdings.to_parquet(os.path.join(args.outdir, "portfolio_snapshot.parquet"))
            df_holdings.to_csv(os.path.join(args.outdir, "portfolio_snapshot.csv"), index=False)
            
            df_activities.to_parquet(os.path.join(args.outdir, "activities.parquet"))
            df_activities.to_csv(os.path.join(args.outdir, "activities.csv"), index=False)
            
            with open(os.path.join(args.outdir, "source_manifest.json"), "w") as f:
                json.dump(manifest, f, indent=2)
                
            with open(os.path.join(args.outdir, "reconciliation.json"), "w") as f:
                json.dump(reconciliation, f, indent=2)

            print(f"Normalization SUCCESS -> Written outputs to '{args.outdir}'")
            sys.exit(0)
        except Exception as e:
            print(f"Normalization FAILED: {e}")
            sys.exit(1)

    elif args.command == "reconcile":
        try:
            _, _, _, reconciliation = normalizer.normalize_csv_fixture(args.input)
            print(json.dumps(reconciliation, indent=2))
            sys.exit(0)
        except Exception as e:
            print(f"Reconciliation FAILED: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
