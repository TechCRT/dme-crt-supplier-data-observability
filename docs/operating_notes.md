# Operating Notes

## Local Tool Chain

The project uses:

- PowerShell
- Python
- SQLite
- Power Query / M
- DAX
- Power BI

No alternate runtime stack is required for the implemented local demo.

## Python Commands

Run tests:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

Run the sample validation demo:

```powershell
$env:PYTHONPATH = "src"
python -m dme_crt_supplier_observability.cli run-demo
```

Validate a specific CSV:

```powershell
$env:PYTHONPATH = "src"
python -m dme_crt_supplier_observability.cli validate-file data\sample_input\supplier_product_records_sample.csv
```

## PowerShell Intake

Use the process-scoped execution-policy command when direct local script execution is blocked:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1
```

Dry-run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1 -DryRun
```

The workflow preserves original intake files and routes processing copies based on validation outcomes.

## Runtime Outputs

Generated runtime artifacts:

- `data/runtime/supplier_observability.sqlite`
- `outputs/run_reports/*.json`
- `data/intake/*.csv`
- `data/intake/.processed_markers/*.json`
- `data/processing/*.csv`
- `data/processed/*.csv`
- `data/review/*.csv`
- `data/rejected/*.csv`

These are ignored by `.gitignore`.

## Analytics Build

The documented Power BI layer uses:

- `queries/TransformOperationsLog.m`
- `analytics/dax_measures.md`
- `analytics/dashboard_wireframe.md`
- `analytics/dashboard_build_notes.md`
- `analytics/screenshots/README.md`

No PBIX or real screenshots are included in the current repository.

## Future Re-Entry Warnings

- Do not push generated runtime artifacts.
- Do not claim production deployment, billing automation, payer policy logic, clinical decisioning, PBIX completion, or real screenshots.
- If a real Power BI report is built later, update proof notes, screenshot notes, and final claims before publishing.
