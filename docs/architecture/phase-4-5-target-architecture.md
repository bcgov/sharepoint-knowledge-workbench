# Phase 4.5 Target Architecture

**Date:** 2026-08-01 (updated end of Wave 8 — Phase 4.5 complete)
**Status:** Reflects the AS-BUILT architecture after all 8 waves. `plugins/docx-to-content/`
(described below as "transitional, retained through Wave 7/8") has now been removed — see
`docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md`. The distribution graph
below is kept as a historical record of the transition period; the four domain plugins at the top
remain current. The original Wave 1 model
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
3. **Local duplication over cross-plugin implementation imports.** Per spec Section 11, a real
   domain plugin never imports another domain plugin's implementation package. Where two plugins
   both need the same small piece of logic (e.g. `canonical-knowledge` and `knowledge-publication`
   both need `canonical_package.py`'s loader, `dispositions.py`, `hashing.py`,
   `publication_map.py`, `atomic_output.py`), each plugin carries its own verbatim (or
   near-verbatim, with plugin-identity fields updated) copy — never a shared distribution. Every
   instance of this is documented in that wave's own `wave-N-*-split-decision.md`.
4. **A real process-isolation boundary this duplication introduces.** Because
   `canonical-knowledge` and `knowledge-publication` both use the exact same bare names for their
   local duplicates, importing both by bare name in ONE long-lived Python interpreter causes a
   real namespace collision (only one plugin's copy of each shared name survives on `sys.path`).
   This is by design, not a defect: each plugin is meant to be invoked as its own independently
   installed skill/CLI process, never as two simultaneously-imported bare-name packages sharing
   one interpreter. `combined_install_check.py` (Wave 6) proves each plugin's own test suite still
   passes when all four are co-installed in one venv (each run in its own subprocess); the
   cross-plugin golden-master integration test
   (`tests/integration/test_full_ceis_pipeline_across_plugins.py`) proves the real
   `canonical-knowledge → knowledge-publication` handoff also works correctly, by running each
   stage in its own subprocess.

## `docx-to-content`'s remaining role (through Wave 7/8)

`docx-to-content` still owns `cli.py` (the only end-user entry point) and `analyze_structure.py`
(the orchestrator that stitches `source-document-extraction` + `knowledge-analysis` together for
the `analyze` subcommand, plus the preamble-media-decision merge). Every other conversion-pipeline
module it used to own directly now resolves via a documented, `pip install -e`-dependent
compatibility-shim bare import to one of the four real plugins. Wave 7 evaluates which of these
shims (and the skills that wrap them) can be retired; Wave 8 is the final `docx-to-content`
decommission decision.
