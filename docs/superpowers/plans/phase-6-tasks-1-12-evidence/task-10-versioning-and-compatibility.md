# Phase 6 Task 10 — Versioning and Compatibility

Based on real, current versions — not a speculative scheme for versions that don't exist yet.

## Current real state

- `sharepoint-agents-and-skills` (the plugin owning both `review-manual-topics` runtime
  definitions) is at `version: 0.1.0-alpha.1` (`plugin.yaml`, `.claude-plugin/plugin.json`).
- `review-manual-topics/SKILL.md` carries no separate version field of its own today — per Task
  9's `SHARED` decision, both runtimes' definitions live in one document, versioned implicitly by
  the plugin's own version.
- `drift_detection.py` and `review_manual_topics.py` are both un-versioned individual modules,
  versioned implicitly the same way (part of the plugin's `0.1.0-alpha.1`).

## Decision

**No new, separate version field is introduced for the shared capability spec at this time.**
Justification: a separate version number is only meaningful once there is a real reason to track
compatibility *between* something that could drift independently — e.g., if the native-sharepoint
and repository-claude sections ever split into separate files, or if a second capability adopts
this same shared-spec pattern and needs to declare which spec version it targets. Neither
condition exists yet (Task 9 kept both runtimes in one file specifically to avoid this problem).
Introducing a version field with nothing yet to version against would be exactly the kind of
speculative universal schema the design spec's own Non-goals section rejects (see Task 1's
brainstorming record).

**Compatibility rule, stated for when it does become relevant:** if `SKILL.md` is ever split per
runtime, each split file must declare which `sharepoint-agents-and-skills` plugin version it was
extracted from (e.g. a `Derived-From-Plugin-Version:` header line), and `drift_detection.py`'s
`detect_drift()` must continue to accept a runtime-agnostic `CaseResult`/case-dict pair regardless
of which file version produced them — the function's job is comparing *behavior* against
*expectation*, not tracking spec provenance itself.

**Deprecation rule, stated for when it becomes relevant:** if a case in the common evaluation set
(`plugins/sharepoint-agents-and-skills/evaluations/common/`) is ever retired, it must be moved to
a `deprecated/` subdirectory with a note citing the replacing case, not deleted outright — per
this repo's own `self-evolution-policy.md` Hard Gate #4 (deletions of any file require explicit
human permission) and the general principle that a retired case's history (what it once caught)
is itself evidence.

## What Task 10 explicitly does not do

Does not introduce a formal semver policy, a compatibility matrix, or a migration tool for
versions that don't exist yet. The two real open items from Task 6 (`AMB-01`'s topic-slug mismatch,
`BOUND-01`'s missing fixture) are content/fixture problems, not versioning problems — not
addressed here.
