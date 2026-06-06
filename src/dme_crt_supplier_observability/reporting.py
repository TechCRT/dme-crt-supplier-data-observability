"""JSON and Markdown reporting helpers."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import RUN_REPORT_DIR
from .models import PipelineRunSummary, ValidationResult


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_report_payload(summary: PipelineRunSummary, results: list[ValidationResult]) -> dict[str, object]:
    severity_counts: Counter[str] = Counter()
    rule_counts: Counter[str] = Counter()
    review_rows: list[dict[str, object]] = []

    for result in results:
        for issue in result.issues:
            severity_counts[issue.severity] += 1
            rule_counts[issue.validation_rule] += 1
        if result.needs_review:
            review_rows.append(
                {
                    "row_number": result.record.row_number,
                    "sku": result.record.sku,
                    "mpn": result.record.mpn,
                    "model": result.record.model,
                    "validation_status": result.validation_status,
                    "issues": [asdict(issue) for issue in result.issues],
                }
            )

    return {
        "generated_at_utc": utc_now(),
        "run": asdict(summary),
        "status_counts": {
            "PASS": summary.rows_passed,
            "WARNING": summary.rows_warning,
            "REJECT": summary.rows_rejected_validation,
        },
        "severity_counts": dict(sorted(severity_counts.items())),
        "validation_rule_counts": dict(sorted(rule_counts.items())),
        "review_rows": review_rows,
        "public_safe_notice": (
            "Sample records are public-safe demonstration data. HCPCS-like fields are "
            "classification-support examples only and are not billing guidance."
        ),
    }


def write_json_report(
    summary: PipelineRunSummary,
    results: list[ValidationResult],
    report_dir: Path | str = RUN_REPORT_DIR,
) -> Path:
    output_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{summary.run_id}.json"
    report_path.write_text(
        json.dumps(build_report_payload(summary, results), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return report_path
