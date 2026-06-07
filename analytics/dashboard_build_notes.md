# Dashboard Build Notes

## Current Status

This document describes the Power BI analytics layer. It does not include a PBIX file or real dashboard screenshots.

## Power Query Setup

1. Create a local SQLite ODBC DSN that points to:

   ```text
   data/runtime/supplier_observability.sqlite
   ```

2. In Power BI Desktop, open Power Query.

3. Create a blank query and paste the contents of:

   ```text
   queries/TransformOperationsLog.m
   ```

4. Replace:

   ```text
   dsn=DME_CRT_SUPPLIER_OBSERVABILITY
   ```

   with the actual local DSN.

5. Load or reference the returned tables:

   - `PipelineLogs`
   - `ValidationErrors`
   - `ProductRecordAudit`
   - `FileIntakeRegistry`
   - `DataQualityByRun`
   - `SupplierProductQuality`
   - `ErrorReviewQueue`

## Transform Coverage

The Power Query template covers:

- SQLite ODBC source access
- All four operational tables
- Text trimming and blank-to-null normalization
- Numeric type conversions
- Date/time conversions
- Date helper columns
- Hour helper columns
- Run integrity rate logic
- Record-level integrity weight
- Rejected-record flags
- Warning and failure visibility flags
- Supplier/product quality aggregation
- Error review queue shaping

## Model Relationships

Recommended relationships:

| From | To | Cardinality |
| --- | --- | --- |
| `PipelineLogs[run_id]` | `ValidationErrors[run_id]` | One-to-many |
| `PipelineLogs[run_id]` | `ProductRecordAudit[run_id]` | One-to-many |
| `PipelineLogs[run_id]` | `FileIntakeRegistry[run_id]` | One-to-many |

Keep cross-filter direction single from `PipelineLogs` into the row-level tables unless a future PBIX review shows a specific need for bidirectional filtering.

## DAX Setup

Create the measures documented in:

```text
analytics/dax_measures.md
```

Required measures:

- Pipeline Success Rate
- Total Records Blocked
- Data Integrity Rate
- Warning or Failure Runs
- Validation Rejection Rate
- Records Requiring Review
- Failed Run Count
- Average Rows Per Run

## Dashboard Pages

Build the three pages documented in:

```text
analytics/dashboard_wireframe.md
```

Pages:

- Pipeline Health Overview
- Supplier/Product Data Quality
- Error Review Queue

## Project Scope

Use the public-safe sample data and local runtime outputs only. Do not add private customer, patient, payer, order, clinical, private supplier agreement, or private financial data.

HCPCS-like values are classification-support examples only and are not billing guidance.

## Operating Notes

- Do not claim a PBIX, deployed semantic model, or real dashboard exists until those files are created.
- If the SQLite schema changes, update the Power Query source SQL, DAX measures, and dashboard wireframe together.
- Keep GitHub release polish separate from this analytics documentation.
