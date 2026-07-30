# Phase 4 Plan Scaffold — Native SharePoint Skills Pilot

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

Do not finalize or execute this plan until Phase 3.0 and Phase 3 exit evidence satisfy the Phase 4 specification.

## Task 0 — Confirm entry evidence

**Deliverable:** entry-gate checklist.  
**Verification:** every prerequisite links to accepted evidence.  
**Stop condition:** any missing prerequisite blocks execution.

## Task 1 — Run Superpowers brainstorming and select the candidate

Compare `review-manual-topics` with any alternative grounded in real Phase 3 needs. Record selection, rejected alternatives, expected value, risks, and required permissions.

**Evidence:** candidate-selection memo.  
**Commit:** planning artifacts only.

## Task 2 — Verify real input availability

Trace every required input to actual Phase 3 library items, fields, and permissions.

**Tests/evidence:** input-availability matrix; negative cases for missing inputs.

## Task 3 — Define the native skill contract

Specify inputs, outputs, steps, prohibited behavior, confirmation points, error handling, and version metadata.

**TDD:** create schema/contract tests before final artifact generation where repository validation code exists.

## Task 4 — Author and validate `SKILL.md`

Write the target-native artifact against the exact schema observed in Phase 3.0.

**Verification:** repository validation plus tenant acceptance in the designated non-production surface.  
**Evidence:** accepted artifact and validation transcript.

## Task 5 — Prepare manual deployment and rollback

Write exact human steps, permission checks, target-path verification, rollback/removal, and evidence capture.

**No automation.**

## Task 6 — Perform authorized manual deployment

A named human deploys the skill and records every action. Confirm deployed content and permissions match the reviewed package.

**Evidence:** manual deployment log and deployed-version trace.

## Task 7 — Execute normal-case evaluations

Run the approved normal cases against real bounded content.

**Evidence:** inputs, expected outcomes, actual outcomes, reviewer dispositions.

## Task 8 — Execute negative and ambiguous evaluations

Prove honest failure, review escalation, and no fabricated authoritative values.

## Task 9 — Execute permission and safety evaluations

Use at least two approved identities. Test access trimming, result placement, list visibility, and protected-content handling.

**Blocking:** any oversharing, access expansion, or unauthorized write.

## Task 10 — Define lifecycle and retirement

Document owner, versioning, review cadence, retirement, and emergency removal. Exercise removal/rollback in the non-production pilot if authorized.

## Task 11 — Consolidate evidence and retrospective

Produce the Phase 4 evidence report. Classify additional candidate skills as `NEXT`, `LATER`, or `RESEARCH`; do not implement them.

## Task 12 — Exit review and merge gate

Run repository tests, artifact checks, documentation review, and final permission review. Report plugin/marketplace metadata disposition and `git status --short`. Obtain explicit approval before merge.

## Cost allocation

- Low-cost agent: inventories, matrices, fixtures, evidence assembly, link checks.
- Mid-tier: contract validator and non-trivial test implementation.
- Strong reasoning: candidate selection, permission/safety design, final review.
