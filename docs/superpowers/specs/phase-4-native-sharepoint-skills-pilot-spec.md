# Phase 4 Specification — Native SharePoint Skills Pilot

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

## 1. Status and authority

**Disposition:** RESEARCH.  
**Entry gate:** Phase 3.0 confirms native skill authoring and `AgentAssets` availability, schema, and write permissions; Phase 3 provides the governed pilot library and real content substrate.  
**Authority:** The master initiative plan is authoritative. This specification refines Phase 4 without changing its gates.

## 2. Goal

Pilot one native SharePoint skill end to end, beginning with manual deployment, and produce evidence across normal, negative, ambiguous, permission, and safety cases.

## 3. Primary candidate

`review-manual-topics` is the leading candidate because it has already been explored as a native `SKILL.md` workflow. Final selection remains `DEFERRED_UNTIL_EVIDENCE` from Phase 3.0 permissions and Phase 3 library inputs.

## 4. Non-goals

- No automated deployment to SharePoint.
- No arbitrary scripts, filesystem operations, Git operations, or external systems from the native skill.
- No Cowork or Copilot Studio packaging.
- No general multi-runtime capability specification. That belongs to Phase 6 after two real runtimes exist.
- No tenant-wide rollout.
- No second native skill before the first candidate is evaluated and accepted.

## 5. Preconditions

| Precondition | Required evidence | Status |
|---|---|---|
| Copilot in SharePoint skill authoring is available | Phase 3.0 probe result | DEFERRED_UNTIL_EVIDENCE |
| `AgentAssets` exists and its actual path/internal identity is confirmed | Phase 3.0 probe result | DEFERRED_UNTIL_EVIDENCE |
| Skill schema accepted by the tenant is known | Accepted sample or rejection evidence | DEFERRED_UNTIL_EVIDENCE |
| Named author/deployer and permission model exist | Access record | DEFERRED_UNTIL_EVIDENCE |
| Governed Phase 3 library exists | Phase 3 exit evidence | BLOCKED |
| Candidate skill inputs exist in the library | Input availability check | BLOCKED |

## 6. Candidate-selection criteria

The selected skill must:

- use only observed native SharePoint capabilities;
- operate within existing user permissions;
- have bounded inputs and outputs;
- avoid destructive actions by default;
- expose clear human review points;
- have testable success and refusal behavior;
- provide differentiated value over a one-off prompt;
- use real Phase 3 content and metadata.

## 7. Skill package

The repository-side design package should contain, subject to repository conventions:

```text
capability specification
native SKILL.md
permission assumptions
deployment manifest
evaluation cases
governance metadata
manual deployment instructions
lifecycle record
```

Only the target-native artifact should be manually deployed into the confirmed `AgentAssets` location. Supporting evidence remains in the repository.

## 8. Skill contract

The skill definition must specify:

- name and purpose;
- when to use and when not to use;
- supported SharePoint context;
- required inputs;
- ordered steps;
- prohibited behavior;
- output format;
- partial-failure behavior;
- permission assumptions;
- human confirmation points;
- version and owner.

## 9. Manual deployment contract

Manual deployment must record:

- named person performing each step;
- target site and confirmed `AgentAssets` identity;
- source repository artifact and version;
- deployed file path and SharePoint version;
- permissions before and after deployment;
- rollback/removal procedure;
- screenshots or sanitized evidence;
- confirmation that no unauthorized artifact remains.

## 10. Evaluation model

### Normal cases

Expected workflow completes on valid selected content.

### Negative cases

Missing inputs, unsupported content, missing list, and inaccessible items fail honestly.

### Ambiguous cases

Unclear metadata or conflicting content is marked for review rather than invented.

### Permission cases

At least two permission identities demonstrate that the skill does not expand access or leak inaccessible content.

### Safety cases

The skill does not create authoritative values, approve its own output, expose protected content in a broad list, or perform destructive/high-volume actions without confirmation.

## 11. Evidence requirements

```text
candidate-selection memo
input-availability check
validated SKILL.md
manual deployment log
normal-case results
negative-case results
ambiguous-case results
permission-case results
safety-case results
consolidated evidence report
lifecycle policy
```

## 12. Lifecycle

Define owner, review cadence, versioning, promotion, supersession, retirement, and emergency disable/removal. Promotion automation is out of scope until Phase 8.

## 13. Exit criteria

- One native skill is manually deployed by an authorized person.
- The deployed file matches the reviewed repository artifact.
- All five evaluation categories have real executed cases and recorded results.
- Permission tests show no oversharing or access expansion.
- Manual deployment and rollback steps are documented.
- A named owner and lifecycle policy exist.
- No second skill or automated deployment is started automatically.

## 14. Deferred work

- Additional skills such as quiz generation or content-outline application.
- Automated deployment and cross-site promotion.
- Shared multi-runtime specification.
- Monitoring at scale.
