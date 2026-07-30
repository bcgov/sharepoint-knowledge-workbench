# Phase 3.0 Evidence-Consumption Matrix

**Status:** draft, companion to `phase-3-governed-sharepoint-knowledge-pilot-spec.md`. Not implementation-
ready. Maps every Phase 3 decision that depends on tenant evidence to the specific Phase 3.0 finding it
needs, so Phase 3.0's report can be checked against actual Phase 3 consumption rather than assumed
sufficient.

| Phase 3 decision | Required Phase 3.0 finding | Evidence artifact | Blocking if absent? | Plan section affected | Owner |
|---|---|---|---|---|---|
| Pilot site/library exists and is authorized for use | Stage 3.0.1.1 — tenant access, licence ring, authority | Access record | Yes | Spec §5, §4 | Tenant admin + technical lead |
| SharePoint surface type available (site/library/column types) | Stage 3.0.1.2 — surface inventory | Inventory with screenshots/exports | Yes | Spec §7 | Technical lead |
| AgentAssets existence/writability | Stage 3.0.2.1 | Probe transcript | No (Phase 4/5 dependency only, not Phase 3 build) | Spec §3 (non-goal) | Technical lead |
| Native `SKILL.md` authoring availability | Stage 3.0.2.2 | Schema sample or "not available" finding | No (Phase 4 dependency only) | Spec §3 (non-goal) | Technical lead |
| Agent-creation approval path | Stage 3.0.2.3 | Approval-path record | No (Phase 5 dependency only) | Spec §3 (non-goal) | Tenant admin |
| Native Markdown rendering enabled | Stage 3.0.2.4 | Screenshot of rendered/failed output | Yes — Spec §6/§9 assume rendered Markdown is the uploaded artifact; if unavailable, re-gate to an observed supported representation | Spec §6, §9 | Technical lead |
| Metadata field types/constraints for a pilot library | Stage 3.0.2.5 | Field type inventory | Yes | Spec §7 (every row) | Technical lead |
| Report + dependency-status map completeness | Stage 3.0.3.1/3.0.3.2 | `tenant-capability-report.md` + dependency-status map | Yes — this is Phase 3's own entry gate | Spec §1, §4 | Technical lead + tenant admin sign-off |
| Library versioning configuration/behaviour *(proposed addition, not yet in master plan)* | Not currently a named Stage 3.0.2.x probe | — | Yes — Spec §13/§14 assume native version history exists or names a fallback | Spec §13, §14 | Technical lead (propose to master-plan owner) |
| Available identities for permission/oversharing testing *(proposed addition)* | Not currently a named Stage 3.0.2.x probe | — | Yes — Stage 3.4.2 requires ≥2 distinct identities | Spec §14 | Technical lead (propose to master-plan owner) |
| Package-only manual-upload feasibility, as its own explicit probe *(proposed addition)* | Currently only implied by the overall Phase 3.0 exit gate | — | Yes — this is Phase 3's stated entry-gate condition | Spec §1, §4, §9 | Technical lead (propose to master-plan owner) |
| Candidate publisher role/permission level for upload, metadata update, republish, rollback *(proposed addition)* | Not currently a named Stage 3.0.2.x probe | — | Yes — Spec §13/§14 assume a publisher role exists with these permissions | Spec §13, §14 | Technical lead (propose to master-plan owner) |
| Write identity status for any reversible Phase 3 pilot writes | Phase 3.0's staged-write convention (steps 1–6) — scope of applicability to Phase 3 itself not yet confirmed | — | Yes — needs an explicit statement that Phase 3.0's convention also governs Phase 3's own reversible test writes | Spec §17 | Technical lead |

**Note on proposed additions:** the five rows marked *(proposed addition, not yet in master plan)* are gaps
this spec's brainstorming surfaced in Phase 3.0's current five named probes (Stage 3.0.2.1–3.0.2.5):
library versioning configuration, permission-test identities, manual-upload feasibility as its own explicit
probe, publisher permissions, and write-identity scope applicability to Phase 3. **Correction (external
review round):** these gaps must be reconciled into the Phase 3.0 specification/plan itself **before**
Phase 3.0 executes, not merely recorded here for later consumption — if Phase 3.0 runs without these five
probes added, Phase 3 will still lack the evidence it needs even after Phase 3.0's report is accepted, and
this matrix's "Blocking if absent?" column would be discovered too late to act on cheaply. Reconciling them
into the master plan's Phase 3.0 subphase (and, correspondingly, its own spec/plan if one exists at that
level) is a separate, explicitly-authorized edit — not made in this session — but it is a precondition for
Phase 3.0's execution to actually satisfy this matrix, not an optional follow-up.
