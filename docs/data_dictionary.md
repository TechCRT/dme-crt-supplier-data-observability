# Data Dictionary

This data dictionary documents the public-safe sample input and SQLite operational ledger used by the local validation pipeline.

## Sample Input

File: `data/sample_input/supplier_product_records_sample.csv`

| Field | Type | Description |
| --- | --- | --- |
| `supplier_name` | Text | Public-safe supplier display name used for intake accountability. |
| `manufacturer` | Text | Product manufacturer or brand. |
| `model` | Text | Product model or product name. |
| `sku` | Text | Supplier SKU. At least one of `sku` or `mpn` is required. |
| `mpn` | Text | Manufacturer part number. At least one of `sku` or `mpn` is required. |
| `product_category` | Text | Supported sample category such as `power_wheelchair`, `controller`, `seating`, or `electronics`. |
| `product_type` | Text | Supported sample type such as `standing_power_chair`, `joystick_controller`, or `seating_cushion`. |
| `hcpcs_candidate` | Text | HCPCS-like classification-support example. Not billing guidance. |
| `compatible_chair_family` | Text | Public-safe compatibility family or product family note. |
| `documentation_source` | Text | Reviewable source description such as manufacturer manual or brochure. |
| `listing_status` | Text | Sample listing workflow status. |
| `compatibility_notes` | Text | Review notes for compatibility-sensitive products. |

## SQLite Tables

Database: `data/runtime/supplier_observability.sqlite`

Runtime database files are generated locally and ignored from source control.

### `pipeline_logs`

Run-level observability table.

| Field | Description |
| --- | --- |
| `pipeline_log_id` | Surrogate primary key. |
| `run_id` | Unique validation run identifier. |
| `script_source` | Source workflow, currently `python_cli`. |
| `source_filename` | Input file name validated during the run. |
| `started_at` | UTC timestamp string for run start. |
| `completed_at` | UTC timestamp string for run completion. |
| `total_rows_detected` | Count of CSV records validated. |
| `rows_passed` | Count of records with `PASS` status. |
| `rows_warning` | Count of records with `WARNING` status. |
| `rows_rejected_validation` | Count of records with `REJECT` status. |
| `status` | Run status: `SUCCESS`, `WARNING`, or `FAILED`. |
| `error_message` | Optional run-level error text. |
| `created_at` | SQLite insert timestamp. |

### `validation_errors`

Row-level validation findings.

| Field | Description |
| --- | --- |
| `error_id` | Surrogate primary key. |
| `run_id` | Run identifier linked to `pipeline_logs`. |
| `source_filename` | Input file name. |
| `row_number` | CSV row number. |
| `field_name` | Field associated with the finding. |
| `rejected_value` | Observed value that triggered the finding. |
| `validation_rule` | Rule identifier. |
| `severity` | `INFO`, `WARNING`, or `ERROR`. |
| `validation_status` | Row status: `PASS`, `WARNING`, or `REJECT`. |
| `error_message` | Human-readable finding text. |
| `created_at` | SQLite insert timestamp. |

### `file_intake_registry`

File-level intake and routing ledger.

| Field | Description |
| --- | --- |
| `file_id` | Surrogate primary key. |
| `run_id` | Run identifier linked to `pipeline_logs`. |
| `source_filename` | Source file name. |
| `source_path` | Local path of the file that was validated. |
| `detected_at` | Timestamp when file was registered. |
| `processed_at` | Timestamp when file processing completed. |
| `file_status` | `DETECTED`, `PROCESSED`, `PROCESSED_WITH_FINDINGS`, or `FAILED`. |
| `file_hash` | SHA-256 hash of the source file. |
| `row_count` | Row count detected in the source file. |
| `notes` | Workflow notes. |

### `product_record_audit`

Validated product row audit table.

| Field | Description |
| --- | --- |
| `audit_id` | Surrogate primary key. |
| `run_id` | Run identifier linked to `pipeline_logs`. |
| `source_filename` | Input file name. |
| `row_number` | CSV row number. |
| `supplier_name` | Supplier display name. |
| `manufacturer` | Manufacturer or brand. |
| `model` | Product model. |
| `sku` | Supplier SKU. |
| `mpn` | Manufacturer part number. |
| `product_category` | Sample product category. |
| `product_type` | Sample product type. |
| `hcpcs_candidate` | Classification-support example only. |
| `compatible_chair_family` | Compatibility family note. |
| `documentation_source` | Reviewable documentation source. |
| `listing_status` | Sample listing workflow status. |
| `compatibility_notes` | Compatibility review notes. |
| `validation_status` | `PASS`, `WARNING`, or `REJECT`. |
| `needs_review` | `1` for warning or rejected rows, otherwise `0`. |
| `warning_count` | Count of warning findings for the row. |
| `error_count` | Count of error findings for the row. |
| `source_row_hash` | Stable hash of the row values. |
| `created_at` | SQLite insert timestamp. |

## Operating Notes

- Do not add private customer, patient, payer, order, clinical, supplier agreement, or financial data.
- If schema fields change, update Power Query, DAX, tests, and this dictionary together.
- Keep HCPCS-like values framed as classification-support examples only.
