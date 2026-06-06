from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from dme_crt_supplier_observability.cli import main
from dme_crt_supplier_observability.db import init_database, observability_counts
from dme_crt_supplier_observability.pipeline import run_demo, validate_file_pipeline


class PipelineTests(unittest.TestCase):
    def test_init_database_creates_required_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.sqlite"

            init_database(db_path)
            counts = observability_counts(db_path)

            self.assertEqual(
                set(counts),
                {"pipeline_logs", "validation_errors", "file_intake_registry", "product_record_audit"},
            )
            self.assertEqual(counts["pipeline_logs"], 0)

    def test_validate_file_logs_pipeline_tables_and_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            db_path = temp_path / "observability.sqlite"
            report_dir = temp_path / "reports"

            summary, results = validate_file_pipeline(
                "data/sample_input/supplier_product_records_sample.csv",
                db_path=db_path,
                report_dir=report_dir,
                reset_db=True,
            )

            self.assertEqual(summary.total_rows_detected, 6)
            self.assertEqual(summary.rows_passed, 2)
            self.assertEqual(summary.rows_warning, 1)
            self.assertEqual(summary.rows_rejected_validation, 3)
            self.assertEqual(summary.status, "WARNING")
            self.assertEqual(len(results), 6)

            counts = observability_counts(db_path)
            self.assertEqual(counts["pipeline_logs"], 1)
            self.assertEqual(counts["file_intake_registry"], 1)
            self.assertEqual(counts["product_record_audit"], 6)
            self.assertGreaterEqual(counts["validation_errors"], 5)

            report_path = Path(summary.report_path or "")
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["run"]["run_id"], summary.run_id)
            self.assertEqual(payload["status_counts"]["REJECT"], 3)
            self.assertIn("public-safe demonstration data", payload["public_safe_notice"])

    def test_run_demo_resets_and_records_single_demo_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            db_path = temp_path / "demo.sqlite"

            first = run_demo(db_path=db_path, report_dir=temp_path / "reports")
            second = run_demo(db_path=db_path, report_dir=temp_path / "reports")

            self.assertNotEqual(first.run_id, second.run_id)
            counts = observability_counts(db_path)
            self.assertEqual(counts["pipeline_logs"], 1)
            self.assertEqual(counts["product_record_audit"], 6)

    def test_cli_init_and_demo_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            db_path = temp_path / "cli.sqlite"
            report_dir = temp_path / "reports"

            with redirect_stdout(StringIO()):
                init_code = main(["--db-path", str(db_path), "--report-dir", str(report_dir), "init-db", "--reset"])
                demo_code = main(["--db-path", str(db_path), "--report-dir", str(report_dir), "run-demo"])

            self.assertEqual(init_code, 0)
            self.assertEqual(demo_code, 0)
            connection = sqlite3.connect(db_path)
            try:
                pipeline_rows = connection.execute("SELECT COUNT(*) FROM pipeline_logs").fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(pipeline_rows, 1)


if __name__ == "__main__":
    unittest.main()
