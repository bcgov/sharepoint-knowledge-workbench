# docx-to-content Plugin — Phase 1 Design Specification v3

**Date:** 2026-07-25  
**Status:** Ready for implementation planning and agent execution  
**Supersedes:** Earlier Phase 1 design drafts  
**Repository boundary:** `manual-conversion-poc/plugins/docx-to-content/`  
**Pilot:** CEIS Manual

## v3.1 Deviation Notice (2026-07-25, Task 0 finding)

Task 0 reconnaissance (see `docs/implementation-baseline.md`) established that the pandoc cleanup
pipeline this spec describes below as "already-tested" and "relocated, not redesigned"
(`pandoc_fixes/{attrs,images,toc,tables,footnotes}.py`, `emf_convert.py`, `pandoc_validate.py`,
`docx_to_md.py`, `md_to_docx.py`) **does not exist anywhere** — not in this repo, not in the
sibling `agent-plugins-skills` monorepo (checked across the working tree, every local and remote
branch, all git history, and all stashes). It was never built; the "paused work" framing was
carried forward from an earlier planning conversation that reached only a design spec (itself
also not found) and never reached implementation.

**Explicit user decision:** build this pipeline from scratch under TDD, using the pandoc defect
categories named throughout this document (raw Word TOC dump, images glued to headings/list
items, leftover pandoc attribute syntax, legacy `.emf`/`.wmf` images) as the design target, not as
a diff against existing code.

Every reference below to "relocation," "already-tested," "already-built," or "preserved unless a
new failing regression test demonstrates a defect" for the cleanup pipeline modules must be read
as **build new, under TDD, against these named defect categories** instead. This does not change
any other part of the v3 architecture (contracts, chunk identity, plan confirmation, validation
policy, renderer protocol, atomic promotion) — only the provenance and construction method of the
cleanup pipeline itself.

## 1. Executive Decision

Build a self-contained `docx-to-content` plugin that proves a Word-authored manual can become validated, reusable canonical content and can be consumed through a renderer contract without re-parsing the source document.

This is not a DOCX-to-Markdown utility. It is the first evidence-producing slice of the broader model:

```text
Content + Template + Renderer = Published Output
```

Phase 1 succeeds only if it produces repeatable evidence that:

- raw pandoc output is transitory;
- canonical content has an explicit, versioned contract;
- extraction, cleanup, chunking, metadata, media, validation, and rendering are traceable;
- one renderer consumes only canonical artifacts, not the DOCX or transitory extraction;
- changing the renderer does not require re-extracting or reinterpreting the DOCX;
- outputs are usable by a human reviewer, not merely present on disk.

## 2. Broader Vision

Organizations maintain manuals, procedures, policies, and training materials as formatted Word/PDF documents. Content and presentation are coupled, making consistency, reuse, link maintenance, bulk template changes, and AI consumption difficult.

The target operating model separates:

1. **Canonical content** — approved business knowledge and structure.
2. **Templates** — reusable presentation and content-shape expectations.
3. **Renderers** — destination-specific transformations.
4. **Consumers** — SharePoint pages, Word/PDF, training packages, Copilot grounding, quizzes, or other later outputs.

Phase 1 does not implement all four layers. It proves the canonical-content boundary and one renderer. The CEIS Manual is evidence, not the architecture.

## 3. Hypothesis and Falsification Criteria

### Hypothesis

A Word-authored manual can be transformed into versioned canonical content consisting of cleaned Markdown, structured metadata, retained media, lineage, and validation results; a renderer can consume that contract to create a navigable output without depending on the source DOCX or transitory pandoc Markdown.

### The hypothesis is falsified if any of these occur

- The renderer must inspect the DOCX or raw extraction to work.
- Chunking loses content, duplicates content, or breaks heading hierarchy.
- Media links work only in the canonical folder but fail after rendering.
- Chunk identifiers change solely because unrelated content is inserted earlier in the document.
- A stale or mismatched conversion plan can be applied without detection.
- Validation can return success with orphan files, missing required fields, stale outputs, broken local links, or unresolved media.
- The result cannot be meaningfully reviewed against the source.
- The implementation works only because of CEIS-specific headings, paths, or content.

## 4. Scope

### Included in Phase 1

- Three skills:
  - `analyze-document`
  - `convert-document`
  - `render-content`
