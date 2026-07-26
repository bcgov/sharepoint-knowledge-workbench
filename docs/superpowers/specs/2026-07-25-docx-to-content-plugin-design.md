# docx-to-content Plugin — Phase 1 Design Spec

**Date:** 2026-07-25
**Status:** Approved for planning
**Location:** self-contained in `manual-conversion-poc/plugins/docx-to-content/` — NOT the sibling
`agent-plugins-skills` monorepo. That was the original plan; it is explicitly reversed for
Phase 1, per direct instruction. Nothing here is published or shared outside this repo yet.

## The Hypothesis Being Tested

Organizations have accumulated hundreds or thousands of Word-authored documents over years —
manuals, procedures, policies. That content+formatting-together authoring model (`plan.md`'s
"Current State") produces documents that go stale, accumulate broken links, use outdated formats,
are token-inefficient for AI to process, and were designed in an era before AI/Copilot agents
existed as consumers of that content at all (`plan-part2.md`'s Copilot Studio / M365 agent
opportunity is the concrete payoff case that only becomes possible once content is separated and
AI-consumable).

The content+formatting-together model is also the *comfortable, familiar* way people have
authored documents for decades — separating content from formatting is genuine friction and
change management, not a free win (`plan.md`, "Challenges" section).

**This POC tests whether that disruption is worth it** — using the CEIS Manual as the concrete
evidence-gathering vehicle. Phase 1's job is to produce **real evidence that the separation is
extensible**, not a token conversion: if the resulting content+metadata can't actually support
multiple different future renderers (SharePoint chunked pages, Copilot Studio grounding, quiz
generation, Word/PDF) without rework, the hypothesis isn't being tested, it's being asserted.

## Scope

**Phase 1 (this spec):** prove the content/format separation exists and is genuinely extensible —
not just asserted. Three skills: analyze a source `.docx`, convert it into clean content +
structured metadata, and render that content through **one concrete renderer** as proof the
architecture is genuinely pluggable (a contract alone is easy to design but easy to get wrong in
ways that only surface when something real implements it).

`plan.md` itself already names the long-term renderer breadth this is working toward: HTML, PDF,
Word, audio scripts, training material, chat-based assistance ("Multiple Output Formats"
section) — Phase 1 doesn't build all of these, it builds the one renderer below plus an interface
shape the rest can plug into later.

**Explicitly deferred to later phases** (named, not forgotten):
- Every renderer beyond the one built in Phase 1 (Word/PDF via `--reference-doc`, PowerPoint,
  audio scripts, Copilot Studio-ready/retrieval-optimized chunking, quiz generation)
