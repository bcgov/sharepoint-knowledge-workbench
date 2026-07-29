# CEIS Manual — Phase 1 Fidelity Evidence Report

Produced against `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md`
Section 10 ("Fidelity Evidence"), for the Task 17/18 real-document acceptance run. This report
was assembled retroactively from artifacts already on disk after the pipeline run (Task 18);
it was not generated as an automatic pipeline output. Automated fields below were read directly
from the run's JSON artifacts and re-verified by direct inspection (`grep`/counts), not
transcribed from memory. The human spot-check section (last) was **not** completed by an
automated process — per this section's own rule ("human review records observed facts only"),
it requires a human to actually look at the rendered output before those rows can be signed off.

**Update:** assembling this report's media reconciliation surfaced a real defect (`image239`,
see the original "Open Items" entry preserved below for the full diagnosis). The root cause — a
naive alt-text regex (`[^\]]*`) that silently stops matching when alt text contains a
markdown-escaped `]` — was found in **four** separate places in the plugin
(`package.py`, `convert.py`, `validate_canonical.py` twice) and fixed in all four, with a new
regression test (`tests/unit/test_package.py::test_alt_text_with_escaped_brackets_still_recognized_as_media_ref`).
`convert`/`render` were rerun against the same confirmed plan (source and plan unchanged, only
pipeline code fixed) and `runs/ceis-manual-v2/` was regenerated. All counts and statuses below
reflect the **regenerated, fixed** output, not the original Task 18 run.

**Governance note on plan reuse:** this validation rerun reused previously approved conversion
plan `sha256:041e1186682322ba11d64abdafbc547dfb793083b9c22a6663aad3008a53d9d3` (the same
confirmed plan from the original Task 18 run, `temp/ceis-manual-analysis/conversion-plan.confirmed.json`).
No changes were made to chunking strategy (`grouped`), topic grouping (25 topics),
`confirmed_topic_roots`, heading boundaries, or plan-generation logic — the rerun was performed
solely to validate the `image239` media-handling defect correction, and this was confirmed
before rerunning (same `plan_id` before and after; 159/159 anchors and 25/25 topics unchanged).
This was not surfaced to the user as an explicit reuse decision at the time it happened, which
in hindsight it should have been, given the project's approval-gate conventions — silently
reusing an old approved plan without saying so plainly is a process gap even when the reuse
itself was technically sound. The full test suite was
449 passed/1 skipped after the fix (up from 448 passed/1 skipped, confirming the new regression
test executes and passes, not just that nothing broke).

## Source Fingerprint and Tool Versions

| Field | Value |
|---|---|
| Source file | `intake/CEIS MANUAL - working version.docx` |
| Source SHA-256 | `c804b65559ff8ad8d3a8dd66f01067ab468191a3487384514cdd1614a9f9178c` |
| Source size | 92,282,471 bytes |
| Confirmed plan ID | `sha256:041e1186682322ba11d64abdafbc547dfb793083b9c22a6663aad3008a53d9d3` |
| Confirmed by / at | `user-or-supervising-agent` / `2026-07-28T15:20:40Z` |
| pandoc | 3.8.3 |
| LibreOffice (`soffice`, used for `.emf`→`.png`) | 26.2.5.2 |
| Python | 3.13.4 |
| Plugin version | `docx-to-content` 0.1.0 |
| Repo commit at time of this report | `1b12eff34e0dfd9b27e248962040463197986e3a` |

## Source Heading Counts by Level

From `temp/ceis-manual-analysis/analysis-report.json`'s `headings` block (source structural scan):

| Level | Count |
|---|---|
| 1 | 11 |
| 2 | 14 |
| 3 | 133 |
| 4 | 1 |
| **Total** | **159** |

`repeated_heading_texts`: 0 — no duplicate heading text anywhere in the source document.

