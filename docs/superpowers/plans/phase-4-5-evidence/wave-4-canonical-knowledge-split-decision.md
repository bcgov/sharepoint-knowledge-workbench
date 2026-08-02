# Wave 4 — `canonical-knowledge` Extraction and `canonical-package`/`publication-map` Split Decision

**Date:** 2026-08-01
**Status:** ✓ APPROVED (in-flight decision during Wave 4 execution, following the same pattern as
`wave-1-analyze-structure-split-decision.md`, `wave-1-shared-contract-decision.md`, and
`wave-3-analysis-plan-split-decision.md`).

## Scope decided

Per the plan's Public Interface Contract table, `canonical-knowledge` **produces**
`canonical-package` and `publication-map` from a *confirmed* `analysis-plan`. Its Known File
Inventory assigns `atomic_output.py`, `chunking.py`, `package.py`, `canonical_package.py`,
`dispositions.py`, `media_disposition.py`, `publication_map.py`, `hashing.py`,
`validate_canonical.py`, and `convert.py` (nine wholesale `git mv`s, plus `media_disposition.py`
which stayed in `docx-to-content` through Wave 3 per that wave's decision doc) — all moved
wholesale, not split by function, matching Wave 1/3's precedent.

**Decided:** `contracts.py`'s remaining `ManifestSourceFingerprint`/`ChunkMetadata`/
`ManifestChunk`/`ManifestGenerator`/`Manifest`/`ValidationIssue`/`ValidationReport`/
`PublicationMapEntry`/`PublicationMap` dataclasses (plus `MANIFEST_SCHEMA_VERSION`,
`CHUNK_METADATA_SCHEMA_VERSION`, `PUBLICATION_MAP_SCHEMA_VERSION`) move to this plugin's own
`canonical_schema/canonical_package.py` and `canonical_schema/publication_map.py`. Only
`RenderResult` (knowledge-publication's future Wave 5 contract) and `SUPPORTED_SCHEMA_VERSION`
(kept as a backward-compatible alias of `MANIFEST_SCHEMA_VERSION`) remain in
`docx-to-content/scripts/contracts.py`.

## Five real cross-plugin-dependency violations this wave caught and fixed

Moving these nine files into a REAL domain plugin (not the transitional `docx-to-content`)
triggered the dependency-boundary rule (spec Section 11: a domain plugin never imports another
domain plugin's implementation package) for the first time on code that had never needed to
respect it before. Each was fixed by **local duplication**, never a shared distribution — the
same discipline Wave 1/2's contract-materialization correction established:

1. **`chunking.py` → `heading_parsing` (source-document-extraction).** `from heading_parsing
   import iter_heading_matches` was legitimate while `chunking.py` lived in transitional
   `docx-to-content`; became prohibited once moved. **Fixed** by inlining a local heading-walk
   implementation (`_HEADING_LINE` regex, `_normalize_heading_text`, `iter_heading_matches`) using
   the locally-duplicated `pandoc_cleanup.heading_emphasis`/`pandoc_cleanup.images` (see #3 below).
2. **`atomic_output.py` → `dependencies` (source-document-extraction).** `import dependencies` for
   `probe_pandoc()`/`probe_soffice()` is prohibited for a real domain plugin. **Fixed** per Wave
   1's original decision (each plugin gets its own thin generator-info wrapper) with a local
   `_probe_version(name)` helper (`shutil.which` + `subprocess.run`, ~15 lines, no shared
   distribution).
3. **`convert.py` → `pandoc.*`/`emf_convert` (source-document-extraction).** Pandoc-cleanup steps
   and legacy `.emf`→`.png` conversion both resolved to `source-document-extraction`'s package.
   **Fixed** by duplicating the entire `pandoc/` family verbatim as `pandoc_cleanup/` (7 files:
   `attrs.py`, `footnotes.py`, `heading_emphasis.py`, `images.py`, `tables.py`, `toc.py`,
   `validate.py` — self-contained, stdlib-only) and copying `emf_convert.py` verbatim (76 lines,
   self-contained `soffice` wrapper).
4. **`package.py` → `topic_grouping`/`identity` (knowledge-analysis).** `import topic_grouping`
   resolved to `knowledge-analysis`'s package. **Fixed** by duplicating only the convert-time
   functions (`classify_headings`, `compute_topic_boundaries`,
   `compute_topic_boundaries_from_roots`, `TopicMember`, `TopicBoundary`,
   `UnassignableHeadingError`) as `chunk_grouping.py`, backed by a new `chunk_identity.py`
   (duplicate of `identity.py`'s `make_chunk_id`/`make_topic_id`/`normalize_heading_path`) — named
   `chunk_identity`/`chunk_grouping` specifically to avoid colliding with `knowledge-analysis`'s
   bare `identity`/`topic_grouping` when both plugins are co-installed.
5. **`convert.py`/`validate_canonical.py` → `plans` (knowledge-analysis).** Both genuinely call
   `plans.verify_plan_against_source`, `plans.verify_plan_integrity`, and `plans.require_confirmed`
   before building/validating a package — despite Wave 3's decision doc predicting "canonical-
   knowledge consumes a confirmed plan dict, it does not need those functions itself." That
   prediction was wrong once implementation reached this point. **Fixed** by duplicating exactly
   those three functions plus `PlanVerificationError` and a local `_compute_plan_id` (using this
   plugin's own `hashing.py`) into a new `plan_verification.py`, imported as `import
   plan_verification as plans` so call sites needed no further edits. This is the correct
   resolution of Wave 3's open question, not a deviation from it.

## Bare-name collision avoidance

New bare top-level names introduced this wave — `canonical_schema`, `chunk_identity`,
`chunk_grouping`, `pandoc_cleanup`, `plan_verification` — were each chosen after grepping
`source-document-extraction` (`schema`, `pandoc`, `identity` N/A there) and `knowledge-analysis`
(`identity`, `topic_grouping`, `plans`, `plan_schema`) for collisions. `emf_convert.py` and
`hashing.py`/`dispositions.py`/`publication_map.py`/`atomic_output.py`/`chunking.py`/`package.py`/
`canonical_package.py`/`validate_canonical.py`/`convert.py` kept their original bare names — none
collide with any other plugin's names as of this wave.

## Test migration

- The nine wholesale files' own unit tests (`test_atomic_output.py`, `test_chunking.py`,
  `test_dispositions.py`, `test_media_disposition.py`, `test_package.py`,
  `test_publication_map.py`, `test_validate_canonical.py`,
  `test_validate_canonical_mutations.py`, `test_canonical_package_mutations.py`) moved wholesale
  (`git mv`) to `plugins/canonical-knowledge/tests/`, with imports updated to the plugin-local
  duplicate modules (`chunk_identity` instead of `identity`, `chunk_grouping` instead of
  `topic_grouping`, `pandoc_cleanup.*` instead of `pandoc.*`, `plan_verification` instead of
  `plans`, `canonical_schema.analysis_plan` instead of `plan_schema.analysis_plan`) and, for
  `test_atomic_output.py`, to mock this plugin's own `_probe_version` instead of a `dependencies`
  module it no longer has.
- Three tests that build a real plan via `analyze_structure.analyze_document` (docx-to-content's
  own orchestrator, not an installable dependency of any of the four domain plugins) were
  initially moved but **moved back** to `docx-to-content/tests/` once the isolated-install gate
  caught the resulting `ModuleNotFoundError: No module named 'analyze_structure'`:
  `test_atomic_promotion.py` (integration), `test_convert.py`, `test_package_load.py` (unit) — and
  `test_atomic_output.py`'s `test_reproducible_conversion_produces_identical_manifests`, moved to
  `docx-to-content/tests/integration/test_atomic_promotion.py` as a new test using `convert.
  convert_document` directly. This repeats Wave 3's `test_cli_plan_integration.py` precedent.
- `tests/contract/test_contracts.py`'s `TestChunkMetadata`/`TestManifest`/`TestValidation`/
  `TestCanonicalJson` classes (plus their `make_manifest_dict`/`make_chunk_metadata_dict` fixtures
  and the `PublicationMap`-dependent half of `test_schema_version_constants_are_independent_per_
  contract`) moved to a new `plugins/canonical-knowledge/tests/contract/
  test_canonical_package_contract.py`; `TestRenderResult` and
  `test_supported_schema_version_constant` stay in `docx-to-content`.
- Every other `docx-to-content` test file referencing the moved dataclasses
  (`test_validate_rendered.py`, `test_validate_rendered_mutations.py`, `test_multipage_markdown.py`,
  `test_independent_fixture.py`) updated to import `canonical_schema.canonical_package as
  contracts` (and, for `test_multipage_markdown.py`, `canonical_schema.publication_map as
  pm_contracts` alongside a separate `contracts` import for the still-local `RenderResult`).
  `renderers/multipage_markdown.py` itself updated the same way (`_canonical_contracts` for
  `MANIFEST_SCHEMA_VERSION`, keeping local `contracts` for `RenderResult`).
- `tests/integration/test_plugin_structure.py`'s `test_required_script_files_exist` updated to
  drop `hashing.py`/`convert.py`/`chunking.py`/`package.py`/`validate_canonical.py` from the
  required-local-files list (now supplied by the installed `canonical-knowledge` package),
  matching the existing precedent for `dependencies.py`/`plans.py`.
- A real bug this wave's test migration caught: `cli.py`'s `cmd_convert` caught
  `plans.PlanVerificationError` (knowledge-analysis's exception class, from `cli.py`'s own
  top-level `plans` import) around a call to `convert.convert_and_promote` — but that function now
  raises canonical-knowledge's own `plan_verification.PlanVerificationError` (a different class
  with the same name), so the `except` clause silently stopped catching it. **Fixed** by catching
  `convert.plans.PlanVerificationError` instead (i.e. through the module `convert.py` itself
  resolves `plans` to), verified by `test_convert_rejects_stale_source_exit_4` failing before the
  fix and passing after.

## Verification

- `canonical-knowledge`: 173/173 tests passed, both editable install (alongside the other three
  plugins in one venv) and isolated wheel install
  (`isolated_install_check.py --plugin canonical-knowledge --import-package canonical_knowledge`,
  exit 0, zero sibling distribution present, no repo-root path on `sys.path`).
- `docx-to-content`: 220 passed / 1 skipped (down from Wave 3's 393/1 — nine files' tests
  relocated, not lost, plus three plan-dependent tests moved back per the isolated-install gate;
  net driven by domain extraction, not test loss).
- `source-document-extraction`: unaffected, 78/78.
- `knowledge-analysis`: unaffected, 70/70.
- `tools/phase-4-5-core-plugin-refactoring`: 40/40 (after updating `test_wave0_test_ledger.py`'s
  stale `> 300` threshold to `> 150`, and `test_wave0_dependency_graph.py`'s hardcoded
  `cli.py -> convert.py` edge assertion to `cli.py -> analyze_structure.py`, the edge that remains
  local after this wave's move — both are the same class of "shrinking-count/moved-file" staleness
  Wave 3 already fixed once).
- Dependency-boundary check against `canonical-knowledge/scripts/` (prohibited: every bare module
  name owned by `source-document-extraction` or `knowledge-analysis`): zero violations.
- `symlink_manager.py diagnose`: all links OK (26 prior + 29 new for `canonical-knowledge`'s
  `build-canonical-package` skill: 15 top-level scripts, 4 `canonical_schema/` modules, 8
  `pandoc_cleanup/` modules, 2 reference-contract docs).
