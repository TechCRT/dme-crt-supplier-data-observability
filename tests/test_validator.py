from __future__ import annotations

import unittest

from dme_crt_supplier_observability.models import ProductRecord
from dme_crt_supplier_observability.rules import duplicate_keys, validate_record
from dme_crt_supplier_observability.validator import load_csv_records, validate_records


class ValidatorTests(unittest.TestCase):
    def test_passing_row_has_pass_status(self) -> None:
        record = ProductRecord(
            row_number=2,
            supplier_name="Mobility Sample Supply",
            manufacturer="Permobil",
            model="F5 Corpus VS",
            sku="F5VS-001",
            mpn="PM-F5VS-BASE",
            product_category="power_wheelchair",
            product_type="standing_power_chair",
            hcpcs_candidate="K0861",
            compatible_chair_family="Permobil F-Series",
            documentation_source="manufacturer manual",
            listing_status="ready_for_review",
            compatibility_notes="Verify configuration before publication",
        )

        result = validate_record(record)

        self.assertEqual(result.validation_status, "PASS")
        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.warning_count, 0)

    def test_rejection_for_missing_required_fields_and_invalid_taxonomy(self) -> None:
        record = ProductRecord(
            row_number=3,
            supplier_name="",
            manufacturer="",
            model="Unknown",
            sku="",
            mpn="",
            product_category="unknown",
            product_type="unknown",
            hcpcs_candidate="BADCODE",
            compatible_chair_family="",
            documentation_source="missing",
            listing_status="rejected",
            compatibility_notes="",
        )

        result = validate_record(record)
        rules = {issue.validation_rule for issue in result.issues}

        self.assertEqual(result.validation_status, "REJECT")
        self.assertIn("required_supplier_name", rules)
        self.assertIn("required_manufacturer", rules)
        self.assertIn("required_sku_or_mpn", rules)
        self.assertIn("valid_product_category", rules)
        self.assertIn("hcpcs_candidate_format", rules)

    def test_duplicate_sku_is_blocking(self) -> None:
        first = ProductRecord(
            2,
            "Supplier A",
            "Maker",
            "Module A",
            "DUP-001",
            "MPN-001",
            "electronics",
            "electronic_module",
            "E2399",
            "Family",
            "manufacturer install sheet",
            "ready_for_review",
            "Requires configuration review",
        )
        second = ProductRecord(
            3,
            "Supplier A",
            "Maker",
            "Module B",
            "DUP-001",
            "MPN-002",
            "electronics",
            "electronic_module",
            "E2399",
            "Family",
            "manufacturer install sheet",
            "ready_for_review",
            "Requires configuration review",
        )

        duplicates = duplicate_keys([first, second])
        results = [validate_record(record, duplicates) for record in (first, second)]

        self.assertEqual({result.validation_status for result in results}, {"REJECT"})
        self.assertTrue(all("duplicate_sku" in {issue.validation_rule for issue in result.issues} for result in results))

    def test_sample_file_validation_contains_pass_warning_and_reject(self) -> None:
        records = load_csv_records("data/sample_input/supplier_product_records_sample.csv")
        results = validate_records(records)
        statuses = {result.validation_status for result in results}

        self.assertEqual(len(results), 6)
        self.assertEqual(statuses, {"PASS", "WARNING", "REJECT"})


if __name__ == "__main__":
    unittest.main()