- Real DOCX analysis using pandoc extraction.
- A user/supervising-agent confirmation gate between analysis and conversion.
- New TDD-built pandoc cleanup pipeline (attrs, images, TOC, tables, footnotes, legacy image
  conversion) targeting the four named defect categories — see v3.1 Deviation Notice above; this
  is not a relocation of existing code.
- Deterministic chunking based on structural anchors, not raw line numbers.
- Versioned manifest and metadata schemas.
- Source and plan fingerprints to detect stale plans.
- Canonical content package generation.
- Local media preservation and path rewriting.
- Canonical validation with explicit PASS/WARN/FAIL policy.
- A renderer protocol and one concrete multipage Markdown renderer.
- Atomic output generation and stale-output cleanup.
- CLI entry points for each skill and the full pipeline.
- Unit, contract, negative, integration, and CEIS acceptance tests.
- Human-review evidence report comparing source-derived facts with output-derived facts.

### Explicitly deferred

- Generalized template authoring or template UI.
- Semantic remapping into policy/procedure/training schemas.
- AI-generated classification or summarization.
- Word/PDF, PowerPoint, audio, quiz, or Copilot Studio renderers.
- Retrieval-optimized chunking.
- SharePoint upload or publishing.
- Destination interview workflow.
- Custom preview/editor.
- Approval and governance workflow integration.
- Publishing this plugin to the sibling monorepo or marketplace.

`md_to_docx.py` may be relocated only if it is part of the already-working code bundle, but it is not wired into Phase 1 execution and is not evidence of a Phase 1 renderer.

## 5. Non-Negotiable Architectural Rules

1. Raw pandoc Markdown is transitory and never canonical.
2. Analysis produces recommendations and a plan; it does not produce canonical chunks.
3. Conversion requires an explicitly confirmed plan.
4. A plan is valid only for the source fingerprint recorded in that plan.
5. Chunk boundaries are structural anchors recorded from analyzed headings, not raw line numbers reused after cleanup.
6. Canonical outputs are written to a staging directory, validated, then atomically promoted.
7. Rendering reads only the canonical package.
8. Validation must detect both missing expected artifacts and unexpected orphan artifacts.
9. WARN is not equivalent to PASS. Acceptance requires an explicit warning disposition record.
10. The CEIS Manual is a regression fixture, not a source of hard-coded rules.
11. The cleanup pipeline is new, TDD-built code (see v3.1 Deviation Notice); once merged, its
    behavior is preserved unless a new failing regression test demonstrates a defect.
12. Every public command returns a non-zero exit code on FAIL.

## 6. Package Contracts

### 6.1 Analysis package

```text
analysis/
  analysis-report.json
  conversion-plan.draft.json
  raw/
    extracted.md
    media/
```

The `raw/` folder is disposable and visibly marked transitory.

### 6.2 Confirmed plan

Conversion requires `conversion-plan.confirmed.json`. Confirmation is represented in data, not inferred from file presence:

```json
{
  "schema_version": "1.0",
  "plan_id": "sha256:...",
  "source": {
    "path": "sourcedocuments/CEIS MANUAL - working version.docx",
    "sha256": "...",
    "size_bytes": 0
  },
  "strategy": "chunked",
  "chunk_level": 2,
  "chunk_anchors": [
    {
      "stable_key": "file-access",
      "heading_text": "FILE ACCESS",
      "heading_level": 2,
      "occurrence": 1,
      "source_heading_path": ["FILE ACCESS"]
    }
  ],
  "content_type": "manual",
  "template_profile": "source-structure-v1",
  "confirmation": {
    "status": "confirmed",
    "confirmed_by": "user-or-supervising-agent",
    "confirmed_at": "ISO-8601 timestamp"
  },
  "analysis_warnings": []
}
```

`plan_id` is calculated from normalized plan content excluding the `plan_id` field itself.

### 6.3 Canonical content package

```text
canonical-content/
  manifest.json
  validation.json
  chunks/
    <chunk-id>.md
    <chunk-id>.meta.json
  media/
    <asset files>
```

### 6.4 Manifest contract

Minimum fields:

```json
{
  "schema_version": "1.0",
  "generator": {
    "plugin": "docx-to-content",
    "plugin_version": "0.1.0"
  },
  "source": {
    "path": "...",
    "sha256": "..."
  },
  "plan_id": "sha256:...",
  "content_type": "manual",
  "template_profile": "source-structure-v1",
  "strategy": "chunked",
  "chunk_count": 0,
  "chunks": [],
  "media": [],
  "validation_report": "validation.json"
}
```

