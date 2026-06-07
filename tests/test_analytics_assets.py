from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AnalyticsAssetTests(unittest.TestCase):
    def test_required_phase3_files_exist(self) -> None:
        required_paths = [
            ROOT / "queries" / "TransformOperationsLog.m",
            ROOT / "analytics" / "dax_measures.md",
            ROOT / "analytics" / "dashboard_wireframe.md",
            ROOT / "analytics" / "dashboard_build_notes.md",
            ROOT / "analytics" / "screenshots" / "README.md",
        ]

        for path in required_paths:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"Missing required Phase 3 asset: {path}")

    def test_power_query_covers_required_tables_and_helpers(self) -> None:
        power_query = (ROOT / "queries" / "TransformOperationsLog.m").read_text(encoding="utf-8")

        for table_name in ["pipeline_logs", "validation_errors", "product_record_audit", "file_intake_registry"]:
            with self.subTest(table_name=table_name):
                self.assertIn(table_name, power_query)

        self.assertIn("Odbc.Query", power_query)
        self.assertIn("NormalizeTextValue", power_query)
        self.assertIn("AddDateHelpers", power_query)
        self.assertIn("data_integrity_rate", power_query)
        self.assertIn("is_rejected_record", power_query)
        self.assertIn("ErrorReviewQueue", power_query)

    def test_dax_document_includes_required_measures(self) -> None:
        dax_doc = (ROOT / "analytics" / "dax_measures.md").read_text(encoding="utf-8")
        required_measures = [
            "Pipeline Success Rate",
            "Total Records Blocked",
            "Data Integrity Rate",
            "Warning or Failure Runs",
            "Validation Rejection Rate",
            "Records Requiring Review",
            "Failed Run Count",
            "Average Rows Per Run",
        ]

        for measure_name in required_measures:
            with self.subTest(measure_name=measure_name):
                self.assertIn(measure_name, dax_doc)

    def test_wireframe_and_screenshot_docs_do_not_claim_real_dashboard(self) -> None:
        wireframe = (ROOT / "analytics" / "dashboard_wireframe.md").read_text(encoding="utf-8").lower()
        screenshots = (ROOT / "analytics" / "screenshots" / "README.md").read_text(encoding="utf-8").lower()

        self.assertIn("no pbix file or real dashboard screenshot", wireframe)
        self.assertIn("no real power bi screenshots", screenshots)
        self.assertIn("operating notes", wireframe)
        self.assertIn("operating notes", screenshots)


if __name__ == "__main__":
    unittest.main()
