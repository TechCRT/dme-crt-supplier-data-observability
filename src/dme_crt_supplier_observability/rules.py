"""Validation rules for public-safe supplier and product records."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable

from .config import (
    CATEGORY_TYPE_MAP,
    COMPATIBILITY_SENSITIVE_TYPES,
    MISSING_MARKERS,
    VALID_PRODUCT_CATEGORIES,
    VALID_PRODUCT_TYPES,
)
from .models import ProductRecord, ValidationIssue, ValidationResult


HCPCS_LIKE_PATTERN = re.compile(r"^[A-Z][0-9]{4}$")


def _is_missing(value: str) -> bool:
    return value.strip().lower() in MISSING_MARKERS


def _issue(
    record: ProductRecord,
    field_name: str,
    rejected_value: str,
    validation_rule: str,
    severity: str,
    error_message: str,
) -> ValidationIssue:
    return ValidationIssue(
        row_number=record.row_number,
        field_name=field_name,
        rejected_value=rejected_value,
        validation_rule=validation_rule,
        severity=severity,
        error_message=error_message,
    )


def duplicate_keys(records: Iterable[ProductRecord]) -> set[str]:
    """Return SKU or MPN keys that appear more than once in a file."""

    seen: dict[str, list[int]] = defaultdict(list)
    for record in records:
        if record.sku:
            seen[f"sku:{record.sku.upper()}"].append(record.row_number)
        if record.mpn:
            seen[f"mpn:{record.mpn.upper()}"].append(record.row_number)
    return {key for key, rows in seen.items() if len(rows) > 1}


def validate_record(record: ProductRecord, file_duplicate_keys: set[str] | None = None) -> ValidationResult:
    issues: list[ValidationIssue] = []
    duplicates = file_duplicate_keys or set()

    if _is_missing(record.supplier_name):
        issues.append(
            _issue(
                record,
                "supplier_name",
                record.supplier_name,
                "required_supplier_name",
                "ERROR",
                "Supplier name is required for intake accountability.",
            )
        )

    if _is_missing(record.manufacturer):
        issues.append(
            _issue(
                record,
                "manufacturer",
                record.manufacturer,
                "required_manufacturer",
                "ERROR",
                "Manufacturer is required for product traceability.",
            )
        )

    if _is_missing(record.model):
        issues.append(
            _issue(
                record,
                "model",
                record.model,
                "required_model",
                "ERROR",
                "Model is required for review and downstream matching.",
            )
        )

    if _is_missing(record.sku) and _is_missing(record.mpn):
        issues.append(
            _issue(
                record,
                "sku_or_mpn",
                "",
                "required_sku_or_mpn",
                "ERROR",
                "At least one supplier SKU or manufacturer part number is required.",
            )
        )

    if record.product_category not in VALID_PRODUCT_CATEGORIES:
        issues.append(
            _issue(
                record,
                "product_category",
                record.product_category,
                "valid_product_category",
                "ERROR",
                "Product category is not in the supported public-safe sample taxonomy.",
            )
        )

    if record.product_type not in VALID_PRODUCT_TYPES:
        issues.append(
            _issue(
                record,
                "product_type",
                record.product_type,
                "valid_product_type",
                "ERROR",
                "Product type is not in the supported public-safe sample taxonomy.",
            )
        )

    allowed_types = CATEGORY_TYPE_MAP.get(record.product_category, set())
    if allowed_types and record.product_type not in allowed_types:
        issues.append(
            _issue(
                record,
                "product_type",
                record.product_type,
                "category_type_alignment",
                "WARNING",
                "Product type is valid but unusual for the selected category.",
            )
        )

    if _is_missing(record.hcpcs_candidate):
        issues.append(
            _issue(
                record,
                "hcpcs_candidate",
                record.hcpcs_candidate,
                "hcpcs_candidate_present",
                "WARNING",
                "HCPCS-like classification-support field is blank.",
            )
        )
    elif not HCPCS_LIKE_PATTERN.match(record.hcpcs_candidate):
        issues.append(
            _issue(
                record,
                "hcpcs_candidate",
                record.hcpcs_candidate,
                "hcpcs_candidate_format",
                "ERROR",
                "HCPCS-like classification-support value must match one letter followed by four digits.",
            )
        )

    if _is_missing(record.documentation_source):
        issues.append(
            _issue(
                record,
                "documentation_source",
                record.documentation_source,
                "documentation_source_present",
                "WARNING",
                "Documentation source is missing or not reviewable.",
            )
        )

    if record.product_type in COMPATIBILITY_SENSITIVE_TYPES and _is_missing(record.compatibility_notes):
        issues.append(
            _issue(
                record,
                "compatibility_notes",
                record.compatibility_notes,
                "compatibility_notes_present",
                "WARNING",
                "Compatibility-sensitive products need review notes before publication.",
            )
        )

    sku_key = f"sku:{record.sku.upper()}" if record.sku else ""
    mpn_key = f"mpn:{record.mpn.upper()}" if record.mpn else ""
    if sku_key and sku_key in duplicates:
        issues.append(
            _issue(
                record,
                "sku",
                record.sku,
                "duplicate_sku",
                "ERROR",
                "Supplier SKU appears more than once in the input file.",
            )
        )
    if mpn_key and mpn_key in duplicates:
        issues.append(
            _issue(
                record,
                "mpn",
                record.mpn,
                "duplicate_mpn",
                "ERROR",
                "Manufacturer part number appears more than once in the input file.",
            )
        )

    return ValidationResult(record=record, issues=issues)
