---
name: create-sharepoint-agent
description: Authors a validated SharePoint Copilot agent (.agent JSON) source file locally, from explicit name/description/instructions/knowledge-source parameters. Does not deploy it.
---

# create-sharepoint-agent

## Purpose

Produces a locally validated `.agent` JSON source file per the reverse-engineered schema
(`schemaVersion 0.2.0`, `customCopilotConfig.gptDefinition`) — new build, parameterized per the
design doc's Section 4 script parameter matrix, not extracted verbatim from any of the 5
experimental `create-*-agent.ps1`/`create-md-comparison-agent.ps1` scripts (all CEIS-hardcoded,
kept in `tools/` as research/evidence of the schema pattern this script implements generically).

## Input boundaries

- `-AgentName`, `-AgentDescription` (required).
- `-AgentInstructionsPath` **or** `-AgentInstructions` (exactly one required).
- `-KnowledgeSourcePaths` (required, at least one URL) — no default; replaces the research
  scripts' hardcoded `items_by_url` blocks.
- `-AgentTemplatePath` (optional) — clone an existing agent's structure, e.g. the confirmed-
  working `CEIS-ASPX-Only-Test` pattern from Phase 5 Task 4/6.
- `-OutputPath` (required); `-Overwrite` required to replace an existing file.

## Prohibited scope

- Zero tenant I/O — no `Connect-PnPOnline` call anywhere in this script.
- Does not deploy the produced package — agent upload is a separate, not-yet-built capability.
- Always sets `behavior_overrides.special_instructions.discourage_model_knowledge = true` to
  force grounding on knowledge sources, matching the confirmed-working reference-agent pattern.

## Scripts

- `../../scripts/create-sharepoint-agent.ps1`

## Tests

`../../tests/unit/test_create_sharepoint_agent.py` — 4 executable tests via `pwsh` (valid
`.agent` JSON produced, at-least-one-knowledge-source enforced, overwrite protection, mutually-
exclusive instruction sources).

**Real bug found and fixed while writing these tests:** `ConvertTo-Json` silently unwraps a
single-element PowerShell array into a bare object — `items_by_url` with exactly one knowledge
source was serialized as `{...}` instead of `[{...}]`, which would have produced schema-invalid
output for the single-source case (the most common one). Fixed with an explicit
`[System.Object[]]` cast.