Per Task 18's real-document finding: the source is internally inconsistent about which level
starts a top-level section (14 sections open at Heading 2, 11 at Heading 1, with every section's
children consistently Heading 3) — a genuine source-authoring inconsistency, not a pandoc
artifact. This is handled by `classify_headings`'s dynamic root-level tracking; see
`start-here.md` for detail.

## Canonical Heading Counts by Level

Computed by summing `heading_level` across every chunk's `anchors` list in
`runs/ceis-manual-v2/canonical-content/chunks/*.meta.json`:

| Level | Count |
|---|---|
| 1 | 11 |
| 2 | 14 |
| 3 | 133 |
| 4 | 1 |
| **Total** | **159** |

**Result: exact match to source, level-by-level.** Every one of the 159 source headings is
retained as an individually addressable structural anchor in the canonical package (confirmed
by `manifest.json`'s statement that all 159 anchors are distributed across 25 topic chunks, one
anchor per original heading, no anchor duplicated or dropped).

## Source and Canonical/Rendered Media Counts

| Stage | Count | Source |
|---|---|---|
| Source (raw pandoc-extracted media, includes legacy `.emf`) | 320 | `find temp/ceis-manual-analysis/raw/media -type f \| wc -l` |
| ...of which legacy `.emf` | 37 | `find ... -name '*.emf' \| wc -l` |
| Source image references detected in text | 341 | `analysis-report.json.statistics.image_reference_count` |
| Canonical media files (`manifest.json.media`) | **319** (fixed; was 318) | counted from manifest |
| Rendered media files (`render/rendered-output/media/`) | **319** (fixed; was 318) | `find ... -type f \| wc -l` |

Reconciliation: 320 raw extracted files → 319 canonical/rendered files. The 1-file gap:

- **`image1.png`** — accounted for and correct: the sole preamble media reference, reviewed by a
  human, classified `obsolete-source-layout-artifact`, dispositioned `omit-as-reviewed-artifact`,
  confirmed absent from both canonical and rendered media.

`image239.emf`/`image239.png` — **previously a real defect, now fixed and reconverted.** It is
body content in the `PROTECTION ORDERS` section (not preamble; no disposition mechanism applies,
nor should one — this was never meant to be excluded). After the regex fix (see report header)
and a rerun of `convert`/`render`, `image239.png` is present in both `canonical-content/media/`
and `render/rendered-output/media/`, and both the canonical chunk and rendered page reference it
correctly as `../media/image239.png` — confirmed by direct inspection, not inferred from
validator status alone.

All legacy `.emf` files convert to `.png` in place (37 `.emf` sources → 0 `.emf` files in
canonical/rendered output; no format survives as `.emf` past `convert`), including `image239.emf`
after the fix.

## Source TOC Evidence and Reconciliation

- Source: a Word-generated Table of Contents field is present (`generated_toc_entries_detected:
  159` in `analysis-report.json`, and `defect_signals.raw_toc_detected: true`).
- Canonical/rendered: `grep -il "table of contents"` across all canonical chunks, all rendered
  pages, and the rendered index returns **zero matches** — the raw TOC dump was removed, not
  carried through.
- Replacement: `publication-map.json` (25 entries, contiguous `order` 0–24) drives
  `render/rendered-output/index.md`'s navigation — a generated index from validated topic
  chunks, not a raw pandoc TOC dump.

## Chunk Count and Structural Anchors

- `manifest.json.chunk_count`: **25** (grouped-strategy topic chunks; `strategy: "grouped"`).
- Every chunk's `source_heading_path`/`source_order` is present and matches `publication-map.json`
  order.
- Total structural anchors across all 25 chunks' `anchors` lists: **159** — matches the source
  heading total exactly (see above).

## Aggregate Normalized Text Comparison

- `canonical-content/validation.json`: `"status": "PASS"`, `"issues": []` — the canonical
  validator's content-loss/duplication comparison (which compares staged chunk content against
  **preamble-stripped** cleaned source text, per the Task 18 fix to `convert.py`'s
  `_run_conversion_pipeline`) reported no discrepancies.