- Any preview or editing tool — SharePoint Online already provides a native side-by-side
  raw/rendered markdown editor at the eventual destination; building one here would be
  redundant. (Confirmed via a live screenshot of SharePoint's markdown editing UI.)
- A destination-interview skill (ask the user where content should go, in what format)
- Any actual publish/upload step into SharePoint — the `manual-conversion-poc` folder currently
  visible in SharePoint/OneDrive is a manually-created separate copy, not synced to this repo;
  getting content there is a real, distinct future step.

**What was already built and is being relocated, not redone:** the cleanup pipeline from the
paused `agent-plugins-skills` work — `pandoc_fixes/{attrs,images,toc,tables,footnotes}.py`,
`emf_convert.py`, `pandoc_validate.py`, `docx_to_md.py`, `md_to_docx.py`, and their tests — all
real, working, tested code addressing four documented pandoc gaps (raw Word TOC dump, images
glued to headings/list items, leftover pandoc attribute syntax, legacy `.emf`/`.wmf` images). This
becomes the guts of the `convert-document` skill below; it is not being rewritten.

## Architecture

Self-contained plugin, scaffolded via `create-plugin` using the same structural conventions as
`agent-plugins-skills` (`.claude-plugin/plugin.json`, `plugin.yaml`, `skills/<skill>/SKILL.md`,
hub-and-spoke `scripts/` shared via file-level symlinks per `symlink-cross-platform.md`), but
living only in this repo.

```
plugins/docx-to-content/
  .claude-plugin/plugin.json
  plugin.yaml
  scripts/                          # canonical hub — real files live here
    pandoc_fixes/
      attrs.py / images.py / toc.py / tables.py / footnotes.py
    emf_convert.py
    pandoc_validate.py
    chunk_metadata.py                # NEW — builds the per-chunk metadata sidecar
    analyze_structure.py             # NEW — structural analysis used by analyze-document
    renderers/
      base.py                        # NEW — the render contract every renderer implements
      multipage_markdown.py          # NEW — the one concrete Phase 1 renderer
  skills/
    analyze-document/
      SKILL.md
      scripts/ → symlinks to the canonical files above
      tests/
    convert-document/
      SKILL.md
      scripts/ → symlinks to the canonical files above
      tests/
    render-content/
      SKILL.md
      scripts/ → symlinks to renderers/base.py, renderers/multipage_markdown.py
      tests/
  requirements.in / requirements.txt   # pytest only; runtime stays stdlib-only
  references/
    pandoc-docx-setup.md               # fresh-machine setup (Python/pandoc/soffice), relocated
    known-pandoc-gaps.md               # relocated
```

### Skill 1: `analyze-document`

Runs pandoc once against the source `.docx` to get raw structure data — heading count/depth, TOC
entry count (Word's raw TOC field, before any cleanup), document length, image count. Presents
these findings plus a **recommended** chunking strategy (single-file vs. multi-page folder) with
explicit reasoning (e.g. "159 headings across 6 levels, ~4500 lines — recommend chunking at
level-2 headings, ~40 resulting files"). Asks the user to confirm or override. Produces a
conversion plan — a small JSON document: `{ "strategy": "chunked"|"single", "chunk_boundaries":
[...], "source_toc_count": N }`. **No content is written at this stage.**

This directly implements the "algorithmic analysis → present findings/recommendation → ask →
formulate a plan" sequence as this skill's internal flow — not a blind auto-decision, not a
no-heuristics interview either.

### Skill 2: `convert-document`

Takes the confirmed plan and executes it, reusing the pipeline order already validated in the
paused work (corrected from the original design's stated order): **attrs → images → toc → tables
→ footnotes**, then legacy image conversion, then `pandoc_validate`'s hard structural checks
(image links resolve, no attribute artifacts, no images embedded in headings, heading count
matches source TOC exactly).

New for this plugin: after cleanup, if the plan's strategy is `"chunked"`, split the cleaned
content at the plan's chunk boundaries into separate files; if `"single"`, keep one file. Either
way, **every chunk gets a metadata sidecar** — a JSON record with:
- `chunk_id` — stable identifier
- `source_heading_path` — e.g. `["FILE ACCESS", "How to Seal a File"]`
- `topic` — the chunk's own top-level heading text (a keyword/topic tag; not AI-generated
  categorization in Phase 1 — that's a deliberately simple, real, inspectable value now, not a
  placeholder for future work)

This metadata is what makes "many future renderers" plausible rather than aspirational — a
SharePoint page renderer, a Copilot Studio grounding exporter, or a quiz generator can all key off
`source_heading_path`/`chunk_id` without re-deriving structure from prose text.

### Skill 3: `render-content`

Defines the render contract (`renderers/base.py`) every future renderer implements: given the
content chunks + their metadata sidecars, produce one output artifact. The contract's shape is
proven, not just asserted, by one concrete implementation: `renderers/multipage_markdown.py` —
takes the chunked content+metadata from `convert-document` and assembles it into a navigable
folder of markdown pages with a generated index/TOC page linking each chunk by its
`source_heading_path`. This is deliberately the *destination-shaped* renderer (matches the
SharePoint folder-of-pages model already validated via the SharePoint markdown editor
screenshot) rather than a format conversion — proving the render layer works end-to-end on the
simplest real case before any format-conversion renderer (Word, PowerPoint, audio) is attempted.

Every future renderer (Word via `md_to_docx.py`, PDF, PowerPoint, audio script generation, a
Copilot Studio-ready exporter) implements the same `base.py` contract — this is what Phase 1 is
actually proving, using `multipage_markdown.py` as the one real, working example.

`multipage_markdown.py` handles both of `convert-document`'s output shapes uniformly: given
`"chunked"` output, it assembles the folder of pages with a generated multi-entry index; given
`"single"` output, it still runs the same code path with exactly one input chunk, producing a
folder containing that one page plus a trivial one-entry index — not a special case, just the
same logic operating on a list of length 1.

### Data flow

```
source.docx
    |
    v  pandoc (raw markdown + extracted media)
    |
analyze-document: structure stats -> present + recommend -> user confirms -> conversion plan (JSON)
    |
    v
convert-document: attrs -> images -> toc -> tables -> footnotes -> legacy image conversion
    |                                                                    |
    v (if plan.strategy == "chunked")                                   v (if "single")
folder of chunk_NNN.md + chunk_NNN.meta.json                    one file.md + one file.meta.json
    |
    v
pandoc_validate: hard-fail on any structural defect (does not depend on chunking strategy)
    |
    v
render-content (multipage_markdown.py): assemble chunks + metadata into a navigable folder
    of pages + generated index, per the base.py render contract
```

### Testing

TDD per `.agent/rules/test-driven-development.md` — failing test before implementation for every
new function (`analyze_structure.py`, `chunk_metadata.py`, the chunk-splitting logic in
`convert-document`, `renderers/base.py`'s contract, `renderers/multipage_markdown.py`). The
relocated `pandoc_fixes`/`emf_convert`/`pandoc_validate` modules keep their existing test suites
unchanged (they're proven working, not being modified). The CEIS Manual remains the end-to-end
regression fixture, exercised through all three skills in sequence.

## Rollout

Built directly in this repo — no PR/merge/reinstall cycle (that protocol was for the
`agent-plugins-skills`-hosted version, which is no longer where this lives). Once both skills pass
their tests and the CEIS Manual regression run produces zero validation failures, this replaces
`output/ceis-manual/CEIS-Manual.md` (the current single-file, unfixed conversion) with the new
plugin's output.
# docx-to-content Plugin — Phase 1 Updated Design Spec

**Date:** 2026-07-25  
**Status:** Approved for planning — updated to address architecture gaps  
**Location:** `manual-conversion-poc/plugins/docx-to-content/`  
**Important boundary:** Phase 1 is self-contained in `manual-conversion-poc`. It is **not** hosted in the sibling `agent-plugins-skills` monorepo for this phase. Nothing here is published or shared outside this repo yet.

---

## Agent Handoff Summary

Build a self-contained `docx-to-content` plugin that proves the Phase 1 hypothesis:

> A Word-authored manual can be converted into cleaned, structured, metadata-backed content that can be rendered through at least one concrete renderer without rework.

This is **not** merely a `docx -> markdown` conversion project. The objective is to prove the first usable slice of a content-centric knowledge management architecture:

```text
Content + Template + Renderer = Published Output
```

Phase 1 must produce inspectable evidence that:

- raw document extraction is transitory, not the final artifact
- canonical content consists of cleaned chunks plus metadata sidecars
- renderers consume a stable content + metadata contract
- at least one real renderer works end-to-end
- the CEIS Manual can be used as the regression fixture

---

## The Hypothesis Being Tested

Organizations have accumulated hundreds or thousands of Word-authored documents over years, including:

- manuals
- procedures
- policies
- training materials

The current document-centric model stores content and formatting together. That model creates recurring problems:

- documents go stale
- links break over time
- formats drift
- templates are difficult to update consistently
- content is difficult to reuse
- heavy Word/PDF files are inefficient for AI retrieval and grounding
- the content was authored before Copilot-style agents were realistic consumers of the information

The familiar Word/PDF authoring model is comfortable for users. Separating content from formatting introduces real friction and change management. This POC tests whether that disruption is worth it.

The CEIS Manual is the concrete evidence-gathering vehicle.

Phase 1 must therefore prove something more meaningful than file conversion. It must show that the extracted content can become structured, inspectable, reusable content that can support future outputs such as:

- SharePoint markdown pages
- Copilot Studio / M365 agent grounding
- quiz generation
- Word/PDF rendering
- training material generation
- audio/script outputs

If the resulting content and metadata cannot support future renderers without rework, the hypothesis is not being tested. It is only being asserted.

---

## Core Architectural Rule

Raw pandoc markdown is **not** the canonical content artifact.

Raw extraction is a temporary intermediate representation used for analysis and cleanup. The value artifact is:

```text
cleaned content chunks + metadata sidecars + validation records + rendered output
```

This distinction is non-negotiable.

---

## Key Terms

### Raw Extraction

Temporary markdown produced from the source `.docx` by pandoc.

Used for:

- structural analysis
- cleanup input
- diagnostic comparison

Not used as:

- final content
- grounding source
- renderer contract
- publication artifact

### Canonical Content

The post-cleanup, structured content output of `convert-document`.

Canonical content consists of:

- one or more cleaned markdown chunk files
- exactly one metadata sidecar per chunk
- a manifest describing the conversion run
- validation output

### Metadata Sidecar

A JSON file paired with a content chunk.

Minimum Phase 1 fields:

```json
{
  "chunk_id": "chunk_007_file-access_how-to-seal-a-file",
  "source_heading_path": ["FILE ACCESS", "How to Seal a File"],
  "topic": "How to Seal a File",
  "source_order": 7,
  "content_type": "manual",
  "template_id": "manual-v1"
}
```

### Renderer Contract

The stable interface that future renderers must consume.

A renderer receives:

- a manifest
- a list of content chunks
- metadata sidecars
- media assets

A renderer produces:

- one output artifact or output folder
- renderer validation output

Phase 1 proves this contract with one concrete renderer: `multipage_markdown.py`.

---

## Scope

### Phase 1 Scope

Phase 1 builds three skills:

1. `analyze-document`
2. `convert-document`
3. `render-content`

Together, they must prove that content/format separation exists and is extensible.

Phase 1 includes:

- temporary raw extraction for analysis
- structural analysis of a `.docx`
- recommendation of chunking strategy
- generation of a conversion plan JSON file
- cleanup of pandoc markdown defects
- legacy image conversion
- chunk generation
- metadata sidecar generation
- validation of canonical content
- rendering through one concrete renderer
- validation of rendered output
- CEIS Manual end-to-end regression run

### Phase 1 Explicitly Defers

The following are named and intentionally deferred:

- Word/PDF renderer via `--reference-doc`
- PowerPoint renderer
- audio/script renderer
- Copilot Studio-ready exporter
- retrieval-optimized chunk exporter
- quiz generation
- SharePoint upload/publishing
- destination-interview skill
- custom preview/editor tool
- generalized template authoring UI
- full semantic remapping into every future template type

SharePoint Online already provides a native side-by-side raw/rendered markdown editing experience at the eventual destination, so building a preview/editor in this repo would be redundant.

---

## Phase 1 Non-Negotiables

- Raw pandoc markdown is transitory and must not be treated as the final content artifact.
- Canonical content must consist of cleaned content chunks plus metadata sidecars.
- Every content chunk must have exactly one metadata sidecar.
- Every metadata sidecar must point to exactly one content chunk.
- Every renderer must consume the same content + metadata contract.
- The Phase 1 renderer must produce a navigable multi-page markdown output.
- The renderer output must be validated, not merely generated.
- Existing working cleanup modules must not be redesigned unless tests prove a defect.
- Phase 1 must leave inspectable artifacts at each stage.
- The CEIS Manual must remain the end-to-end regression fixture.

---

## Template Mapping Decision for Phase 1

The broader vision includes reusable templates for policies, procedures, manuals, and training materials. The workflow diagram includes a template library and a map-into-template step.

For Phase 1, template mapping is intentionally limited.

Phase 1 must record template awareness, but it does **not** need to build a generalized template engine.

### Phase 1 Template Rule

- Treat the CEIS Manual as `content_type: manual`.
- Use a lightweight `template_id: manual-v1` value in metadata and manifest files.
- Preserve source heading structure as the initial manual structure.
- Do not attempt AI-generated categorization or semantic restructuring.
- Do not invent a generalized policy/procedure/training schema yet.

### Why This Is Acceptable

Phase 1 is proving the content + metadata + renderer contract.

It is enough for Phase 1 to show that content chunks carry template-aware metadata that future renderers and future mapping logic can use. Full template normalization belongs in a later phase after the basic extraction/chunk/render contract is proven.

### Conversion Plan Fields

The conversion plan should include at least:

```json
{
  "source_docx": "sourcedocuments/CEIS MANUAL - working version.docx",
  "strategy": "chunked",
  "chunk_level": 2,
  "chunk_boundaries": [],
  "source_toc_count": 0,
  "content_type": "manual",
  "template_id": "manual-v1",
  "section_mapping_mode": "preserve_source_heading_structure"
}
```

---

## Existing Work to Relocate, Not Redesign

The cleanup pipeline already developed in the paused work should be relocated into this self-contained plugin, not rewritten.

Existing modules include:

- `pandoc_fixes/attrs.py`
- `pandoc_fixes/images.py`
- `pandoc_fixes/toc.py`
- `pandoc_fixes/tables.py`
- `pandoc_fixes/footnotes.py`
- `emf_convert.py`
- `pandoc_validate.py`
- `docx_to_md.py`
- `md_to_docx.py`
- existing tests for the above

These address already-diagnosed pandoc gaps:

- raw Word TOC dump
- images glued to headings/list items
- leftover pandoc attribute syntax
- legacy `.emf` / `.wmf` images
- footnote/table cleanup issues

### Relocation Rules

The agent must:

- preserve existing test coverage
- preserve existing behavior
- adapt only paths/imports/module layout as needed
- avoid redesigning cleanup logic without a failing test
- avoid silent rewrites of proven modules
- keep relocated code separately reviewable from new Phase 1 code

---

## Architecture

Self-contained plugin scaffolded with the same conventions as `agent-plugins-skills`, but living only in this repo.

```text
plugins/docx-to-content/
  .claude-plugin/
    plugin.json
  plugin.yaml
  scripts/
    pandoc_fixes/
      attrs.py
      images.py
      toc.py
      tables.py
      footnotes.py
    emf_convert.py
    pandoc_validate.py
    docx_to_md.py
    md_to_docx.py
    analyze_structure.py
    chunk_metadata.py
    manifest.py
    renderers/
      base.py
      multipage_markdown.py
  skills/
    analyze-document/
      SKILL.md
      scripts/ -> symlinks to canonical scripts where appropriate
      tests/
    convert-document/
      SKILL.md
      scripts/ -> symlinks to canonical scripts where appropriate
      tests/
    render-content/
      SKILL.md
      scripts/ -> symlinks to canonical render scripts where appropriate
      tests/
  tests/
    fixtures/
    integration/
  references/
    pandoc-docx-setup.md
    known-pandoc-gaps.md
  requirements.in
  requirements.txt
```

### Dependency Position

- Runtime should remain as close to stdlib-only as practical.
- `pandoc` and `soffice` are external system dependencies.
- `pytest` is acceptable for tests.
- Do not introduce new Python packages without an explicit reason and dependency update.

---

## Skill 1: `analyze-document`

### Purpose

Analyze a source `.docx` and produce a recommended conversion plan.

### Important Clarification

`analyze-document` may run pandoc to produce temporary raw markdown for analysis. That output is diagnostic and transitory. It is not canonical content.

### Inputs

- source `.docx`
- optional target content type, defaulting to `manual` for CEIS
- optional requested chunking preference

### Analysis Outputs

The skill should collect:

- heading count
- heading depth distribution
- estimated document length
- image count
- raw TOC entry count, if detectable
- evidence of known pandoc issues
- recommended chunking strategy
- recommended chunk level
- expected approximate number of chunks
- warnings or assumptions

### Recommendation Logic

The skill should recommend either:

- `single` — one canonical content file
- `chunked` — multiple canonical content chunks

The recommendation must include reasoning.

Example:

```text
159 headings across 6 levels and approximately 4,500 lines suggests the document is too large for a single maintainable markdown page. Recommend chunking at level 2 headings.
```

### Human Decision Point

This skill presents findings and a recommended plan. The user or supervising agent may confirm or override.

### Plan Output

Produces a JSON conversion plan, for example:

```json
{
  "source_docx": "sourcedocuments/CEIS MANUAL - working version.docx",
  "strategy": "chunked",
  "chunk_level": 2,
  "chunk_boundaries": [
    {
      "source_order": 1,
      "heading_path": ["INTRODUCTION"],
      "start_line": 1
    }
  ],
  "source_toc_count": 0,
  "content_type": "manual",
  "template_id": "manual-v1",
  "section_mapping_mode": "preserve_source_heading_structure",
  "analysis_warnings": []
}
```

### No Content Written

`analyze-document` must not write canonical content chunks. It may write temporary analysis output and an analysis report.

---

## Skill 2: `convert-document`

### Purpose

Execute the confirmed conversion plan and produce canonical content.

### Inputs

- source `.docx`
- confirmed conversion plan JSON
- output directory

### Pipeline

Use the validated cleanup pipeline order:

```text
pandoc extraction
  -> attrs cleanup
  -> images cleanup
  -> toc cleanup
  -> tables cleanup
  -> footnotes cleanup
  -> legacy image conversion
  -> canonical chunk generation
  -> metadata sidecar generation
  -> canonical content validation
```

### Chunking

If the plan strategy is `chunked`:

- split cleaned content at confirmed chunk boundaries
- produce one `.md` file per chunk
- produce one `.meta.json` file per chunk

If the plan strategy is `single`:

- produce one `.md` file
- produce one `.meta.json` file
- still use the same manifest and renderer contract

No special-case renderer path should be required for single-file output. Single-file output is just a list of one chunk.

### Stable `chunk_id` Rule

`chunk_id` must be deterministic for a given source structure.

Recommended format:

```text
chunk_<source_order_padded>_<normalized_heading_slug>
```

Example:

```text
chunk_007_file-access_how-to-seal-a-file
```

Rules:

- `source_order` is the ordered chunk position from the conversion plan.
- heading slug is derived from the chunk's top heading path.
- normalize to lowercase.
- replace non-alphanumeric runs with `-`.
- trim leading/trailing dashes.
- append a collision suffix if needed.

This makes IDs stable enough for inspection and future renderer use without requiring a database.

### Metadata Sidecar Fields

Minimum required fields:

```json
{
  "chunk_id": "chunk_007_file-access_how-to-seal-a-file",
  "source_order": 7,
  "source_heading_path": ["FILE ACCESS", "How to Seal a File"],
  "topic": "How to Seal a File",
  "content_type": "manual",
  "template_id": "manual-v1",
  "source_docx": "sourcedocuments/CEIS MANUAL - working version.docx",
  "content_file": "chunk_007_file-access_how-to-seal-a-file.md"
}
```

### Manifest

The conversion should also produce a manifest.

Example:

```json
{
  "source_docx": "sourcedocuments/CEIS MANUAL - working version.docx",
  "content_type": "manual",
  "template_id": "manual-v1",
  "strategy": "chunked",
  "chunk_count": 0,
  "chunks": [],
  "media_dir": "media",
  "validation_report": "validation.json"
}
```

---

## Canonical Content Validation

Validation must run after canonical content generation.

Minimum checks:

- every content chunk exists
- every content chunk has exactly one metadata sidecar
- every metadata sidecar points to an existing content chunk
- every `chunk_id` is unique
- chunk ordering is deterministic
- image links resolve
- no unsupported legacy image references remain
- no pandoc attribute artifacts remain
- no images are embedded inside heading text
- no obvious raw Word TOC dump remains
- manifest references valid files

### TOC Reconciliation Rule

Do **not** blindly hard-fail because extracted heading count differs from the source Word TOC count.

Word TOCs can be stale or configured to include/exclude specific levels.

Instead:

- compare extracted heading structure against source TOC evidence
- hard-fail only on unresolved structural defects
- warn on explainable TOC mismatches
- record all mismatches in the validation report

Suggested validation categories:

```text
PASS       validation succeeded
WARN       review recommended, but artifact is usable
FAIL       structural defect blocks use
```

---

## Skill 3: `render-content`

### Purpose

Prove the renderer contract using one concrete renderer.

### Inputs

- canonical content folder
- manifest
- renderer name, defaulting to `multipage_markdown`
- output folder

### Renderer Contract

All renderers must consume:

- manifest
- content chunk list
- metadata sidecars
- media assets

All renderers must produce:

- output artifact or output folder
- renderer validation report

### Phase 1 Renderer

`multipage_markdown.py` is the only Phase 1 renderer.

It produces:

- a navigable folder of markdown pages
- generated `index.md`
- links from the index to each chunk page
- output structure compatible with future SharePoint markdown-page use

This renderer is deliberately destination-shaped rather than format-conversion-shaped. It proves the contract with the simplest real output before attempting Word, PDF, PowerPoint, audio, or Copilot-specific exporters.

### Single vs Chunked Output

The renderer must handle both output shapes uniformly:

- chunked input = many pages plus index
- single input = one page plus one-entry index

The renderer should not implement a separate special-case path for single-file output.

---

## Renderer Output Validation

After rendering, validate the output.

Minimum checks:

- output folder exists
- `index.md` exists
- every chunk listed in the manifest has a rendered page
- every index link resolves
- every rendered page has a corresponding metadata source
- no orphan rendered pages exist
- no orphan metadata exists
- media references still resolve from rendered pages
- renderer validation report is written

Renderer validation is required because Phase 1 is not only proving conversion. It is proving the render contract.

---

## Data Flow

```text
source.docx
    |
    v
analyze-document
    - temporary pandoc extraction for analysis only
    - structural stats
    - known issue detection
    - recommended chunking strategy
    - recommended lightweight template identity
    - conversion plan JSON
    |
    v
human/supervising-agent confirms or overrides plan
    |
    v
convert-document
    - pandoc extraction
    - attrs cleanup
    - images cleanup
    - toc cleanup
    - tables cleanup
    - footnotes cleanup
    - legacy image conversion
    - chunk generation
    - metadata sidecar generation
    - manifest generation
    - canonical content validation
    |
    v
canonical content folder
    - chunk_NNN_slug.md
    - chunk_NNN_slug.meta.json
    - manifest.json
    - validation.json
    - media/
    |
    v
render-content
    - consume manifest + chunks + metadata + media
    - render through multipage_markdown.py
    - validate rendered output
    |
    v
rendered output folder
    - index.md
    - pages/
    - renderer-validation.json
```

---

## Required Inspectable Artifacts

Every end-to-end run must leave the following artifacts:

```text
analysis-report.json
conversion-plan.json
canonical-content/
  manifest.json
  validation.json
  chunks/
    chunk_001_*.md
    chunk_001_*.meta.json
  media/
rendered-output/
  index.md
  pages/
  renderer-validation.json
```

The agent must not summarize success without these artifacts existing.

---

## Testing Strategy

TDD applies to all new code.

Add failing tests before implementation for:

- `analyze_structure.py`
- `chunk_metadata.py`
- stable `chunk_id` generation
- conversion plan generation
- chunk splitting
- manifest generation
- metadata sidecar generation
- canonical content validation
- `renderers/base.py` contract
- `renderers/multipage_markdown.py`
- renderer output validation

Existing relocated cleanup modules keep their test suites unchanged unless a failing test proves a defect.

### Integration Fixture

Use the CEIS Manual as the end-to-end regression fixture.

The integration test should exercise:

```text
analyze-document -> convert-document -> render-content
```

Acceptance requires:

- all unit tests pass
- all relocated cleanup tests pass
- end-to-end CEIS run completes
- canonical content validation is PASS or documented WARN only
- renderer validation is PASS
- output artifacts are inspectable

---

## Implementation Discipline

The agent must:

- work from this spec as the implementation contract
- avoid scope expansion
- avoid adding deferred renderers
- avoid SharePoint publishing
- avoid custom preview/editor work
- preserve already-working cleanup code
- write tests before new implementation
- keep commits logically separable if using git
- update plugin metadata files if required by the scaffold
- update documentation when behavior changes

The agent must not:

- treat raw pandoc markdown as canonical content
- silently redesign relocated cleanup modules
- skip validation because files were generated
- report completion without artifact evidence
- implement future phases during Phase 1

---

## Rollout

Build directly in `manual-conversion-poc/plugins/docx-to-content/`.

No PR/merge/reinstall cycle is required for Phase 1 because this plugin is no longer being built first in the sibling `agent-plugins-skills` monorepo.

Rollout is complete only when all three skills pass their tests and the CEIS Manual regression run produces:

- analysis report
- confirmed conversion plan
- canonical content chunks
- metadata sidecars
- manifest
- canonical validation report
- rendered multi-page markdown output
- renderer validation report

After successful validation, replace the current unfixed single-file conversion:

```text
output/ceis-manual/CEIS-Manual.md
```

with the new plugin-generated output structure.

---

## Phase 1 Acceptance Criteria

Phase 1 is accepted when the following are true:

- `analyze-document` produces a clear analysis report and conversion plan.
- `convert-document` produces canonical content, metadata sidecars, manifest, and validation report.
- `render-content` produces a navigable markdown folder with generated index.
- Every chunk has exactly one metadata sidecar.
- Every metadata sidecar links to an existing chunk.
- Stable `chunk_id` values are deterministic.
- Renderer output links resolve.
- Image/media references resolve.
- Known pandoc artifacts are removed or reported.
- TOC/heading discrepancies are reconciled as PASS/WARN/FAIL.
- CEIS Manual end-to-end regression succeeds.
- All three skills have tests.
- Existing cleanup tests still pass.
- Deferred future work remains deferred.

---

## Future Phase Candidates

Do not implement these in Phase 1, but keep the architecture compatible with them:

- generalized template library
- template creator/editor skill
- full map-into-template skill
- destination-interview skill
- SharePoint publishing/upload skill
- Word/PDF renderer using `--reference-doc`
- PowerPoint renderer
- audio/script renderer
- Copilot Studio-ready exporter
- retrieval-optimized chunk exporter
- quiz/knowledge-check generator
- content governance workflow
- approval workflow integration

---

## Final Instruction to Agent

Implement Phase 1 as a disciplined proof of the content separation architecture.

Do not optimize for a flashy demo. Optimize for evidence:

- clear artifacts
- deterministic structure
- validation reports
- preserved tested cleanup logic
- one real renderer proving the contract

The desired outcome is not simply markdown.

The desired outcome is proof that the CEIS Manual can move from a Word-authored document into reusable, metadata-backed content that future renderers and Copilot-style knowledge experiences can consume.
