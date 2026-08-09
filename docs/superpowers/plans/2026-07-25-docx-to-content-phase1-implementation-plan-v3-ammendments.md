# docx-to-content Phase 1 Implementation Plan v3

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans`. Execute task-by-task. Do not skip review gates or combine confirmation with conversion.

**Goal:** Implement and validate the Phase 1 `docx-to-content` plugin defined by the v3 specification, using CEIS plus generalization fixtures to prove that versioned canonical content can be rendered without source-document dependency.

**Architecture:** Three CLI-backed skills share core modules. Analysis creates a draft structural plan; explicit confirmation creates a source-bound confirmed plan; conversion produces an atomic, versioned canonical package; rendering consumes only that package through a real renderer protocol. Integrity, fidelity, media/link behavior, stale plans, orphan outputs, and repeatability are testable invariants.

**Tech stack:** Python 3 with standard library, pytest, pandoc CLI, LibreOffice `soffice`, Markdown, JSON, SHA-256.

## Global Constraints

- Work only under `manual-conversion-poc/plugins/docx-to-content/` plus documented output/evidence paths.
- Inspect the actual repo and a working plugin scaffold before creating metadata or symlinks.
- The cleanup pipeline is new code, built from scratch under TDD (see Task 0/Task 2 v3.1 Deviation Notice — the originally-referenced pipeline was never built anywhere). Once merged, preserve its behavior; change it only after a failing regression test.
- Raw pandoc output is transitory.
- Conversion requires a confirmed plan whose source hash matches.
- Chunk identity is structural and hash-based, not ordinal-only.
- Renderers consume only a validated canonical package.
- All writes use staging plus atomic promotion.
- WARN requires explicit disposition; it is not automatic success.
- Public commands return specified non-zero exit codes on failure.
- Do not implement deferred renderers, publishing, semantic mapping, or AI classification.
- Use TDD for every new behavior.
- Commit after each independently reviewable task.

## Task 0: Repository Reconnaissance and Source Inventory — COMPLETE

**Deliverable:** `docs/reports/phase-1-conversion-poc/implementation-baseline.md` containing verified paths and conventions. **Done — see that file for full detail.**

- [x] Locate the existing working plugin scaffold used as the structural reference. **Finding:** no plugin scaffold exists anywhere in `manual-conversion-poc`. The sibling `agent-plugins-skills` monorepo's `plugins/` tree (e.g. `dev-utils`, `exploration-cycle-plugin`) is the only available structural reference, for layout conventions only.
- [x] Record actual `plugin.json`, `plugin.yaml`, skill-frontmatter, test, import, and symlink conventions. **Finding:** no per-skill symlink layer is required by any local convention (none exists to require it); v3's centralized `scripts/` + CLI design (Section 14 of the spec) is retained as-is per explicit user confirmation — no deviation needed here.
- [x] Locate every cleanup source file and its tests; record SHA-256 hashes before relocation. **BLOCKING FINDING, resolved by user decision:** none of `pandoc_fixes/{attrs,images,toc,tables,footnotes}.py`, `emf_convert.py`, `pandoc_validate.py`, `docx_to_md.py`, `md_to_docx.py`, or their tests exist anywhere — not in this repo, not in `agent-plugins-skills` (checked: working tree, every local/remote branch, all git history, all stashes). The referenced design spec (`agent-plugins-skills/docs/superpowers/specs/2026-07-25-pandoc-docx-convert-design.md`, named in this repo's `JOURNAL.md`) also does not exist. **User decision: build the cleanup pipeline from scratch under TDD.** Task 2 below is rewritten accordingly.
- [x] Verify actual CEIS source path. **Verified:** `sourcedocuments/CEIS MANUAL - working version.docx`.
- [x] Verify `pandoc --version`, `soffice --version`, and Python version. **Verified:** pandoc 3.8.3, LibreOffice 26.2.5.2 (`soffice`), Python 3.13.4, pytest present.
- [x] Identify the current generated CEIS output that must not be deleted before cutover. **Identified:** `output/ceis-manual/CEIS-Manual.md`.
- [x] Write `docs/reports/phase-1-conversion-poc/implementation-baseline.md` with commands and observed results. **Done.**
- [ ] Commit: `docs: record docx-to-content implementation baseline`.

**Gate outcome:** the required source modules were not found. Per the gate rule, this was surfaced rather than fabricated under a "relocation" label, and the user made an explicit build-from-scratch decision. Task 0 is closed; proceed to Task 1 only after the Task 0 commit above.

## Task 1: Scaffold From Verified Repository Conventions

**Files:** plugin metadata, package directories, three skill directories, test directories, references.

- [ ] Write a failing structure test that asserts required plugin metadata and all three skill folders exist.
- [ ] Run the test and confirm failure.
- [ ] Scaffold using the verified local convention from Task 0.
- [ ] Include `plugin.json` and marketplace/registry metadata only when the local convention requires them; record every updated registry file.
- [ ] Add `requirements.in` with `pytest`; generate/update the lock file using the repo's dependency process rather than hand-copying it.
- [ ] Run structure test and existing plugin validation command.
- [ ] Commit: `feat: scaffold docx-to-content plugin`.

## Task 2: Build Pandoc Cleanup Pipeline From Scratch Under TDD

**Deviation from original Task 2:** Task 0 found that the cleanup pipeline this task originally
described as "relocation" does not exist anywhere (see `docs/reports/phase-1-conversion-poc/implementation-baseline.md`). This
task is rewritten to build it as new code, TDD-first, targeting the four defect categories the
specs describe rather than copying prior work.

**Files:** new cleanup scripts and tests under the new plugin.

- [ ] Write failing tests for `pandoc_fixes/toc.py`: detect and strip raw Word TOC field dumps
      (nested bracket-link lists) from pandoc markdown output.
- [ ] Write failing tests for `pandoc_fixes/images.py`: detect and fix images glued directly to
      headings or list items (image markdown appearing on the same line as heading/list markup).
- [ ] Write failing tests for `pandoc_fixes/attrs.py`: strip leftover pandoc attribute syntax
      (`{width="..." height="..."}`, `{.underline}`, `{.mark}`, etc.) from running text.
- [ ] Write failing tests for `pandoc_fixes/tables.py` and `pandoc_fixes/footnotes.py`: cover
      known pandoc table/footnote conversion defects (malformed table rows, orphaned footnote
      markers).
- [ ] Write failing tests for `emf_convert.py`: convert legacy `.emf`/`.wmf` media to `.png` via
      `soffice`, verified against the tool version recorded in Task 0.
- [ ] Write failing tests for `pandoc_validate.py`: hard-fail on image links that don't resolve,
      leftover attribute artifacts, and images embedded in heading text.
- [ ] Implement each module to pass its tests, smallest increment first (attrs before images
      before toc before tables before footnotes, since later fixes depend on earlier ones being
      stable per the v3 pipeline order).
- [ ] Build a regression fixture markdown/docx sample covering raw TOC, image-in-heading, pandoc
      attributes, a table, a footnote, and one legacy `.emf`/`.wmf` reference, exercising all
      modules together.
- [ ] Run the complete new regression suite.
- [ ] Commit: `feat: build pandoc cleanup pipeline from scratch`.

**Gate:** This task produces genuinely new architecture and code — unlike the original relocation
framing, do not treat any pre-existing file as a template. Each module's tests must fail before
implementation, per `.agent/rules/test-driven-development.md`.

## Task 3: Define Versioned Contracts and Hashing

**Files:** `scripts/contracts.py`, `scripts/hashing.py`, `references/canonical-contract.md`, tests.

**Required types:** `SourceFingerprint`, `StructuralAnchor`, `ConversionPlan`, `ChunkMetadata`, `ManifestChunk`, `Manifest`, `ValidationIssue`, `ValidationReport`, `RenderResult`.

- [ ] Write failing serialization tests for every required field in spec sections 6 and 8.
- [ ] Write failing tests rejecting missing/unsupported `schema_version`.
- [ ] Write failing tests for deterministic canonical JSON and SHA-256 fingerprints.
- [ ] Write failing tests showing timestamps do not alter content hashes.
- [ ] Implement dataclasses/loaders with strict required-field checking.
- [ ] Implement normalized JSON hashing.
- [ ] Document contracts and compatibility policy in `references/canonical-contract.md`.
- [ ] Run tests.
- [ ] Commit: `feat: add versioned canonical contracts`.

## Task 4: Implement Structural Identity

**Files:** `scripts/identity.py`, tests.

- [ ] Write failing tests for Unicode-safe slug normalization.
- [ ] Write failing tests for repeated heading names under different parent paths.
- [ ] Write failing test proving insertion of an unrelated earlier section changes `source_order` but not `chunk_id`.
- [ ] Write failing test for repeated identical full paths using occurrence disambiguation.
- [ ] Implement `normalize_heading_path()` and `make_chunk_id()` using full path plus short SHA-256.
- [ ] Run tests.
- [ ] Commit: `feat: add stable structural chunk identity`.

## Task 5: Implement Dependencies and CLI Skeleton

**Files:** `scripts/dependencies.py`, `scripts/cli.py`, CLI tests.

- [ ] Write failing tests for missing source, missing pandoc, missing soffice when legacy conversion is required, unsupported command, and exit codes 2/3/4.
- [ ] Implement dependency probing with executable paths and versions.
- [ ] Add CLI subcommands: `analyze`, `confirm`, `convert`, `render`, `run`.
- [ ] Ensure `run` requires an already-confirmed plan and cannot auto-confirm.
- [ ] Add `--help` contract tests.
- [ ] Run tests.
- [ ] Commit: `feat: add command interface and dependency checks`.

## Task 6: Analyze Real DOCX Into a Draft Plan

**Files:** `scripts/analyze_structure.py`, `scripts/plans.py`, analysis tests.

- [ ] Build deterministic synthetic DOCX fixtures or checked-in fixtures for small-single and repeated-headings cases.
- [ ] Write failing test that analysis invokes pandoc into `analysis/raw/` and labels it transitory.
- [ ] Write failing tests for heading counts, depth distribution, reconstructed paths, repeated paths, image formats, raw TOC evidence, and known defect signals.
- [ ] Write failing tests for configurable recommendation heuristics without CEIS heading literals.
- [ ] Write failing test that draft plan contains structural anchors and source fingerprint, not reusable raw line offsets.
- [ ] Write failing test that analysis writes no canonical-content folder.
- [ ] Implement analysis and draft-plan generation.
- [ ] Run synthetic fixture tests.
- [ ] Commit: `feat: analyze docx structure and draft conversion plans`.

## Task 7: Implement Explicit Confirmation and Stale-Plan Rejection

**Files:** `scripts/plans.py`, CLI confirmation tests.

- [ ] Write failing test that `convert` rejects `confirmation.status = draft`.
- [ ] Write failing test that confirmation creates a new confirmed plan rather than mutating the draft.
- [ ] Write failing test that source modification after confirmation causes source-hash mismatch.
- [ ] Write failing test that plan tampering causes `plan_id` mismatch.
- [ ] Implement confirmation command and plan verification.
- [ ] Run tests.
- [ ] Commit: `feat: enforce source-bound plan confirmation`.

## Task 8: Reconcile Structural Anchors After Cleanup

**Files:** `scripts/chunking.py`, tests.

- [ ] Write failing tests showing cleanup can change line numbers while structural anchors still resolve.
- [ ] Write failing tests for missing anchor, duplicate ambiguous anchor, changed heading level, and repeated occurrence resolution.
- [ ] Write failing test that unresolved anchors fail conversion rather than truncate.
- [ ] Implement heading-tree parsing and anchor reconciliation.
- [ ] Implement chunk slicing from reconciled positions.
- [ ] Add aggregate assertion that all non-transitory cleaned lines belong to exactly one chunk, excluding explicitly documented front-matter handling.
- [ ] Run tests.
- [ ] Commit: `feat: reconcile confirmed anchors and split content`.

## Task 9: Implement Canonical Package Builder and Media Rewriting

**Files:** `scripts/convert.py`, `scripts/package.py`, tests.

- [ ] Write failing test for full cleanup order.
- [ ] Write failing test for one sidecar per chunk and no orphan sidecars.
- [ ] Write failing tests for content hashes, plan ID, source hash, schema version, and stable ordering.
- [ ] Write failing tests for media copied once, duplicate media names, relative path rewriting, URL-encoded paths, spaces, anchors, and images referenced from multiple chunks.
- [ ] Write failing tests rejecting absolute paths and `..` traversal.
- [ ] Write failing test for unsupported legacy media remaining after conversion.
- [ ] Implement staging package builder, media inventory, path rewriting, metadata, and manifest.
- [ ] Run tests.
- [ ] Commit: `feat: build canonical packages with media integrity`.

## Task 10: Implement Canonical Validator and Warning Disposition

**Files:** `scripts/validate_canonical.py`, `scripts/dispositions.py`, tests.

- [ ] Add negative tests for every canonical invariant in spec section 9.
- [ ] Include tests for malformed JSON, unsupported schema, counts, duplicate IDs/paths/orders, missing and orphan artifacts, hash mismatch, empty chunks, raw artifacts, broken links/media, stale plan/source, path traversal, and unresolved anchors.
- [ ] Write content-loss and duplicate-content tests using normalized aggregate comparison.
- [ ] Write tests for PASS, WARN, FAIL semantics.
- [ ] Write failing test proving WARN blocks promotion without a complete disposition file.
- [ ] Implement validator and disposition validation.
- [ ] Run tests.
- [ ] Commit: `feat: enforce canonical validation policy`.

## Task 11: Implement Atomic Promotion and Repeatability

**Files:** `scripts/atomic_output.py`, conversion integration tests.

- [ ] Write failing test that failed validation leaves prior accepted output unchanged.
- [ ] Write failing test that successful validation replaces, rather than overlays, old output.
- [ ] Write failing test that stale files from an earlier run disappear.
- [ ] Write failing test that identical source/plan/tool inputs produce identical IDs, manifests, and content hashes.
- [ ] Implement unique staging directories, diagnostic retention on fail, and atomic directory replacement on pass.
- [ ] Run tests.
- [ ] Commit: `feat: add atomic reproducible package output`.

## Task 12: Implement a Real Renderer Protocol

**Files:** `scripts/renderers/protocol.py`, `scripts/package.py`, tests.

- [ ] Write failing test that `CanonicalPackage.load()` validates schema, hashes, references, and accepted status before returning.
- [ ] Write failing protocol-conformance test for a minimal test renderer.
- [ ] Write failing test that renderer code has no DOCX/raw-analysis input.
- [ ] Implement `Renderer` protocol, `CanonicalPackage`, and renderer registry.
- [ ] Reject unsupported renderer names and manifest versions.
- [ ] Run tests.
- [ ] Commit: `feat: define validated renderer protocol`.

## Task 13: Implement Multipage Markdown Renderer

**Files:** `scripts/renderers/multipage_markdown.py`, tests.

- [ ] Write failing tests for single and chunked packages through the same code path.
- [ ] Write failing tests for manifest ordering and hierarchical/path-aware index labels.
- [ ] Write failing tests for media copying and page-relative reference rewriting.
- [ ] Write failing tests for internal links between chunks.
- [ ] Write failing test for repeated headings producing distinct links.
- [ ] Implement renderer to staging output.
- [ ] Run tests.
- [ ] Commit: `feat: add multipage markdown renderer`.

## Task 14: Implement Render Validator and Atomic Promotion

**Files:** `scripts/renderers/validate_rendered.py`, tests.

- [ ] Add negative tests for every render invariant in spec section 9.
- [ ] Test broken index links, missing/orphan pages, count mismatch, broken media/local links, path traversal, stale files, manifest-hash mismatch, and missing chunk traceability.
- [ ] Write test proving prior accepted render survives a failed new render.
- [ ] Implement render validation report and atomic promotion.
- [ ] Run tests.
- [ ] Commit: `feat: validate and atomically publish rendered packages`.

## Task 15: Write Three Skill Contracts

**Files:** three `SKILL.md` files and contract tests.

Each skill document must specify:

- trigger and purpose;
- exact CLI invocation;
- inputs and output artifacts;
- preconditions;
- PASS/WARN/FAIL and exit-code behavior;
- prohibited shortcuts;
- handoff to the next skill.

- [ ] Write failing contract tests for required phrases and command names.
- [ ] Write `analyze-document/SKILL.md` emphasizing transitory raw output and draft plan.
- [ ] Write `convert-document/SKILL.md` emphasizing confirmed plan, source hash, staging, and canonical validation.
- [ ] Write `render-content/SKILL.md` emphasizing canonical-only input and renderer validation.
- [ ] Run contract tests and plugin validator.
- [ ] Commit: `docs: define docx-to-content skill contracts`.

## Task 15a: Structured Content Authoring Guidance

**Added 2026-07-25.** Implements Section 14a of the spec amendments. This is authoring-guidance and reference-doc scope only — no new renderer, publishing, or UI work.

**Files:**
- Create: `references/content-authoring-guide.md`
- Create: `references/supported-markdown-profile.md`
- Create: `references/generated-elements.md`
- Create: `templates/content/manual-topic.md`
- Create: `templates/components/README.md`
- Create: `templates/examples/manual-topic-example.md`
- Create: contract tests for all of the above

Use the Task 0 conventions for path placement; if the verified repo/plugin structure differs from the paths above, use that convention and document the deviation here before continuing.

- [ ] Write failing contract test asserting `templates/content/manual-topic.md` exists and contains the required section headings (`Purpose`, `Before You Begin`, `Procedure`, `Expected Result`, `Exceptions and Special Cases`, `Troubleshooting`, `Related Topics`) and front-matter fields (`content_type`, `title`, `owner`, `status`, `review_date`, `audience`).
- [ ] Write failing contract test asserting the template contains **no** machine-owned fields (`chunk_id`, `content_sha256`, `plan_id`).
- [ ] Write `templates/content/manual-topic.md` per spec Section 14a.
- [ ] Write failing contract test asserting `references/content-authoring-guide.md` exists and explicitly distinguishes author-maintained content from code-generated elements (e.g. contains both "Authors maintain" and "Code maintains" framing), without exposing hashes, renderer protocol names, or package internals.
- [ ] Write `references/content-authoring-guide.md`.
- [ ] Write failing contract test asserting `references/supported-markdown-profile.md` documents relative-path image/link rules and lists permitted vs. prohibited constructs.
- [ ] Write `references/supported-markdown-profile.md`.
- [ ] Write failing contract test asserting `references/generated-elements.md` lists at minimum "table of contents" and "navigation" each with a named canonical source, and does not claim an unimplemented capability as implemented.
- [ ] Write `references/generated-elements.md`.
- [ ] Write `templates/components/README.md` documenting the semantic-callout syntax (e.g. `> [!WARNING]`) and the list of semantic components (note, warning, important, example, prerequisite, procedure step, expected result, decision, exception, troubleshooting item, definition, reference, knowledge check).
- [ ] Write failing contract test asserting `templates/examples/manual-topic-example.md` follows the declared Markdown profile and contains a procedure, a semantic callout, an image reference, an expected result, an exception, troubleshooting, and a related-topic link, using non-sensitive example content.
- [ ] Write `templates/examples/manual-topic-example.md`.
- [ ] Write failing test asserting `convert-document`'s cleanup pipeline (Task 2) detects and removes the Word-generated TOC dump from canonical content while the canonical heading hierarchy remains intact and available for code-generated TOC/navigation.
- [ ] Write failing test asserting template rendering does not insert empty boilerplate for optional sections with no authored content.
- [ ] Write failing test asserting no CEIS-specific heading literal (e.g. `FILE ACCESS`, `DATA CAPTURE`) appears in the generic template/guidance files.
- [ ] Run all tests added in this task.
- [ ] Commit: `docs: add structured content authoring guidance and manual-topic template`.

**Gate:** This task must not introduce a generalized template engine, semantic remapping across content types, a template-authoring UI, or any renderer beyond the existing `multipage_markdown.py`.

## Task 15b: Document Future Output Profiles and SharePoint Publishing Boundary

**Added 2026-07-25.** Implements spec Section 14b. This is documentation-only scope — it must not add any new renderer, dependency, credential, or publishing code.

**Files:**
- Create: `references/future-output-profiles.md`
- Create: a contract test asserting the profile document's structure and claims

- [ ] Write failing contract test asserting `references/future-output-profiles.md` exists and documents exactly these eight profiles: Multipage Markdown, PDF, Word, PowerPoint, Audio/Video, HTML, ZIP Release Package, SharePoint Modern Pages.
- [ ] Write failing contract test asserting only the Multipage Markdown profile is marked `implemented`; all others are `designed-only` or `requires-platform-authorization`.
- [ ] Write failing contract test asserting the SharePoint Modern Pages profile is marked `requires-platform-authorization`, and that no `.aspx` reference anywhere in the doc is described as an authoring or canonical format.
- [ ] Write failing contract test asserting the Word and SharePoint profile sections each contain an explicit drift/source-of-truth warning (canonical Markdown remains the source of truth; no silent round-trip).
- [ ] Write failing contract test asserting no profile entry claims automatic round-trip editing.
- [ ] Write failing test scanning `plugins/docx-to-content/` for any SharePoint, Microsoft Graph, PnP PowerShell, or Entra reference (imports, config keys, credential names) — must find none.
- [ ] Write failing test asserting the Phase 1 renderer registry (from Task 12) contains only `multipage_markdown` — no future renderer name is registered, even as a stub.
- [ ] Write `references/future-output-profiles.md` covering, for each profile: purpose, audience, canonical content accepted, semantic components supported, generated elements, presentation-template mechanism, document-library upload behavior, media handling, validation requirements, edit ownership, round-trip policy, accessibility considerations, known fidelity limitations, implementation status — per spec Section 14b.
- [ ] Run all tests added in this task.
- [ ] Commit: `docs: document future output profiles and sharepoint publishing boundary`.

**Gate:** Do not implement a PDF, Word, PowerPoint, audio/video, HTML, or SharePoint-page renderer. Do not add a SharePoint publishing adapter, Entra authentication, PnP PowerShell, or Microsoft Graph integration. Do not select a SharePoint delivery mode or write any publisher code.

## Task 16: End-to-End Generalization Fixtures

**Files:** integration tests and fixture expectations.

- [ ] Run `small-single` through analyze, confirm, convert, and render.
- [ ] Assert single strategy, one-entry index, valid media, valid local link, and PASS reports.
- [ ] Run `repeated-headings` through the full flow.
- [ ] Assert distinct stable IDs, correct heading paths, deep hierarchy, and PASS reports.
- [ ] Insert an unrelated early section and prove existing chunk IDs remain stable.
- [ ] Verify no fixture test relies on CEIS-only headings.
- [ ] Commit: `test: prove conversion generalizes beyond CEIS`.

## Task 17: CEIS End-to-End Evidence Run

**Output:** a run-specific evidence folder; preserve prior output until acceptance.

- [ ] Execute `analyze` against the real CEIS DOCX.
- [ ] Review recommendation and create confirmed plan through `confirm`.
- [ ] Execute `convert`; require canonical PASS or fully dispositioned WARN.
- [ ] Execute `render`; require PASS.
- [ ] Generate `evidence-report.md` with all metrics and checklist items named in spec section 10.
- [ ] Verify source/canonical/rendered heading and media counts.
- [ ] Verify aggregate normalized text comparison.
- [ ] Verify zero broken local links/media references.
- [ ] Perform and record the six human spot-check categories.
- [ ] Run full pytest suite and plugin validation command.
- [ ] Commit code and evidence separately: `test: validate CEIS Phase 1 evidence`.

## Task 18: Cutover, Documentation, and Metadata Reconciliation

- [ ] Confirm all acceptance criteria against evidence, not task claims.
- [ ] Archive or retain the previous unfixed output according to repo policy; do not delete it silently.
- [ ] Promote the accepted canonical and rendered CEIS outputs to the documented output location.
- [ ] Update README/vision links to the v3 spec, plan, canonical contract, and evidence report.
- [ ] Update applicable `plugin.json`, `marketplace.json`, or other registry metadata only where verified by Task 0 conventions.
- [ ] Run clean checkout/setup test using documented dependencies.
- [ ] Run final full test suite.
- [ ] Commit: `docs: complete docx-to-content Phase 1 cutover`.

## Required Review Gates

After Tasks 2, 7, 11, 14, 15a, 15b, 16, and 17, dispatch a fresh reviewer with:

- the v3 specification;
- this plan;
- task diff;
- test output;
- generated validation/evidence reports.

Reviewer must check spec alignment first and code quality second. Do not start the next gated task until blocking findings are resolved.

## Final Acceptance Checklist

- [ ] Repository baseline is factual and complete.
- [ ] New cleanup suite passes (built from scratch per the v3.1 Deviation Notice, not relocated).
- [ ] Manual-topic template, authoring guide, supported Markdown profile, and generated-elements doc exist and pass contract tests.
- [ ] Word-generated TOC is removed from canonical content; canonical headings remain available for generated navigation.
- [ ] No generalized template engine, semantic remapping, template-authoring UI, or extra renderer was introduced under Task 15a.
- [ ] `future-output-profiles.md` documents all eight destination profiles with correct implementation statuses; only Multipage Markdown is `implemented`.
- [ ] Phase 1 has zero SharePoint, Microsoft Graph, PnP PowerShell, or Entra dependency anywhere in `plugins/docx-to-content/`.
- [ ] CLI commands and exit codes are tested.
- [ ] Draft plan cannot be converted.
- [ ] Stale/tampered plans fail.
- [ ] Structural anchors survive cleanup line changes.
- [ ] Chunk IDs are stable under unrelated insertion.
- [ ] Canonical schemas are versioned and strict.
- [ ] Content loss and duplication checks pass.
- [ ] Media and internal links resolve in canonical and rendered outputs.
- [ ] Orphan, stale, traversal, and malformed artifact tests pass.
- [ ] WARN requires disposition.
- [ ] Atomic promotion protects prior accepted output.
- [ ] Renderer consumes canonical package only.
- [ ] Single and repeated-heading fixtures pass.
- [ ] CEIS evidence report is complete.
- [ ] Human spot checks are recorded.
- [ ] All tests and plugin validation pass.
- [ ] Deferred scope remains deferred.
- [ ] Applicable plugin/marketplace metadata is reconciled.

## Agent Completion Report Format

The implementing agent must report:

1. Tasks completed and commit hashes.
2. Files added/modified.
3. Test commands and exact pass/fail totals from the tools.
4. Canonical and render validation statuses.
5. Warnings and their dispositions.
6. Paths to analysis, confirmed plan, canonical package, rendered package, and evidence report.
7. Any deviations from the spec, with rationale.
8. Confirmation that deferred work was not implemented.

A narrative claim of success without these items is not completion.
