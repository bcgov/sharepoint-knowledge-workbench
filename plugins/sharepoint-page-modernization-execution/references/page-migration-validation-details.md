# Page migration validation details

## Contents

- [Purpose](#purpose)
- [What is checked](#what-is-checked)
- [Usage](#usage)
- [Provenance](#provenance)

## Purpose

Use after `sharepoint-execute-page-bulk-migration` (or a manual `sharepoint-convert-page-to-modern` run) to independently confirm every converted page landed with the metadata it was supposed to get.
It never trusts the conversion run's own exit code: it re-queries the live site. Read-only: REST and PnP read cmdlets only, no tenant writes.

## What is checked

- The modern page exists in `-TargetLibrary` (default `Site Pages`).
- Every target field named as a value in `-FieldMapping` is non-empty.
- Every field named in `-LiteralFieldValues` equals its expected value exactly.

Pass the same `-FieldMapping` and `-LiteralFieldValues` JSON files used for the conversion run being validated. It writes a pass/fail test report (`-ReportPath`) and exits non-zero on any failure, so it
can be used in a pipeline. `-IncludeSkipped` includes pages the run skipped.

## Usage

```bash
pwsh -File scripts/spo-validate-page-conversion.ps1 -ManifestPath run-manifest.csv -FieldMapping field-mapping.json -LiteralFieldValues literals.json -ReportPath test-report.csv
```

## Provenance

Generalized from the originating SharePoint migration repository's `link-conversion/Test-LinkConversion.ps1`: hardcoded expected field names were replaced with the same caller-supplied `-FieldMapping` /
`-LiteralFieldValues` JSON files the conversion skill accepts. Source repository only.
