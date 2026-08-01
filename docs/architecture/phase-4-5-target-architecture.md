# Phase 4.5 Target Architecture

**Date:** 2026-08-01 (Wave 1)
**Status:** Reflects the Wave 1-approved decisions in `docs/superpowers/plans/phase-4-5-evidence/wave-1-decisions.json`. Waves 2-5 implement this; nothing described here has been physically extracted yet — `plugins/docx-to-content/` remains the single running plugin until Wave 8.

## Distribution graph

```
                         ┌─────────────────────────────────┐
                         │   knowledge_workbench_contracts  │
                         │   (types, schemas, validation     │
                         │    only — no runtime logic)       │
                         │                                    │
                         │  normalized_source_document.py    │
                         │  analysis_plan.py                 │
                         │  canonical_package.py              │
                         │  publication_map.py                │
                         │  rendered_output_profile.py        │
                         │  tree_hash.py  repo_root.py*       │
                         └───────────────┬────────────────────┘
                                         │ declared dependency
              ┌──────────────────────────┼──────────────────────────┬──────────────────────────┐
              │                          │                          │                           │
              ▼                          ▼                          ▼                           ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│ source-document-       │  │ knowledge-analysis     │  │ canonical-knowledge    │  │ knowledge-publication  │
│ extraction              │  │                         │  │                         │  │                         │
│                          │  │                         │  │                         │  │                         │
│ extract_and_normalize() │→│ recommend_from_         │→│ build_canonical_        │→│ render()                │
│                          │  │  normalized()           │  │  package()              │  │                         │
│ owns (post-split):       │  │ owns (post-split):      │  │ owns:                   │  │ owns:                   │
│ - _run_pandoc_raw        │  │ - topic-boundary        │  │ - convert.py (minus     │  │ - renderers/*            │
│ - heading parsing        │  │   reasoning             │  │   run_pandoc_extraction)│  │                          │
│ - source statistics      │  │ - recommend_strategy    │  │ - canonical_package.py  │  │ Declares:                │
│ - defect detection       │  │ - analysis-plan          │  │ - chunking/dispositions │  │ - contracts              │
│ - dependencies.py        │  │   generation             │  │ - identity/media_       │  │ - runtime (own thin      │
│ - emf_convert.py         │  │ - topic_grouping.py     │  │   disposition            │  │   generator-info)       │
│ - pandoc_fixes/* (6)     │  │                          │  │ - publication_map.py     │  │                          │
│ - path_safety.py         │  │ Declares:                │  │ - validate_canonical.py  │  │                          │
│ - pandoc_validate.py     │  │ - contracts              │  │ - hashing.py             │  │                          │
│ - convert.py's           │  │                          │  │ - own thin generator-info│  │                          │
│   run_pandoc_extraction  │  │                          │  │                          │  │                          │
│   (unification with      │  │                          │  │ Declares:                │  │                          │
│   _run_pandoc_raw is a   │  │                          │  │ - contracts               │  │                          │
│   Wave 2 implementation  │  │                          │  │ - runtime                │  │                          │
│   decision)              │  │                          │  │                          │  │                          │
│                          │  │                          │  │                          │  │                          │
│ Declares: contracts       │  │                          │  │                          │  │                          │
└───────────┬──────────────┘  └──────────────────────────┘  └────────────┬─────────────┘  └────────────┬─────────────┘
            │                                                              │                             │
            └──────────────────────────────┬───────────────────────────────┴──────────────┬──────────────┘
                                            │                                               │
                                            ▼                                               ▼
                         ┌─────────────────────────────────┐         ┌─────────────────────────────────┐
                         │   knowledge_workbench_runtime     │         │   plugins/docx-to-content         │
                         │   (small deterministic runtime     │         │   (retained through Wave 7/8       │
                         │    primitives — NOT a general       │         │    as a compatibility layer)       │
                         │    shared-utility dumping ground)  │         │                                    │
                         │                                    │         │   cli.py — RETAINED, not moved:    │
                         │  atomic_output.py                  │         │   - cmd_analyze (calls extract_    │
                         │    create_staging_dir()            │         │     and_normalize + recommend_     │
                         │    promote()                       │         │     from_normalized in sequence)   │
                         │                                    │         │   - cmd_confirm / cmd_convert /    │
                         │  (build_generator_info/             │         │     cmd_render (compatibility      │
                         │   write_generator_info NOT here —  │         │     wrappers over the new           │
                         │   depend on dependencies.py,        │         │     packages)                      │
                         │   duplicated per-domain instead)   │         │                                    │
                         └─────────────────────────────────┘         └─────────────────────────────────┘
```

`*` `repo_root.py` is exported for repository-tooling use only (Wave 6 integration-evidence
generation) — never imported by any plugin's production code or by `knowledge_workbench_runtime`,
enforced by `tools/phase-4-5-core-plugin-refactoring/dependency_boundary.py`.

## Skill disposition (approved, Wave 1 — reassessed in Wave 7, not pre-decided)

| Skill | Disposition |
|---|---|
| `analyze-document` | `TEMPORARY_COMPATIBILITY_WRAPPER` |
| `convert-document` | `TEMPORARY_COMPATIBILITY_WRAPPER` |
| `render-content` | `TEMPORARY_COMPATIBILITY_WRAPPER` |
| `orchestrate-conversion` | `RETAINED_PUBLIC_ORCHESTRATOR` — **not** retired in Wave 6, unlike the plan's original proposal. Preserves the `analyze → human confirmation → canonical construction → render` sequence as the intentional public workflow entry point. Orchestration only, no domain logic. |

All four are reassessed in Wave 7 using the final consumer scan — this diagram records the Wave 1 approval, not a Wave 7 retirement decision.

## What Wave 0's 22 flagged edges resolve to

Of the 22 edges Wave 0 flagged `REQUIRES_HUMAN_DECISION` (touching `analyze_structure.py`, `convert.py`, or `atomic_output.py` — all three now have approved dispositions above), **17 are resolved** by this wave's decisions (visible in `wave-0-classified-edges.json` as `PROVISIONALLY_ACCEPTED`, with `proposed_source_domain`/`proposed_target_domain` still literally `UNRESOLVED` at whole-script granularity where the split is function-level, since a script-level dependency graph cannot represent a per-function split — Wave 2's implementation resolves the concrete new-file location). **5 edges remain genuinely open**, not covered by anything approved this round — real cross-domain boundary questions deferred to the relevant extraction wave:

- `package.py -> topic_grouping.py`
- `topic_grouping.py -> identity.py`
- `renderers/protocol.py -> canonical_package.py` (the renderer-reads-canonical-internals question, flagged since Wave 0)
- `renderers/validate_rendered.py -> path_safety.py`
- `validate_canonical.py -> pandoc_validate.py`

## Non-goals recorded in this wave

- `knowledge_workbench_runtime` is explicitly **not** a general-purpose shared-utility distribution — its scope is `atomic_output.py`'s two atomicity primitives only, per spec §13c. Adding anything else to it requires the same kind of explicit human decision this wave required for `atomic_output.py` itself.
- Marketplace adoption remains `NOT_APPLICABLE_WITH_DECISION` — no marketplace catalog is created in Phase 4.5.
