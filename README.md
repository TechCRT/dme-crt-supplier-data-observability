# DME/CRT Supplier Data Validation & Pipeline Observability

A technical case study demonstrating a local data operations workflow for supplier and product records in the DME/CRT space.

The system validates incoming supplier/product CSV files, logs pipeline activity to SQLite, routes files through a PowerShell intake workflow, and defines a Power BI-ready analytics layer for monitoring pipeline health and data quality.

The implementation shows practical data operations judgment: structured intake, row-level validation, durable audit tables, testable Python code, and clear observability outputs.

## Project Summary

This project models a common operations problem: supplier/product records often arrive with missing fields, inconsistent categories, duplicate identifiers, unsupported values, or documentation gaps.

The workflow catches those issues before downstream use by:

1. Accepting a supplier/product CSV file.
2. Running validation checks against each row.
3. Logging pipeline activity and row-level findings to SQLite.
4. Routing files based on validation outcome.
5. Producing reviewable JSON run reports.
6. Providing Power Query, DAX, and dashboard documentation for Power BI analysis.

## Workflow

```text
data/intake/
-> PowerShell intake workflow
-> data/processing/
-> Python validation pipeline
-> SQLite observability tables
-> JSON run report
-> data/processed/, data/review/, or data/rejected/
-> Power BI-ready analytics layer
```

## Design Pattern

```text
supplier/product CSV
-> normalized row model
-> validation rules
-> pass, warning, or reject outcome
-> reviewable file routing and SQLite audit records
-> JSON run report
-> analytics-ready observability layer
```

The key boundary is between validation and action. Warning rows are routed for review instead of being treated as clean records, rejected rows are separated from reviewable warnings, and each run leaves row-level audit evidence.

## Implementation Coverage

* Supplier/product data validation
* Local pipeline observability
* SQLite schema design
* PowerShell intake automation
* Python CLI development
* Row-level validation and error reporting
* File routing by validation outcome
* Power Query and DAX planning
* Dashboard-ready data quality reporting
* Public-safe documentation discipline

## Project Scope

This repository uses mock/public-safe sample data only.

It does not include patient data, customer addresses, payer records, order IDs, clinical records, private supplier agreements, or private financial data.

HCPCS-like values are included only as classification-support examples. This project does not provide billing guidance, reimbursement automation, payer-policy logic, clinical decisioning, or deployment evidence.

## Repository Layout

```text
automation/
  database/
    schema.sql
  powershell/
    Run-SamplePipeline.ps1
    Watch-IntakeFolder.ps1

analytics/
  dax_measures.md
  dashboard_build_notes.md
  dashboard_wireframe.md
  screenshots/
    README.md

data/
  sample_input/
    supplier_product_records_sample.csv

docs/
  data_dictionary.md
  github_release_checklist.md
  methodology.md
  operating_notes.md
  powershell_intake_workflow.md
  proof_notes.md
  review/
  validation_rules.md

queries/
  TransformOperationsLog.m

src/
  dme_crt_supplier_observability/

tests/
```

## Quick Start

Run from the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m dme_crt_supplier_observability.cli run-demo
```

The demo initializes the local SQLite runtime database, validates the public-safe sample CSV, and writes a JSON run report.

Expected demo pattern:

```text
6 total sample rows
2 passing rows
1 warning row
3 rejected rows
Pipeline status: WARNING
```

The `WARNING` status is expected because the sample file intentionally includes clean, review-needed, and rejected records.

## Python CLI

```powershell
$env:PYTHONPATH = "src"

python -m dme_crt_supplier_observability.cli init-db --reset
python -m dme_crt_supplier_observability.cli seed-db --reset
python -m dme_crt_supplier_observability.cli validate-file data\sample_input\supplier_product_records_sample.csv
python -m dme_crt_supplier_observability.cli run-demo
```

## PowerShell Intake Demo

Windows may block direct script execution depending on local execution policy. Use the process-scoped command below:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1
```

Dry-run mode:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1 -DryRun
```

The PowerShell workflow preserves the original intake file and routes only the processing copy.

Routing behavior:

```text
Clean file -> data/processed/
Warnings only -> data/review/
Rejected rows present -> data/rejected/
```

## SQLite Observability Tables

The local SQLite schema tracks both run-level and row-level outcomes.

```text
pipeline_logs
validation_errors
file_intake_registry
product_record_audit
```

These tables support operational review questions such as:

* Which files were processed?
* Which runs completed with warnings or failures?
* Which rows were rejected?
* Which validation rules are triggered most often?
* Which supplier/product records require review?

## Analytics Layer

The repository includes a Power BI-ready analytics specification:

```text
queries/TransformOperationsLog.m
analytics/dax_measures.md
analytics/dashboard_wireframe.md
analytics/dashboard_build_notes.md
analytics/screenshots/README.md
```

Power BI status: analytics-ready.

The repo includes the Power Query template, DAX measures, dashboard wireframe, and build notes needed to create the report in Power BI Desktop. No PBIX file or real dashboard screenshots are included in this release.

Dashboard pages are planned around:

```text
Pipeline Health Overview
Supplier/Product Data Quality
Error Review Queue
```

## Tests

Run the test suite:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

The tests cover:

* Validation rule behavior
* Duplicate handling
* SQLite table creation
* Pipeline log insertion
* File intake registry insertion
* Product audit insertion
* Validation error insertion
* JSON report creation
* CLI demo execution
* PowerShell asset contracts
* Analytics documentation boundaries

## Evidence

Review artifacts are stored under:

```text
docs/review/
```

Included review documents:

```text
final_rubric_score.md
github_readiness_report.md
final_claims_and_boundaries.md
final_next_steps.md
```

Runtime databases, generated run reports, routed CSV copies, marker files, package outputs, and local cache files are excluded by `.gitignore`.

## Maintenance Notes

If validation severity changes, update the tests, validation documentation, DAX assumptions, and dashboard notes together.

If a PBIX report is created later, add only real screenshots captured from the Power BI report and keep all data public-safe.

## Author

Joel Landry Nge

