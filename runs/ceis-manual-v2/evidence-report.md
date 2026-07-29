# CEIS Manual — Phase 1 Fidelity Evidence Report

Produced against `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md`
Section 10 ("Fidelity Evidence"), for the Task 17/18 real-document acceptance run. This report
was assembled retroactively from artifacts already on disk after the pipeline run (Task 18);
it was not generated as an automatic pipeline output. Automated fields below were read directly
from the run's JSON artifacts and re-verified by direct inspection (`grep`/counts), not
transcribed from memory. The human spot-check section (last) was **not** completed by an
automated process — per this section's own rule ("human review records observed facts only"),
it requires a human to actually look at the rendered output before those rows can be signed off.

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
| Canonical media files (`manifest.json.media`) | 318 | counted from manifest |
| Rendered media files (`render/rendered-output/media/`) | 318 | `find ... -type f \| wc -l` |

Reconciliation: 320 raw extracted files → 318 canonical/rendered files. Of the 2-file gap:

- **`image1.png`** — accounted for and correct: the sole preamble media reference, reviewed by a
  human, classified `obsolete-source-layout-artifact`, dispositioned `omit-as-reviewed-artifact`,
  confirmed absent from both canonical and rendered media.
- **`image239.emf`/`image239.png`** — **NOT accounted for; a real defect** (see "Open Items"
  below, elevated from a rounding note to a confirmed finding). This is body content in the
  `PROTECTION ORDERS` section (not preamble, no disposition mechanism applies), and it did not
  survive conversion.

All legacy `.emf` files were otherwise converted to `.png` in place (37 `.emf` sources → 0 `.emf`
files in canonical/rendered output; no format survives as `.emf` past `convert`) — `image239.emf`
is the one exception.

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
- Canonical: summed `media_refs` across all chunk metadata = **340** (some images referenced more
  than once in text; 318 unique media files backing them).
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
| Content loss and duplication checks pass | ✅ | `canonical-content/validation.json` PASS |
| **Media and internal links resolve in canonical and rendered outputs** | ❌ **FAIL** | **`image239.png` reference is broken in both promoted canonical and rendered output — see Open Items below. Both validators reported PASS despite this, which is itself a second finding (validator gap).** |
| Orphan, stale, traversal, and malformed artifact tests pass | ✅ (existing suite, not the real-document validators that missed image239) | 448 passed/1 skipped |
| WARN requires disposition | ✅ | media-decision mechanism enforces this for preamble media; no undispositioned WARN occurred on this run |
| Atomic promotion protects prior accepted output | ✅ | staging-then-promote pattern in `convert.py`/`validate_rendered.py` |
| Renderer consumes canonical package only | ✅ | `render(self, package, output_dir)` signature, per `render-content/SKILL.md` |
| Single and repeated-heading fixtures pass | ✅ (existing suite) | 448 passed/1 skipped |
| CEIS evidence report is complete | ⚠️ **Partial** | this report exists now, but the human spot-check rows and the image239 defect are unresolved |
| Human spot checks are recorded | ❌ | not yet done — see checklist above |
| All tests and plugin validation pass | ⚠️ | unit/integration suite passes (448/1 skipped), but real-document canonical/render validation missed a real broken reference — "passing" is not the same as "no defects" |
| Deferred scope remains deferred | ✅ | general (non-preamble) media classification confirmed still not implemented |
| Applicable plugin/marketplace metadata is reconciled | not verified this pass | out of scope for this report; check separately before closeout |

**Net result: this checklist cannot be signed off as fully passing.** The `image239` defect fails
the "media and internal links resolve" item outright, and surfaces a second, more concerning
finding — the canonical/render validators did not catch it — which itself may need a fix (a
broken-link scan that only trusts recorded `media_refs` rather than re-scanning rendered markdown
for image links) before this checklist item can honestly be marked passing on a future rerun.

## Open Items Not Resolved by This Report

1. **Confirmed defect, blocking a clean Phase 1 close-out:** `image239.emf` (referenced in the
   `PROTECTION ORDERS` topic, source text: "NOTE — When Protection Orders are Varied or
   Cancelled...") did not survive conversion.
   - The file is absent from both `canonical-content/media/` and `render/rendered-output/media/`
     (confirmed by direct filesystem search — not present under either directory, anywhere).
   - Both the promoted canonical chunk (`chunks/protection-orders--2955bfec.md`) and the promoted
     rendered page (`pages/protection-orders--2955bfec.md`) contain the markdown image reference
     with an **absolute, machine-local path** into a deleted staging directory
     (`.../run-e2fc65dd382742c5a9958ad52d6d323a/_staging/raw/media/image239.png`) rather than a
     relative path into the promoted `media/` folder that this reference was never rewritten.
   - **Both `canonical-content/validation.json` and
     `render/rendered-output/renderer-validation.json` report `"status": "PASS"` with
     `"issues": []`** — the broken-link/media-reference checks in this pipeline did not catch this.
     This is a validator gap, not only a one-off conversion miss: the absolute-path reference
     evidently isn't being checked as a media reference at all (it is absent from the chunk's own
     `media_refs` list, which the validator likely trusts as authoritative rather than re-scanning
     the raw markdown for image links).
   - **Consequence:** the Task 18 "convert PASS / render PASS" claim has a real, reproducible
     hole. Anyone opening the promoted output on a different machine gets a broken image link in
     this section, undetected by either validator.
   - **This should be fixed (media-conversion pipeline + validator gap) before Phase 1 is
     declared formally closed** — it is a genuine content-fidelity defect, not documentation
     debt.
2. Rows 1, 3, 4, 6 of the human spot-check checklist above still need an actual human pass.
3. This report was written after the fact, from artifacts already on disk, not generated inline
   by the pipeline at Task 18 run time — future runs should generate it as part of the run rather
   than reconstructing it retroactively.