- No separate standalone aggregate-diff artifact exists outside `validation.json`; the PASS
  status *is* the aggregate comparison result the validator computed.

## Broken-Link Counts (Canonical and Rendered)

- Canonical: summed `local_links` across all chunk metadata = **0**. Source `local_link_count`
  was 185 — these were Word-internal TOC/bookmark navigation links belonging to the raw TOC field
  that was removed (see TOC reconciliation above); their removal is consistent with, not evidence
  against, correct behavior, but this report does not independently re-derive that every one of
  the 185 was TOC-only. Flagged below as an open item for a closer look if ever revisited.
- Canonical: summed `media_refs` across all chunk metadata (re-derived after the fix) includes
  `image239.png`'s reference, which was previously invisible to this same count (the extraction
  regex that builds `media_refs` is the one that was fixed) — 319 unique media files now back
  every in-text reference, with no unresolved reference remaining.
- `render/rendered-output/renderer-validation.json`: `"status": "PASS"`, `"issues": []` — the
  render validator (which checks index/page link integrity, per `render-content/SKILL.md`)
  reported zero broken links.
- `render-result.json`: `"status": "PASS"`, `"errors": []`, `"warnings": []`.

## Warnings and Dispositions

- Canonical validation: no warnings (`issues: []`, straight PASS, not a dispositioned WARN).
- Render validation: no warnings (`issues: []`, `warnings: []`).
- Analysis-time warnings (`analysis_warnings` on the plan, from Task 18):
  `MIXED_LOGICAL_ROOT_LEVELS` and `PROMOTED_TOPIC_ROOT` — both reviewed by a human during plan
  confirmation (11 topics promoted from Heading 1 to logical root status, 0 ambiguous roots);
  resolved via `confirmed_topic_roots` (25 entries) recorded on the confirmed plan, not left
  outstanding.
- Media decision: `image1.png` — human-confirmed classification/disposition recorded on the
  confirmed plan (see media counts section above); not left pending
  (`decision_authority: "human-confirmed"`, not `"pending"`).

## Human Spot-Check Checklist (Spec Section 10)

**Not yet completed.** Per the spec, "human review records observed facts only" — these rows
require a person to actually open the rendered output and look, not an automated inference. The
table below identifies *where* to look (so the check is fast), but every "Observed" cell is
blank pending that review.

| # | Category | Where to look | Observed (fill in) |
|---|---|---|---|
| 1 | Title/front matter | `render/rendered-output/index.md` (title/subtitle/version metadata) | |
| 2 | One table-heavy section | **N/A — source has zero tables** (`analysis-report.json.statistics.table_count: 0`); no table-heavy section exists in this document to check. |  |
| 3 | One image-heavy section | e.g. `render/rendered-output/pages/ceis-training--*.md` or another topic page with many `image_refs` — inspect a chunk `.meta.json` for the highest `media_refs` count to pick the best candidate | |
| 4 | One deep heading hierarchy | any topic chunk descending to Heading 4 (only 1 exists source-wide — locate via the level-4 anchor in the canonical chunk metadata) | |
| 5 | One footnote/cross-reference case | **N/A — source has zero footnotes** (`footnote_definition_count: 0`, `footnote_reference_count: 0`); no such case exists in this document to check. |  |
| 6 | Beginning, middle, end of manual | `pages/data-capture-standards--*.md` (topic 0), a mid-list topic (e.g. `pages/orders--*.md`, topic 12), `pages/ceis-support-faq--*.md` (topic 24, last) | |

Rows 2 and 5 are genuinely inapplicable to this source document (verified from the objective
statistics above, not assumed) — they should be marked N/A with that justification when this
checklist is signed off, not left silently blank forever. Rows 1, 3, 4, 6 require an actual human
look before this report can be considered complete.

## Final Acceptance Checklist (Plan Section, Walked Against Real Evidence)

