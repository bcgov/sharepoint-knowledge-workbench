# Wave 3 — `knowledge-analysis` Extraction and `analysis-plan` Split Decision

**Date:** 2026-08-01
**Status:** ✓ APPROVED (in-flight decision during Wave 3 execution, following the same pattern as
`wave-1-analyze-structure-split-decision.md` and `wave-1-shared-contract-decision.md`).

## Scope decided

The plan's Known File Inventory assigns `identity.py`, `topic_grouping.py`, and `plans.py`
inconsistently across two different documents: `topic_grouping.py` → `knowledge-analysis`;
`identity.py` and `plans.py` → `canonical-knowledge` (per the plan's Known File Inventory table).
But the Public Interface Contract table is explicit: Wave 3's `knowledge-analysis` **produces**
`analysis-plan` via `recommend_from_normalized`. Since `analysis-plan` is exactly what
`plans.build_draft_plan` constructs (a draft `ConversionPlan`), and `identity.make_chunk_id` is
required to compute `StructuralAnchor.stable_key` for that same plan, both must move with the
contract they help produce — the same reasoning Wave 1 already applied to
`analyze_structure.py`'s split.

**Decided:** `identity.py`, `topic_grouping.py`, `plans.py`, and four of `contracts.py`'s 15
dataclasses (`SourceFingerprint`, `StructuralAnchor`, `Confirmation`, `ConversionPlan`, plus the
`CONVERSION_PLAN_SCHEMA_VERSION` constant) move to `knowledge-analysis` **entirely** — not split
by function. `canonical-knowledge` (Wave 4) does not get its own copy of `identity.py`/
`topic_grouping.py`/`plans.py`'s confirm/verify functions; that plugin's own boundary decision
(what it needs from a *confirmed* plan) is deferred to Wave 4, following the same "decide when you
get there, don't guess ahead" discipline as Wave 1/2.

`media_disposition.py`'s preamble-media-proposal (`propose_media_decisions`) stays in
`docx-to-content` for now, unmoved — it's `canonical-knowledge`-domain per the Known File
Inventory, and it needs filesystem access to the extracted media directory that
`recommend_from_normalized`'s fixed `(normalized_source_document: dict) -> dict` signature doesn't
carry. The compatibility orchestrator (`analyze_structure.py`'s `analyze_document`, still in
`docx-to-content`) calls it directly and merges the proposal into the plan `recommend_from_normalized`
returns, recomputing `plan_id` via `knowledge-analysis`'s own `plan_hashing.compute_plan_id`.

## Two real bugs this wave caught and fixed (both from the flat-bare-import model)

1. **`hashing` name collision.** `docx-to-content` keeps its own `hashing.py` (needed by
   `package.py`/`canonical_package.py`/`validate_canonical.py`, unmoved `canonical-knowledge`
   domain). `knowledge-analysis` also needs a `content_hash`/`compute_plan_id` module. Both being
   `pip install -e`'d together in the compatibility-shim environment means a bare `hashing` name
   would collide and silently resolve to whichever wins the `sys.path` race — the exact same class
   of bug as Wave 2's `contracts`/`schema` collision. **Fixed** by naming
   `knowledge-analysis`'s module `plan_hashing.py`, not `hashing.py`.
2. **`iter_heading_matches` re-export loss.** `docx-to-content/scripts/chunking.py` called
   `analyze_structure.iter_heading_matches(...)` — a re-export Wave 2 left on `analyze_structure.py`
   as a side effect of its import block, which Wave 3's rewrite of `analyze_document` removed.
   **Fixed** by having `chunking.py` import `iter_heading_matches` directly from
   `heading_parsing` (the real owner, `source-document-extraction`), not through
   `analyze_structure` — the correct fix, since `analyze_structure.py` was never meant to be a
   re-export hub.

**Lesson for Wave 4/5 (repeating Wave 2's lesson):** before naming any bare top-level module in a
new plugin, grep every other plugin likely to be co-installed for that exact name. Before deleting
or rewriting any re-export a currently-unmoved file depends on, grep every consumer of that
re-export first.

## Test migration

- `identity.py`/`topic_grouping.py`/`plans.py`'s own unit tests (`test_identity.py`,
  `test_topic_grouping.py`, `test_plans.py`) moved wholesale (`git mv`) to
  `plugins/knowledge-analysis/tests/unit/`.
- Two tests inside the old `test_plans.py` that exercised `cli.py`'s `confirm`/`convert` command
  wiring (not `plans.py`'s own logic) were **not** moved — `cli.py` stays in `docx-to-content`, so
  moving them would create a `knowledge-analysis` → `docx-to-content` dependency. They moved instead
  to a new `docx-to-content/tests/unit/test_cli_plan_integration.py`.
- `tests/contract/test_contracts.py`'s `TestSourceFingerprint`/`TestStructuralAnchor`/
  `TestConversionPlan`/`TestComputePlanId` classes moved to a new
  `plugins/knowledge-analysis/tests/contract/test_analysis_plan_contract.py`; the remaining classes
  (`ChunkMetadata`, `Manifest`, `ValidationIssue`/`Report`, `RenderResult`) stay in `docx-to-content`.
- `test_analyze_structure.py`'s `SOURCE_DOCUMENT_EXTRACTION`-tagged tests already left in Wave 2;
  its `test_recommendation_constants_are_named_and_configurable` (duplicated already in
  `knowledge-analysis`'s `test_analysis.py`) was removed rather than kept as dead weight.
- Every other `docx-to-content` test file referencing the moved dataclasses
  (`test_convert.py`, `test_validate_canonical.py`, `test_package.py`, `test_package_load.py`,
  `test_renderer_protocol.py`, `test_multipage_markdown.py`, `test_atomic_output.py`,
  `test_independent_fixture.py`, `test_chunking.py`, `test_cli.py`) updated to import
  `plan_schema.analysis_plan` (aliased `contracts` or `plan_contracts` depending on whether the
  file also needs `docx-to-content`'s own remaining `contracts.py` classes).

## Verification

- `knowledge-analysis`: 70/70 tests passed, both editable install and isolated wheel install
  (`isolated_install_check.py --plugin knowledge-analysis --import-package analysis`, exit 0, zero
  sibling distribution present).
- `docx-to-content`: 393 passed/1 skipped (down from 452/1 — tests relocated, not lost; net -59:
  55 knowledge-analysis unit + `test_cli_plan_integration.py`'s 2 tests stayed, minus 1 removed
  duplicate, plus test-contract-file reshuffling).
- `source-document-extraction`: unaffected, 78/78.
- `tools/phase-4-5-core-plugin-refactoring`: 40/40 (after updating `test_wave0_test_ledger.py`'s
  stale `> 400` threshold to `> 300` — `docx-to-content`'s own test count legitimately shrinks each
  wave as domains extract; the ledger tool itself is unchanged, only the test's threshold was
  stale).
- Dependency-boundary check against `knowledge-analysis/scripts/`: zero violations.
- `symlink_manager.py diagnose`: all 26 links OK (17 from Wave 2's `source-document-extraction`
  fix + 9 new for `knowledge-analysis`'s `analyze-content-structure` skill).
