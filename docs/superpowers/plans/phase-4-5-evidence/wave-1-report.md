# Wave 1 Report — Contracts Distribution, Ownership, Migration Strategy, Decision Artifact

**Date:** 2026-08-01
**Branch:** `phase-4-5-core-plugin-refactoring`
**Plan:** `docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`, Wave 1

## Summary

Wave 1's mechanical/TDD steps (contracts distribution, dependency-boundary checker, isolated-install harness with two negative controls) were built first and confirmed green. The plan's Step 6 human-decision checkpoint was then presented as a genuine stop — not a rubber-stamp — and the human reviewer approved with three specific revisions to the original proposal, each requiring real follow-up work beyond what Wave 1's own text anticipated:

1. A more extraction-favoring split of `analyze_structure.py` than originally proposed.
2. Rejection of both options originally offered for `atomic_output.py`, in favor of a new, separate, narrowly-scoped `knowledge-workbench-runtime` distribution — requiring a specification amendment (§13c) before Wave 2.
3. `orchestrate-conversion` retained as the intentional public workflow orchestrator, not retired in Wave 6 as the plan's original example proposed.

All follow-up work from these three revisions is complete: the two decision documents were rewritten with "Approved (final)" sections, §13c was added to the approved spec, the new runtime distribution was built and tested, the test-ownership ledger was filled reflecting all three decisions, the target-architecture diagram documents the approved (not proposed) state, and Wave 0's 22 flagged edges were re-resolved against the actual decisions (17 now `PROVISIONALLY_ACCEPTED`; 5 correctly remain `REQUIRES_HUMAN_DECISION` — genuinely uncovered by anything approved this session).

An independent review (`cli-agents:pr-reviewer`) found two real issues (a self-contradictory comment/rationale in the edge classifier, and a missing per-test override for `atomic_output.py`'s two generator-info tests) — both fixed and reverified before this report was written.

## Steps 1-5 (mechanical, TDD)

- **Contracts distribution** (`contracts/python/`): `pyproject.toml`, five contract schema modules (`normalized_source_document`, `analysis_plan`, `canonical_package`, `publication_map`, `rendered_output_profile`), `tree_hash.py`, `repo_root.py`. Built and `pip install -e`'d into a throwaway venv: **21 tests passed**, real installed-package import (not `sys.path`), venv removed.
- **Dependency-boundary checker** (`tools/phase-4-5-core-plugin-refactoring/dependency_boundary.py`): `check_no_prohibited_imports`, `check_no_repo_root_import_in_production_code` — **6 tests passed**.
- **Isolated-install harness** (`isolated_install_check.py`): real build→install→import-outside-pytest→test flow per the plan's spec, plus a `check_declares_dependency()` static metadata check I added (needed because the plan's harness always installs the contracts wheel alongside every plugin, so it structurally cannot catch a plugin that imports contracts without declaring it — only a metadata check can). Two negative-control fixtures under `tests/fixtures/`, both confirmed to correctly fail: one via a real venv install (`ModuleNotFoundError` on an undeclared upstream plugin import), one via the metadata check (`check_declares_dependency` returns `False`).

## Step 6 — human decision checkpoint (the actual stop)

Presented as a genuine proposal, not "approve as proposed" bait — the human reviewer identified real gaps and revised three areas:

### 1. `analyze_structure.py` split — revised

