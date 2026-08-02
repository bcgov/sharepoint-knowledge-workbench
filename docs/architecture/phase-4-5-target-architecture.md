# Phase 4.5 Target Architecture

**Date:** 2026-08-01 (updated end of Wave 8 — Phase 4.5 complete)
**Status:** Reflects the AS-BUILT architecture after all 8 waves. `plugins/docx-to-content/`
(described below as "transitional, retained through Wave 7/8") has now been removed — see
`docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md`. The distribution graph
below is kept as a historical record of the transition period, using the plugin names in effect
during Waves 1-8 (`knowledge-analysis`, `canonical-knowledge`, `knowledge-publication`) — see
`docs/reports/phase-4-5-core-plugin-refactoring/plugin-skill-name-migration.md` for the
2026-08-02 rename to `document-structure-analysis`/`structured-content-assembly`/
`structured-content-rendering`. The four domain plugins at the top remain current under their new
names. The original Wave 1 model
described a shared `knowledge_workbench_contracts`/`knowledge_workbench_runtime` distribution
pair — that model was corrected mid-Wave-2 (see `wave-2-contract-materialization-correction.md`
and `wave-2-flat-scripts-correction.md`) and no longer reflects reality. **No shared contracts or
runtime distribution exists or was ever published.** Each plugin materializes its own
contract/runtime code.

## As-built distribution graph

```
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│ source-document-       │  │ knowledge-analysis     │  │ canonical-knowledge    │  │ knowledge-publication  │
│ extraction (Wave 2)    │  │ (Wave 3)               │  │ (Wave 4)               │  │ (Wave 5)               │
│                        │  │                        │  │                        │  │                        │
│ extraction.py:         │  │ analysis.py:           │  │ canonical_knowledge.py:│  │ knowledge_publication  │
│  extract_and_          │  │  recommend_from_       │  │  build_canonical_      │  │  .py: render()         │
│  normalize()           │  │  normalized()          │  │  package()             │  │                        │
│                        │  │                        │  │                        │  │                        │
│ Produces:               │  │ Produces:              │  │ Produces:              │  │ Produces:              │
│  normalized-source-    │  │  analysis-plan          │  │  canonical-package,    │  │  rendered-output-      │
│  document               │  │  (schema/analysis_plan │  │  publication-map        │  │  profile               │
│  (schema/normalized_    │  │   .py)                 │  │  (canonical_schema/)    │  │  (render_result.py)    │
│  source_document.py)    │  │                        │  │                        │  │                        │
│                        │  │ Consumes:               │  │ Consumes:              │  │ Consumes:              │
│                        │  │  normalized-source-     │  │  analysis-plan          │  │  canonical-package,    │
│                        │  │  document (local        │  │  (local consumer copy: │  │  publication-map        │
│                        │  │  parsing only, no       │  │  canonical_schema/      │  │  (local consumer copy: │
│                        │  │  cross-plugin import)   │  │  analysis_plan.py)     │  │  canonical_schema/)    │
│                        │  │                        │  │                        │  │                        │
│ pip install -e         │  │ pip install -e         │  │ pip install -e         │  │ pip install -e         │
│  plugins/source-        │  │  plugins/knowledge-    │  │  plugins/canonical-    │  │  plugins/knowledge-    │
│  document-extraction    │  │  analysis               │  │  knowledge              │  │  publication            │
│                        │  │                        │  │                        │  │                        │
│ Zero dependency on any  │  │ Zero dependency on any │  │ Zero dependency on any │  │ Zero dependency on any │
│ other workbench dist.   │  │ other workbench dist.  │  │ other workbench dist.  │  │ other workbench dist.  │
└───────────┬────────────┘  └───────────┬────────────┘  └───────────┬────────────┘  └───────────┬────────────┘
            │                            │                            │                            │
            └────────────────────────────┴──────────────┬─────────────┴────────────────────────────┘
                                                          │  (compatibility-shim bare imports ONLY;
                                                          │   retired in Wave 7/8)
                                                          ▼
                                     ┌─────────────────────────────────────┐
                                     │   plugins/docx-to-content            │
                                     │   (transitional, retained through   │
                                     │    Wave 7/8 as an orchestration      │
                                     │    layer over the four real plugins) │
                                     │                                       │
                                     │   cli.py — analyze/confirm/convert/  │
                                     │   render/run subcommands, still the  │
                                     │   only entry point end users invoke  │
                                     │   directly; delegates to the four    │
                                     │   installed plugins via bare-import  │
                                     │   compatibility shims, documented    │
                                     │   inline and retired per             │
                                     │   wave-1-decisions.json.             │
                                     └───────────────────────────────────────┘
```

