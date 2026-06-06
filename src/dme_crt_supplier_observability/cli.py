"""Command line interface for the supplier validation pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dme_crt_supplier_observability.config import DEFAULT_DB_PATH, DEFAULT_SAMPLE_FILE, RUN_REPORT_DIR
from dme_crt_supplier_observability.db import init_database, observability_counts
from dme_crt_supplier_observability.pipeline import run_demo, seed_database, validate_file_pipeline


def _path(value: str) -> Path:
    return Path(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dme-crt-supplier-observability",
        description="Validate public-safe DME/CRT supplier product records and log pipeline observability data.",
    )
    parser.add_argument("--db-path", type=_path, default=DEFAULT_DB_PATH, help="SQLite database path.")
    parser.add_argument("--report-dir", type=_path, default=RUN_REPORT_DIR, help="Run report output directory.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-db", help="Create SQLite observability tables.")
    init_parser.add_argument("--reset", action="store_true", help="Delete the existing local database first.")

    seed_parser = subparsers.add_parser("seed-db", help="Seed the database by validating the sample CSV.")
    seed_parser.add_argument("--input-file", type=_path, default=DEFAULT_SAMPLE_FILE, help="Sample CSV path.")
    seed_parser.add_argument("--reset", action="store_true", help="Delete the existing local database first.")

    validate_parser = subparsers.add_parser("validate-file", help="Validate a CSV and log the run.")
    validate_parser.add_argument("input_file", type=_path, help="CSV file to validate.")
    validate_parser.add_argument("--reset-db", action="store_true", help="Delete the existing local database first.")

    demo_parser = subparsers.add_parser("run-demo", help="Run the Phase 1 sample-data demo.")
    demo_parser.add_argument("--input-file", type=_path, default=DEFAULT_SAMPLE_FILE, help="Sample CSV path.")
    demo_parser.add_argument("--no-reset", action="store_true", help="Keep the existing local database.")

    return parser


def _print_summary(summary) -> None:
    print(f"run_id={summary.run_id}")
    print(f"status={summary.status}")
    print(f"source={summary.source_filename}")
    print(f"rows_total={summary.total_rows_detected}")
    print(f"rows_passed={summary.rows_passed}")
    print(f"rows_warning={summary.rows_warning}")
    print(f"rows_rejected={summary.rows_rejected_validation}")
    print(f"db_path={summary.db_path}")
    print(f"report_path={summary.report_path}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-db":
        db_path = init_database(args.db_path, reset=args.reset)
        print(f"initialized_db={db_path}")
        print(f"table_counts={observability_counts(db_path)}")
        return 0

    if args.command == "seed-db":
        summary = seed_database(
            db_path=args.db_path,
            input_file=args.input_file,
            report_dir=args.report_dir,
            reset_db=args.reset,
        )
        _print_summary(summary)
        return 0

    if args.command == "validate-file":
        summary, _ = validate_file_pipeline(
            input_file=args.input_file,
            db_path=args.db_path,
            report_dir=args.report_dir,
            reset_db=args.reset_db,
        )
        _print_summary(summary)
        return 0

    if args.command == "run-demo":
        summary = run_demo(
            db_path=args.db_path,
            input_file=args.input_file,
            report_dir=args.report_dir,
            reset_db=not args.no_reset,
        )
        _print_summary(summary)
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