Source: `docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments.md`'s
"Final Acceptance Checklist". Each item below is marked against actual evidence gathered for
this report, not against task narrative.

| Item | Status | Evidence |
|---|---|---|
| Repository baseline is factual and complete | ✅ | Task 0 recon (`docs/implementation-baseline.md`), superseded-path caveat noted in `start-here.md` |
| New cleanup suite passes (built from scratch, not relocated) | ✅ | `plugins/docx-to-content/scripts/pandoc_fixes/`, 448 passed/1 skipped |
| Manual-topic template, authoring guide, supported Markdown profile, generated-elements doc exist and pass contract tests | ✅ | `references/content-authoring-guide.md`, `references/generated-elements.md`, `tests/contract/test_content_authoring_guidance.py` present and passing |
| Word-generated TOC removed from canonical content; headings remain available for generated nav | ✅ | "no raw TOC dump" grep above; `publication-map.json` drives index |
| No generalized template engine/semantic remapping/authoring UI/extra renderer introduced under Task 15a | ✅ (not independently re-audited this pass; consistent with single-renderer registry found) | `renderers/protocol.py` registry contains only `multipage_markdown` |
| `future-output-profiles.md` documents all eight profiles; only Multipage Markdown `implemented` | ✅ | `references/future-output-profiles.md` exists, contract-tested |
| Zero SharePoint/Graph/PnP/Entra dependency anywhere in `plugins/docx-to-content/` | ✅ | enforced by `tests/contract/test_future_output_profiles.py::TestNoSharePointReferenceInPluginSource`, passing |
| CLI commands and exit codes are tested | ✅ | `tests/contract/`, `tests/integration/` cover analyze/confirm/convert/render exit codes |
| Draft plan cannot be converted | ✅ | `convert` requires `confirmation.status == "confirmed"`, tested |
| Stale/tampered plans fail | ✅ | `plans.verify_plan_against_source`/`verify_plan_integrity`, tested |
| Structural anchors survive cleanup line changes | ✅ | 159/159 anchor match, this report |
| Chunk IDs are stable under unrelated insertion | ✅ (not re-verified this pass; covered by `repeated-headings` fixture per Task 16) | existing test suite |
| Canonical schemas are versioned and strict | ✅ | `manifest.json.schema_version: "1.0"`, `contracts.py` strict `from_dict` |
| Content loss and duplication checks pass | ✅ | `canonical-content/validation.json` PASS (re-verified after fix and rerun) |
| **Media and internal links resolve in canonical and rendered outputs** | ✅ **Fixed** | `image239.png` reference repaired (see media-count section); root-cause regex fixed in 4 locations with a regression test; `convert`/`render` rerun; both validators PASS and the fix was independently confirmed by direct file inspection, not validator status alone |
| Orphan, stale, traversal, and malformed artifact tests pass | ✅ | 449 passed/1 skipped |
| WARN requires disposition | ✅ | media-decision mechanism enforces this for preamble media; no undispositioned WARN occurred on this run |
| Atomic promotion protects prior accepted output | ✅ | staging-then-promote pattern in `convert.py`/`validate_rendered.py` |
| Renderer consumes canonical package only | ✅ | `render(self, package, output_dir)` signature, per `render-content/SKILL.md` |
| Single and repeated-heading fixtures pass | ✅ (existing suite) | 449 passed/1 skipped |
| CEIS evidence report is complete | ⚠️ **Partial** | media defect now resolved and documented, but the human spot-check rows are still unresolved |
| Human spot checks are recorded | ❌ | not yet done — see checklist above; requires a human, not automatable |
| All tests and plugin validation pass | ✅ | 449 passed/1 skipped; canonical/render validation on the regenerated output independently confirmed correct by direct file inspection (media files present, references resolve), not just validator self-report |
| Deferred scope remains deferred | ✅ | general (non-preamble) media classification confirmed still not implemented |
| Applicable plugin/marketplace metadata is reconciled | not verified this pass | out of scope for this report; check separately before closeout |

