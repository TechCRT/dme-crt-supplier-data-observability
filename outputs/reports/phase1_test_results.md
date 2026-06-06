# Phase 1 Test Results

Date: 2026-06-06

## Test Command

```powershell
$env:PYTHONPATH='src'; python -m unittest discover -s tests
```

Result:

```text
Ran 8 tests in 0.559s
OK
```

## Coverage Areas

The Phase 1 test suite covers:

- Passing row validation
- Required-field rejection behavior
- Unsupported category/type rejection behavior
- HCPCS-like format rejection behavior
- Duplicate SKU handling
- Sample file validation across `PASS`, `WARNING`, and `REJECT`
- SQLite table creation
- Pipeline log insertion
- File intake registry insertion
- Product audit insertion
- Validation error insertion
- JSON report creation
- CLI `init-db` and `run-demo`
- Demo reset behavior

## Demo Verification

Final demo command:

```powershell
$env:PYTHONPATH='src'; python -m dme_crt_supplier_observability.cli run-demo
```

Final demo result:

- Run ID: `run-20260606091609-9f58a896`
- Status: `WARNING`
- Rows total: 6
- Rows passed: 2
- Rows warning: 1
- Rows rejected: 3
- Runtime table counts: `pipeline_logs=1`, `validation_errors=8`, `file_intake_registry=1`, `product_record_audit=6`

## Known Test Boundaries

- Tests are standard-library `unittest` tests, not a coverage-report workflow.
- PowerShell intake behavior is intentionally not tested in Phase 1 because it belongs to Phase 2.
- Power Query, DAX, and Power BI dashboard assets are intentionally not tested in Phase 1 because they belong to Phase 3.

## Future Re-Entry Warnings

- Keep `PYTHONPATH=src` when running the package before adding an install workflow.
- On Windows, close SQLite connections explicitly before deleting or resetting database files.
- Do not interpret the demo `WARNING` status as a runtime failure; it reflects intentionally included review and rejection examples.
- If test expectations change after severity review, update tests and phase reports together.
