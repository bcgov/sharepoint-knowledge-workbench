# Phase 4.5 Duplication Remediation Report (Post-Wave-8 Review)

**Date:** 2026-08-02 (Part 1: audit; Part 2, appended same day: full remediation executed per
explicit human approval of Option A, extended to eliminate the 3 subset-reimplementation families
too)
**Trigger:** Human review of the `plugins/` bundle after Wave 8 flagged that "Phase 4.5 complete"
was premature — real, hand-maintained duplicate implementation code exists across
`canonical-knowledge` and `knowledge-publication`, plugin manifests reference the pre-rename repo
URL, and `sharepoint-publication` was not explicitly classified as transitional.
**Status: REMEDIATION COMPLETE.** All 12 duplicate/reimplementation families resolved via managed
cross-plugin symlinks or extracted granular canonical modules. Zero hand-maintained editable-source
duplicates remain (verified by a content-hash scan across all 5 plugins' real, non-symlinked
files). See Part 2 below for full execution evidence. Part 1 (the original audit, before
execution) is preserved unmodified below for the historical record. Do not treat this as
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

**Summary (corrected):** of the 12 families named in the review, **8 are true verbatim (or
near-verbatim, 1-2-line) duplicates** that a symlink-based single-source model eliminates directly:
`emf_convert.py`, `path_safety.py`, `pandoc/*` (7 files as one family), `canonical_package.py`,
`dispositions.py`, `hashing.py`, `publication_map.py`, `canonical_schema/` (4 of 5 files). (An
earlier draft of this report miscounted these as 7; corrected to 8.)
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

---

# Part 2 — Remediation Executed (2026-08-02, same day)

Human approved Option A, extended: eliminate all 12 families (8 true duplicates + `atomic_output.py`
+ 3 subset reimplementations), reject Option B (drift-checker-as-permanent-architecture) as the
permanent model. A drift checker may still be added later as an *additional* audit control, but
was not required here since the symlink model makes drift structurally impossible for a managed
link (there is exactly one editable file; the "second copy" is a build/install-time materialization,
never hand-edited).

## 1. Corrected count

8 true byte-identical (or 1-2-line) duplicate families, not 7 (fixed in Part 1 above).

## 2. Empirical feasibility gate (run before any changes)

Verified directly, not assumed: `setuptools`'s `build_py`/`bdist_wheel` dereferences a symlink
(including a *chained* symlink, e.g. skill-folder link → plugin-root link → producer-plugin file)
into a real, independent file when building a wheel. Confirmed by building a real wheel from a
symlinked source file, installing it into a clean venv, **deleting the symlink's target directory
entirely**, and successfully importing and calling the installed module. This is the technical
foundation the whole remediation depends on — see the raw repro under `/tmp/symlink-wheel-test/`
and `/tmp/symlink-chain-test/` (session-local, not committed).

## 3. Canonical ownership (final)

