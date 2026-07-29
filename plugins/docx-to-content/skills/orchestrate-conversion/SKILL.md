---
name: orchestrate-conversion
plugin: docx-to-content
description: Drive a source Word document through the full analyze→confirm→convert→render pipeline in one guided session, pausing at the mandatory human plan-review and media-classification gates.
allowed-tools: Bash, Read, Write
examples:
  - "Convert intake/Manual.docx through the full pipeline, walking me through plan review."
---

# Orchestrate Conversion

## Trigger and Purpose

Use this skill when a human wants to take a source `.docx` all the way
through the pipeline in one guided session, instead of invoking
`analyze-document`, `convert-document`, and `render-content` separately by
hand. It does not replace those three skills or their CLI contract — it is
a thin sequencing layer over the exact same `python -m scripts.cli`
commands they document, run in order, with the mandatory human checkpoints
made explicit instead of left to the human to remember.

This skill introduces no new code. Every command below is the same
contract already specified in `analyze-document/SKILL.md`,
`convert-document/SKILL.md`, and `render-content/SKILL.md` — read those
first if any step's exit-code or validation behavior is unclear.

## Step 1 — Analyze

```bash
python -m scripts.cli analyze --source <docx> --output <analysis-dir>
```

Exit code `3`/`4` (missing source, missing pandoc, usage error): stop and
report — do not attempt a workaround.

## Step 2 — Present the draft plan for review

Read `<analysis-dir>/plan.json` (and the raw analysis report alongside it)
and summarize for the human, in chat, before touching anything else:

- Proposed topic count and roots from `proposed_topics` (source level,
  any `promoted-root`/`ambiguous-root` classifications), and whether
  `strategy: "grouped"` looks appropriate versus the default
  `"single"`/`"chunked"`.
- Every entry in `analysis_warnings` (e.g.
  `MIXED_LOGICAL_ROOT_LEVELS`, `PROMOTED_TOPIC_ROOT`).
- Preamble findings: detected title/subtitle/version metadata, any
  raw Word TOC dump, any `Ctrl+F`-style instructional text slated for
  omission.
- Every record in `media_decisions` whose `classification` is
  `"requires-human-review"` or `disposition` is
  `"requires-human-decision"`.

## Step 3 — Resolve unclassified media inline

For each media record still needing review: find the actual file (under
`<analysis-dir>`'s extracted media directory), **Read it** (this skill has
Read access to images), describe what it actually shows, and ask the human
for the real `classification`/`disposition` (see the vocabularies in
`scripts/media_disposition.py`'s `CLASSIFICATIONS`/`DISPOSITIONS`). Do not
guess a disposition from file size or position alone — those are the
*proposal's* signals, not a substitute for looking at the image, per
`propose_media_decisions`'s own docstring.

Once the human decides, record it on the draft plan with an inline Python
call (there is no CLI subcommand for this — `apply_media_decision` is a
plan-transform function, not a `cli.py` entry point):

```bash
python -c "
import json
from pathlib import Path
from scripts import contracts, plans

plan_path = Path('<analysis-dir>/plan.json')
plan = contracts.ConversionPlan.from_dict(json.loads(plan_path.read_text()))
plan = plans.apply_media_decision(
    plan,
    source_media_id='<filename>',
    classification='<classification>',
    disposition='<disposition>',
    reason='<human-provided reason>',
)
plan_path.write_text(json.dumps(plan.to_dict(), indent=2))
"
```

Repeat until every media record has a real classification/disposition —
`convert` will fail (`unclassified_media`) on any that is still pending.

## Step 4 — Get explicit plan approval, looping on changes

Ask the human to approve the plan as summarized in Step 2/3, or request
changes (e.g. a different `strategy`, a different topic-root call). If
changes are requested:

- For a `strategy` or `confirmed_topic_roots` change that doesn't require
  re-scanning the source, edit `plan.json` directly and recompute
  `plan_id` (same pattern as Step 3's inline Python, via
  `hashing.compute_plan_id`).
- For anything requiring a fresh structural scan, re-run `analyze` and
  rebuild the draft, but preserve already-reviewed
  `confirmed_topic_roots`/`media_decisions` where the human confirms they
  still apply — do not make the human re-answer settled questions (this is
  the same rebuild-not-restart handling Task 18 needed after the
  `strategy` default was caught late).

Loop Steps 2–4 until the human gives an explicit go-ahead. Do not proceed
to `confirm` without it — this is the spec's Section 7.1/7.2 gate and it
is not optional.

## Step 5 — Confirm

```bash
python -m scripts.cli confirm --draft-plan <analysis-dir>/plan.json --output <confirmed-plan>
```

Exit code `4` (already confirmed, usage error): stop and report.

## Step 6 — Convert

```bash
python -m scripts.cli convert --source <docx> --plan <confirmed-plan> --output <run-dir>
```

Check the reported validation status:

- **PASS**: continue to Step 7.
- **WARN**: only proceed once every warning is dispositioned (see
  `convert-document/SKILL.md`'s Staging and Canonical Validation section)
  — do not treat an incomplete disposition set as good enough to continue.
- **FAIL**: stop. Report the raw validation output. Do not attempt to
  patch around it or re-run render anyway.

## Step 7 — Render

```bash
python -m scripts.cli render --canonical <run-dir>/canonical-content --renderer multipage-markdown --output <run-dir>/render
```

- **PASS**: continue to Step 8.
- **FAIL**: stop and report the raw validation output; rendered output is
  retained in staging for diagnosis, not promoted.

## Step 8 — Summarize

Report the final promoted location (`<run-dir>/canonical-content/` and
`<run-dir>/render/rendered-output/`), the validation status at each stage,
topic/page counts, and any decisions the human made along the way (media
dispositions, strategy choice) so there's a record of what was approved.

## Prohibited Shortcuts

- Must not run `confirm` before the human has explicitly approved the
  draft plan in Step 4 — presenting a summary is not the same as approval.
- Must not invent a classification/disposition for a media record instead
  of asking the human, and must not skip Reading the actual image file.
- Must not proceed past a FAIL or an undispositioned WARN at Step 6 or 7.
- Must not skip straight from Step 1 to Step 5 — every draft plan goes
  through Steps 2–4 even if it looks unremarkable.

## Relationship to the Individual Skills

This skill does not supersede `analyze-document`, `convert-document`, or
`render-content` — a human may still invoke any of those directly for a
single step, or to resume a pipeline this skill was interrupted partway
through (e.g. after Step 4's approval, jump straight to `confirm`/`convert`
per `convert-document/SKILL.md`).
