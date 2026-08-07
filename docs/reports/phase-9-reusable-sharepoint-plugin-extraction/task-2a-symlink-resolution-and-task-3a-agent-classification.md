# Phase 9 — Task 2a (Symlink Resolution) and Task 3a (Agent Classification)

**Source baseline:** `jag-csb-cmat-sharepoint-online` @ `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f` (2026-08-05 09:19:39 -0700), plugin `sharepoint-migration`.
**Date executed:** 2026-08-07.
**Source repository modified:** NO — read-only inspection only (§17 preserved).
**Status:** `CONFIRMED` — mechanical inspection, every link resolved on disk.

> These two tasks are prerequisites for Task 4 classification (per the 2026-08-07 plan amendments). Spec §8d's implementation-status column was derived from raw symlink counts that include broken, deprecated-target, and plugin-escaping links; this document supplies the corrected signal.

---

## Task 2a — Resolved-symlink matrix

**Total symlinks under `skills/`: 128.**

| Class | Count | Extractable? |
|---|---|---|
| `LIVE` | 106 | Yes, subject to genericity review |
| `DEPRECATED_TARGET` | 12 | **No** — not without explicit recorded human decision |
| `ESCAPES_PLUGIN` | 6 | **No** — fails genericity contract by definition |
| `BROKEN` | 4 | **No** — recorded as source defects, never copied |

### Non-`LIVE` links in full

#### `BROKEN` (4) — dangling targets

| Skill | Link | Intended target |
|---|---|---|
| `sp-auditing-schema` | `compare-live-schema-test-vs-spo.ps1` | `scripts/schema-audit/compare-live-schema-test-vs-spo.ps1` |
| `sp-migrating-content` | `wave4-pio-cases.ps1` | `scripts/waves/wave4-pio-cases.ps1` |
| `sp-migrating-content` | `wave5-icm-cases.ps1` | `scripts/waves/wave5-icm-cases.ps1` |
| `sp-migrating-content` | `wave6-itau-cases.ps1` | `scripts/waves/wave6-itau-cases.ps1` |

Note the three `sp-migrating-content` links also use a wrong relative depth (`../../../../scripts/waves/` from a `scripts/waves/` subfolder). Not repaired — §17 forbids source modification.

#### `DEPRECATED_TARGET` (12) — all `sp-migrating-content` → `scripts/_deprecated/stages/`

`deploy-stage1`, `stage2`, `stage3`, `stage3b`, `stage4`, `stage5`, `stage6`, `stage6b`, `stage6-modern-calendar-single`, `stage7`, `stage8`, `stage9` (`.ps1`).

#### `ESCAPES_PLUGIN` (6) — all `sp-discovering-web-parts/references/` → `../../../../../01_source_sharepoint/analysis/`

`ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md`, `ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW-update-summary.md`, `CMAT-WEBPART-MODERNIZATION-VARIANCE-ANALYSIS.md`, `PROBLEMATIC-WEBPARTS-SUMMARY.md`, `SCRIPT-EDITOR-CODE-EXTRACTION.md`, `UNIQUE-PAGES-AND-WEBPARTS-REQUIRING-ANALYSIS.md`.

All six are **CMAT project analysis output**, not reusable capability. They traverse five levels up, out of `plugins/` entirely.

### Recomputed implementation signal — deltas against spec §8d

Only three skills change. **All three anchor §8e plugin justifications**, which is why this pass had to precede Task 4.

| Skill | §8d raw count | `LIVE` only | Delta | Effect on §8e |
|---|---|---|---|---|
| `sp-migrating-content` | 44 | **29** | −15 | Sole basis for `sharepoint-content-migration`. 12 deprecated + 3 broken removed. The wave-execution *mechanism* must be re-identified from the 29 live links — the current evidence does **not** establish it exists outside `_deprecated/`. |
| `sp-discovering-web-parts` | 19 | **13** | −6 | Anchors `sharepoint-discovery` as "richest discovery skill". The 6 removed are project analysis documents, not code. Still the richest discovery skill at 13. |
| `sp-auditing-schema` | 7 | **6** | −1 | Sole basis for `sharepoint-schema`. Survives — 6 live links remain, justification holds. |

