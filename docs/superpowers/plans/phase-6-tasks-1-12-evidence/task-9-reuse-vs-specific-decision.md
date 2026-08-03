# Phase 6 Task 9 — Reuse-vs-Specific Decision Record

One real decision, applying Tasks 3/7's classifications concretely to this capability's actual
artifacts (not a new abstract framework).

## Decision

| Artifact | Disposition | Reasoning |
|---|---|---|
| Capability intent/governance rules (essential list, Task 3) | `SHARED` | Single source of truth: `plugins/sharepoint-agents-and-skills/skills/review-manual-topics/SKILL.md`. Both runtimes' sections already live in one document, not two forked copies — kept this way; a future edit to a shared rule (e.g. the related-topic cap) only needs one file changed. |
| Evaluation cases (Task 5's common set) | `SHARED` | One canonical set at `plugins/sharepoint-agents-and-skills/evaluations/common/`, `applicable_runtimes` field declares scope per case rather than forking the set. |
| Deterministic topic-resolution logic | `INDEPENDENT` (target-specific implementation of a shared policy) | `review_manual_topics.py` (repository-claude) has no equivalent on the native-sharepoint side to share code with — the native runtime's resolution is agent-context behavior, not code. Sharing is at the *policy* level (proven equivalent, Task 4 Finding 3), not the code level. Forcing a code-sharing relationship where none can exist would be the "unnecessary abstraction" Task 7 already rejected. |
| Drift-detection tooling (`drift_detection.py`, Task 8) | `SHARED`, but scoped to what's actually comparable | Lives once, in `sharepoint-agents-and-skills` (the plugin that owns both runtimes' `review-manual-topics` definitions) — not duplicated per runtime. Its `detect_drift()` function is runtime-agnostic (accepts a structural `CaseResult`, doesn't care which runtime produced it); `run_case_against_repository_claude()` is the one runtime-specific producer function today. A future `run_case_against_native_sharepoint()` (once live-tenant automation exists) would be `ADAPTED` — new producer function, same shared `detect_drift()` consumer, per this same file. |
| Permission/identity cases (Task 5) | `INDEPENDENT` (native-sharepoint only) | Not shared, not adapted — `repository-claude` has no permission model to adapt these onto (Task 3/4 finding); forcing them onto that runtime would create tests that always trivially "pass" for the wrong reason, hiding rather than proving anything. |

## What this decision does NOT do

Does not create a new abstraction layer, base class, or shared-capability-spec file format beyond
what Tasks 3/5/8 already produced. Task 7 already established the "avoid unnecessary abstraction"
precedent; Task 9's job was to apply reuse/specific/adapted labels to the artifacts that already
exist, not invent new ones to label.