### 6.5 Chunk metadata contract

```json
{
  "schema_version": "1.0",
  "chunk_id": "file-access--a1b2c3d4",
  "source_order": 7,
  "source_heading_path": ["FILE ACCESS"],
  "topic": "FILE ACCESS",
  "content_type": "manual",
  "template_profile": "source-structure-v1",
  "source_sha256": "...",
  "plan_id": "sha256:...",
  "content_file": "file-access--a1b2c3d4.md",
  "content_sha256": "...",
  "local_links": [],
  "media_refs": []
}
```

### 6.6 Stable chunk identity

A chunk ID must not depend on ordinal position alone. It is derived from:

- normalized full heading path;
- heading occurrences needed to distinguish repeated paths;
- a short hash of the normalized structural key.

Example:

```text
file-access-how-to-seal-a-file--7d91c4a2
```

`source_order` remains metadata for display ordering but is not identity.

## 7. Skill Contracts

### 7.1 `analyze-document`

**Input:** source `.docx`, analysis output directory, optional content type/profile.  
**Output:** analysis report and draft plan.

Required analysis:

- verify source exists and is readable;
- fingerprint source;
- verify required executables and report versions;
- run pandoc once into the transitory raw folder;
- count headings by level;
- reconstruct heading paths;
- detect repeated heading paths;
- count local images and image formats;
- detect raw TOC evidence and known pandoc defect signals;
- estimate chunk candidates for candidate heading levels;
- recommend single or chunked strategy with reasons;
- output structural anchors, not line-number contracts;
- write draft plan with `confirmation.status = "draft"`;
- never write canonical content.

Recommendation heuristics are advisory and configurable constants. They must not encode CEIS-specific heading names.

### 7.2 `convert-document`

**Input:** source `.docx`, confirmed plan, output root.  
**Output:** validated canonical package.

Preconditions:

- confirmation status is `confirmed`;
- source fingerprint matches plan;
- plan schema is supported;
- plan anchors can be reconciled after cleanup;
- destination is not promoted until validation succeeds.

Pipeline:

```text
DOCX
-> pandoc extraction to staging
-> attrs cleanup
-> image-placement cleanup
-> TOC cleanup
-> table cleanup
-> footnote cleanup
-> legacy image conversion
-> structural-anchor reconciliation
-> chunking
-> media path rewrite/copy
-> metadata and hashes
-> manifest
-> canonical validation
-> atomic promotion
```

The conversion must fail rather than silently truncate if the number of chunks differs from confirmed anchors or if any confirmed anchor cannot be reconciled.

### 7.3 `render-content`

**Input:** canonical package, renderer name, output root.  
**Output:** rendered package and validation report.

Renderer preconditions:

- canonical validation status is PASS, or WARN with an explicit accepted-warning disposition file;
- supported manifest schema;
- all hashes and references validate.

The multipage Markdown renderer:

- consumes the manifest ordering;
- writes one page per chunk;
- writes a hierarchical or path-aware `index.md`;
- rewrites/copies media references so rendered pages resolve locally;
- does not read the DOCX, analysis raw folder, or conversion plan directly;
- writes to staging and atomically promotes after validation;
- removes stale output from previous runs by replacing the output directory, not overlaying it.

## 8. Renderer Protocol

Use an actual protocol/abstract interface rather than a data loader labeled as a contract.

```python
class Renderer(Protocol):
    name: str
    supported_manifest_versions: frozenset[str]

    def render(self, package: CanonicalPackage, output_dir: Path) -> RenderResult:
        ...
```

`CanonicalPackage.load()` performs schema and integrity validation before a renderer receives data.

A renderer result includes:

- renderer name and version;
- source manifest hash;
- output files;
- validation status;
- errors and warnings.

## 9. Validation Policy

### PASS

No errors and no undispositioned warnings.

### WARN

No errors, but reviewable discrepancies exist. WARN cannot be promoted to accepted output until `warning-disposition.json` records each warning as accepted or resolved.

### FAIL

Any invariant, integrity, schema, reference, or required-fidelity check fails. Commands exit non-zero and staging output is retained for diagnosis but not promoted.