**Net result: one item remains outstanding — human spot checks.** The `image239` media defect
that previously failed this checklist has been fixed at the root cause (not worked around), with
a regression test guarding against recurrence, and the real CEIS output regenerated and
re-verified. The only checklist item still open is the human spot-check pass, which by the
spec's own rule cannot be completed by an automated process.

## Defect Found and Fixed During This Report's Assembly

**Original finding (now resolved):** `image239.emf` (referenced in the `PROTECTION ORDERS` topic,
source text: "NOTE — When Protection Orders are Varied or Cancelled...") did not survive the
original Task 18 conversion.

- The file was absent from both `canonical-content/media/` and `render/rendered-output/media/`.
- Both the promoted canonical chunk and the promoted rendered page contained the markdown image
  reference with an **absolute, machine-local path** into a deleted staging directory rather than
  a relative path into the promoted `media/` folder — never rewritten.
- **Both `canonical-content/validation.json` and `render/rendered-output/renderer-validation.json`
  reported `"status": "PASS"` with `"issues": []`** despite this — a validator gap, not only a
  conversion miss.

**Root cause, identified:** the image's alt text ("...Form 14 `\[Order Terminating a Protection
Order\]`...") contains a markdown-escaped `]` byte. Four separate copies of the same naive regex
— `!\[[^\]]*\]\(...\)` — silently stop matching alt text at that literal `]`, so the whole
reference was never recognized as media *at all*, in:

1. `convert.py`'s `_ABS_MEDIA_REF` (absolute-path relativization — never ran on this ref)
2. `package.py`'s `_IMAGE_REF` (media copy/rewrite — never copied or rewrote this ref)
3. `validate_canonical.py`'s `_IMAGE_REF_FOR_COMPARISON` (content-loss comparison — irrelevant
   here since the text wasn't lost, only mis-parsed)
4. `validate_canonical.py`'s `_IMAGE_REF` in `_check_media_references` — **this is the actual
   broken-link validator, and it never saw the reference to check it**

`renderers/validate_rendered.py`'s `_IMAGE_REF`/`_LINK_REF` carried the identical bug on the
render side and were fixed alongside the others as the same class of defect, though the specific
`image239` case surfaced through the canonical side first.

**Fix applied:** all four (in `package.py`, `convert.py`, `validate_canonical.py`, and
`renderers/validate_rendered.py`) now use `(?:[^\]\\]|\\.)*` for the alt/link-text portion —
matches any character that isn't an unescaped `]`, correctly treating `\]` as an escaped literal
rather than a terminator. A regression test,
`tests/unit/test_package.py::test_alt_text_with_escaped_brackets_still_recognized_as_media_ref`,
reproduces the exact failure mode (confirmed failing before the fix, passing after) so this
cannot silently regress. `convert`/`render` were rerun against the same confirmed plan (source
and plan unchanged) and the real output was regenerated — `image239.png` now correctly present
and referenced in both canonical and rendered output, confirmed by direct file inspection.

**Not fixed, and out of scope for this pass:** three other files contain structurally similar
`!\[[^\]]*\]\(...\)` / `[^\]]*` patterns that were not touched here because they are not
implicated in this specific defect (analysis-time detection and glued-image cleanup, not
media copy/validation): `pandoc_validate.py` (`_IMAGE_LINK`, `_HEADING_WITH_IMAGE`),
`analyze_structure.py` (`_IMAGE_REF`, `_IMAGE_REFERENCE`), `pandoc_fixes/images.py` (`_IMAGE`).
Whether any of these has a live bug of the same class is unverified — worth a dedicated pass if
a future document surfaces one, rather than opportunistic changes here.

## Remaining Open Item

1. Rows 1, 3, 4, 6 of the human spot-check checklist above still need an actual human pass — the
   only item this report cannot close on its own.
