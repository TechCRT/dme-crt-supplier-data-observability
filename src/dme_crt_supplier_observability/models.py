"""Typed models shared across validation, persistence, and reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


def clean_value(value: object) -> str:
    """Return a trimmed string for CSV and SQLite use."""

    if value is None:
        return ""
    return str(value).strip()


@dataclass(frozen=True)
class ProductRecord:
    row_number: int
    supplier_name: str
    manufacturer: str
    model: str
    sku: str
    mpn: str
    product_category: str
    product_type: str
    hcpcs_candidate: str
    compatible_chair_family: str
    documentation_source: str
    listing_status: str
    compatibility_notes: str

    @classmethod
    def from_mapping(cls, row_number: int, values: Mapping[str, object]) -> "ProductRecord":
        return cls(
            row_number=row_number,
            supplier_name=clean_value(values.get("supplier_name")),
            manufacturer=clean_value(values.get("manufacturer")),
            model=clean_value(values.get("model")),
            sku=clean_value(values.get("sku")),
            mpn=clean_value(values.get("mpn")),
            product_category=clean_value(values.get("product_category")).lower(),
            product_type=clean_value(values.get("product_type")).lower(),
            hcpcs_candidate=clean_value(values.get("hcpcs_candidate")).upper(),
            compatible_chair_family=clean_value(values.get("compatible_chair_family")),
            documentation_source=clean_value(values.get("documentation_source")),
            listing_status=clean_value(values.get("listing_status")).lower(),
            compatibility_notes=clean_value(values.get("compatibility_notes")),
        )

    def stable_identity(self) -> str:
        if self.sku:
            return f"sku:{self.sku.upper()}"
        if self.mpn:
            return f"mpn:{self.mpn.upper()}"
        return f"row:{self.row_number}"


@dataclass(frozen=True)
class ValidationIssue:
    row_number: int
    field_name: str
    rejected_value: str
    validation_rule: str
    severity: str
    error_message: str


@dataclass
class ValidationResult:
    record: ProductRecord
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def validation_status(self) -> str:
        if any(issue.severity == "ERROR" for issue in self.issues):
            return "REJECT"
        if any(issue.severity == "WARNING" for issue in self.issues):
            return "WARNING"
        return "PASS"

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "WARNING")

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "ERROR")

    @property
    def needs_review(self) -> bool:
        return self.validation_status in {"WARNING", "REJECT"}


@dataclass(frozen=True)
class PipelineRunSummary:
    run_id: str
    source_filename: str
    source_path: str
    started_at: str
    completed_at: str
    total_rows_detected: int
    rows_passed: int
    rows_warning: int
    rows_rejected_validation: int
    status: str
    db_path: str
    report_path: str | None = None
