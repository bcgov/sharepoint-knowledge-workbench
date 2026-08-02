> **Superseded note (2026-08-02, Wave 9):** the "local duplication" approach this doc records
> below (hand-copying `canonical_package.py`, `dispositions.py`, `hashing.py`,
> `publication_map.py`, `atomic_output.py`, `path_safety.py`, `canonical_schema/*` into this
> plugin) was replaced with managed cross-plugin file-level symlinks to `canonical-knowledge`'s
> and `source-document-extraction`'s canonical source — see
> `docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md`. The
> reasoning below is kept as the historical record of the original (superseded) decision.

# Wave 5 — `knowledge-publication` Extraction and `rendered-output-profile` Split Decision

**Date:** 2026-08-01
**Status:** ✓ APPROVED (human pre-authorized Waves 5-8 execution and per-wave commits during this
session; in-flight decision recorded per the same pattern as Waves 1/3/4).

## Scope decided

Per the plan's Public Interface Contract table, `knowledge-publication` **produces**
`rendered-output-profile` (`RenderResult`) from `canonical-package`/`publication-map`. Its Known
File Inventory assigns `scripts/renderers/` (3 modules: `protocol.py`, `multipage_markdown.py`,
`validate_rendered.py`) wholesale. `contracts.py` — by Wave 4's decision, already stripped to only
`RenderResult` + `SUPPORTED_SCHEMA_VERSION` — moves wholesale too, renamed `render_result.py`
(avoiding a bare `contracts` name collision with any future/other plugin's own `contracts.py`).

**Decided:** since `docx-to-content/scripts/contracts.py` had zero remaining production-code
consumers once `RenderResult` moved (confirmed by grep: no file did a literal `import contracts`
outside `renderers/`), the file was deleted outright (`git mv` to the new name, not left behind as
an empty placeholder) — matching the established `dependencies.py`/`plans.py` precedent from Waves
2/3 of fully removing a file once nothing local needs it, rather than leaving a near-empty stub.

## Local duplication: a larger set than Wave 4's, and why

The renderer pipeline's actual runtime dependency graph is deeper than "3 files + RenderResult"
suggests. `renderers/protocol.py` imports `CanonicalPackage` (the renderer-side loader class) for
its `Renderer.render()` type signature; `renderers/multipage_markdown.py` and
`renderers/validate_rendered.py` both import `atomic_output` (staging/promotion) and the
`canonical_schema` consumer-copy types; `validate_rendered.py` additionally imports `path_safety`
(source-document-extraction's media/link classification) and needs `write_render_result`/
`write_rendered_validation_report` support. Loading a `CanonicalPackage` also transitively requires
`dispositions.py` (warning-disposition reconciliation), `hashing.py` (content-hash verification),
and `publication_map.py` (grouped-package publication-map loading) — `canonical_package.py`'s own
three bare imports.

Rather than a partial/awkward subset, **the entire consumer-side chain was duplicated verbatim**
into `knowledge-publication`: `canonical_package.py`, `dispositions.py`, `hashing.py`,
`publication_map.py`, `atomic_output.py` (with a local `_probe_version` and
`"plugin": "knowledge-publication"`, per Wave 4's precedent), `path_safety.py`, and a
`canonical_schema/` consumer copy of the `canonical-package`/`publication-map` schemas (mirroring
`canonical-knowledge`'s own `canonical_schema/analysis_plan.py` consumer-copy pattern one contract
layer up). This is consistent with the established "never cross-plugin import implementation"
discipline (Waves 2-4) — it is simply a larger instance of the same rule, because the render
pipeline's own dependency graph is deeper than the convert pipeline's was.

No new bare-name collisions: `canonical_package`, `dispositions`, `hashing`, `publication_map`,
`atomic_output`, `path_safety`, `canonical_schema` are the exact same bare names
`canonical-knowledge` already uses for its own equivalents — safe, since these are now three
independent, non-communicating duplicate copies across two plugins, not a shared distribution; a
combined-environment collision test (all four wheels co-installed) is explicitly deferred to Wave 6
per the plan's own Gate note.

## Test migration

- The renderer files' own unit/contract tests moved wholesale (`git mv`) to
  `plugins/knowledge-publication/tests/`: `test_validate_rendered.py`,
  `test_validate_rendered_mutations.py`, `test_renderer_protocol.py`, `test_multipage_markdown.py`
  (unit), and `test_contracts.py` → renamed `test_render_result_contract.py` (contract, now 100%
  about the `render_result` module it tests).
- Three real cross-plugin-dependency violations found via the isolated-install gate (same pattern
  as Wave 4's masked-by-shared-venv bugs):
  1. `test_multipage_markdown.py`/`test_validate_rendered.py` used `import package as
     package_module` (canonical-knowledge's builder) solely for its tiny `extract_media_refs`
     regex helper. **Fixed** by inlining a local `_extract_media_refs` test-only helper (5 lines,
     the same `_IMAGE_REF` regex) instead of duplicating all of `package.py` for one function.
  2. `test_validate_rendered_mutations.py` imported its shared fixture helper via
     `from tests.unit.test_validate_rendered import ...` — works when `docx-to-content`'s
     `tests/__init__.py`-bearing package structure is on `sys.path`, but `knowledge-publication`'s
     `tests/` has no `__init__.py` (matching `canonical-knowledge`'s Wave 4 precedent). **Fixed**
     by importing bare `from test_validate_rendered import ...`.
  3. `test_renderer_protocol.py`'s full-pipeline tests (`_accepted_package_dir`, built via
     `analyze_structure.analyze_document` + `convert.convert_and_promote` + `plans.confirm_plan`)
     depend on modules that are not installable dependencies of `knowledge-publication`. **Fixed**
     by moving `test_registry_register_and_get_renderer_round_trip`,
     `test_dispatch_render_end_to_end_with_test_renderer`, and
     `test_dispatch_render_rejects_unsupported_manifest_version` to a new
     `docx-to-content/tests/unit/test_renderer_protocol_integration.py`, matching Wave 4's
     `test_atomic_promotion.py`/`test_convert.py`/`test_package_load.py` precedent. The structural,
     non-pipeline tests (`test_renderer_protocol_shape_is_structural_typing`,
     `test_render_signature_has_no_docx_or_analysis_or_plan_parameter`,
     `test_canonical_package_load_signature_only_accepts_package_dir`,
     `test_registry_rejects_unknown_renderer_name`) stayed in `knowledge-publication`.
  4. `test_multipage_markdown.py`'s own full-pipeline test
     (`test_end_to_end_render_of_small_single_fixture`) was removed outright (not duplicated) since
     its exact scenario is already covered by
     `docx-to-content/tests/integration/test_atomic_promotion.py`'s existing coverage plus the newly
     added `test_renderer_protocol_integration.py` tests — a distinct end-to-end path through the
     same real fixture would have been redundant, not additional coverage.
- `docx-to-content/tests/integration/test_plugin_structure.py` updated: `contracts.py` dropped from
  the required-local-files list (deleted, not a placeholder); `test_renderers_directory_exists`/
  `test_required_renderer_files_exist` replaced with a single
  `test_renderers_directory_no_longer_local` (matching the `test_pandoc_directory_no_longer_local`
  precedent from Wave 2). The now-empty `scripts/renderers/` directory itself (git does not track
  empty directories, so `git mv`-ing its 4 files out left a stray empty dir on disk) was removed
  with `rmdir`.

## `cli.py` compatibility shim

`renderers.multipage_markdown`/`renderers.protocol`/`renderers.validate_rendered` moved from the
top-level import block into a new Wave 5 compatibility-shim block (alongside Wave 3's `plans`/
`topic_grouping` and Wave 4's `convert`/`package`/`canonical_package` blocks), requiring
`knowledge-publication` to be `pip install -e`'d into whatever environment runs `docx-to-content`'s
tests during the transition — documented in the shim comment, removed in Wave 7/8.

## Verification

- `knowledge-publication`: 49/49 tests passed, both editable install (alongside the other three
  plugins in one venv) and isolated wheel install
  (`isolated_install_check.py --plugin knowledge-publication --import-package
  knowledge_publication`, exit 0, zero sibling distribution present, no repo-root path on
  `sys.path`).
- `docx-to-content`: 170 passed / 1 skipped (down from Wave 4's 220/1 — renderer-domain tests
  relocated, not lost, plus 3 full-pipeline renderer tests moved to a new integration test file).
- `source-document-extraction`: unaffected, 78/78. `knowledge-analysis`: unaffected, 70/70.
  `canonical-knowledge`: unaffected, 173/173.
- `tools/phase-4-5-core-plugin-refactoring`: 40/40 (docx-to-content's shrinking test count, 170,
  still comfortably clears the `> 150` floor set in Wave 4's own correction to this same test).
- Dependency-boundary check against `knowledge-publication/scripts/` (prohibited: every bare module
  name owned by `source-document-extraction` or `knowledge-analysis`, plus `canonical-knowledge`'s
  convert-pipeline-only modules `chunking`/`package`/`convert`/`chunk_grouping`/`chunk_identity`/
  `validate_canonical`/`pandoc_cleanup`/`canonical_knowledge`/`media_disposition` — the
  render-pipeline duplicate set `canonical_package`/`dispositions`/`hashing`/`publication_map`/
  `atomic_output` is deliberately excluded from the prohibited list per the local-duplication
  decision above): zero violations.
- `symlink_manager.py diagnose`: all links OK (55 prior + 17 new for `knowledge-publication`'s
  `render-content` skill: 8 top-level scripts, 3 `canonical_schema/` modules, 4 `renderers/`
  modules, 2 `__init__.py`s, 1 reference-contract doc).