## Key corrections from the original (Wave 1) model

1. **No shared distribution.** The Wave 1 plan's `knowledge_workbench_contracts` (types/schemas)
   and `knowledge_workbench_runtime` (shared runtime primitives) packages were never built as
   real, separately-installed distributions — the mid-Wave-2 correction replaced them with each
   contract's producer plugin materializing its own authoritative schema, and each plugin carrying
   plugin-local **consumer copies** (kept in sync by hand, documented per-file) of any contract it
   only consumes. `contracts/python/` and `runtime/python/` were deleted entirely.
2. **Flat `scripts/` layout, not `src/<import_name>/`.** Every plugin uses bare top-level module
   names (`scripts/extraction.py`, not `scripts/source_document_extraction/extraction.py`),
   matching `docx-to-content`'s own pre-existing convention. Cohesive multi-file families are
   grouped into a subfolder (`scripts/pandoc/`, `scripts/canonical_schema/`,
   `scripts/renderers/`), never a package named after the plugin itself.
3. **Cross-plugin implementation sharing without a shared distribution.** Per spec Section 11, a
   real domain plugin never *imports* another domain plugin's implementation package at runtime.
   Where two plugins need the same small piece of logic (e.g. `structured-content-assembly` and
   `structured-content-rendering` both need `canonical_package.py`'s loader, `dispositions.py`,
   `hashing.py`, `publication_map.py`, `atomic_output.py`), each consumer plugin now carries a
   **managed cross-plugin file-level symlink** (via `symlink_manager.py`, recorded in
   `symlinks.json`) to the canonical owner's real file, rather than a hand-maintained duplicate
   copy — `setuptools` dereferences the symlink into a real, independent file when building each
   plugin's own wheel, so the installed/distributed artifact never depends on the producer plugin
   being present. **This superseded the original hand-duplication approach** each wave's own
   `wave-N-*-split-decision.md` describes; see
   `docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md` for the
   full rationale and verification evidence.
4. **A real process-isolation boundary this sharing introduces.** Because
   `structured-content-assembly` and `structured-content-rendering` both use the exact same bare names for their
   shared modules, importing both by bare name in ONE long-lived Python interpreter causes a
   real namespace collision (only one plugin's copy of each shared name survives on `sys.path`).
   This is by design, not a defect: each plugin is meant to be invoked as its own independently
   installed skill/CLI process, never as two simultaneously-imported bare-name packages sharing
   one interpreter. `combined_install_check.py` (Wave 6) proves each plugin's own test suite still
   passes when all four are co-installed in one venv (each run in its own subprocess); the
   cross-plugin golden-master integration test
   (`tests/integration/test_full_ceis_pipeline_across_plugins.py`) proves the real
   `structured-content-assembly → structured-content-rendering` handoff also works correctly, by running each
   stage in its own subprocess.

## `docx-to-content`'s remaining role (through Wave 7/8)

`docx-to-content` still owns `cli.py` (the only end-user entry point) and `analyze_structure.py`
(the orchestrator that stitches `source-document-extraction` + `document-structure-analysis` together for
the `analyze` subcommand, plus the preamble-media-decision merge). Every other conversion-pipeline
module it used to own directly now resolves via a documented, `pip install -e`-dependent
compatibility-shim bare import to one of the four real plugins. Wave 7 evaluates which of these
shims (and the skills that wrap them) can be retired; Wave 8 is the final `docx-to-content`
decommission decision.
