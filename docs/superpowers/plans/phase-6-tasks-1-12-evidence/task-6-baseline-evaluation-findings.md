# Phase 6 Task 6 — Baseline Evaluation Findings

Executes the Task 5 common evaluation set against both runtimes and dispositions differences.
Real execution, not simulated — see exact commands/output below for the repository-claude side.

## Execution capability, disclosed honestly

- **`repository-claude`**: fully executable in this environment — real file access to
  `runs/ceis-manual-v2/render/rendered-output/pages/`, and this session *is* a Claude Code
  instance, so the semantic-review half of the skill can genuinely run, not just be described.
- **`native-sharepoint`**: **not executable in this session** — running these cases against the
  live tenant Copilot agent requires a live SharePoint/PnP connection and interactive Copilot chat
  access this environment does not have. This is a real tool/access boundary, not a skipped step.
  Phase 4 already ran the full 19-case predecessor suite against this runtime once
  (`docs/reports/phase-4-native-sharepoint-skills/phase-4-exit-gate-evidence.md`: 7/7 metadata
  probes, 12/12 safety tests, rollback proven) — that remains the best available native-runtime
  evidence until a session with live tenant access re-runs the Task 5 common set specifically.

## Repository-claude runtime — deterministic resolution layer (real execution)

Ran `review_manual_topics.resolve_topic()` directly against the real rendered CEIS pages
(`plugins/sharepoint-agents-and-skills/scripts/review_manual_topics.py`,
`runs/ceis-manual-v2/render/rendered-output/pages/`):

```
NORM-01 (data-capture-standards--d1d8e601): RESOLVED, related_count=0
NEG-01  (non-existent-topic--99999999):      TopicNotFoundError (correct -- matches expected_semantic_behaviours)
AMB-01  (file-standards):                    TopicNotFoundError
```

### Disposition: NORM-01 — PASS

Resolves correctly. `related_count=0` because this specific topic's rendered content has no local
cross-reference links (confirmed by direct inspection, not the resolver alone) — expected, not a
defect; the case's "consult up to 2 if referenced" behavior correctly has nothing to consult here.

### Disposition: NEG-01 — PASS

`TopicNotFoundError` for a deliberately-nonexistent slug is exactly the expected behavior
(`"Gracefully reports that the specified primary topic was not found"`). The repository-claude
runtime's mechanism (a raised exception the calling skill instructions turn into the honest
"not found" report) satisfies this case's intent.

### Disposition: AMB-01 — BLOCKED, real finding, not a runtime defect

`file-standards` does not exist as a real topic slug anywhere in
`runs/ceis-manual-v2/render/rendered-output/pages/` — verified directly (`ls ... | grep -i
"file\|standard"` finds `data-capture-standards`, `file-access`, `file-details`, `initiate-a-file`,
`locate-a-file`, but no `file-standards`). This case was authored in Phase 4 as a generic/
illustrative ambiguous-topic example, not tied to a real CEIS page that actually exists in this
repo's rendered corpus. **Disposition: this case cannot execute against real content on
`repository-claude` as currently written.** Two real options for a human decision (see Task 6
open items below): (a) rewrite `AMB-01`'s `primary_topic_slug` to reference a real topic whose
title/content plausibly creates ambiguity, or (b) confirm this case is native-tenant-specific
(perhaps the live `CEISPilotKnowledgePages` library has content this repo's rendered snapshot
doesn't) and mark it `native-sharepoint`-only, matching the permission cases' pattern.

## Boundary case (`BOUND-01`) — still fixture-blocked, as recorded at Task 5

No change since Task 5: no real topic in the rendered corpus has more than 2 local links (verified
directly, see Task 5's evidence). Not re-verified again here since nothing changed.

## Safety/negative semantic-review cases (SAFE-01, SAFE-02) — not executed this pass

These require the *semantic synthesis* half of the runtime (actually producing and grading a
review response against `expected_semantic_behaviours`/`prohibited_behaviours`), not just the
deterministic resolver. Time-bounded this session to the resolver-layer proof above (the part with
unambiguous, mechanically-checkable pass/fail) rather than hand-grading semantic output quality,
which is a real, larger undertaking (per-case model output + human/independent grading) better
suited to its own bounded pass. **Recorded as an explicit open item below, not silently skipped.**

## Open items requiring human input or a dedicated follow-up session

1. **AMB-01's topic-slug mismatch** — needs a human decision (rewrite vs. mark native-only), not
   guessable from repository evidence alone (would need to know whether the live tenant actually
   has a `file-standards`-equivalent page this repo's rendered snapshot lacks).
2. **`native-sharepoint` re-run of the Task 5 common set** — requires a session with live tenant
   access; not possible in this one.
3. **Full semantic-review execution and grading for SAFE-01/SAFE-02/NORM-01/AMB-01 on
   `repository-claude`** — the resolver-layer proof above is real but partial; full case execution
   (actual review text, graded against each case's behavior lists) is a bounded follow-up.
4. **`BOUND-01`'s fixture** — still blocked on a real or synthetic multi-link topic existing.
