"""Run PII-aware QA and de-identification on the synthetic dataset."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .privacy import deidentify_record, pseudonymize, require_hash_key
from .validate import quality_summary, validate_rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PII-aware customer data QA pipeline."
    )
    parser.add_argument(
        "--input",
        default="data/raw/synthetic_customers.csv",
        help="Input CSV. The repository sample is synthetic.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Directory for generated privacy-safe outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.input)
    out_dir = Path(args.output_dir)
    key = require_hash_key()

    rows = read_csv(source)
    ref_fn = (
        lambda customer_id: pseudonymize(customer_id, key)[:12]
        if customer_id
        else "MISSING_ID"
    )

    issues = validate_rows(rows, ref_fn)
    deidentified = [deidentify_record(row, key) for row in rows]
    summary = quality_summary(len(rows), issues)

    write_csv(out_dir / "deidentified_customers.csv", deidentified)
    write_csv(out_dir / "qa_issues.csv", issues)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "qa_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(
        f"Rows: {summary['total_rows']} | "
        f"Passed: {summary['rows_passing_all_checks']} | "
        f"Rows with issues: {summary['rows_with_issues']} | "
        f"Issues: {summary['total_issues']} | "
        f"Pass rate: {summary['pass_rate_pct']}%"
    )
    print(
        "Only de-identified data and privacy-safe QA logs were written."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
