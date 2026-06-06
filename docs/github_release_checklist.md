# GitHub Release Checklist

Use this checklist before pushing the repository to GitHub.

## Required Files

- [x] `README.md`
- [x] `LICENSE`
- [x] `.gitignore`
- [x] `automation/database/schema.sql`
- [x] `automation/powershell/Watch-IntakeFolder.ps1`
- [x] `automation/powershell/Run-SamplePipeline.ps1`
- [x] `data/sample_input/supplier_product_records_sample.csv`
- [x] `docs/data_dictionary.md`
- [x] `docs/validation_rules.md`
- [x] `docs/operating_notes.md`
- [x] `docs/proof_notes.md`
- [x] `docs/github_release_checklist.md`
- [x] `.github/workflows/python-tests.yml`
- [x] `queries/TransformOperationsLog.m`
- [x] `analytics/dax_measures.md`
- [x] `analytics/dashboard_wireframe.md`
- [x] `analytics/dashboard_build_notes.md`
- [x] `analytics/screenshots/README.md`
- [x] `tests/`
- [x] `src/`

## Verification

- [x] Python tests pass locally.
- [x] Demo command runs locally.
- [x] Public-safe sample data boundary is documented.
- [x] PowerShell execution-policy fallback is documented.
- [x] PBIX and screenshot absence is explicitly documented.
- [x] Runtime artifacts are ignored by `.gitignore`.
- [x] Final repo copy and zip are created under `outputs/final_repo/`.

## Do Not Claim

- Production deployment
- Billing automation
- Payer policy logic
- Clinical decisioning
- Private-data processing
- PBIX completion
- Real dashboard screenshots

## Future Re-Entry Warnings

- If Git is initialized later, inspect `git status --short` before staging.
- Do not commit runtime databases, generated JSON run reports, pycache files, or routed CSV copies.
- If a real PBIX is added, capture screenshot evidence and update claims before release.
