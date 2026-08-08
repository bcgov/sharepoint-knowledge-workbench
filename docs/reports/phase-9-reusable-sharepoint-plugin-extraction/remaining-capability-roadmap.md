# Phase 9 — Remaining-Capability Roadmap

**Status:** `EVIDENCE_BASED`, `NOT_AUTHORIZATION`. Satisfies the "remaining-capability roadmap" and
"backlog disposition record" items in Phase 9 spec §18/§20.
**Source baseline:** `jag-csb-cmat-sharepoint-online` @ `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f`.
**Date:** 2026-08-07.

Every one of the source plugin's 34 skills, plus its 9 agents, has a disposition below. Nothing is
left unclassified. Ranking uses evidence gathered during this phase, not the original planning
estimates — several of which the evidence overturned (see the retrospective).

---

## 1. Onboarded this phase

| Capability | Destination | Skills | Tests |
|---|---|---|---|
| `sp-uploading-content` | `sharepoint-content-publication` (existing) | 1 | 31 (plugin total) |
| `sp-validating-app-registration` | `workbench-setup` (existing) | 1 | 52 (plugin total) |
| 4 generic agents | `sharepoint-agents-and-skills` (existing) | 4 agents | 68 (plugin total) |
| `sp-extracting-links`, `sp-remediating-links`, `sp-validating-link-integrity` | `sharepoint-link-remediation` (new) | 3 | 121 |
| `sp-discovering-pages`, `sp-analysing-aspx-pages`, `sp-discovering-web-parts`, `sp-discovering-navigation`, `sp-discovering-forms`, `sp-discovering-permissions` | `sharepoint-discovery` (new) | 5 | 71 |
| `sp-auditing-schema`, `sp-extracting-choices` | `sharepoint-schema` (new) | 2 | 50 |
| `sp-analysing-aspx-pages`, `sp-converting-aspx-pages` | `sharepoint-page-modernization` (new) | 2 | 54 |
| `combine-preview.ps1` (from `sp-running-sharegate-jobs`) | `sharepoint-page-modernization` (existing) | 1 | 63 (plugin total) |

---

## 2. Ranked remaining work

### Rank 1 — Live-tenant collection (NEW PLUGIN REQUIRED, design decision needed)

**Gap, not an extraction.** `sp-discovering-site-structure`'s backing scripts call
`Connect-PnPOnline` and query a live tenant. Every plugin Phase 9 built is deliberately
zero-tenant-I/O, operating on exports you already have. **Nothing in this workbench currently
collects those exports** — a real capability hole at the front of every discovery workflow.

- **Why it is rank 1:** every analysis plugin delivered this phase depends on an export that a
  human must currently produce by hand.
- **Blocked on a human decision, not effort:** it needs its own plugin with an explicit
  connection/write-safety boundary, designed against `workbench-setup`'s connector-injection
  contract (`test_connection(connection, connector=...)`, `NotImplementedError` without one).
- **Cost:** high. The two candidate source scripts carry 147 and 178 project literals (§8h) —
  the most saturated non-deprecated files in the source.
- **Recommendation:** design first, extract second. Do not fold into `sharepoint-discovery`.

### Rank 2 — `sp-running-sharegate-jobs`

- **Status:** `IMPLEMENTED` (3 LIVE symlinks). **Corrected 2026-08-07:** the symlink count is not
  uniformly ShareGate-dependent. One of the three, `combine-preview.ps1`, was independently
  verified to have zero ShareGate calls, zero live-tenant I/O (no `Connect-PnPOnline`/`Get-PnP`/
  `New-ClientContext`/`Invoke-WebRequest`/`Invoke-RestMethod`), and zero project literals — a
  purely offline, disk-only preview-composition capability that happened to be filed under a
  ShareGate-dependent skill. It has been extracted to `sharepoint-page-modernization`'s
  `compose-page-preview` skill; see provenance Record 16.
- **Remaining blocker:** the other two scripts in this skill (the ShareGate upload jobs
  themselves) are genuinely dependent on the external **commercial licensed tool**. Per §8d that
  dependency must be documented in `DEPENDENCIES.md` and explicitly accepted before those two are
  extracted — not silently assumed.
- **Cost:** low once the dependency decision is made, for the two remaining scripts only.

### Rank 3 — Discovery synthesis (REBUILD, not extract)

