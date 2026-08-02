# Phase 5 — CEIS Grounding-Only Prototype

Exploratory prototype comparing SharePoint agent grounding quality/citation behavior across two
content representations of the CEIS Manual: the existing `.aspx` topic pages
(`SitePages/CEISPilotKnowledgePages/`) and a newly-uploaded rendered `.md` set. Design:
`docs/superpowers/specs/2026-08-02-phase-5-ceis-grounding-prototype-design.md`.

## Setup

Copy `config.psd1.example` to `config.psd1` and fill in `ClientId`/`TenantId`/`SiteUrl` for
`AG-CSB-INTRANET-DEV` (same values as `tools/phase-3-sharepoint-discovery/config.psd1` /
`tools/phase-4-native-sharepoint-skills/tenant-config.psd1`).

## Evaluations

`evaluations/{normal,negative,ambiguous,currency}/*.json` — schema-validated case files (see
`tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json`, shared, extended
with a `currency` category for this phase). `permission` and `safety` categories are deliberately
absent this round — permission testing needs a second licensed identity (not available); safety
testing is Phase 4's concern (native-skill write/delete safety), not this grounding-only prototype's.

Run `python3 evaluations/validate_cases.py` to validate every case file against the schema.

## Test-run results

Each case is run manually against both the `.aspx`-grounded agent and the `.md`-grounded agent in
the SharePoint chat pane (no API for this — Copilot chat is browser-only). Results recorded in
`results/<case-id>-aspx.md` and `results/<case-id>-md.md` (see Task 6 of the implementation plan).