### Canonical validation must detect

- unsupported/missing schema versions;
- source or plan fingerprint mismatch;
- malformed JSON and missing required fields;
- manifest `chunk_count` mismatch;
- duplicate chunk IDs, content paths, metadata paths, or source orders;
- missing expected chunks/sidecars;
- orphan chunks/sidecars/media;
- mismatched IDs between manifest and sidecars;
- mismatched content hashes;
- empty chunks;
- heading path missing from chunk content where required;
- content loss/duplication using normalized aggregate comparison;
- unresolved structural anchors;
- raw TOC artifacts;
- pandoc attributes;
- images embedded in headings;
- unsupported legacy media;
- broken local document links;
- broken media references;
- path traversal or absolute-path references.

### Render validation must detect

- missing index/pages/output report;
- broken index links;
- missing or orphan pages;
- page count mismatch;
- broken local links and media references from pages;
- path traversal or absolute references;
- stale files from previous render runs;
- manifest hash mismatch;
- rendered page content not traceable to a chunk ID.

## 10. Fidelity Evidence

Automated structural validation is necessary but insufficient. The CEIS acceptance run must produce `evidence-report.md` containing:

- source fingerprint and tool versions;
- source heading counts by level;
- canonical heading counts by level;
- source media count and canonical/rendered media count;
- source TOC evidence and reconciliation result;
- chunk count and list of structural anchors;
- aggregate normalized text comparison result;
- broken-link counts for canonical and rendered outputs;
- warnings and dispositions;
- a human spot-check checklist covering at least:
  - title/front matter;
  - one table-heavy section;
  - one image-heavy section;
  - one deep heading hierarchy;
  - one footnote or cross-reference case;
  - beginning, middle, and end of the manual.

Human review records observed facts only. It does not require pixel-perfect reproduction because presentation is intentionally separated.

## 11. Generalization Evidence

The automated suite must include at least two synthetic fixtures in addition to CEIS:

1. `small-single.docx` or deterministic equivalent: small document, single strategy, image and internal link.
2. `repeated-headings.docx` or deterministic equivalent: repeated heading names under different parents, deep hierarchy, and chunk identity stability test.

No test may rely on the literal strings `FILE ACCESS`, `DATA CAPTURE`, or other CEIS-only headings except CEIS regression assertions.

## 12. CLI and Exit-Code Contract

Provide real command entry points:

```bash
python -m scripts.cli analyze --source <docx> --output <analysis-dir>
python -m scripts.cli confirm --draft-plan <path> --output <confirmed-plan>
python -m scripts.cli convert --source <docx> --plan <confirmed-plan> --output <run-dir>
python -m scripts.cli render --canonical <canonical-dir> --renderer multipage-markdown --output <render-dir>
python -m scripts.cli run --source <docx> --confirmed-plan <path> --output <run-dir>
```

Exit codes:

- `0`: PASS
- `2`: validation or contract FAIL
- `3`: dependency/precondition failure
- `4`: user input or unsupported schema/renderer
- unexpected exceptions remain non-zero and include a concise diagnostic

No all-in-one command may bypass plan confirmation.

## 13. Output Safety and Reproducibility

- Create a unique staging directory under the requested output root.
- Never overlay a previous canonical or rendered directory.
- Promote with directory replacement only after validation.
- Record plugin version, Python version, pandoc version, and soffice version.
- Produce deterministic JSON ordering and UTF-8 output.
- Normalize timestamps out of content hashes.
- Re-running against identical source, plan, and tool versions must produce identical IDs, manifests, and content hashes, excluding explicitly documented run metadata.

## 14. Plugin Structure

```text
plugins/docx-to-content/
  .claude-plugin/plugin.json
  plugin.yaml
  scripts/
    cli.py
    contracts.py
    hashing.py
    dependencies.py
    analyze_structure.py
    plans.py
    convert.py
    chunking.py
    package.py
    validate_canonical.py
    pandoc_fixes/
    renderers/
      protocol.py
      multipage_markdown.py
      validate_rendered.py
  skills/
    analyze-document/SKILL.md
    convert-document/SKILL.md
    render-content/SKILL.md
  tests/
    unit/
    contract/
    integration/
    fixtures/
  references/
    pandoc-docx-setup.md
    known-pandoc-gaps.md
    canonical-contract.md
  requirements.in
  requirements.txt
```

