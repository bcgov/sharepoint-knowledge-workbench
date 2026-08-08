---
name: analyze-webpart-code
plugin: sharepoint-discovery
description: Groups classic SharePoint web parts by functional behaviour -- inline script, external helper scripts, text-only, empty, or unretrievable -- so near-duplicate instances collapse into a reviewable set. Classification knowledge is caller-supplied via a KnowledgeBase; read-only.
allowed-tools: Bash, Read
examples:
  - "python -c \"from webpart_code_analysis import run; print(run(extract_path='webparts.json', output_dir='out/').status)\""
---

# Analyze Web Part Code

## Trigger and Purpose

Classic SharePoint sites accumulate hundreds of web-part instances that are
mostly copies of a handful of real behaviours. Use this skill to collapse an
exported web-part content dump into distinct functional groups, so a
modernization review covers each *behaviour* once instead of each instance.

Produces three artifacts: a groups JSON, a Markdown analysis report, and a
per-instance review CSV.

## Categories

| Category | Meaning |
|---|---|
| `InlineLogic` | Contains inline script implementing real behaviour |
| `ExternalHelpersOnly` | References external helper scripts, no inline logic |
| `TextOnly` | Static content, no code |
| `Empty` | No meaningful content |
| `ScriptEditorMissing` | **Content could not be retrieved** -- not a classification, a gap |

`ScriptEditorMissing` is deliberately distinct. An unretrievable web part is an
unknown, not an empty one, and a run containing any of them reports `PARTIAL`
with the count -- never `OBSERVED`.

## Classification knowledge is caller-supplied

`KnowledgeBase` and `InlineLogicRule` let you supply the helper-script table
and behavioural heuristics. The source implementation hardcoded roughly thirty
helper-script names and named business-rule heuristics specific to one
organisation; **all of that site-specific knowledge is removed here.**
`DEFAULT_KNOWLEDGE_BASE` is deliberately generic.

## Read-only guarantee

No tenant contact, no writes outside the output directory you name. A missing
input is `UNAVAILABLE` and creates no output directory.

## Usage

```bash
python -c "
from webpart_code_analysis import run
outcome = run(extract_path='webpart-content.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Scripts

- `scripts/webpart_code_analysis.py` -- `run`, `analyse`, `classify`, `recommend`, `generate_report`, `generate_instance_csv`, `KnowledgeBase`, `InlineLogicRule`
- `scripts/discovery_inputs.py` -- shared status vocabulary and input loading

## Stage 2 — AI-reasoning pass over this skill's output

This skill performs Stage 1 only: deterministic grouping. Assigning a
modernization disposition per group (business behaviour, MVP decision,
SPFx candidacy) and collapsing groups that share one mechanism into a
single shared decision is Stage 2, agent-assisted by design — route to
`sharepoint-webpart-modernization-analysis-agent` (in
`sharepoint-agents-and-skills`) once this skill's grouped output exists.

## Provenance

Adapted from `sp-discovering-web-parts` in the originating SharePoint migration
repository. Note that 6 of that skill's 19 symlinks pointed at project analysis
*data* outside the plugin boundary; that data was **not** extracted, but the
Stage-2 reasoning *framework* those analysis documents applied (per-group
disposition fields, category-level defaults, and the pattern-collapse
discipline) was later generalized into
`sharepoint-webpart-modernization-analysis-agent` after a Phase 9 audit
follow-up confirmed it was a distinct, valuable, reusable pattern separate
from the project-specific data it had originally been applied to. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
