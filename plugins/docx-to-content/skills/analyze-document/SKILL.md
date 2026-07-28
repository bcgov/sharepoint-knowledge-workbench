---
name: analyze-document
plugin: docx-to-content
description: Analyze a source Word document's structure and produce a transitory raw analysis plus a draft conversion plan for human confirmation.
allowed-tools: Bash, Read, Write
examples:
  - "python -m scripts.cli analyze --source sourcedocuments/Manual.docx --output analysis/Manual"
---

# Analyze Document

## Trigger and Purpose

Use this skill as the FIRST step whenever a new source `.docx` needs to enter the
docx-to-content pipeline, or when re-analyzing a source after it changed. It
inspects the document's real structure (headings, sections, embedded/legacy
media) and produces a **draft** `ConversionPlan` for a human to review — it
never converts content and never writes canonical output.

## Exact CLI Invocation

```bash
python -m scripts.cli analyze --source <docx> --output <analysis-dir>
```

- `--source` — path to the source `.docx` file (must exist).
- `--output` — directory to write analysis output to (created if missing).

## Inputs and Output Artifacts

- **Input**: a single `.docx` file on disk.
- **Output**: `<analysis-dir>/` containing raw, **transitory** analysis
  output (heading/structure scan, detected legacy `.emf` media, analysis
  warnings) and a **draft plan** (`confirmation.status == "draft"`).

The raw analysis output is intermediate working material, not a durable
artifact of the pipeline — it exists only to inform the draft plan and the
human reviewing it. It is never treated as canonical content and is not
promoted anywhere. Do not persist it as if it were a finished deliverable.

The analysis report also includes a `proposed_topics` preview: every
level-1 heading in the source, grouped with its descendant headings, with a
deterministic `topic_id`, anchor count, and child-heading count. This is
what a human reviews before deciding whether to set the draft plan's
`strategy` to `"grouped"` (see convert-document's grouped-strategy section)
instead of the default `"single"`/`"chunked"` recommendation — it does not
change what `analyze` writes to the plan itself.

## Preconditions

- The source file at `--source` must exist (missing file → exit code 3).
- `pandoc` must be available on `PATH` (missing dependency → exit code 3).

## PASS/WARN/FAIL and Exit-Code Behavior

- **PASS** (exit code `0`): analysis completed; a draft plan was written to
  `--output`.
- **FAIL** (exit code `2`): malformed/unsupported plan or contract data.
- Dependency/precondition failure (missing source file, missing pandoc):
  exit code `3`.
- Usage error (unknown subcommand, missing required argument, unsupported
  renderer or schema): exit code `4`.
- There is no WARN outcome for `analyze` itself — structural concerns
  discovered here are recorded as `analysis_warnings` on the draft plan for
  the human reviewer to see during confirmation, not as a validation
  disposition.

## Prohibited Shortcuts

- Must not skip straight to `convert` using the **draft** plan this skill
  produces — a draft plan has `confirmation.status == "draft"` and `convert`
  requires an already-**confirmed** plan.
- Must not treat the raw analysis output as canonical content or copy it
  into `canonical-content/`.
- Must not hand-edit the draft plan's `plan_id` — it is a computed hash
  (`hashing.compute_plan_id`) and any downstream integrity check will
  reject a tampered value.

## Handoff to the Next Skill

The draft plan produced here must be reviewed by a human and explicitly
promoted via `confirm` (see `convert-document/SKILL.md`) before any
conversion happens:

```bash
python -m scripts.cli confirm --draft-plan <path> --output <confirmed-plan>
```