- `sp-synthesizing-discovery` is `REJECTED` as an extraction (see §3) but the *capability* — rolling
  up per-domain discovery outputs into one review — is genuinely useful and now has five real
  producers feeding it (`sharepoint-discovery`'s five skills).
- **This is new design work**, not a port. It should aggregate real sibling outputs, and must not
  reproduce the source's fabricated estimates.

### Rank 4 — Broader upload capability

- Wave 1 extracted `sp-uploading-content` narrowly. The source's dual-mechanism (PnP + raw REST)
  generalized upload is richer.
- **Gated:** publication-path work depends on Phase 3's unmet exit gate (library schema and
  source-of-truth lifecycle). Defer until Phase 3 closes.

### Rank 5 — `sharepoint-content-migration`

- **Excluded on evidence, not deferred by preference.** Task 2a recomputed `sp-migrating-content`
  from 44 raw symlinks to **29 LIVE** — 12 resolve into `scripts/_deprecated/stages/`, 3 dangle.
- §8e's provisional justification does **not** survive that correction: the reusable
  wave-execution *mechanism* is unproven outside deprecated code.
- **Re-entry trigger:** someone demonstrates a live, non-deprecated wave mechanism separable from
  the organisation-specific wave *content*. Until then, extracting it means building on
  `_deprecated/`.
- **Audited 2026-08-07 — exclusion CONFIRMED, and the re-entry trigger is now known not to fire.**
  All 29 LIVE symlink targets were resolved and deduplicated. They comprise: 5 `scripts/lib/`
  helpers (generic, but already available and not wave-specific), `extract-choices.ps1` (already
  extracted in Wave 6), a config example, a calendar-remediation script
  (`KEEP_PROJECT_SPECIFIC`), 11 `test-wave*.ps1` files, and 9 `wave*.ps1` scripts named for
  organisation-specific domain concepts (`wave2-persons`, `wave3-person-dependents`,
  `wave7-city-calendars`, `wave8-cross-references`, `wave9-document-libraries`).
  The only plausible generic runner, `wave-cases.ps1` (76 lines), hardcodes
  `[ValidateSet('4','5','6')]` mapping to three organisation-specific case-list types. **There is
  no separable generic wave mechanism among the live targets** — the mechanism/content split that
  §8d proposed does not exist in extractable form. This is now a verified finding, not an
  assumption.

---

## 3. Rejected — with evidence

| Capability | Disposition | Evidence |
|---|---|---|
| `sp-synthesizing-discovery` | `REJECT` (as extraction) | Hardcodes `total_pages: 654`, `total_wps: 193`, `flagged_links: 4792`; only `total_pages` is ever replaced with real data. Fabricates `oob_pages`/`custom_pages`/`spfx_candidates` from arbitrary ratios (`* 0.7`, `* 0.25`, `* 0.1`). Would ship invented numbers as measurement. |
| `sp-provisioning-modern-calendars` | `KEEP_PROJECT_SPECIFIC` | Court-scheduling domain concept. |
| `sp-synthesizing-deployment-matrix` | `PLANNED_WITH_NO_IMPLEMENTATION` | Was `UNVERIFIED_ACTIVE_CLAIM`. **Resolved this phase:** direct inspection confirms the `active` claim is unfounded — no backing implementation. |
| `sp-generating-migration-reports` | `PLANNED_WITH_NO_IMPLEMENTATION` | **RESOLVED 2026-08-07 by direct inspection.** The skill directory contains only the 3-file baseline (`SKILL.md`, `evals/evals.json`, `evals/results.tsv`) — zero scripts, zero symlinks. Its `status: active` claim is unfounded. No longer `REQUIRES_HUMAN_DECISION`; **both** of the spec's `UNVERIFIED_ACTIVE_CLAIM` items are now resolved, and both were unfounded. |
| Field-deletion (`-Cleanup`) | `REJECT` | The source's duplicate-field script called `Remove-PnPField` — a destructive tenant write. Deliberately not extracted; a test enforces its absence. |
| `ords-integration-migration` (all 4 skills) | `OUT_OF_SCOPE` | All 4 `SKILL.md` files read directly: Oracle/court-appearance ETL. No generic SharePoint helper found. |
| 11 `PLANNED_WITH_NO_IMPLEMENTATION` skills | Gaps | `sp-discovering-lists`, `-content-types`, `-workflows`, `sp-mapping-content-types`, `-lists`, `-taxonomy`, `sp-remediating-page-layouts`, `-web-parts`, `-document-content-links`, `sp-validating-content`, `-permissions`. **No empty skills were created for any of them.** |

## 4. Agents — 5 of 9 remaining