Original proposal drew the extraction/analysis line after raw pandoc invocation only. **Approved (final) split is more extraction-favoring**: `source-document-extraction` owns `_run_pandoc_raw`, `_normalize_heading_text`, `iter_heading_matches`, `parse_headings`, `_counts_by_level`, `_repeated_heading_texts`, `_repeated_paths`, `_image_stats`, `detect_raw_toc`, `detect_defect_signals` — every function that produces a source-level observation, not just the pandoc call itself. `knowledge-analysis` owns only the semantic layer: topic-boundary reasoning, `recommend_strategy`, analysis-plan generation. `cli.py::cmd_analyze` (corrected function name — not `analyze_structure.py::analyze_document`, which this document's own first pass got wrong) is the temporary compatibility orchestrator. Full detail: `wave-1-analyze-structure-split-decision.md`.

### 2. `atomic_output.py` — both original options rejected

Neither "duplicate into both plugins" (the plan's stated default — rejected: 173 lines of crash-recovery-critical code should not exist as two hand-synced copies) nor "promote into `knowledge_workbench_contracts`" (rejected: the contracts distribution's scope is types/schemas/validation only, and executable atomicity logic doesn't belong there regardless of genericity) was approved. **Approved instead:** a new, separate, narrowly-scoped distribution, `knowledge-workbench-runtime` (Python package `knowledge_workbench_runtime`), containing only `create_staging_dir`/`promote`. `build_generator_info`/`write_generator_info` are explicitly **not** part of it (they depend on `dependencies.py`, a `source-document-extraction`-domain module) — each consuming domain (`canonical-knowledge`, `knowledge-publication`) implements its own thin generator-info wrapper instead. This decision required a narrow specification amendment before Wave 2 — added as `docs/superpowers/specs/phase-4-5-core-knowledge-plugin-domain-refactoring-spec.md` §13c, covering why `atomic_output` isn't a contract, why duplication was rejected, the approved scope (with an explicit non-goal: this must never become a generic shared-utility dumping ground), independent packaging/testing/versioning, and the requirement that both consuming plugins declare it explicitly. Full detail: `wave-1-shared-contract-decision.md`.

**Built and tested:** `runtime/python/` — `pyproject.toml`, `src/knowledge_workbench_runtime/atomic_output.py` (the two atomicity functions only, with the original module's crash-recovery documentation preserved), `tests/test_atomic_output.py` (5 tests, including a `monkeypatch`-based test that a simulated `os.rename` failure during `promote()` correctly restores `final_dir` to its exact pre-call state). Installed into a throwaway venv, all 5 passed, venv removed.

### 3. Original skill dispositions — one revised

`analyze-document`, `convert-document`, `render-content` remain `TEMPORARY_COMPATIBILITY_WRAPPER` as originally proposed. **`orchestrate-conversion` is `RETAINED_PUBLIC_ORCHESTRATOR`**, not `REPLACED_AND_RETIRED` as the plan's own example value suggested — it preserves the `analyze → human confirmation → canonical construction → render` sequence as the intentional public workflow entry point, orchestration only, no domain logic. All four dispositions (including this one) are reassessed in Wave 7 using the final consumer scan; this approval does not pre-approve retirement of any of them.

`wave-1-decisions.json` records `status: "APPROVED"` with all three revisions and their rationale.

## Wave 0's 22 flagged edges — resolved against the actual decisions

`tools/phase-4-5-core-plugin-refactoring/wave0_classify_edges.py` was updated: `atomic_output.py` changed from a single-domain guess to `UNRESOLVED` (matching `analyze_structure.py`/`convert.py`'s treatment — it also functionally splits, contrary to this document's own first-pass assumption that it resolved to one distribution), and the `UNRESOLVED`-branch disposition changed from `REQUIRES_HUMAN_DECISION` to `PROVISIONALLY_ACCEPTED` (the decision is made; only the physical Wave 2+ implementation is pending, so the old disposition wrongly implied the decision itself was still open). The vocabulary was extended with `NEUTRAL_RUNTIME_DISTRIBUTION` (9th value, not present in the original reviewer-specified list because that decision didn't exist yet when the list was written — documented as an extension, not silently invented).

**Result: 17 of the 22 edges resolved** (now `PROVISIONALLY_ACCEPTED`, citing the relevant decision doc). **5 edges remain genuinely open** — real cross-domain boundary questions not covered by anything approved this session, correctly left `REQUIRES_HUMAN_DECISION` rather than force-resolved:

- `package.py -> topic_grouping.py`
- `topic_grouping.py -> identity.py`
- `renderers/protocol.py -> canonical_package.py` (the renderer-reads-canonical-internals question, flagged since Wave 0)
- `renderers/validate_rendered.py -> path_safety.py`
- `validate_canonical.py -> pandoc_validate.py`

These are deferred to the relevant extraction wave, not silently decided here.

## Test-ownership ledger filled

`wave-0-test-ledger.json`'s `proposed_owner_domain` filled for all **526 entries** via `tools/phase-4-5-core-plugin-refactoring/wave1_test_ownership.py`, built for this wave. File-level domain mapping for 43 of 45 test files; per-test overrides for the two files whose production counterpart splits (`test_analyze_structure.py`: 20 → `SOURCE_DOCUMENT_EXTRACTION`, 9 → `KNOWLEDGE_ANALYSIS`, 1 → `CROSS_CUTTING_MULTIPLE_DOMAINS`; `test_atomic_output.py`: 8 → `NEUTRAL_RUNTIME_DISTRIBUTION`, 2 → `CROSS_CUTTING_MULTIPLE_DOMAINS` for the generator-info tests — the second override was added after independent review found the first pass had missed it, unlike its sibling `test_analyze_structure.py`, which got the override correctly the first time).

Final distribution: `CANONICAL_KNOWLEDGE` 211, `SOURCE_DOCUMENT_EXTRACTION` 78, `REPOSITORY_ORCHESTRATION` 68, `KNOWLEDGE_PUBLICATION` 54, `NEUTRAL_CONTRACT_DISTRIBUTION` 39, `KNOWLEDGE_ANALYSIS` 25, `CROSS_CUTTING_MULTIPLE_DOMAINS` 23, `OUT_OF_PHASE_4_5_SCOPE` 20, `NEUTRAL_RUNTIME_DISTRIBUTION` 8 (total 526).

## Target-architecture diagram

`docs/architecture/phase-4-5-target-architecture.md` — distribution graph reflecting all three approved decisions (the `analyze_structure.py`/`convert.py` split boundaries, the separate `knowledge_workbench_runtime` distribution with `atomic_output.py`'s two halves shown correctly, `orchestrate-conversion` shown retained in `plugins/docx-to-content` rather than retired), plus the "what Wave 0's 22 edges resolve to" table and the explicit `knowledge_workbench_runtime` non-goal (not a general dumping ground).

## Independent review

`cli-agents:pr-reviewer`, run against the full uncommitted working tree. **Ship decision: SHIP**, with two CONCERNs, both fixed before this report:

1. `wave0_classify_edges.py` had a comment claiming `atomic_output.py` was "fully resolved" to `NEUTRAL_RUNTIME_DISTRIBUTION` while the actual dict entry (correctly) mapped it to `UNRESOLVED` — real documentation drift inside evidence-of-record tooling. Fixed: comment corrected, rationale text made dynamic (names the actual file(s) touched rather than a hardcoded list), and the now-reachable-again logic re-verified.
2. `wave1_test_ownership.py`'s file-level default routed all of `test_atomic_output.py` to `NEUTRAL_RUNTIME_DISTRIBUTION`, missing that 2 of its 10 tests (`test_build_generator_info_reuses_dependencies_probes`, `test_write_generator_info_is_deterministic_json_utf8`) exercise the functions explicitly excluded from that distribution. Fixed: per-test override added, both artifacts regenerated.

One NIT (build artifacts / `.egg-info` left in the working tree from throwaway `pip install -e` runs, no `.gitignore` coverage) also fixed: artifacts removed, root `.gitignore` extended with `build/`, `*.egg-info/`, `.venv-*/` entries covering both distributions and future ones.

## Full required test matrix (after all fixes)

```
Contracts distribution (throwaway venv, real installed package):  21 passed
Runtime distribution (throwaway venv, real installed package):     5 passed
Tooling suite (fast):                                              38 passed, 1 deselected
Tooling suite (slow — real venv/wheel isolated-install checks):     1 passed
Dependency-boundary tests (subset of the above):                    6 passed
docx-to-content baseline (unchanged, reconfirmed):                529 passed, 1 skipped
```

## Wave 1 Gate — status

- [x] `knowledge_workbench_contracts` wheel builds and installs cleanly in a throwaway venv; its tests pass.
- [x] `knowledge_workbench_runtime` wheel builds and installs cleanly in a throwaway venv; its tests pass (added scope, approved this wave, not in the plan's original gate text but required by the human decision).
- [x] Dependency-boundary checker (including the `repo_root` production-code prohibition) implemented and tested.
- [x] Isolated-install harness implemented, with both negative controls proven to correctly fail.
- [x] `wave-1-decisions.json` committed with human-approved values (not proposals).
- [x] `wave-0-test-ledger.json` fully assigned (526/526).
- [x] Target architecture diagram committed, reflecting approved decisions.
- [x] Independent review performed, all findings fixed and reverified.

**Wave 1 is complete.** Wave 2 (source-document-extraction extraction) is next and is **not started** — per explicit instruction, this session stops here for review before any plugin extraction begins.
