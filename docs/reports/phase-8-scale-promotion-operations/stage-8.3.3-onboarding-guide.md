# Stage 8.3.3 — Onboarding Guide: `review-manual-topics` (native-sharepoint)

**Status:** `GUIDE_WRITTEN_ATTEMPT_PENDING`. Spec Section 8.3 requires "a person unfamiliar with
the capability must be able to follow it successfully, with gaps recorded as evidence." **No such
attempt has occurred.** This document is the guide only — do not treat its existence as satisfying
this stage.

## What this capability is

`review-manual-topics` is a native SharePoint Copilot skill that performs a read-only editorial
review of exactly one selected CEIS manual topic page (content completeness, section structure,
cross-reference consistency, terminology clarity) against Phase 3 CEIS publication standards. It
has two runtimes; this guide covers only the **native-sharepoint** runtime.

## Where it lives

- **Repository source:**
  `plugins/sharepoint-agents-and-skills/skills/review-manual-topics/SKILL.md`
- **Deployed location:** `AgentAssets/Skills/review-manual-topics/SKILL.md` in the
  `AG-CSB-INTRANET-DEV` SharePoint tenant (site
  `https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV`).
- **Deployment/reconciliation/rollback scripts:**
  `plugins/sharepoint-agents-and-skills/scripts/{deploy-and-verify-skill.ps1,
  reconcile-deployed-skill.ps1, rollback-skill-deployment.ps1}`.
- **Configuration (not tracked in git — must exist locally):**
  `plugins/sharepoint-agents-and-skills/config.psd1`, created by copying the committed canonical
  template `plugins/sharepoint-agents-and-skills/config.psd1.example` and filling in the real
  `SiteUrl` (required) and `ClientId`/`TenantId` (optional, for app-only auth) — these are the
  only fields this plugin's three scripts actually read.

## How to verify it's currently correct

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1
```

Read-only. Compares the live deployed file's SHA-256 against the repository artifact's hash.
Requires an interactive PnP/Entra session (`-Interactive` login prompt).

## How to promote a change

See `stage-8.1.1-promotion-path.md` for the full path. In short: edit the repository `SKILL.md`,
get it reviewed/approved, then run `deploy-and-verify-skill.ps1 -Execute`, then re-run the
reconciliation command above to confirm.

## How to roll it back

See `stage-8.1.1-promotion-path.md` Section 7, or `stage-8.3.2-retirement-exercise.md` for the
full remove/confirm/restore sequence. In short:
`rollback-skill-deployment.ps1 -Execute -ConfirmExactTarget "CONFIRM-REMOVE"`.

## Who owns it

See `stage-8.3.1-ownership-support-charter.md` — Richard Fremmerlid is the accountable owner,
technical maintainer, content owner, and deployment authority; no second operator is documented.

## Known limitations to be aware of before operating this capability

1. The native runtime does not enforce the shared 2-related-topic cap in code — only by
   instruction. Live drift has been observed twice (see the capability activation record,
   Section 6, and the incident drill, `stage-8.3.1-incident-drill.md`).
2. The 4-identity permission matrix was waived at Phase 4 exit, not executed.
3. Negative/ambiguous evaluation categories were only partially executed at Phase 4 exit.

## Unfamiliar-operator checklist (to be run by someone who has not operated this capability before)

**Corrected design (this round):** an earlier version of this checklist asked the operator to find
answers "without being told" the path/facts this same guide states above it — a self-contradiction
(it cannot both hand the operator the answer and test unaided discovery of that answer). This
checklist instead **tests whether an unfamiliar person can successfully follow this guide to
operate the capability**, not whether they can discover the same facts unaided. It is the actual
test instrument for this stage's acceptance requirement and has **not yet been attempted by
anyone**. When it is, record the attempt's outcome (succeeded/where they got stuck, and whether the
guide itself was accurate and sufficient) as a new file, `stage-8.3.3-onboarding-attempt-
record.md`, rather than editing this checklist in place.

- [ ] Using only this guide, locate the repository source file for the skill and confirm it opens.
- [ ] Using only this guide, identify which SharePoint tenant/site the skill is deployed to.
- [ ] Using only this guide, run the reconciliation command and correctly interpret a match vs.
  mismatch result.
- [ ] Using only this guide, identify who the accountable owner is and where the full ownership
  charter lives.
- [ ] Using only this guide, describe (without executing, unless authorized) what to do if the
  skill needs to be rolled back.
- [ ] Using only this guide, name at least one known limitation of this capability.
- [ ] Record any point where the guide itself was inaccurate, missing, or insufficient to complete
  a step — this is itself a required finding, not an incidental note.

## Open acceptance item

**Stage 8.3.3 remains open** until the checklist above is actually attempted by a person
unfamiliar with this capability and the attempt's real outcome (including any gaps found) is
recorded — not assumed successful because this guide exists.
