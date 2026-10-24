# Single page conversion details

## Contents

- [Purpose](#purpose)
- [Field mapping is caller-supplied](#field-mapping-is-caller-supplied)
- [Usage](#usage)
- [Provenance](#provenance)

## Purpose

Convert one classic `.aspx` page to a modern SharePoint Site Page within the same site, stamping any source metadata you want carried over onto the converted page under different (target)
field names.

## Field mapping is caller-supplied

`-FieldMapping` (source field internal name to target field internal name) and `-LiteralFieldValues` (target field internal name to a fixed value, for example a migration tag) are both optional JSON
files you provide. No project-specific field names ship with the skill.

## Usage

```bash
# Dry run
pwsh -File scripts/page-modernization-execution/spo-convert-page-to-modern.ps1 -PageName "article.aspx" -SourceLibrary "ClassicPages"

# Real conversion with field mapping
pwsh -File scripts/page-modernization-execution/spo-convert-page-to-modern.ps1 -PageName "article.aspx" -SourceLibrary "ClassicPages" -FieldMapping field-mapping.json -LiteralFieldValues literals.json -Execute -ConfirmToken CONVERT-SPO-PAGE
```

## Provenance

Generalized from the originating SharePoint migration repository's `link-conversion/LinkConversion.ps1`: the hardcoded destination-site name and hardcoded source-to-target field mapping were
replaced with caller-supplied `-FieldMapping` / `-LiteralFieldValues` JSON files. Source repository only.
