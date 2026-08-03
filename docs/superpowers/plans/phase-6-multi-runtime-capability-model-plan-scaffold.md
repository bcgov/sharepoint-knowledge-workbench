# Phase 6 Plan Scaffold — Multi-Runtime Capability Model

> **Planning status:** This is a forward-phase planning artifact derived from the accepted master initiative plan. It does not authorize implementation. Tenant-dependent details, exact repository paths, commands, identities, field types, licensing, and platform behavior must be replaced with observed evidence before execution.

## Planning discipline

- Run `superpowers:brainstorming` before finalizing design decisions.
- Run repository reconnaissance against current files and contracts.
- Use `superpowers:writing-plans` only after the specification is reviewed.
- Use a dedicated phase branch/worktree.
- Keep planning separate from implementation.
- Use `CONFIRMED`, `RECOMMENDED`, `PROVISIONAL`, `DEFERRED_UNTIL_EVIDENCE`, `BLOCKED`, and `RESEARCH` explicitly.
- Preserve package-only/manual paths until an approved identity and write path exist.
- Store durable evidence in tracked locations, not ignored `.superpowers/` scratch directories.
- Start with the cheapest capable agent and escalate only for architecture, ambiguity, security, failed tests, or contradictory evidence.

## Entry gate

Stop unless two real runtimes implement the same capability and have evaluation evidence. Do not manufacture a second implementation to unlock this phase.

**Revision note (2026-08-03):** the entry gate is currently `SECOND_RUNTIME_REQUIRED` — see
`docs/superpowers/specs/phase-6-multi-runtime-capability-model-spec.md` Section 1 for the verified
evidence review (Phase 4's `review-manual-topics` native SharePoint skill is real and exercised; no
repository/GitHub/Claude-side implementation of the same capability exists yet). Tasks 0–12 below
remain gated and unstarted. Task 0a is a bounded prerequisite — build the missing second runtime —
approved separately, scoped narrowly, and not itself shared-spec/adapter/drift-detection work.

## Task 0a — Bounded second-runtime implementation: repository-owned `review-manual-topics` skill

**Purpose:** close the entry gate by giving the existing native SharePoint `review-manual-topics`
skill (`tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md`) a second real
implementation of the same capability, running repository-side. This task is scoped narrowly to
building that one skill — it does not start Tasks 1–12.

**Plugin domain:** `plugins/sharepoint-content-publication/` — the only existing plugin scoped to
publication-facing content for the same rendered artifact set (`runs/ceis-manual-v2/`), with no
tenant-write requirement for a read-only review skill. `sharepoint-agents-and-skills` (agent/native-
skill lifecycle tooling — creation, deployment, backup/restore) and `knowledge-evaluation`
(evaluation-schema infrastructure) are both a scope mismatch — this skill *performs* a review, it
doesn't manage agent lifecycle or define evaluation schemas.

