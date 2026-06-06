# PowerShell Intake Workflow

## Purpose

The PowerShell intake layer demonstrates a local file workflow for public-safe DME/CRT supplier and product CSV records. It connects folder intake automation to the existing Python validator and SQLite observability ledger without changing the Phase 1 validation rules.

This workflow does not process patient data, customer addresses, payer records, order IDs, clinical records, private supplier agreements, or private financial data. HCPCS-like fields remain classification-support examples only.

## Folder Routing

The workflow uses workspace-relative paths:

| Folder | Purpose |
| --- | --- |
| `data/intake/` | Source folder scanned for `.csv` files. Original intake files are preserved. |
| `data/processing/` | Temporary working folder for copied intake files. |
| `data/processed/` | Destination for processing copies with no warnings or rejections. |
| `data/review/` | Destination for processing copies with warnings and no rejected rows. |
| `data/rejected/` | Destination for processing copies with rejected rows or validator execution failure. |
| `data/intake/.processed_markers/` | Hash marker files that prevent repeated processing unless `-Reprocess` is used. |
| `outputs/run_reports/` | JSON reports created by the Python validator. |
| `data/runtime/` | SQLite runtime database location. |

## Scripts

### `automation/powershell/Watch-IntakeFolder.ps1`

Scans or monitors `data/intake/` for `.csv` files, copies each detected file to `data/processing/`, invokes the Python validator, and routes the processing copy to the appropriate outcome folder.

Common commands:

```powershell
.\automation\powershell\Watch-IntakeFolder.ps1 -Once
.\automation\powershell\Watch-IntakeFolder.ps1 -Once -DryRun
.\automation\powershell\Watch-IntakeFolder.ps1 -Once -Reprocess -ResetDatabase
```

Leave `-Once` off to keep polling `data/intake/` every 10 seconds. Use `-PollSeconds` to change the interval.

### `automation/powershell/Run-SamplePipeline.ps1`

Copies `data/sample_input/supplier_product_records_sample.csv` into `data/intake/` with a timestamped filename, then calls the watcher for that file.

Common commands:

```powershell
.\automation\powershell\Run-SamplePipeline.ps1
.\automation\powershell\Run-SamplePipeline.ps1 -DryRun
.\automation\powershell\Run-SamplePipeline.ps1 -NoResetDatabase
```

The default sample run resets the SQLite runtime database for a repeatable demo. Use `-NoResetDatabase` to append to the existing local ledger.

If local execution policy blocks direct script execution, use a process-scoped execution-policy command from the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1
```

Dry-run command path:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\automation\powershell\Run-SamplePipeline.ps1 -DryRun
```

## Routing Logic

Routing is based on the JSON report produced by the existing Python validator:

- `processed`: zero rejected rows and zero warning rows
- `review`: zero rejected rows and one or more warning rows
- `rejected`: one or more rejected rows, missing report, or validator execution failure

The Phase 1 severity choices are unchanged:

- Missing `documentation_source`: `WARNING`
- Missing compatibility notes for compatibility-sensitive products: `WARNING`
- Duplicate SKU/MPN: `ERROR`
- Unsupported category/type and invalid HCPCS-like format: `ERROR`

## Non-Destructive Behavior

The workflow copies intake files to processing instead of moving the original source file. The processing copy is routed to an outcome folder after validation. Hash markers prevent repeated processing of the same source file during monitoring, but `-Reprocess` can be used for a deliberate demo rerun.

Generated CSV copies, marker files, runtime databases, and JSON run reports are excluded by `.gitignore`.

## Future Re-Entry Warnings

- Do not treat this as a production file watcher or deployment service; it is a local portfolio demonstration.
- Do not add private supplier, patient, customer, payer, order, or financial data to the intake folders.
- Keep Phase 3 analytics work separate; Power Query, DAX, and dashboard files are not part of this phase.
- If PowerShell execution policy blocks direct script execution, run the documented commands from a PowerShell session where local scripts are allowed or use the dry-run path to verify routing intent.
