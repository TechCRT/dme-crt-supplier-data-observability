# DAX Measures

These measures are designed for a Power BI model built from `queries/TransformOperationsLog.m`. They assume the model contains typed tables named `PipelineLogs`, `ValidationErrors`, `ProductRecordAudit`, and `FileIntakeRegistry`.

No PBIX file is included in Phase 3. These measures document the intended analytics layer and should be pasted into Power BI after the Power Query tables are loaded.

## Core Measures

### Pipeline Success Rate

```DAX
Pipeline Success Rate =
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(PipelineLogs[run_id]),
        PipelineLogs[status] = "SUCCESS"
    ),
    DISTINCTCOUNT(PipelineLogs[run_id])
)
```

Format as percentage. This measures clean runs with no warning/failure status.

### Total Records Blocked

```DAX
Total Records Blocked =
CALCULATE(
    COUNTROWS(ProductRecordAudit),
    ProductRecordAudit[validation_status] = "REJECT"
)
```

Use this for rejected-record reporting and operational queue sizing.

### Data Integrity Rate

```DAX
Data Integrity Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(ProductRecordAudit),
        ProductRecordAudit[validation_status] = "PASS"
    ),
    COUNTROWS(ProductRecordAudit)
)
```

Format as percentage. This rate intentionally treats warning rows as not fully clean, while still separating them from blocked records.

### Warning or Failure Runs

```DAX
Warning or Failure Runs =
CALCULATE(
    DISTINCTCOUNT(PipelineLogs[run_id]),
    FILTER(
        PipelineLogs,
        PipelineLogs[status] <> "SUCCESS"
            || PipelineLogs[rows_warning] > 0
            || PipelineLogs[rows_rejected_validation] > 0
    )
)
```

Use this on the Pipeline Health Overview page to highlight runs needing review.

### Validation Rejection Rate

```DAX
Validation Rejection Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(ProductRecordAudit),
        ProductRecordAudit[validation_status] = "REJECT"
    ),
    COUNTROWS(ProductRecordAudit)
)
```

Format as percentage. This is the blocked-record share of validated product rows.

### Records Requiring Review

```DAX
Records Requiring Review =
CALCULATE(
    COUNTROWS(ProductRecordAudit),
    ProductRecordAudit[needs_review_flag] = TRUE()
)
```

Includes both warning rows and rejected rows.

### Failed Run Count

```DAX
Failed Run Count =
CALCULATE(
    DISTINCTCOUNT(PipelineLogs[run_id]),
    PipelineLogs[status] = "FAILED"
)
```

This remains zero in the current public-safe demo unless validator execution fails or a future run logs a failed status.

### Average Rows Per Run

```DAX
Average Rows Per Run =
AVERAGEX(
    VALUES(PipelineLogs[run_id]),
    CALCULATE(SUM(PipelineLogs[total_rows_detected]))
)
```

Use this to show intake volume per validation run.

## Supporting Measures

```DAX
Total Pipeline Runs =
DISTINCTCOUNT(PipelineLogs[run_id])
```

```DAX
Total Validation Findings =
COUNTROWS(ValidationErrors)
```

```DAX
Error Finding Count =
CALCULATE(
    COUNTROWS(ValidationErrors),
    ValidationErrors[severity] = "ERROR"
)
```

```DAX
Warning Finding Count =
CALCULATE(
    COUNTROWS(ValidationErrors),
    ValidationErrors[severity] = "WARNING"
)
```

```DAX
Processed File Count =
DISTINCTCOUNT(FileIntakeRegistry[file_id])
```

```DAX
Files With Findings =
CALCULATE(
    DISTINCTCOUNT(FileIntakeRegistry[file_id]),
    FileIntakeRegistry[file_has_findings] = TRUE()
)
```

## Model Notes

- Relate `PipelineLogs[run_id]` one-to-many to `ValidationErrors[run_id]`, `ProductRecordAudit[run_id]`, and `FileIntakeRegistry[run_id]`.
- Keep `ProductRecordAudit` as the row-level product quality fact table.
- Keep `ValidationErrors` as the error review queue fact table.
- Use `PipelineLogs` for run-level status, date, and volume measures.
- Use `FileIntakeRegistry` for source-file intake and routing visibility.
- HCPCS-like fields are classification-support examples only and should not be used for billing guidance.

## Future Re-Entry Warnings

- Do not claim these measures are deployed until they are loaded into a PBIX or Power BI semantic model.
- If table or column names change in Power Query, update this DAX document at the same time.
- Keep warning rows separate from rejected rows; warning records require review but are not blocked records.
