# Phase 2 Demo Notes

Date: 2026-06-06

## Demo Objective

Demonstrate the complete local Phase 2 path:

`data/sample_input/` -> `data/intake/` -> `data/processing/` -> Python validator -> SQLite ledger and JSON report -> final route folder.

## Commands

Direct command attempted first:

```powershell
& .\automation\powershell\Run-SamplePipeline.ps1
```

Local execution-policy blocker:

```text
Running scripts is disabled on this system.
FullyQualifiedErrorId: UnauthorizedAccess
```

Successful command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1
```

Python test command rerun after Phase 2 edits:

```powershell
$env:PYTHONPATH='src'; python -m unittest discover -s tests
```

Dry-run command verified:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1 -DryRun
```

## Final Demo Output

Final run ID: `run-20260606093147-df25e4e6`

Validator output:

```text
status=WARNING
source=20260606043146_phase2_sample_20260606043146.csv
rows_total=6
rows_passed=2
rows_warning=1
rows_rejected=3
```

Route result:

```text
Routed processing copy to REJECTED: data/rejected/20260606043146_phase2_sample_20260606043146.csv
```

The rejected route is correct for the demo sample because it contains invalid taxonomy values, an invalid HCPCS-like value, a missing manufacturer, and duplicate SKU rows.

## Runtime Artifacts

Relevant final artifacts:

- JSON report: `outputs/run_reports/run-20260606093147-df25e4e6.json`
- Routed file: `data/rejected/20260606043146_phase2_sample_20260606043146.csv`
- Marker file: `data/intake/.processed_markers/5b0b3deb959081c3.json`
- SQLite runtime database: `data/runtime/supplier_observability.sqlite`

`data/processing/` was empty after final routing except for `.gitkeep`.

## Public-Safe Notes

The demo uses only the existing public-safe sample CSV. The workflow does not introduce patient, customer, payer, order, clinical, private supplier agreement, or private financial data.

## Future Re-Entry Warnings

- Do not delete preserved intake files unless a cleanup pass is explicitly requested.
- If rerunning the sample pipeline, expect new timestamped intake and routed copies.
- If using the watcher without `-Reprocess`, marker files may intentionally skip previously seen source content.
- Keep Phase 3 analytics work separate until the user explicitly requests it.