| Agent | Literals | Disposition |
|---|---|---|
| `sp-discovery-agent`, `sp-migration-agent` | 3 each | **CORRECTED 2026-08-07 (full-content re-read, not just literal count):** `AGENT_REQUIRES_GENERICIZING` was wrong for both — the low literal count was a false signal, exactly the router-agent trap flagged below. `sp-discovery-agent` (173 lines) is not a lightweight router: every one of its 14 steps invokes `-SiteUrl`/`-UseIntegratedAuth` live-tenant PnP scripts — it **is** Part A (collection) wearing an agent costume, not separable from it — defaults to a CMAT-specific output layout, and step 14 calls `generate-master-discovery-meta-review.py`, the exact script already `REJECT`ed for fabricating headline metrics (`sp-synthesizing-discovery`, §3). `sp-migration-agent` (25 lines) routes across 4 capabilities; only `sp-uploading-content` exists in this workbench — the other 3 targets are excluded (`sp-migrating-content`), unevaluated/CMAT-coupled (`sp-content-migration`), or blocked on the ShareGate decision. **Neither is extraction-ready.** `sp-discovery-agent`'s re-entry trigger is Part A's design being approved; `sp-migration-agent`'s is its routing targets existing. |
| `sp-deployment-planner` | 14 | `RESEARCH` — no confirmed generic plugin owner |
| `sp-migration-orchestrator` | 36 | `ORCHESTRATOR_COUPLED_TO_CMAT_WAVES` |
| `sp-wave-orchestrator` | 161 | `KEEP_PROJECT_SPECIFIC` — highest literal density in the audit |

**Caveat learned this phase:** literal density is the *wrong* cost model for router-shaped agents.
The four extracted agents scored zero literals yet required their entire routing tables rebuilt,
because they routed to ~15 source skills that do not exist here. Expect the same for
`sp-discovery-agent`/`sp-migration-agent`.

## 4a. `sharepoint-provisioning` disposition OVERTURNED (2026-08-07)

**Original spec §8e verdict:** "Not justified as a standalone plugin — no confirmed generic
implemented skill exists here at all." **That verdict is wrong.** It was based on scanning only
`sharepoint-migration`'s 34 skills; `ords-integration-migration` was checked by `SKILL.md` alone
until this session's direct-script review found real value hiding there, the same pattern that
surfaced `combine-preview.ps1` (Wave 4) and the certificate-auth precedent (design spec).

**Real, generic, implemented pattern found:**
`scripts/ag-tenant/reset-and-provision-etl-target-schema.ps1` (351 lines) + its dependency
`scripts/lib/content-type-lib.ps1` (138 lines, 6 functions, **zero project literals already**).
Stripped of the CMAT domain content (list names, field names, calendar/court-appearance
specifics), the underlying pattern is:

- Declarative JSON-schema-driven provisioning: site columns + content-type field definitions
  (with hidden flags) + a target list inventory, not per-list hardcoded logic.
- **Reconcile, not blind recreate**: content types/columns are create-if-missing; display-name
  drift against the schema is detected and fixed; fields no longer declared are explicitly
  unlinked.
- A genuine PnP limitation workaround: `Add-PnPField` does not support `-Formula` — calculated
  columns require raw Field XML construction. Proven, non-obvious technique worth keeping.
- Three incident-derived safety fixes, each independently valuable: duplicate-title detection
  before any delete (real incident — a stray duplicate list caused auth to silently resolve to
  the wrong one), fail-loud (not silent) if a list unexpectedly survives deletion, and an
  explicit show/hide reconciliation pass rather than create-time-only.
- `-DryRun` support throughout, matching this workbench's existing convention.

**Not extracted — deliberately, not by oversight.** This is write-capable and destructive by
design (deletes and recreates lists). Every Phase 9 plugin built so far is either read-only or
gated like `remediate-links` (dry-run default + injected writer + confirmation token). A
provisioning plugin needs that same safety-gate design decided **before** any code is written —
spec §13 requires "a separately approved plan with dry-run, confirmation, least privilege,
rollback, evidence" for this category. `New-ModernCalendarList` (referenced but not yet located
in this pass) likely carries further generic provisioning logic and should be checked in the same
pass if this candidate is pursued.

**Recommendation:** rank this alongside Rank 1 (collection) as high-value, design-gated work —
not effort-gated. A short design pass mirroring `remediate-links`'s three-gate pattern would make
`sharepoint-provisioning` genuinely buildable.

## 5. Not required by any evidence

Deployment/publication of modernization output, CMAT rebind (§17 forbids), and a general-purpose
routing agent (§5 non-goal) remain out of scope.
