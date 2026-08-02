# Phase 4.5 Duplication Remediation Report (Post-Wave-8 Review)

**Date:** 2026-08-02
**Trigger:** Human review of the `plugins/` bundle after Wave 8 flagged that "Phase 4.5 complete"
was premature — real, hand-maintained duplicate implementation code exists across
`canonical-knowledge` and `knowledge-publication`, plugin manifests reference the pre-rename repo
URL, and `sharepoint-publication` was not explicitly classified as transitional.
**Status:** Audit complete, two low-risk items fixed (repo URLs, explicit transitional
classification). **The duplicate-code architecture itself is NOT yet changed** — this report ends
with a proposed remediation and stops for a decision, per instruction. Do not treat this as
"Phase 4.5 fully clean" until the duplication question below is resolved.

## 1. Duplicate-family audit (byte-for-byte, verified this pass)

| Family | Paths | Byte-identical? | Cross-plugin or intra-plugin |
|---|---|---|---|
| `emf_convert.py` | `source-document-extraction/scripts/emf_convert.py` (owner) → `canonical-knowledge/scripts/emf_convert.py` | **Yes, identical** | Cross-plugin |
| `path_safety.py` | `source-document-extraction/scripts/path_safety.py` (owner) → `knowledge-publication/scripts/path_safety.py` | **Yes, identical** | Cross-plugin |
| `pandoc/*.py` (7 files: `attrs.py`, `footnotes.py`, `heading_emphasis.py`, `images.py`, `tables.py`, `toc.py`, `validate.py`) | `source-document-extraction/scripts/pandoc/` (owner) → `canonical-knowledge/scripts/pandoc_cleanup/` | **Yes, identical** (only `__init__.py`'s docstring differs — a comment, not logic) | Cross-plugin |
| `atomic_output.py` | `canonical-knowledge/scripts/atomic_output.py` and `knowledge-publication/scripts/atomic_output.py` | **No** — 2-line deliberate divergence: the `"plugin"` field in `build_generator_info()` and one doc-reference comment | Cross-plugin, two independent producers (each plugin stamps its own identity) |
| `canonical_package.py` | `canonical-knowledge/scripts/canonical_package.py` (owner) → `knowledge-publication/scripts/canonical_package.py` | **Yes, identical** | Cross-plugin |
| `dispositions.py` | `canonical-knowledge/scripts/dispositions.py` (owner) → `knowledge-publication/scripts/dispositions.py` | **Yes, identical** | Cross-plugin |
| `hashing.py` | `canonical-knowledge/scripts/hashing.py` (owner) → `knowledge-publication/scripts/hashing.py` | **Yes, identical** | Cross-plugin |
| `publication_map.py` | `canonical-knowledge/scripts/publication_map.py` (owner) → `knowledge-publication/scripts/publication_map.py` | **Yes, identical** | Cross-plugin |
| `canonical_schema/` (4 of 5 files: `__init__.py`, `shared.py`, `canonical_package.py`, `publication_map.py`) | `canonical-knowledge/scripts/canonical_schema/` (owner) → `knowledge-publication/scripts/canonical_schema/` | **Yes, identical** for the 4 shared files. `canonical-knowledge` additionally has a 5th file, `analysis_plan.py` (its own consumer copy of `knowledge-analysis`'s contract), which `knowledge-publication` does not need and does not have. | Cross-plugin |
| `identity.py` / `chunk_identity.py` | `knowledge-analysis/scripts/identity.py` (owner) vs `canonical-knowledge/scripts/chunk_identity.py` | **No** — same algorithm (`make_chunk_id`/`make_topic_id`/slug logic byte-identical in *behavior*), but `chunk_identity.py` strips most of the prose docstrings and inlines a local `_content_hash` instead of importing `knowledge-analysis`'s `plan_hashing.content_hash`. Not a literal copy; a deliberately trimmed reimplementation kept in sync by hand. | Cross-plugin |
| `topic_grouping.py` / `chunk_grouping.py` | `knowledge-analysis/scripts/topic_grouping.py` (197 lines, full analysis-time + convert-time surface) vs `canonical-knowledge/scripts/chunk_grouping.py` (167 lines) | **No** — `chunk_grouping.py` is a genuine **subset**: only the convert-time functions (`compute_topic_boundaries`, `compute_topic_boundaries_from_roots`, `classify_headings`, etc.), not the analysis-time preview functions `knowledge-analysis` also needs. Not the same file at two sizes; a narrower reimplementation. | Cross-plugin |
| `plans.py` / `plan_verification.py` | `knowledge-analysis/scripts/plans.py` (272 lines: `build_draft_plan`, `confirm_plan`, `apply_media_decision`, verify/require functions) vs `canonical-knowledge/scripts/plan_verification.py` (82 lines: only `verify_plan_against_source`/`verify_plan_integrity`/`require_confirmed`/`PlanVerificationError` + a local `_compute_plan_id`) | **No** — same relationship as above: a genuine functional subset, not a full-file copy. | Cross-plugin |

**Summary:** of the 12 families named in the review, **7 are true verbatim (or near-verbatim,
1-2-line) duplicates** that a symlink-based single-source model could eliminate directly:
`emf_convert.py`, `path_safety.py`, `pandoc/*` (7 files as one family), `canonical_package.py`,
`dispositions.py`, `hashing.py`, `publication_map.py`, `canonical_schema/` (4 of 5 files).
`atomic_output.py` is a near-duplicate with one deliberate per-plugin difference. **3 families are
NOT literal duplicates** — `chunk_identity.py`, `chunk_grouping.py`, and `plan_verification.py` are
narrower, hand-trimmed reimplementations of a *subset* of their producer's functionality, not
copies of the same content. A plain symlink cannot represent "the same file, but smaller" — this
distinction matters for the remediation options below.

## 2. Why this happened (root cause, not excuse)

Every wave's decision doc (Wave 4, Wave 5) explicitly reasoned through this and chose hand-copying
because a **runtime** cross-plugin import is prohibited by spec Section 11 ("a domain plugin never
imports another domain plugin's implementation package under any circumstance") — and the
intra-plugin hub-and-spoke symlink model (plugin-root `scripts/` → skill-folder, via
`symlink_manager.py`) was never evaluated for the **cross-plugin, build-time** case: a symlink from
`knowledge-publication/scripts/hashing.py` to `../../canonical-knowledge/scripts/hashing.py`,
resolved into a real, independent file copy when each plugin's wheel is built, would satisfy both
constraints simultaneously — zero pip/runtime dependency between the two installed wheels, but also
zero hand-maintained drift risk between the two source copies. This was a real gap in Wave 4/5's
design reasoning, not a deliberate rejection — neither wave's decision doc considered or rejected a
cross-plugin symlink option; they moved straight to "duplicate the file."

## 3. Fixed this pass (safe, mechanical, done)

- **All 5 plugin manifests' `repository` field** corrected from
  `https://github.com/richfrem/manual-conversion-poc` (pre-rename) to
  `https://github.com/richfrem/sharepoint-knowledge-workbench` (current `origin`).
- **`sharepoint-publication` explicitly classified** `TRANSITIONAL_HOLDING_LOCATION` in both its
  `plugin.json` description and README header, with an explicit "do not count toward Phase 4.5
  exit criteria" statement. It was already documented as not-yet-decomposed in prose; it now
  carries the classification as a scannable, machine-greppable label per the review's requested
  wording.

## 4. NOT fixed this pass (proposed, awaiting decision)

Per the review's explicit instruction ("produce a remediation report and stop"), the duplicate-code
architecture itself has **not** been changed. Two remediation options, for a decision:

**Option A — cross-plugin symlinks for the 8 true-duplicate families, via `symlink_manager.py`.**
For each: designate the producer plugin (`source-document-extraction` for `emf_convert.py`/
`path_safety.py`/`pandoc/*`; `canonical-knowledge` for `canonical_package.py`/`dispositions.py`/
`hashing.py`/`publication_map.py`/4-of-5 `canonical_schema/` files) as canonical, replace the
consumer plugin's copy with a `symlink_manager.py create --src <producer path> --dst <consumer
path>` entry. Requires verifying that `setuptools`'s `bdist_wheel`/`build_py` command dereferences
symlinks into real file copies when building the consumer's wheel (needs a real test: build a wheel
from a plugin containing a cross-plugin symlink and confirm the resulting `.whl` contains a real
file, not a broken link, and that `isolated_install_check.py` still reports zero sibling
distribution present). If confirmed, this converts 8 families from "two independently hand-edited
copies that can silently drift" to "one source, one managed symlink, edited once." `atomic_output.py`
would need either a small parameterization (accept `plugin_name` as an argument instead of a
hardcoded string) to become byte-identical and symlinkable, or stay duplicated with its 2-line
diff explicitly accepted. `chunk_identity.py`/`chunk_grouping.py`/`plan_verification.py` cannot
become simple symlinks (they are subsets, not copies) — leave those as hand-maintained
reimplementations, but consider adding a drift test in each duplicate's own suite that asserts
behavioral parity against the producer's function for the overlapping surface (e.g.
`chunk_identity.make_chunk_id` produces the same output as `identity.make_chunk_id` for the same
input), so drift is caught by CI rather than only by manual review.

**Option B — leave as-is, but document the tradeoff explicitly and add a repo-level drift-check
tool.** Keep the current hand-copy model (matches what Waves 4/5 shipped and what all tests
currently verify), but add a `tools/phase-4-5-core-plugin-refactoring/duplicate_drift_check.py`
that diffs every documented duplicate-family pair and fails if any true-duplicate pair (the 7
byte-identical families above) has silently diverged, run as part of the standard gate sequence
going forward. This accepts the maintenance burden but makes drift detectable immediately rather
than by manual bundle review.

**This report does not choose between A and B.** Recommend A for the 8 true-duplicate families
(lower long-term maintenance risk, and the mechanism — `symlink_manager.py` — already exists and is
already trusted for the intra-plugin case) plus a drift test for the 3 genuine-subset families,
but this is a real architecture decision that should be made explicitly, not inferred.

## 5. Verification run this pass (all green, no regressions from the two fixes applied)

- `symlink_manager.py diagnose`: all links OK.
- Stale repository-reference scan (`grep -rl "manual-conversion-poc" plugins/*/.claude-plugin/plugin.json`): zero hits (was 5, now 0).
- All 5 plugin-local suites: `source-document-extraction` 78/78, `knowledge-analysis` 70/70,
  `canonical-knowledge` 173/173, `knowledge-publication` 49/49, `sharepoint-publication` 20/20.
- Isolated installs (all four real domain plugins): PASS, zero sibling distribution present.
- Combined install (`combined_install_check.py`): `{'source-document-extraction': 0,
  'knowledge-analysis': 0, 'canonical-knowledge': 0, 'knowledge-publication': 0}` — zero collisions.
- CEIS golden master (`tests/integration/test_full_ceis_pipeline_across_plugins.py`): PASSED, zero
  skips.

## 6. What "Phase 4.5 complete" should actually mean

The prior session's "Phase 4.5 is fully complete" claim was premature in exactly the way the review
describes: all tests passing and all waves' own gates passing does not by itself mean the
architecture matches the originally-intended hub-and-spoke, zero-hand-duplication model — Waves 4/5
satisfied the *letter* of "no runtime cross-plugin import" but did not fully explore whether the
existing symlink infrastructure could have satisfied it *without* hand-duplication. That gap is
real and is what this report exists to surface, not to paper over.
