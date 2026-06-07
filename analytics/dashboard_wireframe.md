# Dashboard Wireframe

This document provides a dashboard wireframe only. No PBIX file or real dashboard screenshot is included.

## Page 1: Pipeline Health Overview

Purpose: show whether the local intake and validation workflow is running cleanly and where attention is needed.

Top KPI row:

| KPI | Measure |
| --- | --- |
| Pipeline Success Rate | `Pipeline Success Rate` |
| Warning or Failure Runs | `Warning or Failure Runs` |
| Failed Run Count | `Failed Run Count` |
| Average Rows Per Run | `Average Rows Per Run` |

Main visuals:

| Visual | Data |
| --- | --- |
| Run status trend | `PipelineLogs[completed_date]`, count of `run_id`, grouped by `status` |
| Rows processed by run | `PipelineLogs[source_filename]`, `rows_passed`, `rows_warning`, `rows_rejected_validation` |
| File intake status | `FileIntakeRegistry[file_status]`, count of `file_id` |
| Run detail table | `run_id`, `source_filename`, `completed_datetime`, `total_rows_detected`, `status` |

Filters:

- Completed date
- Source filename
- Run status
- File status

## Page 2: Supplier/Product Data Quality

Purpose: surface product-data quality by supplier, manufacturer, product category, and product type.

Top KPI row:

| KPI | Measure |
| --- | --- |
| Data Integrity Rate | `Data Integrity Rate` |
| Total Records Blocked | `Total Records Blocked` |
| Validation Rejection Rate | `Validation Rejection Rate` |
| Records Requiring Review | `Records Requiring Review` |

Main visuals:

| Visual | Data |
| --- | --- |
| Supplier quality matrix | `supplier_name`, `manufacturer`, `records_total`, `records_passed`, `records_warning`, `records_rejected` |
| Product category quality bar chart | `product_category`, count of rows by `validation_status` |
| Product type review queue count | `product_type`, `records_requiring_review` |
| Rejected record table | `source_filename`, `row_number`, `supplier_name`, `manufacturer`, `model`, `sku`, `mpn`, `validation_status`, `error_count` |

Filters:

- Supplier name
- Manufacturer
- Product category
- Product type
- Validation status

## Page 3: Error Review Queue

Purpose: give an operator a clear queue of validation findings that need remediation or source-data review.

Top KPI row:

| KPI | Measure |
| --- | --- |
| Total Validation Findings | `Total Validation Findings` |
| Error Finding Count | `Error Finding Count` |
| Warning Finding Count | `Warning Finding Count` |
| Records Requiring Review | `Records Requiring Review` |

Main visuals:

| Visual | Data |
| --- | --- |
| Findings by rule | `ValidationErrors[validation_rule]`, count of `error_id`, stacked by `severity` |
| Findings by field | `ValidationErrors[field_name]`, count of `error_id` |
| Error queue table | `run_id`, `source_filename`, `row_number`, `field_name`, `rejected_value`, `validation_rule`, `severity`, `error_message` |
| Review status helper | `ProductRecordAudit[needs_review_flag]`, `validation_status`, row counts |

Filters:

- Severity
- Validation rule
- Field name
- Source filename
- Run ID

## Layout Guidance

- Keep each page dense and operational rather than promotional.
- Use restrained colors: green for pass/success, amber for warnings/review, red for rejected/failed.
- Keep row-level tables readable with conditional formatting on `severity` and `validation_status`.
- Avoid implying deployment evidence; title the report as a local observability dashboard.

## Screenshot Placeholder

Until a PBIX is created, use `analytics/screenshots/README.md` as the screenshot placeholder. Replace it only after capturing real Power BI screenshots.

## Operating Notes

- Do not claim a live dashboard exists without PBIX or screenshot evidence.
- Preserve the three-page structure unless later data volume or reviewer feedback justifies a change.
- Keep rejected-record reporting and warning review visibility separate.