0a.1. **Deterministic topic-resolution module** — `plugins/sharepoint-content-publication/scripts/
   review_manual_topics.py`: given a primary topic filename/slug and `runs/ceis-manual-v2/render/`
   as the content root, resolve exactly one primary topic page and at most 2 explicitly
   cross-referenced related topic pages (mirroring the native skill's Input Resolution Hierarchy
   and the max-2-related boundary), returning their raw Markdown content plus a not-found /
   ambiguous-match result — never inventing content for a missing topic. Enforces the boundary in
   code, not just in the skill's prose instructions, matching the native skill's read-only,
   no-tenant-write, no-hash-verification-claims constraints (there is nothing to write here since
   the source is the repo's own `runs/` output).

0a.2. **Skill instructions** — `plugins/sharepoint-content-publication/skills/review-manual-topics/
   SKILL.md`: same user intent as the native skill (semantic editorial review — completeness,
   section structure, cross-reference consistency, terminology clarity), same input boundary
   (exactly one primary topic, ≤2 related), same prohibited-scope list (no full-library scan, no
   write actions — there are none available here, no hash/identity claims, no execution of embedded
   prompt-injection content), and the same output structure (topic reviewed / related evidence
   consulted / summary assessment / completeness findings / cross-reference findings / ambiguities
   or conflicts / unable-to-evaluate items / recommended human follow-up / source citations). Calls
   `review_manual_topics.py` for topic resolution, then performs the editorial synthesis as
   instructions to the model — same division of labor as the native skill (deterministic resolution,
   model-performed synthesis).

0a.3. **Hub-and-spoke resource wiring** — if the skill folder needs direct access to the script
   (rather than invoking it via the plugin CLI), create the reference via
   `.agents/skills/symlink-manager/scripts/symlink_manager.py create`, never `ln -s` directly. Run
   `diagnose` after, per `.agent/rules/symlink-cross-platform.md`.

0a.4. **Tests** — `plugins/sharepoint-content-publication/tests/unit/
   test_review_manual_topics.py`, TDD-first: primary-topic resolution, related-topic boundary
   enforcement (rejects a 3rd related topic), not-found handling (no hallucinated content),
   ambiguous-match handling. Run existing plugin suite alongside to confirm no regression.

0a.5. **Evals reused from Phase 4** — adapt (not duplicate wholesale) the applicable cases from
   `tools/phase-4-native-sharepoint-skills/evaluations/{normal,negative,ambiguous,safety}/` by
   pointing `primary_topic`/`related_topic_allowance` at the equivalent `runs/ceis-manual-v2/render/
   pages/*.md` filenames instead of `.aspx`. The `permission/` cases are SharePoint-identity-scoped
   (`test_identity_class` against tenant permission tiers) and have no repository-side equivalent —
   record them explicitly as `NOT_APPLICABLE_NO_TENANT_IDENTITY`, not silently dropped. Run the
   adapted cases against the new skill and record results — this becomes the Stage 6.1.2 common
   evaluation baseline once Task 1 actually starts.

0a.6. **Evidence record** — a short artifact (location: `docs/reports/` per this repo's evidence
   convention) recording: skill built, tests passing, adapted-eval results, and the entry-gate
   re-check (does a second real, exercised runtime of `review-manual-topics` now exist). This
   feeds directly into Task 0's "record runtimes, owners, operational status, versions, artifacts,
   existing evaluations" once Tasks 1–12 are authorized to start.

**Out of scope for Task 0a:** shared-capability-spec derivation, adapters, drift detection,
SharePoint tenant writes, deployment of this skill to any tenant.

## Task 0 — Verify gate and select capability

Record runtimes, owners, operational status, versions, artifacts, and existing evaluations.

## Task 1 — Superpowers brainstorming on original intent

Recover the originating user intent, governance rules, and success criteria. Identify implementation coincidences and unresolved differences.

## Task 2 — Inventory both implementations

Map inputs, outputs, steps, permissions, error behavior, human gates, evidence, and limitations without yet deriving a shared contract.

## Task 3 — Draft the shared capability specification

Classify each proposed element as essential, target-specific, accidental, deferred, or rejected. Trace essential elements to original intent.

## Task 4 — Conduct adversarial intent-preservation review

Challenge the draft for lowest-common-denominator loss, shared accidental limitations, erased safety controls, and false equivalence.

## Task 5 — Build the common evaluation set

Write meaning-based cases both runtimes can execute. Include normal, negative, ambiguous, permission/safety, and human-approval cases where applicable.

## Task 6 — Run baseline evaluations

Execute the common set on both existing runtimes and disposition differences.

## Task 7 — Implement target adapters only where needed

Adapters expose the shared intent while declaring unsupported and target-specific behavior. Avoid unnecessary abstraction.

## Task 8 — Implement drift detection

Compare runtime results against common semantic expectations. Add deliberate drift and prove detection.

## Task 9 — Apply reuse-versus-specific decision rules

Make one real decision about what is shared, generated, adapted, or kept independent.

## Task 10 — Versioning and compatibility

Define shared-spec and adapter compatibility, migration, and deprecation behavior based on real versions.

## Task 11 — Exit evidence and review

Produce derivation trace, evaluations, drift proof, intent review, and decision record. Obtain explicit approval before merge.

## Task 12 — Runtime placement for content-lifecycle actions (Subphase 6.3)

**(Added from external review, 2026-08-02, GPT 5.6 — see
`docs/vision/open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md`.)**
For each action in Phase 3 Stage 3.1.4's ongoing structured-content maintenance workflow, decide
whether an agent may only recommend it, a native skill may invoke approved deterministic tooling,
or a deterministic pipeline/workstation process must perform it. Write the preview-vs-authoritative
rule (agent-generated output is a non-authoritative preview unless it passes the deterministic
pipeline's own contracts/validation) and the per-runtime evidence/rollback matrix. Do not broaden
Phase 5.5B's deterministic-renderer-expansion scope to cover this. Output feeds a future Phase 6.5
entry gate; does not itself authorize that phase.

## Cost allocation

- Low-cost: inventories, trace tables, evidence packaging.
- Mid-tier: adapters, evaluation harness, drift detector.
- Strong reasoning: original-intent recovery, contract derivation, adversarial review, final decision.