Follow proven repository conventions discovered from the actual repo. Do not invent symlink or metadata syntax without first inspecting the local scaffold and an existing working plugin.

## 14a. Structured Content Authoring Guidance

**Added 2026-07-25.** This refines what canonical content is intended to be maintained as. It does not weaken or replace any v3 integrity/validation requirement in the sections above, and it does not authorize additional renderers, publishing, or UI scope.

### Core decision

- Markdown is the human-maintained canonical content format.
- JSON sidecars/manifests are the machine-maintained control metadata (identity, lineage, hashes, validation, media/link inventories, package manifests, renderer coordination).
- Templates describe what content belongs in a content type, not visual layout.
- Renderers own destination-specific presentation.
- Code generates navigation, indexes, and summaries — these are never hand-authored.

### Author responsibility model

Authors maintain: accurate business content, meaningful headings/subheadings, procedure steps, genuinely tabular tables, useful images/captions, essential links, warnings, notes, examples, exceptions, troubleshooting guidance.

Authors do **not** maintain: tables of contents, page numbers, breadcrumbs, prev/next navigation, indexes, keyword summaries, derivable related-topic listings, publication timestamps, content hashes, package manifests, renderer metadata, branding, or destination-specific layout.

Framing: "Authors maintain content + meaningful structure. Code maintains derived structure + presentation + output formatting." Never frame this as "authors no longer care about formatting."

### Template terminology (three distinct concepts)

1. **Content-structure template** — a Markdown authoring skeleton describing expected sections and meaning, not visual layout.
2. **Reusable semantic components** — note, warning, important, example, prerequisite, procedure step, expected result, decision, exception, troubleshooting item, definition, reference, knowledge check. These describe meaning, not appearance.
3. **Presentation template** — renderer-specific: branding, typography, spacing, colours, headers/footers, page layout, callout appearance, navigation layout. Stays separate from canonical Markdown.

### Phase 1 scope for this guidance

Include: Markdown as canonical prose format, preserved meaningful structure, authored-vs-generated distinction, initial authoring guidance, one initial manual-topic content-structure template.

Exclude (unchanged from existing v3 deferred scope): a generalized template engine, semantic remapping across policy/procedure/manual/training schemas, a template-authoring UI, additional renderers. The manual-topic template is authoring guidance and a concrete pilot target — it must not become CEIS-specific conversion logic.

### Initial manual-topic template

```markdown
---
content_type: manual-topic
title:
owner:
status: draft
review_date:
audience:
---

# Topic Title

## Purpose

## Before You Begin

## Procedure

1. First meaningful action.

## Expected Result

## Exceptions and Special Cases

## Troubleshooting

### Problem

### Resolution

## Related Topics
```

Sections are intentionally simple and non-exhaustive. Do not generate empty boilerplate sections merely to satisfy the template's shape.

### Metadata ownership

Author-maintained front matter: `content_type`, `title`, `owner`, `status`, `audience`, `effective_date` (where applicable), `review_date`.

Machine-owned metadata (`chunk_id`, source fingerprint, `plan_id`, content hash, link/media inventories, generated timestamps, renderer traceability, validation status) belongs only in sidecars/manifests — never duplicated into Markdown front matter without a demonstrated requirement.

### Supported Markdown profile

A documented, deliberately limited authoring profile: headings/subheadings, paragraphs, ordered/unordered lists, tables, links, relative-path images, emphasis, block quotes or one documented semantic-callout syntax, optional author-owned front matter. No arbitrary embedded HTML or undocumented extensions by default. Example semantic-callout syntax:

```markdown
> [!WARNING]
> A sealed file must not be accessed without the required authorization.
```

### Generated elements

Table of contents, page navigation, indexes, keyword summaries, breadcrumbs, prev/next links, cross-document topic listings, publication metadata, and renderer-specific numbering are generated/derived, not canonical authored prose, whenever they can be determined reliably. The Word-generated TOC found in raw pandoc extraction must be removed from canonical content; a renderer or generation step recreates navigation from canonical structure. Detection/removal of generated-looking content must remain validated and reviewable — do not strip something merely because it resembles derived content if that risks removing real business information.

### Files to add

Using the Task 0 conventions (or documenting a deviation if the verified structure differs):

```text
references/
  content-authoring-guide.md
  supported-markdown-profile.md
  generated-elements.md
templates/
  content/
    manual-topic.md
  components/
    README.md
  examples/
    manual-topic-example.md
```

