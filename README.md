# DME/CRT Supplier Data Validation & Pipeline Observability Dashboard

This portfolio project demonstrates a local data operations workflow for public-safe DME/CRT supplier and product records. It validates incoming supplier/product CSV files, logs pipeline activity to SQLite, routes files through a PowerShell intake workflow, and documents a Power BI analytics layer for pipeline health and data quality review.

The project is built to show practical data operations judgment: clear intake routing, row-level validation, durable audit tables, testable Python code, and dashboard-ready observability outputs.

## What This Project Does

Workflow:

1. A CSV file is placed in `data/intake/`.
2. PowerShell copies it to `data/processing/`.
3. Python validates each product row.
4. SQLite records run logs, file intake status, product audit rows, and validation findings.
5. The processing copy is routed to `data/processed/`, `data/review/`, or `data/rejected/`.
6. JSON and Markdown reports document run evidence.
7. Power Query, DAX, and dashboard wireframe docs define the analytics layer.

## Public-Safe Boundary

The repository uses mock/public-safe sample data only. It does not include patient data, customer addresses, payer records, order IDs, clinical records, private supplier agreements, or private financial data.

HCPCS-like fields are classification-support examples only. This project does not provide billing guidance, reimbursement automation, payer policy logic, clinical decisioning, or production deployment claims.

## Repository Layout

```text
automation/
  database/schema.sql
  powershell/Run-SamplePipeline.ps1
  powershell/Watch-IntakeFolder.ps1
data/
  sample_input/supplier_product_records_sample.csv
docs/
  data_dictionary.md
  github_release_checklist.md
  operating_notes.md
  powershell_intake_workflow.md
  proof_notes.md
  validation_rules.md
queries/
  TransformOperationsLog.m
analytics/
  dax_measures.md
  dashboard_build_notes.md
  dashboard_wireframe.md
  screenshots/README.md
src/
  dme_crt_supplier_observability/
tests/
outputs/reports/
```

## Quick Start

Run from the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m dme_crt_supplier_observability.cli run-demo
```

The demo initializes the SQLite runtime database, validates the public-safe sample file, and writes a JSON run report under `outputs/run_reports/`.

Expected demo pattern:

- 6 total sample rows
- 2 passing rows
- 1 warning row
- 3 rejected rows
- Pipeline status `WARNING` because the sample intentionally includes review and rejection examples

## Python CLI

```powershell
$env:PYTHONPATH = "src"
python -m dme_crt_supplier_observability.cli init-db --reset
python -m dme_crt_supplier_observability.cli seed-db --reset
python -m dme_crt_supplier_observability.cli validate-file data\sample_input\supplier_product_records_sample.csv
python -m dme_crt_supplier_observability.cli run-demo
```

## PowerShell Intake Demo

Direct local script execution may be blocked by Windows execution policy. The documented process-scoped command is:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1
```

Dry-run path:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1 -DryRun
```

The PowerShell workflow preserves the original intake file and routes only the processing copy.

## Analytics Layer

Phase 3 documents the Power BI build layer:

- `queries/TransformOperationsLog.m`
- `analytics/dax_measures.md`
- `analytics/dashboard_wireframe.md`
- `analytics/dashboard_build_notes.md`
- `analytics/screenshots/README.md`

No PBIX file or real dashboard screenshots are included. The dashboard is represented as documented Power Query, DAX measures, wireframe, build notes, and screenshot placeholder instructions.

## Tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

The test suite covers validation behavior, duplicate handling, SQLite logging, JSON reporting, demo execution, PowerShell asset contracts, and analytics documentation boundaries.

## Evidence

Project evidence and phase reports are stored in `outputs/reports/`, including:

- Phase summaries
- Test results
- Rubric scores
- Analytics layer review
- Final claims and boundaries
- GitHub readiness report

Runtime databases, generated run JSON files, routed CSV copies, and final package outputs are ignored by `.gitignore`.

## Future Re-Entry Warnings

- Do not add private customer, patient, payer, order, clinical, private supplier agreement, or financial data.
- Do not claim production deployment, billing automation, payer policy logic, clinical decisioning, PBIX completion, or real dashboard screenshots.
- If a PBIX is created later, update `analytics/screenshots/README.md`, dashboard notes, proof notes, and final claims with exact evidence.
- If validation severity changes, update tests, docs, DAX assumptions, and phase reports together.
