# Phase 2 Summary

Date: 2026-06-06

## Scope Completed

Phase 2 adds the PowerShell intake and end-to-end routing layer while keeping the Phase 1 Python validation rules and severity choices unchanged.

Completed deliverables:

- `automation/powershell/Watch-IntakeFolder.ps1`
- `automation/powershell/Run-SamplePipeline.ps1`
- `docs/powershell_intake_workflow.md`
- Intake/routing folders under `data/intake/`, `data/processing/`, `data/processed/`, `data/review/`, and `data/rejected/`
- Hash marker support under `data/intake/.processed_markers/`
- Python test coverage for required Phase 2 assets and script contract checks
- Phase 2 reports

## Workflow Behavior

The PowerShell workflow:

- Scans `data/intake/` for `.csv` files
- Copies intake files to `data/processing/`
- Invokes the existing Python CLI with `validate-file`
- Reads the generated JSON run report
- Routes the processing copy to `data/processed/`, `data/review/`, or `data/rejected/`
- Preserves the original intake file
- Writes a marker file so monitoring does not repeatedly process the same source file unless `-Reprocess` is used

## Final Demo Result

Successful command path:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1
```

Final verified run:

- Run ID: `run-20260606093147-df25e4e6`
- Status: `WARNING`
- Rows detected: 6
- Rows passed: 2
- Rows requiring review: 1
- Rows rejected: 3
- Validation findings logged: 8
- Routed processing copy: `data/rejected/20260606043146_phase2_sample_20260606043146.csv`
- JSON report: `outputs/run_reports/run-20260606093147-df25e4e6.json`
- Runtime table counts: `pipeline_logs=1`, `validation_errors=8`, `file_intake_registry=1`, `product_record_audit=6`

The rejected route is expected because the public-safe sample intentionally includes rejected rows.

## Public-Safe Boundary

The Phase 2 workflow uses the same public-safe sample data as Phase 1. It does not introduce patient data, customer addresses, payer records, order IDs, clinical records, private supplier agreements, or private financial data. HCPCS-like values remain classification-support examples only.

## User Review Needed

Review the Phase 2 folder routing behavior before Phase 3:

- Original intake files are preserved in `data/intake/`.
- Processing copies are moved into the final route folder.
- Files with any rejected rows route to `data/rejected/`.
- Files with warnings and no rejected rows route to `data/review/`.
- Clean files route to `data/processed/`.

## Future Re-Entry Warnings

- Do not start Phase 3 analytics assets until explicitly requested.
- Do not change the Phase 1 validation rules or severity choices unless a later review pass requests it.
- Do not treat the PowerShell watcher as a production service; it is a local portfolio automation layer.
- Generated intake copies, marker files, runtime databases, and JSON run reports are runtime artifacts and are excluded from source control by `.gitignore`.