`content-authoring-guide.md` covers the author responsibility model, meaningful-vs-derived structure, concise authoring rules, link-don't-duplicate guidance, and a list of code-generated elements. It stays free of hashes, renderer protocols, or package internals — written for a business content author.

`supported-markdown-profile.md` documents permitted constructs, supported front-matter fields, semantic component syntax, relative-link/media conventions, prohibited constructs, validation expectations, and valid/invalid examples.

`generated-elements.md` documents each generated element and its canonical source, e.g.:

```text
Table of contents    — source: canonical heading hierarchy
Navigation            — source: manifest ordering and heading paths
Keyword summaries      — source: later generation process; not implemented in Phase 1
```

Never claim a generated capability is implemented unless it actually is.

`manual-topic-example.md` is one realistic, non-sensitive completed example: front matter, headings, a numbered procedure, a warning/note, an image reference, an expected result, an exception, troubleshooting, and a related-topic link.

### Required tests (additive to Section 15 acceptance criteria)

- the manual-topic template exists;
- the author guide distinguishes meaningful from generated structure;
- generated-elements doc lists TOC and navigation;
- the template contains no machine-owned fields (`chunk_id`, `content_sha256`, `plan_id`);
- the supported Markdown profile defines relative image/link rules;
- the example follows the declared profile;
- the conversion pipeline removes the detected Word-generated TOC from canonical content;
- canonical headings remain available for code-generated TOC/navigation;
- empty optional template sections are not blindly inserted;
- no CEIS-specific heading names are hard-coded into the generic template logic.

## 14b. Upload-Friendly Output Profiles and SharePoint Publishing Boundary

**Added 2026-07-25.** This defines the intended expansion path for future output formats. It does **not** authorize implementing additional renderers in Phase 1.

### Core decision

Separate three responsibilities: (1) canonical content creation, (2) destination rendering, (3) destination publishing/upload. Canonical content and Phase 1 rendering must operate without SharePoint connectivity, Microsoft Graph, PnP PowerShell, tenant credentials, an Entra app registration, admin consent, or SharePoint site-write permissions. A future publishing adapter may use those under an approved authorization path — they must never become dependencies of canonical content maintenance or Phase 1 rendering.

### SharePoint authorization boundary

Do not assume automated SharePoint modern-page creation will be permitted. Prefer generating ordinary, validated output files a user can upload/sync into a SharePoint document library without page APIs. Do not: assume `Sites.ReadWrite.All`/`Sites.Selected` will be approved, assume PnP PowerShell is available, register an Entra app as part of this plugin, store tenant credentials in-repo, make SharePoint access a test precondition, treat raw `.aspx` as an authoring/canonical format, or claim publication succeeded when only local rendering succeeded.

### Preferred destination hierarchy (documentation order, not build order)

1. Markdown package 2. PDF 3. Word 4. PowerPoint 5. Audio/video with transcript 6. HTML 7. ZIP release package 8. SharePoint modern-page publishing (optional adapter)

### Destination profile contract — `references/future-output-profiles.md`

For every profile, document: purpose, audience, canonical content accepted, semantic components supported, generated elements, presentation-template mechanism, document-library upload behavior, media handling, validation requirements, edit ownership, round-trip policy, accessibility considerations, known fidelity limitations, and implementation status. Statuses: `implemented`, `designed-only`, `deferred`, `requires-platform-authorization`. **Only multipage Markdown is `implemented` in Phase 1.**

Profile summaries (full detail lives in `future-output-profiles.md`, not duplicated here):

