# List content audit: model, scripts and known issues

## Contents

- [Case-keyed ground truth model](#case-keyed-ground-truth-model)
- [Scripts and tools](#scripts-and-tools)
- [Known issues registry](#known-issues-registry)

## Case-keyed ground truth model

When SharePoint list items or target lookup parent lists (`Persons`) are re-migrated or ID-shifted, lookup
pointers can drop (`$null`), point to stale integer IDs, or misbind to the wrong entity through string-matching
collisions. The audit uses a case-keyed ground truth model:

1. Index on-premises source data by immutable natural business keys (`Case_x0020_ID` / `Title`).
2. Translate source Person IDs into verified SPO target Person IDs through deterministic multi-attribute mapping
   (`id-mapping-verified.json`).
3. Compare expected ground truth against actual live SPO state.
4. Output zero-PII metrics and export row-by-row variance reports for targeted in-place healing.

## Scripts and tools

| Script | Type | Description |
| :--- | :--- | :--- |
| `scripts/export-persons-sp2016-to-csv.ps1` | PowerShell 7 | Prerequisite: exports SP2016 On-Prem Persons with natural assurance keys (CS Number, FPS, Name, DOB, Role, etc.) to `.agents/scratch/pii-data/persons-sp2016-onprem.csv`. |
| `scripts/export-persons-spo-to-csv.ps1` | PowerShell 7 | Prerequisite: exports live SPO PROD Persons with the same natural assurance keys to `.agents/scratch/pii-data/persons-spo-prod.csv`. |
| `scripts/analyze-persons-mapping-assurance.py` | Python 3 | Prerequisite: performs 4-tier deterministic matching (CS Number, FPS, strict Name+DOB, extended composite) between the two Persons exports, writing the zero-PII `id-mapping-verified.json` consumed by the analyzer. Supports `--delete-pii-after` to purge the raw PII CSVs once the mapping is built. |
| `scripts/export-list-content-pairs.ps1` | PowerShell 7 | Discovery step: populates paired CSV datasets of current list content from SP2016 and SPO PROD into `.agents/scratch/pii-data/`, for downstream deep variance analysis. |
| `scripts/audit-list-lookup-reconciliation.ps1` | PowerShell 7 | Extracts SP2016 ground truth, queries live SPO, reconciles lookups, and computes Case ID suffix skew into `.agents/scratch/audit-reports/`. |
| `scripts/analyze-lookup-variances.py` (or `analyze-all-variances.py`) | Python 3 | Full-spectrum content, row and lookup variance auditor generating zero-PII reports in `.agents/scratch/audit-reports/`. Cross-references `known-issues.json` to annotate output with previously documented root causes instead of re-analyzing them. |
| `scripts/check-list-id-suffix-skew.ps1` | PowerShell 7 | Standalone diagnostic measuring Item ID vs Case Number suffix shifts. |
| `scripts/backfill-itau-cases-person-lookups.ps1` | PowerShell 7 | High-speed 2-phase batch healer for `ITAU_Cases` specifically: translates its 8 on-prem Person Lookup columns via `id-mapping-verified.json` and applies non-destructive in-place updates through PnP batching (100 cases per batch). Not generic: hardcoded to `ITAU_Cases`' field set. |
| `known-issues.json` | Data (JSON) | Persistent, version-controlled registry of previously root-caused parity issues (for example the Persons Item ID drift from a duplicate ShareGate redeploy) and their sanctioned remediation. |

## Known issues registry

`known-issues.json` (in the skill's `scripts/` folder) is a persistent log of parity issues already root-caused in
Phase 2, so later passes don't re-derive the same explanation. Each entry documents the affected list(s) and
column(s), the observable symptom signature, the confirmed root cause, the current status (resolved,
accepted-gap, or needs-backfill), and the sanctioned remediation.

Add a new entry whenever Phase 2 confirms a fresh root cause for a recurring variance, instead of leaving the
explanation only in a one-off analysis document that can go stale.
