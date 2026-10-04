# Migration planning pipeline and honest outcomes

## Contents

- [The pipeline](#the-pipeline)
- [Deterministic half vs. templating half](#deterministic-half-vs-templating-half)
- [Honest outcomes](#honest-outcomes)
- [Related rules](#related-rules)

## The pipeline

`sharepoint-site-migration` plans a site migration in four implemented stages. All of it is pure planning with no tenant I/O; see
`pipeline-overview.mmd` for the diagram.

1. **Setup** (`sharepoint-initialize-migration-project`): confirms the repository-root `config.psd1` exists with a `Connection` block, then creates
   a per-migration working directory.
2. **Discover** (`sharepoint-normalize-migration-inventory`): validates and normalizes an already-produced source-site export directory.
3. **Analyze (Stage 3a)** (`sharepoint-analyze-migration-dependencies`): shapes the export into a dependency matrix, gated by completeness checks, and
   computes a wave order with `wave_planning.plan_waves`.
4. **Generate (Stage 3b)** (`sharepoint-scaffold-migration-wave-scripts`): templates one wave-script skeleton per wave plus a single human wave guide, one wave
   at a time and never an unattended run-everything script.

`sharepoint-plan-migration-waves` exposes `wave_planning.plan_waves` on its own for a caller that already has a dependency-annotated object list.

## Deterministic half vs. templating half

Stage 3a is plain, TDD-tested Python: the same input always produces the same output, which is why it is not an agent-assisted step. Stage 3b is also a
thin, pure, deterministic templating function, not an AI-model call, so its output is exactly test-verifiable (real names present, zero project-specific
leakage, honest refusal on a `Failed` matrix). Live-tenant discovery (`sharepoint-collection`, Part A) is design-only and not authorized to build; the
discover stage accepts an export a human already produced.

## Honest outcomes

All stages report `Outcome` from `provisioning_outcomes.py`: `OBSERVED`, `EMPTY`, `UNAVAILABLE` or `FAILED`. Missing or incomplete input is reported with the exact
issue named; nothing is fabricated or silently skipped.

## Related rules

Three plugin rules sit alongside the skills (linked into the skills that use them): `deployment-decision-principles.md` (whether a completeness finding
warrants a generated wave script or a manual-handling recommendation), `test-driven-wave-deployment.md` (why the split exists and why each wave is a gated
step) and `schema-driven-sharepoint-deployment.md`.
