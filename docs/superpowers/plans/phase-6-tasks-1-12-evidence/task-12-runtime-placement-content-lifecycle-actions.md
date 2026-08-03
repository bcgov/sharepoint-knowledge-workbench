# Phase 6 Task 12 — Runtime Placement for Content-Lifecycle Actions (Subphase 6.3)

**Corrected 2026-08-03, Phase 6 remediation.** The original version of this document described
step 5 ("Republish and reconcile in SharePoint") as if deterministic tooling performs the actual
tenant write. That overstated what Task 0.15 actually built:
`sharepoint-content-publication`'s design (and its five implemented skills) is deliberately
package-only/zero-unauthorized-tenant-write — real automated tenant writes remain gated behind an
unapproved write-identity decision (Stage 3.4.3), per `start-here.md`'s own Task 0.15 record. Step
5 is corrected below to reflect that split explicitly, rather than implying an authorization this
repo has not made.

Per `docs/vision/open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md`'s
resolution and `docs/vision/master-initiative-plan-workstreams-and-phases.md`'s Stage 3.1.4 note:
Stage 3.1.4 owns *what* the ongoing structured-content maintenance workflow's actions are; Phase 6
Subphase 6.3 (this task) owns *which runtime* performs each one. **Output feeds a future Phase 6.5
entry gate; does not itself authorize Phase 6.5.**

## Precondition check

Stage 3.1.4's own deliverable (`source-of-truth-lifecycle.md`) does not exist yet — verified: no
such file found in this repository. Stage 3.1.4 has not itself enumerated a discrete action list;
it has only posed the governing questions (is manual editing prohibited/tolerated/reconciled, what
counts as drift, etc. — `master-initiative-plan-workstreams-and-phases.md` lines 322-330). **This
task therefore works from the one concrete action sequence that already exists in written form**
— the "Follow-up elaboration" loop in the open-question document — rather than inventing a
different one. If Stage 3.1.4 later produces a differently-shaped action list, this table should
be re-derived against it, not assumed still correct by inertia.

## Runtime placement, per action in the existing documented loop

| # | Action | Runtime | Classification |
|---|---|---|---|
| 1 | Edit or change proposal originates (direct SharePoint edit, change proposal, review comment, agent-assisted drafting) | SharePoint agent/native skill | **Agent may only recommend/gather intent** — proposes or drafts, never itself authoritative |
| 2 | Review and apply the approved change to structured source content | GitHub Copilot/Claude workbench (human-directed) | **Native skill may invoke approved deterministic tooling** — a human-directed workbench session applying a change, not an autonomous agent action |
| 3 | Recalculate identity, lineage, hashes, cross-references, publication mappings for the updated structured content package | Deterministic tooling (`structured-content-assembly`) | **Deterministic pipeline must perform** — this is exactly the class of claim (hash/identity proof) `review-manual-topics`'s own governance rules already prohibit any agent/skill from making itself (Task 1's essential-elements list) |
| 4 | Re-render all affected representations | Deterministic tooling (`structured-content-rendering`) | **Deterministic pipeline must perform** — same renderers this session verified real (`render-multipage-markdown`, `render-sharepoint-aspx`), never an agent re-implementing rendering ad hoc |
| 5a | Prepare, validate, and reconcile the publication plan (package the rendered output, dry-run against the target library schema, reconcile expected-vs-actual publication state) | Deterministic tooling (`sharepoint-content-publication`) | **Deterministic pipeline must perform** — matches that plugin's five already-implemented skills exactly |
| 5b | The actual tenant write (upload, page create/update) | **Human-authorized, not automated** | **Neither an agent nor deterministic tooling may perform this autonomously today** — `sharepoint-content-publication`'s design is deliberately package-only/zero-unauthorized-tenant-write; a real write identity/path remains gated behind Stage 3.4.3's unapproved decision. Deterministic tooling produces the human-actionable plan; a human executes the write until that decision is made. |
| 6 | SharePoint agents/native skills consume the updated published content | SharePoint agent/native skill | **Native skill may invoke approved deterministic tooling to read/serve** — this is exactly `review-manual-topics`'s own existing scope, unchanged |
| 7 | Discover another improvement, loop repeats | SharePoint agent/native skill | **Agent may only recommend** — same as step 1, closing the loop |

## Preview-vs-authoritative rule (restated formally, per the task's own requirement)

**Agent-generated output (steps 1, 6, 7 above) is a non-authoritative preview unless and until it
passes the deterministic pipeline's own contracts and validation (steps 3–5a).** No agent or
native skill may claim its own output is authoritative, hash-verified, or ready for publication —
those claims belong exclusively to the deterministic pipeline stages, matching the exact division
`review-manual-topics`'s own Prohibited Operational Scope already establishes for a narrower case
(no hash claims, no canonical-identity claims). This task generalizes that same rule across the
full content-lifecycle loop rather than leaving it implicit to one skill. **This rule is retained
unchanged by this remediation's step-5 correction** — splitting 5 into 5a/5b does not weaken it;
it clarifies that even the deterministic pipeline's own output (the publication plan) is not
self-executing into a tenant write, which is a stricter reading of "non-authoritative until
approved," not a looser one.

## Per-runtime evidence/rollback matrix

| Runtime | Evidence produced | Rollback mechanism |
|---|---|---|
| SharePoint agent/native skill (steps 1, 6, 7) | Conversational output/recommendation only — no artifact requiring rollback, since nothing authoritative was written | N/A — no write occurred |
| GitHub Copilot/Claude workbench (step 2) | The edited source content itself, under this repo's own git history | `git revert`/`git checkout` on the structured-content source, same as any other repo change — no new mechanism needed |
| Deterministic tooling — assembly/render (steps 3–4) | `manifest.json`, `validation.json`, `renderer-validation.json`, `render-result.json` (already-real artifacts this session directly verified exist for the real CEIS manual) | Atomic promotion already in place (`atomic_output.py`'s stage-then-promote pattern, verified working this session for both Markdown and ASPX renders) — a FAIL never promotes, prior accepted output survives |
| Deterministic tooling — publication prep/validation/reconciliation (step 5a) | Package, dry-run validation report, reconciliation report (per `sharepoint-content-publication`'s existing five implemented skills) | `rollback-sharepoint-publication` skill (implemented, Task 0.15) — exact-target rollback, already built |
| Human-authorized tenant write (step 5b) | Whatever the human's own write action produces (e.g. tenant upload confirmation) — not automated evidence this codebase generates | Human-performed, same as any manual tenant action; no automated rollback mechanism exists for this step until a real write identity/path is approved (Stage 3.4.3) |

## What this task does not do

Does not authorize Phase 6.5. Does not authorize building any new runtime placement described
above that doesn't already exist (e.g. no autonomous agent write path is being created — steps
3–5a remain exactly the already-existing, already-tested deterministic plugins, and step 5b's
tenant write remains human-authorized only). This is a placement decision recorded as evidence for
a future phase's entry gate, per the task definition's own final sentence.
