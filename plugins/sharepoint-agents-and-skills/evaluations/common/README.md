# Common Evaluation Set — `review-manual-topics`

Phase 6 Task 5's deliverable: a meaning-based evaluation set both `review-manual-topics` runtimes
(`native-sharepoint`, `repository-claude`) can execute, reusing Phase 4's original 11 cases
(`tools/phase-4-native-sharepoint-skills/evaluations/`) rather than re-deriving them, plus one new
case Task 4's adversarial review found was missing.

## Contents

11 cases carried forward from Phase 4, each annotated with `applicable_runtimes`:

- **normal (1), negative (1), ambiguous (1), safety (2)** — `applicable_runtimes: ["native-
  sharepoint", "repository-claude"]`. Each also carries a `primary_topic_slug` field (the
  runtime-agnostic topic identifier, stripped of the native runtime's `.aspx`/`.html` extension)
  alongside the original `primary_topic` (kept as originally authored, for the native runtime).
  Per Task 3's `ACCIDENTAL`-classification finding, the file-extension difference is not
  meaningful — each runtime's harness resolves `primary_topic_slug` against its own native
  content format.
- **permission (6)** — `applicable_runtimes: ["native-sharepoint"]` only. Per Task 3/Task 4's
  finding, `repository-claude` has no tenant identity or permission model at all — these cases are
  not applicable there, not a coverage gap.

Plus 1 new case added at Task 5:

- **`case-boundary-01-related-topic-cap-exceeded.json`** — both runtimes. Added because Task 4's
  adversarial review found the original 11-case suite had zero coverage of the related-topic cap
  actually being exceeded (only that it isn't exceeded when the input doesn't invite it). Currently
  `_fixture_status: REQUIRES_FIXTURE` — verified against the real rendered CEIS content
  (`runs/ceis-manual-v2/render/rendered-output/pages/*.md`) that **no existing topic has more than
  2 local cross-reference links** (checked directly, not assumed), so this case cannot run against
  real content as-is. A synthetic fixture topic (or a real multi-link topic, once one exists) is
  required before this case executes — tracked as an open item in Task 6's findings.

## Total: 12 cases (11 reused + 1 new)

## Format

Each case is unchanged from Phase 4's own schema (`case_id`, `category`, `objective`,
`primary_topic`, `related_topic_allowance`, `test_identity_class`, `prompt`, `run_count`,
`expected_semantic_behaviours`, `prohibited_behaviours`), plus this task's additions
(`applicable_runtimes`, and for non-permission cases, `primary_topic_slug`).

## Reuse rationale

Per the design spec's own note (`docs/superpowers/specs/2026-08-02-multi-document-destination-
configuration-design.md` is unrelated; the correct citation is
`docs/superpowers/specs/phase-6-multi-runtime-capability-model-spec.md`'s "Smallest bounded
second-runtime candidate" paragraph): "Phase 4's evaluation cases... are reusable as-is as the
Stage 6.1.2 common evaluation set once both runtimes exist." Both runtimes now exist (Task 0.2/0.3,
merged into `sharepoint-agents-and-skills`). This directory is that reuse, not a rewrite —
`applicable_runtimes` annotations are the only structural addition, added to make each case's
cross-runtime applicability explicit rather than implicit.
