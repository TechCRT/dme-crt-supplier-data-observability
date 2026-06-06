"""CSV loading and file-level validation orchestration."""

from __future__ import annotations

import csv
from pathlib import Path

from .config import REQUIRED_COLUMNS
from .models import ProductRecord, ValidationResult
from .rules import duplicate_keys, validate_record


def load_csv_records(input_file: Path) -> list[ProductRecord]:
    path = Path(input_file)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Input file has no header row: {path}")

        missing_columns = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing_columns:
            missing_display = ", ".join(missing_columns)
            raise ValueError(f"Input file is missing required columns: {missing_display}")

        return [ProductRecord.from_mapping(row_number, row) for row_number, row in enumerate(reader, start=2)]


def validate_records(records: list[ProductRecord]) -> list[ValidationResult]:
    duplicates = duplicate_keys(records)
    return [validate_record(record, duplicates) for record in records]


def validate_csv_file(input_file: Path) -> list[ValidationResult]:
    return validate_records(load_csv_records(Path(input_file)))
