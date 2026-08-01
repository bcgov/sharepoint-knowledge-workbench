# Wave 1 Step 2 — `contracts.py` / `cli.py` / `convert.py` / `atomic_output.py` Disposition

**Date:** 2026-08-01
**Status:** ✓ APPROVED (human decision, 2026-08-01), with `atomic_output.py`'s disposition **rejecting both options this document originally proposed**. See "Approved `atomic_output.py` disposition (final)" below; `contracts.py`/`cli.py`/`convert.py` dispositions are approved as originally proposed.

## Approved `atomic_output.py` disposition (final)

The human reviewer rejected both options this document originally offered:

- **Rejected: duplicate into both plugins** (the plan's stated default) — 173 lines of crash-recovery-critical code (the `promote()` atomicity/rollback logic) must not exist as two hand-synced copies.
- **Rejected: promote into `knowledge_workbench_contracts`** — the contracts distribution's scope is **types, schemas, and validation only**; `create_staging_dir`/`promote` are executable runtime/workflow logic, not a schema, and do not belong there regardless of how generic they are.

**Approved instead:** a new, narrowly scoped neutral distribution, provisional name `knowledge-workbench-runtime` (Python import package `knowledge_workbench_runtime`), sibling to `knowledge_workbench_contracts` but structurally and philosophically distinct:

| Distribution | Scope |
|---|---|
| `knowledge_workbench_contracts` | types, schemas, validation only — no executable workflow/runtime logic |
| `knowledge_workbench_runtime` | small, deterministic, cross-plugin runtime primitives — initially scoped to atomic output promotion and directly related filesystem primitives only, **not a generic shared-utility dumping ground** |

Initial approved responsibility of `knowledge_workbench_runtime`: `create_staging_dir`/`promote` (the pure filesystem atomicity primitives, no dependency on any domain plugin). `build_generator_info`/`write_generator_info` are **not** included — they depend on `dependencies.probe_pandoc()`/`probe_soffice()`, which is `source-document-extraction`-domain logic, so each of `canonical-knowledge` and `knowledge-publication` implements its own thin generator-info wrapper (duplicating only ~15 lines of version-probing glue, not the atomicity primitive). Both `canonical-knowledge` and `knowledge-publication` declare `knowledge-workbench-runtime` explicitly as a dependency in their own `pyproject.toml` — no implicit/transitive reliance.

This decision requires a narrow specification amendment before Wave 2 (see `docs/superpowers/specs/phase-4-5-core-knowledge-plugin-domain-refactoring-spec.md`'s new §13c), covering: why `atomic_output` is not a contract, why duplication was rejected, the allowed runtime-utility scope (and the explicit non-goal of becoming a generic dumping ground), independent packaging/testing/versioning for the new distribution, and the requirement that both consuming plugins declare it explicitly. Final distribution name and starting version remain Wave 1 human decisions, recorded in `wave-1-decisions.json`.

This supersedes the two options below, which are retained for the record as the original (rejected) proposal.

---

## Original proposal (superseded, retained for the record)

## Provenance note

Same as `wave-1-analyze-structure-split-decision.md`: "same content as Revision 2 Wave 1 Step 2" refers to a plan revision not present anywhere in this repository's history. Derived fresh below, grounded in the real files.

## `contracts.py` (533 lines, 15 dataclasses)

Already settled by the plan itself and Wave 0's classification (`NEUTRAL_CONTRACT_DISTRIBUTION`, `SHARED_CONTRACT` dependency classification on every edge touching it): splits into the five schema modules of `contracts/python/src/knowledge_workbench_contracts/`. Mapping of the 15 existing dataclasses onto the five contract modules:

| Existing `contracts.py` class | New contract module |
|---|---|
| *(none — new concept introduced by the four-way split)* | `normalized_source_document.py` — schema for what `source-document-extraction` produces: extracted markdown text + media manifest. Did not exist as a formal contract in the monolithic plugin because extraction and analysis were never separated before. |
| `SourceFingerprint`, `ManifestSourceFingerprint`, `StructuralAnchor`, `Confirmation`, `ConversionPlan` | `analysis_plan.py` |
| `ChunkMetadata`, `ManifestChunk`, `ManifestGenerator`, `Manifest` | `canonical_package.py` |
| `PublicationMapEntry`, `PublicationMap` | `publication_map.py` |
| `RenderResult` | `rendered_output_profile.py` |
| `ValidationIssue`, `ValidationReport` | Used by both `canonical_package.py` and `rendered_output_profile.py` validation paths — defined once in `canonical_package.py` (the earlier-produced contract) and imported by `rendered_output_profile.py`, not duplicated. |

Wave 1 Step 3 implements each module's schema dataclass(es) + `validate()` function, following `contracts.py`'s existing `_require`/`_check_schema_version` pattern. **Full field-by-field porting of every dataclass's current behavior is Waves 2-5 work** (per the plan's own "Move/adapt legacy scripts" step), not Wave 1 — Wave 1 proves the distribution is real, buildable, and installable with a correct, minimal schema for each of the five contracts.

## `cli.py` (385 lines)

Settled by the plan's own Known File Inventory table: **"compatibility orchestrator (not moved)"**. It stays in `plugins/docx-to-content/scripts/cli.py` through Wave 7, importing from whichever new packages are installed (via the compatibility-shim mechanism described in the Waves 2-5 common step sequence), then is retired along with the rest of `docx-to-content` in Wave 8. No new plugin owns it.

## `convert.py` (316 lines, 6 functions)

Per the plan's table: **"split source-extraction/canonical-knowledge."** Reading the actual functions:

| Function | Proposed domain |
|---|---|
| `run_pandoc_extraction` | `source-document-extraction` — a second direct-`pandoc`-invocation function, structurally parallel to `analyze_structure.py`'s `_run_pandoc_raw` (see the split decision doc). These two should likely become a single shared extraction primitive inside `source-document-extraction`, not two separate functions doing the same kind of work — flagged here as a **Wave 2 implementation decision**, not decided in this document. |
| `apply_cleanup_pipeline`, `_relativize_media_refs`, `_run_conversion_pipeline`, `convert_document`, `convert_and_promote` | `canonical-knowledge` — cleanup, chunking-preparation, validation, and atomic promotion of the canonical package. Consumes the `analysis-plan` contract (from `knowledge-analysis`) and produces `canonical-package`/`publication-map`, matching the Wave 4 table exactly. |

## `atomic_output.py` (173 lines)

Per the plan's table: **"duplicated: canonical-knowledge + knowledge-publication."** The module's own docstring states plainly: *"Nothing about this module is canonical-package-specific: `create_staging_dir`/`promote` operate on plain directories and know nothing about manifests, chunks, or renderers."* This is a genuinely generic staging/atomic-promotion utility, not domain logic — which raises a real alternative to the plan's default "duplicate it" disposition:

**Two options, presented for the human decision (not resolved here):**

1. **Duplicate (the plan's stated default):** copy `atomic_output.py` verbatim into both `canonical-knowledge` and `knowledge-publication`. Simple, but creates two copies of atomicity-safety-critical logic that must be kept in sync by hand if ever fixed (e.g. the Task-18-era `promote()` crash-recovery logic).
2. **Promote to the neutral contracts distribution** (`knowledge_workbench_contracts`), alongside `tree_hash.py`. This avoids duplication, but requires resolving one real dependency wrinkle first: `build_generator_info`/`write_generator_info` currently call `dependencies.probe_pandoc()`/`probe_soffice()` — and `dependencies.py` is `source-document-extraction`-domain per the plan's table, so the neutral distribution cannot import it (no plugin's implementation package may be imported by another plugin or by the neutral distribution, per the plan's dependency-boundary rule). If Option 2 is chosen, `create_staging_dir`/`promote` (pure filesystem operations, no `dependencies.py` dependency) move to the contracts distribution, while `build_generator_info`/`write_generator_info` (which do depend on `dependencies.py`) are **not** promoted — each of `canonical-knowledge` and `knowledge-publication` implements its own thin `write_generator_info` using its own available version-probing (duplicating only the ~15-line generator-info logic, not the atomicity primitive).

**This document's original recommendation was Option 2** (promote to `knowledge_workbench_contracts`) — **rejected by the human reviewer**, who instead approved a third option not listed above: a new, separate `knowledge_workbench_runtime` distribution (not the contracts distribution) for the atomicity primitive only. See "Approved `atomic_output.py` disposition (final)" at the top of this document for the actual decision.