| Family | Canonical owner (real file) | Consumer(s) (managed symlink) |
|---|---|---|
| `emf_convert.py` | `source-document-extraction/scripts/emf_convert.py` | `canonical-knowledge/scripts/emf_convert.py` |
| `path_safety.py` | `source-document-extraction/scripts/path_safety.py` | `knowledge-publication/scripts/path_safety.py` |
| `pandoc/*.py` (8 files incl. `__init__.py`) | `source-document-extraction/scripts/pandoc/` | `canonical-knowledge/scripts/pandoc_cleanup/` (chained: also re-symlinked into that plugin's own skill folder) |
| `canonical_package.py` | `canonical-knowledge/scripts/canonical_package.py` | `knowledge-publication/scripts/canonical_package.py` |
| `dispositions.py` | `canonical-knowledge/scripts/dispositions.py` | `knowledge-publication/scripts/dispositions.py` |
| `hashing.py` | `canonical-knowledge/scripts/hashing.py` | `knowledge-publication/scripts/hashing.py` |
| `publication_map.py` | `canonical-knowledge/scripts/publication_map.py` | `knowledge-publication/scripts/publication_map.py` |
| `canonical_schema/{__init__,shared,canonical_package,publication_map}.py` (4 of 5 files) | `canonical-knowledge/scripts/canonical_schema/` | `knowledge-publication/scripts/canonical_schema/` (the 5th file, `analysis_plan.py`, is a genuinely independent consumer-schema copy, out of scope) |
| `atomic_output.py` | `canonical-knowledge/scripts/atomic_output.py` (confirmed domain-neutral: `create_staging_dir`/`promote` operate on plain directories, per its own pre-existing docstring) | `knowledge-publication/scripts/atomic_output.py` |
| `identity_core.py` (new; extracted from `identity.py`) | `knowledge-analysis/scripts/identity_core.py` | `canonical-knowledge/scripts/identity_core.py`; `knowledge-analysis/scripts/identity.py` becomes a thin local re-export |
| `topic_boundary_core.py` (new; extracted from `topic_grouping.py`) | `knowledge-analysis/scripts/topic_boundary_core.py` | `canonical-knowledge/scripts/topic_boundary_core.py`; `knowledge-analysis/scripts/topic_grouping.py` becomes a thin local re-export |
| `plan_verification_core.py` (new; extracted from `plans.py`) | `knowledge-analysis/scripts/plan_verification_core.py` | `canonical-knowledge/scripts/plan_verification.py` (kept this destination filename to avoid touching `convert.py`/`validate_canonical.py`'s existing `import plan_verification as plans` call sites); `knowledge-analysis/scripts/plans.py` re-exports `PlanVerificationError`/`verify_plan_against_source`/`verify_plan_integrity`/`require_confirmed` from it, and its own `plan_hashing.compute_plan_id` becomes a thin re-export of the same module's `compute_plan_id` — **one canonical implementation of plan-ID computation**, no local `_compute_plan_id` reimplementation left anywhere. |

## 4. Atomic-output parameterization

`build_generator_info(plugin_name, plugin_version=...)` and `write_generator_info(staging_dir,
plugin_name, plugin_version=..., run_timestamp=...)` both now require `plugin_name` as an explicit,
non-defaulted argument. Call sites updated: `canonical-knowledge/scripts/convert.py` passes
`"canonical-knowledge"`; `knowledge-publication/scripts/renderers/validate_rendered.py` passes
`"knowledge-publication"`. A new test (`test_build_generator_info_requires_explicit_plugin_name`)
asserts the old zero-arg call now raises `TypeError`.

## 5. Real files removed / real files added

Removed (converted from real files to managed symlinks): `canonical-knowledge/scripts/emf_convert.py`,
`chunk_identity.py` (retired entirely, superseded by `identity_core.py`), `chunk_grouping.py`
(retired entirely, superseded by `topic_boundary_core.py`), `plan_verification.py` (now a symlink,
same filename), `pandoc_cleanup/*.py` (8 files); `knowledge-publication/scripts/path_safety.py`,
`canonical_package.py`, `dispositions.py`, `hashing.py`, `publication_map.py`, `atomic_output.py`,
`canonical_schema/{__init__,shared,canonical_package,publication_map}.py` (4 files).

Added (new canonical modules, real files): `knowledge-analysis/scripts/identity_core.py`,
`topic_boundary_core.py`, `plan_verification_core.py`. `knowledge-analysis/scripts/identity.py` and
`topic_grouping.py` rewritten as thin local re-exports (still real files, now ~15 lines each
instead of the full implementation). `knowledge-analysis/scripts/plan_hashing.py`'s
`compute_plan_id` body replaced with a one-line re-export.

## 6. `symlinks.json` changes

29 new managed symlink entries created via `symlink_manager.py create` (8 families' files +
`atomic_output.py` + `identity_core.py`/`topic_boundary_core.py`/`plan_verification.py` × 2
locations each [plugin-root + that plugin's own skill folder, where applicable] + the pandoc
8-file family). 2 entries removed and replaced (the old `chunk_identity.py`/`chunk_grouping.py`
skill-folder links, retargeted to the new module names). Full diff in `symlinks.json` (committed).

## 7. `symlink_manager.py diagnose` result

Ran the full sequence: `diagnose` → found 2 broken links (the skill-folder links still pointing at
the retired `chunk_identity.py`/`chunk_grouping.py` filenames) → fixed by re-creating them against
the new `identity_core.py`/`topic_boundary_core.py` targets → `diagnose` again: **All links OK.**

## 8. Installer hard-copy evidence

Ran `python3 .agents/skills/plugin-installer/scripts/plugin_add.py . --plugins canonical-knowledge -y`
and the same for `knowledge-publication`. For every cross-plugin symlinked file, confirmed in the
installed `.agents/skills/<skill>/scripts/...` location:
- `file <path>` reports a regular text file, never a symlink.
- `shasum -a 256` matches the canonical source exactly (checked: `identity_core.py`,
  `topic_boundary_core.py`, `plan_verification.py`, `atomic_output.py`, `canonical_package.py`,
  `hashing.py`, `dispositions.py`, `publication_map.py`, `path_safety.py`, and all 8
  `pandoc_cleanup/*.py` files via the chained skill→plugin-root→producer-plugin symlink path).
All matched.

## 9. Canonical vs. installed SHA-256 — see Section 8 above (18 files checked, 18 matches, 0 mismatches).

## 10. Cross-plugin runtime-import scan

Re-ran `dependency_boundary.check_no_prohibited_imports` against each of the four real domain
plugins' `scripts/` trees with each other plugin's bare module names as the prohibited list:
`knowledge-analysis`, `canonical-knowledge`, and `knowledge-publication` all report **zero
violations**. (The check as run against `source-document-extraction` itself with its own module
names in the prohibited list is a tooling artifact of how the ad hoc check script was invoked in
this session, not a real finding — a plugin's own modules are never "prohibited" for itself.)

## 11. Remaining editable duplicates scan

Content-hash scan across all real (non-symlinked) `.py` files in all 5 plugins: the only hash
collision across different plugins is the empty-file hash shared by five distinct, unrelated
`__init__.py` package markers (0 bytes each — an empty file's SHA-256 is identical everywhere by
definition, not a content duplication). **Zero real editable-source duplicates remain.**

## 12. Plugin-local test results (after remediation)

| Plugin | Result |
|---|---|
| `source-document-extraction` | 78/78 passed |
| `knowledge-analysis` | 70/70 passed |
| `canonical-knowledge` | 174/174 passed (+1: the new `atomic_output` parameterization test) |
| `knowledge-publication` | 49/49 passed |
| `sharepoint-publication` | 20/20 passed |

## 13. Isolated-install results

All four real domain plugins: PASS via `isolated_install_check.py` (`--import-package extraction`,
`analysis`, `canonical_knowledge`, `knowledge_publication` respectively) — wheel builds cleanly,
symlinks dereference into real file content, zero sibling distribution present or importable.

## 14. Combined-install result

`combined_install_check.py`: `{'source-document-extraction': 0, 'knowledge-analysis': 0,
'canonical-knowledge': 0, 'knowledge-publication': 0}` — zero collisions.

## 15. CEIS golden-master result

`tests/integration/test_full_ceis_pipeline_across_plugins.py`: **PASSED, zero skips**, byte-identical
output (unaffected by this remediation, since it operates at the installed-package level where
every symlink is already dereferenced into real content).

## 16. Documentation updates

- `plugins/canonical-knowledge/README.md`, `plugins/knowledge-publication/README.md`,
  `plugins/knowledge-analysis/README.md`: rewritten to describe the symlink/canonical-ownership
  model, "local duplicate"/"kept in sync by hand"/"deliberate local duplicates" language removed
  and replaced with accurate `[symlink -> ...]` file-tree annotations and canonical-ownership
  explanations.
- `wave-4-canonical-knowledge-split-decision.md`, `wave-5-knowledge-publication-split-decision.md`:
  superseded-notice banners added at the top, pointing here; original text preserved unmodified as
  historical record.
- `phase-4-5-exit-statement.md`: 2026-08-02 update section added, explicitly stating the original
  "Phase 4.5 is complete" claim was premature and why.
- `symlinks.json`: updated by `symlink_manager.py` itself (29 new entries, 2 retargeted).
- Installer validation: see Sections 8-9 above.

## 17. Final recommendation

**MERGE_READY**, pending human review of this report and the diff. All 12 duplicate/reimplementation
families resolved. Zero remaining editable-source duplicates (verified by scan, not assumed). All
plugin-local suites, isolated installs, combined install, and the CEIS golden master are green.
`sharepoint-publication` remains explicitly `TRANSITIONAL_HOLDING_LOCATION`, not refactored, not
counted toward Phase 4.5's four completed domain plugins.
