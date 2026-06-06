# Proof Notes

This file records local evidence for the portfolio project. It is not a deployment log.

## Test Evidence

Final Phase 4 test command:

```powershell
$env:PYTHONPATH='src'; python -m unittest discover -s tests
```

Expected passing suite:

```text
Ran 19 tests in 0.453s
OK
```

Covered areas:

- Product validation rules
- Duplicate SKU handling
- SQLite table creation
- Pipeline logs
- File intake registry
- Product audit rows
- Validation errors
- JSON report creation
- CLI demo behavior
- PowerShell asset contracts
- Analytics documentation boundaries

## Demo Evidence

Phase 4 reruns the demo command:

```powershell
$env:PYTHONPATH='src'; python -m dme_crt_supplier_observability.cli run-demo
```

Expected sample pattern:

- Run ID: `run-20260606095815-4b3c2c57`
- 6 total rows
- 2 passing rows
- 1 warning row
- 3 rejected rows
- Pipeline status `WARNING`
- Runtime table counts: `pipeline_logs=1`, `validation_errors=8`, `file_intake_registry=1`, `product_record_audit=6`

This pattern is expected because the sample file intentionally includes warning and rejection examples.

## Analytics Evidence

Phase 3 documents the Power BI analytics layer through:

- Power Query / M file
- DAX measure documentation
- Dashboard wireframe
- Build notes
- Screenshot placeholder instructions

No PBIX file and no real screenshots are present.

## Boundary Evidence

The project uses mock/public-safe sample data only. It does not contain patient data, customer addresses, payer records, order IDs, clinical records, private supplier agreements, or private financial data.

## Future Re-Entry Warnings

- Update this file with exact final test/demo run IDs after each final release pass.
- Do not treat local runtime JSON reports as production monitoring evidence.
- Do not claim dashboard screenshots exist until real screenshots are added.
