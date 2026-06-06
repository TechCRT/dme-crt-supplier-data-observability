"""SQLite persistence for pipeline observability tables."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Iterable

from .config import DEFAULT_DB_PATH, SCHEMA_PATH
from .models import PipelineRunSummary, ProductRecord, ValidationResult


def connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database(db_path: Path | str = DEFAULT_DB_PATH, reset: bool = False) -> Path:
    path = Path(db_path)
    if reset and path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    connection = connect(path)
    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()
    return path


def file_sha256(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_hash(record: ProductRecord) -> str:
    joined = "|".join(
        [
            record.supplier_name,
            record.manufacturer,
            record.model,
            record.sku,
            record.mpn,
            record.product_category,
            record.product_type,
            record.hcpcs_candidate,
            record.compatible_chair_family,
            record.documentation_source,
            record.listing_status,
            record.compatibility_notes,
        ]
    )
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def insert_pipeline_log(connection: sqlite3.Connection, summary: PipelineRunSummary) -> None:
    connection.execute(
        """
        INSERT INTO pipeline_logs (
            run_id, script_source, source_filename, started_at, completed_at,
            total_rows_detected, rows_passed, rows_warning, rows_rejected_validation,
            status, error_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            summary.run_id,
            "python_cli",
            summary.source_filename,
            summary.started_at,
            summary.completed_at,
            summary.total_rows_detected,
            summary.rows_passed,
            summary.rows_warning,
            summary.rows_rejected_validation,
            summary.status,
            None,
        ),
    )


def register_file_intake(
    connection: sqlite3.Connection,
    summary: PipelineRunSummary,
    file_hash: str,
    file_status: str,
    notes: str,
) -> None:
    connection.execute(
        """
        INSERT INTO file_intake_registry (
            run_id, source_filename, source_path, processed_at, file_status,
            file_hash, row_count, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            summary.run_id,
            summary.source_filename,
            summary.source_path,
            summary.completed_at,
            file_status,
            file_hash,
            summary.total_rows_detected,
            notes,
        ),
    )


def insert_validation_results(
    connection: sqlite3.Connection,
    summary: PipelineRunSummary,
    results: Iterable[ValidationResult],
) -> None:
    for result in results:
        record = result.record
        connection.execute(
            """
            INSERT INTO product_record_audit (
                run_id, source_filename, row_number, supplier_name, manufacturer, model,
                sku, mpn, product_category, product_type, hcpcs_candidate,
                compatible_chair_family, documentation_source, listing_status,
                compatibility_notes, validation_status, needs_review, warning_count,
                error_count, source_row_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                summary.run_id,
                summary.source_filename,
                record.row_number,
                record.supplier_name,
                record.manufacturer,
                record.model,
                record.sku,
                record.mpn,
                record.product_category,
                record.product_type,
                record.hcpcs_candidate,
                record.compatible_chair_family,
                record.documentation_source,
                record.listing_status,
                record.compatibility_notes,
                result.validation_status,
                1 if result.needs_review else 0,
                result.warning_count,
                result.error_count,
                record_hash(record),
            ),
        )
        for issue in result.issues:
            connection.execute(
                """
                INSERT INTO validation_errors (
                    run_id, source_filename, row_number, field_name, rejected_value,
                    validation_rule, severity, validation_status, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.run_id,
                    summary.source_filename,
                    issue.row_number,
                    issue.field_name,
                    issue.rejected_value,
                    issue.validation_rule,
                    issue.severity,
                    result.validation_status,
                    issue.error_message,
                ),
            )


def table_count(connection: sqlite3.Connection, table_name: str) -> int:
    cursor = connection.execute(f"SELECT COUNT(*) AS row_count FROM {table_name}")
    return int(cursor.fetchone()["row_count"])


def observability_counts(db_path: Path | str = DEFAULT_DB_PATH) -> dict[str, int]:
    connection = connect(db_path)
    try:
        return {
            "pipeline_logs": table_count(connection, "pipeline_logs"),
            "validation_errors": table_count(connection, "validation_errors"),
            "file_intake_registry": table_count(connection, "file_intake_registry"),
            "product_record_audit": table_count(connection, "product_record_audit"),
        }
    finally:
        connection.close()
