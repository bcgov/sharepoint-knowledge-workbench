# Resume — Phase 1 and Phase 2 complete (both merged to main); begin Phase 3 planning in a fresh session

## Planning Artifacts (read these first, in this order)

1. `docs/vision/master-initiative-plan-workstreams-and-phases.md` — the whole-spectrum master plan
   (Phase 1 through 8, plus 3.0 and 5.5), with a git/session workflow every phase follows (branch/worktree
   per phase, commit per task, exit-gate-is-merge-gate, update this file, start the next phase in a fresh
   session). Went through external adversarial review (round 3/4, `temp/plan-reviews/full-plan-review/`).
2. `docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md` — the
   approved Phase 2 design spec.
3. `docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md` — the approved,
   18-task (Task 0–17), TDD-ready Phase 2 implementation plan. Three rounds of external review behind it
   (`temp/plan-reviews/`, `temp/plan-reviews/phase2/`, `temp/plan-reviews/full-plan-review/`). **All 18
   tasks executed and merged to `main`** — see the "Phase 2 ... complete" section below for full evidence.
4. This file, below — Phase 1 and Phase 2's detailed history and verified status. Trust this over any
   other handoff summary; verify against `git log` regardless.

**Actual next action, in order:**
1. **Phase 1 is fully complete** — the `fix-grid-table-rendering-defect` PR (#2) is merged to
   `origin/main`, and the human spot-check pass (rows 1, 2, 3, 4, 6 of
   `runs/ceis-manual-v2/evidence-report.md`'s checklist) was completed as a human+agent walkthrough. Row 5
   remains N/A (genuinely no footnotes in the source). Nothing further is needed on Phase 1.
2. **Phase 2 (Canonical/Publication Contract Hardening) is fully complete and merged to `main`** — all 18
   tasks (0–17) executed via `superpowers:subagent-driven-development`, two independent final whole-branch
   reviews performed (both dispositioned, all Important/real-bug findings fixed and re-reviewed clean), the
   golden-master proof passed (real CEIS manual publication content byte-identical to the Task 0 baseline),
   full suite green at 509 passed/1 skipped, merged via PR into `origin/main`. See the "Phase 2 ... complete"
   section below for full detail.
3. **Begin Phase 3 planning in a new session** — do not continue in the same long-running session that did
   Phase 1/Phase 2 execution. Per the master plan's phase-gating discipline, Phase 3 is only planned at a
   structural level today (gated on evidence — tenant facts, pilot outcomes — that doesn't exist yet); read
   `docs/vision/master-initiative-plan-workstreams-and-phases.md`'s Phase 3 section before scoping detailed
   work.

## Authoritative Inputs (Phase 1 detail)

Before changing anything, read in full:

1. `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md` — the authoritative v3 spec (includes the v3.1 Deviation Notice, Section 14a authoring guidance, Section 14b future-output-profiles/SharePoint boundary).
2. `docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments.md` — the authoritative v3 plan for Tasks 0–16.
3. `docs/superpowers/plans/2026-07-28-docx-to-content-topic-grouping.md` — the plan for the grouped-strategy work (Tasks 1–9 of that plan), **complete and merged**.
4. `docs/implementation-baseline.md` — Task 0 reconnaissance findings (dated 2026-07-25; paths in it reference the pre-rename `sourcedocuments/`/`output/` directory names — historically accurate, not a live reference).
5. This file — the actual, verified current status. Trust this over any other handoff summary; verify against `git log` regardless.

The v1 spec/plan (`2026-07-25-docx-to-content-plugin-design.md` / `...-implementation-plan.md`, no `-ammendments` suffix) are superseded, kept only for historical comparison.

**Broader context:** this repo is Phase 1 of a larger initiative — see `docs/vision/README.md` and `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` for direction beyond Phase 1 (repository/plugin boundaries, SharePoint delivery, agents, publication, evaluation). Those documents propose future direction; they do not authorize work beyond the current approved Phase 1 plan.

## Where the work lives

Work happens directly on `main` in this repo — there is no separate worktree:

```text
plugin path:   plugins/docx-to-content/
run tests:     cd plugins/docx-to-content && python3 -m pytest tests/ -q
```

Two commits landed this session on top of the prior session's merge (`99faab2`):
- `b325ae6` — mixed-level logical-root detection for the grouped topic strategy (topic_grouping.py's `classify_headings`, `confirmed_topic_roots` persisted on the plan, `.gitignore` hygiene: `.superpowers/`/`.pytest_cache/` at every depth, two tracked SDD reports preserved to `docs/reports/`).
- `40bf069` — general media-disposition mechanism (`media_disposition.py`, `plans.apply_media_decision`, `ConversionPlan.media_decisions`, `validate_canonical._check_media_decisions`) plus two real-document convert fixes (glued-image heading-identity normalization; preamble-aware content-loss comparison).

Check `git log origin/main..main --oneline` before assuming remote state matches local — confirm with the user before pushing.

## Actual Current Status (verified, not reported)

**Tasks 0–16 and Task 17-topic-grouping are complete** (see prior session detail in git history; `main` up through `90a6033`/merge `99faab2` documents itself).

**Task 18 (real CEIS pilot cutover) is now complete**, run end-to-end through the plugin CLI against the real document (`intake/CEIS MANUAL - working version.docx`):

1. **`analyze` rerun** found a real crash: `topic_grouping.compute_topic_boundaries` hardcoded "every level-1 heading starts a topic," but the real document authors its first 14 top-level sections as Heading 2 and the remaining 11 as Heading 1 (verified against raw docx XML — standard Word styles, no pandoc bug, a genuine source-authoring inconsistency; every section's children are consistently Heading 3, never a genuine Heading 2 child beneath a Heading 1). Fixed via `classify_headings`'s dynamic root-level tracking (`root`/`promoted-root`/`ambiguous-root`/`internal-heading` classification), with the confirmed root set persisted on the plan (`confirmed_topic_roots`) so `convert` consumes it rather than recomputing the heuristic.
2. **Real `proposed_topics` reviewed**: exactly 25 topics (14 at source level 2, 11 promoted from level 1), `MIXED_LOGICAL_ROOT_LEVELS`/`PROMOTED_TOPIC_ROOT` warnings surfaced and reviewed, zero ambiguous roots (the real document's inconsistency is one-directional).
3. **`strategy: "grouped"` set** on the draft plan (a process bug during this session set it only after an initial confirm defaulted to `"chunked"` — caught before proceeding, plan rebuilt with `strategy=grouped` preserving the already-reviewed `confirmed_topic_roots`/`media_decisions`, then reconfirmed).
4. **Preamble/image findings re-verified**: title ("Civil Electronic Information System")/subtitle ("SEARCHABLE GUIDE")/version ("Version 1.9") → publication metadata; `Ctrl+F` instruction → omitted; Word TOC → raw dump detected, removed and regenerated from the publication map; `image1.png` → directly inspected (not inferred from dimensions), found to be a stale (2021-02-11) Internet Explorer browser-window screenshot of the CEIS-in-Motion portal landing page (OS taskbar, tab bar, address bar, active Find-toolbar search state all visible; the CEIS wordmark is embedded within it, not a standalone branding asset) — classified `obsolete-source-layout-artifact`, dispositioned `omit-as-reviewed-artifact` (not cropped — cropping would have manufactured an unapproved derived branding asset). This is the first real use of the new general media-disposition mechanism (see below).
5. **Explicit human plan confirmation obtained** before any `confirm`/`convert`/`render` ran (spec Section 7.1/7.2 gate honored).
6. **`confirm` → `convert` → `render` run against the real document**: `convert` validation status **PASS**, 159 structural anchors retained for lineage, 25 topic chunks, every anchor assigned to exactly one topic, `publication-map.json` present (25 entries, contiguous order 0–24). `render` validation status **PASS**, 25 pages, `index.md` in publication-map order, no raw TOC survived, `image1.png` confirmed absent from both canonical and rendered media.
7. Output lives at `runs/ceis-manual-v2/` (canonical-content + render/rendered-output). **Decision (user-confirmed): kept side by side with the old pre-plugin `runs/ceis-manual/`, not replaced** — the old directory is retained deliberately as historical evidence of the bare-pandoc problem the plugin was built to solve; `runs/ceis-manual-v2/` is the current, authoritative, plugin-produced output. `CLAUDE.md`'s "Conversion workflow" section has been updated to describe both and say so explicitly.

**Two real, generalizable defects were found and fixed while running the real document for the first time** (every prior test used synthetic fixtures that happened not to exercise these paths):
- Heading-identity divergence for a heading with an image glued directly onto its own line: `analyze_structure._normalize_heading_text` now also applies `pandoc_fixes.images.fix_glued_images` (previously only `strip_whole_heading_emphasis`, Task 17's fix for a different divergence of the same class), matching what convert's cleanup pipeline actually does before reconciliation.
- Content-loss/duplication false positive on any document with non-empty preamble content: `convert.py`'s `_run_conversion_pipeline` now compares staged chunk content against **preamble-stripped** cleaned text (`sliced_document.preamble` is never copied into any chunk by design — chunking.py — but the validation comparison was using the full cleaned document, which every synthetic test fixture's empty preamble had masked).

**General media-disposition mechanism added** (`scripts/media_disposition.py`, `plans.apply_media_decision`, `ConversionPlan.media_decisions`, `validate_canonical._check_media_decisions`), scoped deliberately to preamble media only (the one concrete integration point that exists today — `SlicedDocument.preamble`, never copied into canonical output). `analyze` proposes objective-signal-only records (`requires-human-review`/`requires-human-decision`) for every preamble media reference; a human confirms the real classification/disposition via `plans.apply_media_decision` before `confirm`; a still-pending record blocks conversion (`unclassified_media`), a reviewed omission does not. **Full body-content media classification** (screenshots inside procedures, decorative-vs-meaningful, derived-asset authorization workflow) was explicitly scoped OUT as future work — not attempted this session.

Full plugin suite as of this session's last commit (`40bf069`): **448 passed, 1 skipped**.

### What is NOT done yet — explicitly withheld pending further direction

- **General (non-preamble) media classification/disposition** — screenshots inside procedures, decorative-vs-meaningful classification, derived-asset authorization — is future work per the media-disposition mechanism's deliberately narrow Task 18 scope.
- **Nothing has been pushed to `origin`** — `main` is ahead of `origin/main` (check exact count via `git log origin/main..main --oneline`); confirm with the user before pushing.

## Evidence-report assembly, a real defect found AND fixed, real output regenerated (this session)

Assembled `runs/ceis-manual-v2/evidence-report.md` (spec Section 10's required Task 17/18
deliverable, never previously produced) by reconciling `manifest.json`/`validation.json`/
`renderer-validation.json`/`analysis-report.json`/chunk metadata against each other. This
surfaced a real defect, not just a documentation gap — and it has since been **fixed, verified,
and the real CEIS output regenerated**, not just described:

**The defect:** `image239.emf` (body content in `PROTECTION ORDERS`, not preamble) was absent
from both promoted canonical and rendered media, with a dead absolute-path reference baked into
both promoted outputs, and **both validators reported PASS with zero issues** despite it.

**Root cause:** the image's alt text contains a markdown-escaped `]` (from Word content quoting
"[Order Terminating a Protection Order]"). Four copies of the same naive regex —
`!\[[^\]]*\]\(...\)` — silently stop matching alt text at that literal `]` byte, so the reference
was never recognized as media at all, in: `convert.py`'s `_ABS_MEDIA_REF`, `package.py`'s
`_IMAGE_REF`, and **two** places in `validate_canonical.py` (`_IMAGE_REF_FOR_COMPARISON` and,
critically, `_IMAGE_REF` inside `_check_media_references` — the actual broken-link validator,
which never saw the reference to check it). `renderers/validate_rendered.py` carried the
identical bug on the render side.

**Fix:** all four sites now use `(?:[^\]\\]|\\.)*` for alt/link text — correctly treats `\]` as
an escaped literal rather than a terminator. A regression test was added first and confirmed
failing against the old code, then passing after the fix:
`tests/unit/test_package.py::test_alt_text_with_escaped_brackets_still_recognized_as_media_ref`.
Full suite: **449 passed, 1 skipped** (up from 448 — the new test executes, nothing else broke).

**Regeneration:** `convert` and `render` were rerun against the *same* confirmed plan (source and
plan unchanged — only pipeline code was fixed) via:
```bash
python -m scripts.cli convert --source "../../intake/CEIS MANUAL - working version.docx" --plan ../../temp/ceis-manual-analysis/conversion-plan.confirmed.json --output ../../runs/ceis-manual-v2
python -m scripts.cli render --canonical ../../runs/ceis-manual-v2/canonical-content --renderer multipage-markdown --output ../../runs/ceis-manual-v2/render
```
Both PASS. `runs/ceis-manual-v2/` now has **319/319** media files on both the canonical and
rendered sides (up from 318/318), `image239.png` present and correctly referenced as
`../media/image239.png` in both the canonical chunk and the rendered page — confirmed by direct
file inspection, not validator status alone. 159/159 heading anchors, 25/25 topic chunks
unchanged (the fix only affected media handling, not chunking/anchoring).

**Process gap, flagged for the record:** this rerun reused the already-approved confirmed plan
from Task 18 without explicitly telling the user that's what was happening — no new
chunking/strategy questions were asked because none were needed (nothing about topic boundaries
changed), but silently reusing an old approval rather than stating "reusing plan `<id>`, no
chunking changes, only the media fix is being validated" is a real gap against this project's
approval-gate conventions, caught by the user after the fact, not surfaced proactively. See the
governance note in `runs/ceis-manual-v2/evidence-report.md`'s header for the full note. Going
forward: any time a prior confirmed plan is reused rather than re-derived, say so explicitly
before running `convert`/`render` again, even when re-analysis is genuinely unnecessary.

**Update: also fixed.** Three more files carried the identical `[^\]]*` bug
(`pandoc_validate.py`'s `_IMAGE_LINK`/`_HEADING_WITH_IMAGE`, `analyze_structure.py`'s
`_IMAGE_REF`/`_LOCAL_LINK`/`_IMAGE_REFERENCE`, `pandoc_fixes/images.py`'s `_IMAGE`). Initially
left unfixed as "out of scope," which was a self-evolution-policy violation (Fix Forward, Never
Skip) caught by the user — fixed instead of deferred. Full suite still 449/1. Rerunning `analyze`
against the real document confirmed the fix: `image_reference_count` went from 341 → 342 (the
same `image239` reference now correctly recognized at analysis time too), all other counts
(159 headings, 185 local links, 25 topics) unchanged.

**Update (this session, resumed): completed.** The human spot-check checklist has now been
filled in — see `runs/ceis-manual-v2/evidence-report.md`'s "Human Spot-Check Checklist" section.
All applicable rows (1, 2, 3, 4, 6) were reviewed by a human (in-chat file review plus an
independent GitHub preview check for Row 3's inline images); Row 5 remains genuinely N/A (zero
footnotes in the source). **Phase 1's human sign-off precondition is satisfied; nothing further
is outstanding on Phase 1.**

## Table-detection/rendering defect found and fixed (later session, during human spot-check attempt)

While starting the human spot-check pass (row 6, viewing the last topic page,
`ceis-support-faq--218dfe1f.md`), a real defect surfaced: its rendered table had a spurious
`| --- | --- |` separator row injected after almost every data row, corrupting otherwise-valid
pandoc grid-table markup.

**Root cause:** `pandoc_fixes/tables.py`'s `fix_malformed_tables` was designed/tested only against
GFM-style pipe tables. Pandoc emits **grid tables** (bounded by `+---+`/`+===+` lines) for
complex/merged-cell Word tables — a format the function never recognized. Its `_PIPE_ROW` regex
matches every pipe-delimited row, including grid-table data rows; since the `+---+` boundary lines
reset internal `in_table` state, every content row looked like a fresh headerless pipe table,
triggering a spurious separator insertion after each one. A second, related defect shared the same
blind spot: `analyze_structure.py`'s `compute_statistics` only counted GFM-style separators toward
`table_count`, so this document (which has 3 grid tables, zero pipe tables) was reported as
`table_count: 0` — which had incorrectly justified marking spot-check row 2 as N/A.

**Fix:** `fix_malformed_tables` now recognizes grid-table boundary lines and passes grid-table
blocks through untouched (they already carry a valid `+===+` header separator). `compute_statistics`
now also counts grid-table header separators toward `table_count`. Regression tests added first,
confirmed failing against the old code, then passing after the fix:
`tests/unit/test_tables.py::TestFixMalformedTables::test_leaves_grid_table_untouched` and
`tests/unit/test_analyze_structure.py::test_table_count_detects_pandoc_grid_tables`. Full suite:
**451 passed, 1 skipped** (up from 449).

**Regeneration:** `analyze`, `convert`, and `render` rerun against the real document, reusing the
same already-approved `conversion-plan.confirmed.json` (stated explicitly before rerunning, per
this project's prior process-gap lesson — no new chunking/strategy/media questions were needed,
since only table-handling code changed). Both `convert` and `render`: **PASS**. Media (319/319) and
chunk/page counts (25/25) unchanged on both sides — the fix affected only table markup.
`analyze`'s `table_count` now correctly reports `3` (was `0`); other statistics (159 headings, 185
local links, 342 image references, 25 topics) unchanged. `evidence-report.md`'s checklist and
"Table-Detection and Rendering Defect" section updated with this finding; row 2 is no longer
marked N/A and now requires an actual human look, same as the other unresolved rows.

## Orchestrate-conversion skill (added this session, after Task 18)

Deferred work from before Task 18 is now done: `plugins/docx-to-content/skills/orchestrate-conversion/SKILL.md`
is a pure-instruction (no new code) skill that sequences the same
`analyze`/`confirm`/`convert`/`render` CLI calls the other three skills
already document, with the mandatory human plan-review and media-decision
gates made explicit (pause-and-summarize after `analyze`, inline
image-review + `plans.apply_media_decision` for unclassified preamble
media, loop until explicit approval before `confirm`, stop on any FAIL or
undispositioned WARN at `convert`/`render`). It has not yet had a real
dry run against an actual document in this session — do that before
relying on it for a second real conversion. No new tests were added since
no new code was written; full suite still 448 passed, 1 skipped
(unchanged, verified after adding the skill).

## Phase 2 (Canonical/Publication Contract Hardening) — complete, merged to main

All 18 tasks (0-17) of `docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md`
are complete, executed via `superpowers:subagent-driven-development` (fresh implementer + fresh reviewer
per task), and merged to `main` via PR. Two independent final whole-branch reviews were performed (one
found only a stale docstring; a second, more thorough review found one genuine cross-task integration bug
in `CanonicalPackage.load()`'s non-grouped branch — a malformed `publication-map.json` could escape the
module's documented `CanonicalPackageError` contract — plus stale contract-doc drift in
`publication-map-contract.md`/`canonical-contract.md`). All findings were fixed (a guard + regression test
for the bug, doc corrections for the drift) and independently re-reviewed clean before merge.

**Full suite: 509 passed, 1 skipped** (`python3 -m pytest tests/ -q` from `plugins/docx-to-content/`). The
1 skip is `tests/unit/test_package_load.py:189` ("small_single.docx fixture has no media references to
tamper with") — a pre-existing, unrelated fixture limitation, not Task 16's golden-master test.

**Task 16's golden-master test PASSED, not skipped** — this is the actual completion evidence, per Task
17's own explicit warning not to conflate the aggregate pass count with this specific proof:
```
tests/integration/test_golden_master.py::test_index_is_byte_identical_to_golden_master PASSED
tests/integration/test_golden_master.py::test_pages_are_file_set_identical_and_byte_identical_to_golden_master PASSED
tests/integration/test_golden_master.py::test_media_is_file_set_identical_and_byte_identical_to_golden_master PASSED
tests/integration/test_golden_master.py::test_control_metadata_is_semantically_correct_not_byte_identical PASSED
```
This proves the real CEIS manual's published output (`index.md`, all 25 `pages/**`, all 319 `media/**`
files) is byte-identical to the Task 0 pre-Phase-2 baseline — Phase 2 changed only internal contract
metadata, never a single byte of the actual publication content.

### Pre-existing tests whose assertions intentionally changed (Tasks 1, 2, 4)

- **Task 1** (`package_identity` double-prefix fix) — `tests/unit/test_package.py::test_grouped_package_identity_is_not_double_prefixed`
  is a new test (not a changed pre-existing one) asserting `package_identity == plan_id` and does not
  start with `sha256:sha256:`.
- **Task 2** (`source_manifest_hash` → `source_content_sha256` field rename):
  - `tests/contract/test_contracts.py::test_render_result_uses_source_content_sha256_not_manifest_hash` — new test for the renamed field.
  - `tests/unit/test_multipage_markdown.py::test_single_chunk_package_renders_one_page_and_index` — assertion changed from `result.source_manifest_hash == FAKE_SHA` to `result.source_content_sha256 == FAKE_SHA`.
  - `tests/unit/test_renderer_protocol.py` (`_ListChunksTestRenderer` fixture helper) — constructor kwarg renamed `source_manifest_hash=` → `source_content_sha256=`.
  - `tests/unit/test_validate_rendered.py::test_manifest_hash_mismatch_detected` — assertion changed from checking issue code `manifest_hash_mismatch` to `source_content_stale` (this test's name is stale/cosmetic per Task 2's own deferred-minor note; the assertion body is correct).
- **Task 4** (`chunk_id` now holds a real chunk ID, not a path; `parent_topic_id` removed):
  - `tests/unit/test_multipage_markdown.py` (`_build_synthetic_grouped_package` fixture helper) — `chunk_id="chunks/alpha--22222222.md"` → `chunk_id="alpha--22222222"` (and same for `beta--11111111`).
  - `tests/unit/test_publication_map.py::test_publication_map_supports_parent_topic_id_hierarchy` — no longer passes `parent_topic_ids=` to `build_publication_map`; now asserts `"parent_topic_id" not in as_dict["entries"][0]` instead of asserting the field is `None`.

Every other pre-existing test not listed above still passes unchanged.

## Next action on resume — this is the actual remaining work

1. **Phase 1 is done.** The human spot-check pass (the item that was blocking Phase 1 formal
   sign-off and Phase 2's Task 0 precondition) was completed — see
   `runs/ceis-manual-v2/evidence-report.md`'s checklist. Nothing further needed here.
2. **Phase 2 is done and merged to `main`.** Nothing further needed here — see the section above.
3. **Begin Phase 3 planning** in a fresh session (see "Actual next action" at the top of this file). Do it
   in its own branch/worktree, per the master plan's git/session workflow, not directly on `main`.
4. Do a real (or fixture) dry run of `orchestrate-conversion` end-to-end to validate the instructions
   actually hold up in practice, if not already done.
5. If/when broader (non-preamble) media classification becomes a real need on a future document, design it
   as its own scoped task — the vocabularies (`CLASSIFICATIONS`/`DISPOSITIONS` in
   `scripts/media_disposition.py`) already sketch the fuller taxonomy discussed this session, but nothing
   beyond preamble media is implemented.

## Efficiency notes for continuing this session or a fresh one

- Work directly on `main` — there is no worktree to re-enter. The `fix-grid-table-rendering-defect`
  branch (PR #2) is merged and deleted (local + remote); it no longer needs tracking. If isolation is
  wanted for further work (e.g. Phase 2), create a fresh worktree via `superpowers:using-git-worktrees`
  rather than assuming an old one still exists.
- This repo's `CLAUDE.md`: use the cheapest viable sub-agent model per dispatch, and don't spawn a sub-agent when the job doesn't need one. This entire Task 18 session (mixed-level root detection, media-disposition mechanism, both real-document convert fixes) was done directly via Read/Edit/Bash, not dispatched sub-agents — the work was well-understood, self-verifiable via the test suite, and the human (via chat) was the actual source of the classification decisions the pipeline itself can't infer (e.g. image1.png's disposition required looking at the actual image, not just objective signals).
- `origin` is `https://github.com/richfrem/manual-conversion-poc.git`. `main` is the default branch on GitHub.
- A `temp/bundles/manifest.json` exists for bundling key files via the `context-bundler` skill into a single `.md` for external review — keep it updated as files change if that hand-off is still wanted.
- The confirmed plan used for the real Task 18 run lives at `temp/ceis-manual-analysis/conversion-plan.confirmed.json` (and its draft counterpart) — `temp/` is gitignored (scratch), so this is not a durable artifact; re-run `analyze`/`confirm` fresh if resuming after `temp/` has been cleared.
