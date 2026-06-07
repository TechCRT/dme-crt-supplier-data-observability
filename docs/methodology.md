# Methodology

This project uses a validation-first workflow for public-safe supplier and product CSV records.

## Workflow Pattern

```text
supplier/product CSV
-> normalized row model
-> validation rules
-> pass, warning, or reject outcome
-> reviewable file routing and SQLite audit records
-> JSON run report
-> analytics-ready observability layer
```

## Source-Aware Input

The workflow starts with a CSV file whose source filename, content hash, row count, and processing status are recorded in the file intake registry. The original intake file is preserved, and the PowerShell workflow routes a processing copy.

## Normalized Row Model

The Python validator converts each CSV row into a stable product record shape before applying rules. Blank values, duplicate identifiers, category/type values, HCPCS-like examples, documentation sources, and compatibility notes are handled consistently across rows.

## Validation And Rule Classification

Validation rules produce explicit findings with field name, rejected value, rule identifier, severity, and row status. A row can pass, require review, or be rejected:

- `PASS`: no validation findings.
- `WARNING`: review-needed findings without blocking errors.
- `REJECT`: one or more blocking validation errors.

## Human Review Boundary

Warnings are kept separate from rejected rows. The PowerShell workflow routes warning-only files to `data/review/`, rejected files to `data/rejected/`, and clean files to `data/processed/`.

## Bounded Output And Audit Trail

Each run produces a JSON report and SQLite audit records. The four operational tables support run-level status, row-level validation findings, file intake routing, and product record audit history. The analytics documentation builds from those tables without claiming a completed PBIX report.
