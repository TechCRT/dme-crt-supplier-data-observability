"""Pipeline orchestration for validation, SQLite logging, and reports."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .config import DEFAULT_DB_PATH, DEFAULT_SAMPLE_FILE, RUN_REPORT_DIR
from .db import (
    connect,
    file_sha256,
    init_database,
    insert_pipeline_log,
    insert_validation_results,
    register_file_intake,
)
from .models import PipelineRunSummary, ValidationResult
from .reporting import write_json_report
from .validator import validate_csv_file


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"run-{stamp}-{uuid4().hex[:8]}"


def _status_for(results: list[ValidationResult]) -> str:
    if any(result.validation_status == "REJECT" for result in results):
        return "WARNING"
    if any(result.validation_status == "WARNING" for result in results):
        return "WARNING"
    return "SUCCESS"


def _file_status_for(summary: PipelineRunSummary) -> str:
    if summary.rows_rejected_validation or summary.rows_warning:
        return "PROCESSED_WITH_FINDINGS"
    return "PROCESSED"


def validate_file_pipeline(
    input_file: Path | str,
    db_path: Path | str = DEFAULT_DB_PATH,
    report_dir: Path | str = RUN_REPORT_DIR,
    reset_db: bool = False,
) -> tuple[PipelineRunSummary, list[ValidationResult]]:
    db_file = init_database(db_path, reset=reset_db)
    source = Path(input_file)
    started_at = _timestamp()
    results = validate_csv_file(source)
    completed_at = _timestamp()
    summary = PipelineRunSummary(
        run_id=_run_id(),
        source_filename=source.name,
        source_path=str(source),
        started_at=started_at,
        completed_at=completed_at,
        total_rows_detected=len(results),
        rows_passed=sum(1 for result in results if result.validation_status == "PASS"),
        rows_warning=sum(1 for result in results if result.validation_status == "WARNING"),
        rows_rejected_validation=sum(1 for result in results if result.validation_status == "REJECT"),
        status=_status_for(results),
        db_path=str(db_file),
        report_path=None,
    )
    report_path = Path(report_dir) / f"{summary.run_id}.json"
    summary = replace(summary, report_path=str(report_path))
    write_json_report(summary, results, report_dir=report_dir)

    connection = connect(db_file)
    try:
        insert_pipeline_log(connection, summary)
        register_file_intake(
            connection,
            summary,
            file_hash=file_sha256(source),
            file_status=_file_status_for(summary),
            notes="Validated by Phase 1 Python CLI.",
        )
        insert_validation_results(connection, summary, results)
        connection.commit()
    finally:
        connection.close()

    return summary, results


def seed_database(
    db_path: Path | str = DEFAULT_DB_PATH,
    input_file: Path | str = DEFAULT_SAMPLE_FILE,
    report_dir: Path | str = RUN_REPORT_DIR,
    reset_db: bool = False,
) -> PipelineRunSummary:
    summary, _ = validate_file_pipeline(
        input_file=input_file,
        db_path=db_path,
        report_dir=report_dir,
        reset_db=reset_db,
    )
    return summary


def run_demo(
    db_path: Path | str = DEFAULT_DB_PATH,
    input_file: Path | str = DEFAULT_SAMPLE_FILE,
    report_dir: Path | str = RUN_REPORT_DIR,
    reset_db: bool = True,
) -> PipelineRunSummary:
    return seed_database(
        db_path=db_path,
        input_file=input_file,
        report_dir=report_dir,
        reset_db=reset_db,
    )
