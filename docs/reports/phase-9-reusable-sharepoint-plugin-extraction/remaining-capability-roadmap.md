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

- **Status:** `IMPLEMENTED` (3 LIVE symlinks), generic *if* ShareGate is an assumed available tool.
- **Blocker:** an external **commercial licensed tool** dependency. Per §8d it must be documented
  in `DEPENDENCIES.md` and explicitly accepted before extraction — not silently assumed.
- **Cost:** low once the dependency decision is made.

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

---

## 3. Rejected — with evidence

| Capability | Disposition | Evidence |
|---|---|---|
| `sp-synthesizing-discovery` | `REJECT` (as extraction) | Hardcodes `total_pages: 654`, `total_wps: 193`, `flagged_links: 4792`; only `total_pages` is ever replaced with real data. Fabricates `oob_pages`/`custom_pages`/`spfx_candidates` from arbitrary ratios (`* 0.7`, `* 0.25`, `* 0.1`). Would ship invented numbers as measurement. |
| `sp-provisioning-modern-calendars` | `KEEP_PROJECT_SPECIFIC` | Court-scheduling domain concept. |
| `sp-synthesizing-deployment-matrix` | `PLANNED_WITH_NO_IMPLEMENTATION` | Was `UNVERIFIED_ACTIVE_CLAIM`. **Resolved this phase:** direct inspection confirms the `active` claim is unfounded — no backing implementation. |
| `sp-generating-migration-reports` | `REQUIRES_HUMAN_DECISION` | Still `UNVERIFIED_ACTIVE_CLAIM` — 0 scripts, 0 symlinks. Not re-verified this phase. **Open item.** |
| Field-deletion (`-Cleanup`) | `REJECT` | The source's duplicate-field script called `Remove-PnPField` — a destructive tenant write. Deliberately not extracted; a test enforces its absence. |
| `ords-integration-migration` (all 4 skills) | `OUT_OF_SCOPE` | All 4 `SKILL.md` files read directly: Oracle/court-appearance ETL. No generic SharePoint helper found. |
| 11 `PLANNED_WITH_NO_IMPLEMENTATION` skills | Gaps | `sp-discovering-lists`, `-content-types`, `-workflows`, `sp-mapping-content-types`, `-lists`, `-taxonomy`, `sp-remediating-page-layouts`, `-web-parts`, `-document-content-links`, `sp-validating-content`, `-permissions`. **No empty skills were created for any of them.** |

## 4. Agents — 5 of 9 remaining

| Agent | Literals | Disposition |
|---|---|---|
| `sp-discovery-agent`, `sp-migration-agent` | 3 each | `AGENT_REQUIRES_GENERICIZING` — low scrub cost, viable next |
| `sp-deployment-planner` | 14 | `RESEARCH` — no confirmed generic plugin owner |
| `sp-migration-orchestrator` | 36 | `ORCHESTRATOR_COUPLED_TO_CMAT_WAVES` |
| `sp-wave-orchestrator` | 161 | `KEEP_PROJECT_SPECIFIC` — highest literal density in the audit |

**Caveat learned this phase:** literal density is the *wrong* cost model for router-shaped agents.
The four extracted agents scored zero literals yet required their entire routing tables rebuilt,
because they routed to ~15 source skills that do not exist here. Expect the same for
`sp-discovery-agent`/`sp-migration-agent`.

## 5. Not required by any evidence

Deployment/publication of modernization output, CMAT rebind (§17 forbids), and a general-purpose
routing agent (§5 non-goal) remain out of scope.