- **Multipage Markdown** — `implemented`. Canonical Markdown is source of truth; rendered output is `generated-read-only`; no automatic round-trip.
- **PDF** — `designed-only`. Publication/record copy; `generated-read-only`; no round-trip.
- **Word** — `designed-only`. Editable derivative only under explicit governance; must never become a silent competing source of truth with canonical Markdown; any accepted edits require a separate re-import/reconciliation workflow, not silent merge.
- **PowerPoint** — `designed-only`. Requires canonical content + presentation purpose + slide plan + visual template; source chunk IDs must remain traceable in generated metadata/notes; `generated-read-only`.
- **Audio/Video** — `designed-only`. Transcript must accompany generated media; tables/images require intentional narration treatment, not literal markup readout; `generated-read-only`.
- **HTML** — `designed-only`. Generated output; document-library upload and web hosting are separate concerns — do not assume uploaded HTML behaves as a hosted site; `generated-read-only`.
- **ZIP release package** — `designed-only`. Archival/transfer bundle, not a reading/editing experience; only implement if trivial and non-disruptive after Phase 1 acceptance passes.
- **SharePoint modern pages** — `requires-platform-authorization`. `.aspx` is a platform storage detail, never an authoring format. Do not select a delivery mode (manual transfer / authorized delegated / authorized application / hybrid page ownership) or write publisher code until an approved authorization model, target site, supported interfaces, ownership model, and overwrite/drift policy are supplied.

### Document-library-oriented output structure (conceptual only, not created/uploaded in Phase 1)

```text
Knowledge Content/
  Canonical/<content-set>/{index.md, topics/, media/}
  Published/{Markdown,Word,PDF,PowerPoint,Audio,HTML}/
  Releases/{manifests,validation,evidence,archives}/
```

### Generated-versus-maintained ownership classification

Every destination profile is one of: `canonical`, `generated-read-only`, `generated-editable-with-drift-detection`, `hybrid-renderer-and-local-owned`. Phase 1: canonical Markdown package = `canonical`; multipage Markdown renderer output = `generated-read-only`; SharePoint modern page = undecided future profile; Word/PDF/PowerPoint/HTML/audio = `generated-read-only` by default. No future output may silently become a second source of truth.

### Phase 1 implementation boundary (reaffirmed)

Implement only: canonical Markdown package, metadata/media/manifests, the multipage Markdown renderer, v3's required validation/evidence, and `future-output-profiles.md` as architectural guidance. Do **not** implement: PDF/Word/PowerPoint/audio/video/HTML/SharePoint-page renderers, ZIP release automation (unless trivial and non-disruptive), a SharePoint publishing adapter, Entra authentication, PnP PowerShell, or Microsoft Graph integration.

### Required guidance tests

- `references/future-output-profiles.md` exists;
- multipage Markdown is marked `implemented`; every other profile is not;
- SharePoint modern pages are marked `requires-platform-authorization`;
- raw `.aspx` is not identified as an authoring format anywhere;
- canonical content, rendering, and publishing are documented as separate responsibilities;
- no future profile claims round-trip editing;
- Word and SharePoint profile entries each include a drift/source-of-truth warning;
- no future renderer is registered in the Phase 1 renderer registry;
- Phase 1 has zero SharePoint, Graph, PnP, or Entra dependency (no such import, config, or credential reference anywhere in `plugins/docx-to-content/`).

## 15. Acceptance Criteria

Phase 1 is accepted only when:

- all three CLI-backed skills exist and use the same core modules;
- draft plans cannot be converted;
- stale plans are rejected by source hash mismatch;
- canonical and render contracts are versioned;
- IDs remain stable when unrelated earlier content is inserted;
- structural anchors reconcile after cleanup;
- content loss/duplication checks pass;
- all local links and media references resolve;
- orphan and stale artifact tests pass;
- canonical validation is PASS;
- render validation is PASS;
- synthetic single and repeated-heading fixtures pass;
- CEIS end-to-end run passes;
- `evidence-report.md` is complete and human spot checks are recorded;
- the renderer never reads source DOCX or transitory extraction;
- the new cleanup regression suite (built under the v3.1 Deviation Notice) still passes;
- the manual-topic template, authoring guide, supported Markdown profile, and generated-elements doc exist and pass their contract tests (Section 14a);
- the detected Word-generated TOC is removed from canonical content, with canonical headings still available for code-generated navigation;
- `references/future-output-profiles.md` exists, documents all eight destination profiles with correct implementation statuses, and Phase 1 has zero SharePoint/Graph/PnP/Entra dependency (Section 14b);
- deferred features remain unimplemented.

## 16. Rollout

Build and validate in this repository only. Preserve the current unfixed output until the new canonical and rendered packages pass acceptance. Replace or archive old generated output only as an explicit final cutover step after evidence review. Do not delete source documents or prior evidence automatically.

## 17. Implementation Principle

Do not optimize for the appearance of completion. Optimize for falsifiable evidence, repeatability, integrity, and a clean boundary between source extraction, canonical knowledge, and destination rendering.
