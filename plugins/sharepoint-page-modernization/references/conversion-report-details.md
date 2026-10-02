# Conversion report details

## Contents

- [Why](#why)
- [Inputs](#inputs)
- [Gaps are named, never hidden](#gaps-are-named-never-hidden)
- [Honest outcomes](#honest-outcomes)
- [Scope and provenance](#scope-and-provenance)

## Why

A conversion manifest (`assets/manifest-schema.json`) is structured JSON: accurate, but not quick for a reviewer to scan. The skill turns an already-produced manifest into a readable
Markdown disposition report: what web parts were classified, what could not be migrated, and how confident the layout and mapping decisions were.

## Inputs

One manifest file conforming to the schema's required top-level fields: `sourcePage`, `convertedAt`, `manifestHash`, `mapping`, `environmentProfile`, `source`, `target`, `webParts`, `layout`,
`gaps`, `confidence`, `outcome`. This script only renders a manifest; it does not produce one (see `page-modernization-pipeline.md`).

## Gaps are named, never hidden

Every entry in the manifest's `gaps` array is rendered as its own line in the Gaps section; none are dropped or summarized away. An empty `gaps` array renders an explicit "No gaps recorded" line, so a
reviewer never has to guess whether the section was skipped or genuinely empty.

## Honest outcomes

| Condition | Outcome | Report written? |
|---|---|---|
| Manifest missing a required field | `Unavailable` | No |
| Manifest `outcome` field is not a valid outcome status | `Failed` | No |
| Manifest has one or more `gaps` | `Partial` (gap count named) | Yes |
| Manifest has no gaps | `Observed` | Yes |

## Scope and provenance

Reads the manifest file and writes the one report (`--output`, or `conversion-report.md` in the current directory by default). No network calls and no tenant I/O.

Generalized from a disposition-worksheet capability in another SharePoint migration repository's `sharepoint-migration` plugin; only the shape (classification table, gap and dependency summary,
confidence section) was carried over, not its organisation-specific rule categories or hardcoded paths. Source repository only.
