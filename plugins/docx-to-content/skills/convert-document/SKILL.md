---
name: convert-document
plugin: docx-to-content
description: Confirm a draft plan and convert a source Word document into a validated canonical content package.
allowed-tools: Bash, Read, Write
examples:
  - "python -m scripts.cli confirm --draft-plan analysis/Manual/plan.json --output analysis/Manual/plan.confirmed.json"
  - "python -m scripts.cli convert --source sourcedocuments/Manual.docx --plan analysis/Manual/plan.confirmed.json --output runs/Manual"
---

# Convert Document

## Trigger and Purpose

Use this skill after `analyze-document` has produced a draft plan and a human
has reviewed it. It has two steps: explicitly **confirm** the draft plan
(a deliberate, one-way human action), then **convert** the source `.docx`
into a staged, validated **canonical content** package using that confirmed
plan and its recorded source hash.

## Exact CLI Invocation

```bash
python -m scripts.cli confirm --draft-plan <path> --output <confirmed-plan>
python -m scripts.cli convert --source <docx> --plan <confirmed-plan> --output <run-dir>
```

- `confirm --draft-plan` — path to the draft plan produced by `analyze`.
- `confirm --output` — path to write the confirmed plan to.
- `convert --source` — path to the source `.docx` file (must exist).
- `convert --plan` — path to the **confirmed** plan file.
- `convert --output` — run directory to write canonical output under.

## Inputs and Output Artifacts

- **Inputs**: the draft plan (`confirm`), then the source `.docx` plus the
  confirmed plan (`convert`).
- **Output of `confirm`**: a confirmed plan file with
  `confirmation.status == "confirmed"`, `confirmation.confirmed_by`,
  `confirmation.confirmed_at`, and a freshly recomputed `plan_id`.
- **Output of `convert`**: `<run-dir>/canonical-content/` — the canonical
  content package (chunked content, media, `manifest.json`,
  `validation.json`) — built first in a unique staging directory and only
  promoted to `canonical-content/` if validation allows it.

## Preconditions

- `confirm` rejects a plan that is already confirmed (double-confirming a
  plan is not idempotent — confirm the draft it came from instead).
- `convert` requires `--plan` to already have `confirmation.status ==
  "confirmed"` (a draft plan is rejected, exit code `4`) — `convert` never
  confirms a draft itself.
- The `--source` file must exist and match the **source_sha256** recorded
  on the confirmed plan; `convert` verifies the plan against the source
  (`plans.verify_plan_against_source`) and against its own integrity
  (`plans.verify_plan_integrity`) before touching content. A stale or
  tampered plan is rejected, not silently reprocessed.
- `pandoc` must be available on `PATH`.

## Staging and Canonical Validation

`convert` never writes directly to the final `canonical-content/` location.
It builds the package in a fresh, unique staging directory first, runs the
canonical validator (`validate_canonical.py`) against that staged package,
and only promotes it to `<run-dir>/canonical-content/` if the validation
report allows it:

- **PASS**: no errors, no undispositioned warnings — promoted.
- **WARN**: reviewable discrepancies exist — promoted ONLY once every
  warning is recorded in `warning-disposition.json` as `accepted` or
  `resolved` (see `dispositions.py`). An undispositioned WARN is not
  promoted.
- **FAIL**: any invariant/integrity/schema/reference/required-fidelity
  check fails — the run exits non-zero, staging output is retained on disk
  for diagnosis, and `canonical-content/` is left untouched.

## PASS/WARN/FAIL and Exit-Code Behavior

- **PASS** (exit code `0`): plan confirmed / package built, validated, and
  promoted.
- **WARN**: promotion proceeds only with a complete
  `warning-disposition.json`; an incomplete disposition set blocks
  promotion the same as FAIL.
- **FAIL** (exit code `2`): malformed/unsupported plan or contract data, or
  a canonical validation FAIL (missing anchors, ambiguous anchors, illegal
  media references, unconverted legacy media, etc.).
- Dependency/precondition failure (missing source file, missing pandoc):
  exit code `3`.
- Usage error (already-confirmed plan passed to `confirm`, draft plan
  passed to `convert`, stale/tampered plan): exit code `4`.

## Grouped Strategy

`convert` supports a third `plan.strategy` value alongside the default
`"single"`/`"chunked"`: `"grouped"`. Instead of one canonical chunk file
per heading (the `"single"`/`"chunked"` behavior, unchanged), `"grouped"`
folds every heading under a top-level (level-1) section into a single
**topic** chunk file — roughly 25 topic files for a document with ~159
headings, rather than 159 files. Structural-anchor lineage is not lost:
each topic chunk's sidecar carries an `anchors` list (`stable_key`,
`source_heading_path`, `occurrence`, `heading_level` for every heading
folded into it, in source order), so every original heading remains
individually addressable. A `publication-map.json` sidecar is written
alongside `manifest.json`, giving explicit topic ordering for rendering
(see `references/publication-map-contract.md`). Set `strategy: "grouped"`
on the draft plan (reviewing the analysis report's `proposed_topics`
preview first) before running `confirm`.

## Prohibited Shortcuts

- Must not bypass `confirm` and hand-write `confirmation.status:
  "confirmed"` into a draft plan — `plan_id` is a computed hash over the
  plan's content and any tampering is caught by
  `plans.verify_plan_integrity`.
- Must not promote a staged package to `canonical-content/` manually when
  validation reported FAIL, or WARN with undispositioned warnings.
- Must not reuse a confirmed plan against a different source document —
  the recorded `source_sha256` is checked against the actual source file.

## Handoff to the Next Skill

Once a canonical content package is promoted, hand it to `render-content`:

```bash
python -m scripts.cli render --canonical <canonical-dir> --renderer multipage-markdown --output <render-dir>
```