**All other 31 skills:** raw count equals `LIVE` count, no change. Spec §8d's relative ordering is otherwise intact.

---

## Task 3a — Agent classification (9 agents)

Previously classified nowhere (spec §8f). Literal-density scan (`JUSTIN|CEIS|ORDS|courthouse|appearance|AG-CSB|ITAU|PIO|ICM|wave`) per agent:

| Agent | Literal hits | Orchestration coupling | Destination disposition |
|---|---|---|---|
| `sp-link-agent.md` | **0** | `GENERIC_SHAREPOINT_AGENT` | Candidate — pairs with `sharepoint-link-remediation` |
| `sp-modernization-agent.md` | **0** | `GENERIC_SHAREPOINT_AGENT` | Candidate — pairs with `sharepoint-page-modernization` |
| `sp-schema-agent.md` | **0** | `GENERIC_SHAREPOINT_AGENT` | Candidate — pairs with `sharepoint-schema` |
| `sp-validation-agent.md` | **0** | `GENERIC_SHAREPOINT_AGENT` | Candidate — but `sharepoint-validation-and-reconciliation` is **not** a justified plugin (§8e); needs an existing-plugin owner or deferral |
| `sp-discovery-agent.md` | 3 | `AGENT_REQUIRES_GENERICIZING` | Candidate — pairs with `sharepoint-discovery`; low scrub cost |
| `sp-migration-agent.md` | 3 | `AGENT_REQUIRES_GENERICIZING` | Candidate — pairs with `sharepoint-content-migration`; low scrub cost |
| `sp-deployment-planner.md` | 14 | `AGENT_REQUIRES_GENERICIZING` | `RESEARCH` — moderate coupling, no confirmed generic plugin owner |
| `sp-migration-orchestrator.md` | 36 | `ORCHESTRATOR_COUPLED_TO_CMAT_WAVES` | `RESEARCH` — orchestrates the wave model |
| `sp-wave-orchestrator.md` | **161** | `ORCHESTRATOR_COUPLED_TO_CMAT_WAVES` | `KEEP_CMAT_SPECIFIC` — highest literal density of any artifact in the audit |

**Headline finding:** four agents are **completely free of project literals** and are the cleanest extraction candidates found anywhere in this audit — cheaper to onboard than most skills. Agent extraction cost is inversely related to orchestration depth: per-domain agents are clean, orchestrators are deeply CMAT-coupled.

**Destination rule (§8c) applied:** this repository already owns `plugins/sharepoint-agents-and-skills/`. Every extraction-eligible agent above must be matched against that plugin before any new agent-hosting plugin is proposed. No new agent plugin is justified by this classification.

**Not yet done:** these classifications are based on literal density plus filename/role. A content read of each agent is required before extraction to confirm the coupling judgment and identify hidden environment assumptions (spec §5's coupling matrix, Task 5).

---

## Consequences for Task 4 and the wave plan

1. **`sharepoint-content-migration` is the weakest of the 5 provisionally-justified candidate plugins** — its sole anchor lost 15 of 44 links, and the reusable mechanism is unproven outside deprecated code. Recommend deferring it to a late wave pending the mechanism-vs-content separation the spec requires.
2. **`sharepoint-schema` and `sharepoint-discovery` justifications survive** the correction.
3. **Agents are cheaper to onboard than skills** and four are zero-cost on genericity. Recommend pulling agent extraction earlier than the original plan implies, matched into the existing `sharepoint-agents-and-skills` plugin.
4. **22 links (17%) are not extractable.** Any extraction that copies link topology wholesale would import 4 broken links into a repository whose symlink gate (`symlink_manager.py diagnose`) rejects broken links outright.
