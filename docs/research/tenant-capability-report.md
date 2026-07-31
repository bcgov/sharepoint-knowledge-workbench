# Tenant Capability Report — Phase 3.0 (SharePoint Tenant-Capability Discovery)

**Deliverable for:** `docs/vision/master-initiative-plan-workstreams-and-phases.md`, Stage 3.0.3.1.
**Tenant probed:** BC Gov dev site `AG-CSB-ITAU-CMAT-DEV`
(`https://bcgov.sharepoint.com/sites/AG-CSB-ITAU-CMAT-DEV`), connected account
`richard.fremmerlid@gov.bc.ca`, app registration `ag.csb.cmat.interactive` (intentionally
manage-only: no permission-management rights).
**Evidence sources synthesized here:**
- `tools/phase-3-sharepoint-discovery/reports/phase-3-0-discovery-report.json` (read-only PnP
  inventory, commit `744d7a3`, exported 2026-07-29T23:08:58Z).
- `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` (staged,
  authorized write-based capability probes, same site, same session).

This report answers each of Subphase 3.0.2's five probe questions with cited evidence per the
plan's required format, then states the overall gating decision. It supersedes no prior document —
it is the synthesis the plan names as the sole Phase 3.0 exit-gate deliverable.

---

## Probe 1 (Stage 3.0.2.1) — AgentAssets: does it exist, where, who can write?

**Finding:** `AgentAssets` exists on this site as a standard document library
(`Get-PnPList -Identity 'AgentAssets'` → `Observed`). It does **not** have unique role assignments
(`HasUniqueRoleAssignments: false`), meaning it inherits site-level permissions rather than
carrying its own distinct permission boundary. Who exactly can write to it (which specific
principals/roles) is **not determinable** with the tested manage-only app registration —
`RoleAssignments` returned `Forbidden` ("Attempted to perform an unauthorized operation"),
requiring Manage Permissions/Full Control on the list.

Separately, write-based probing (not just read-only inventory) confirmed that `.agent` files are
**not required** to live in `AgentAssets` specifically — any document library can host one; the
UI's own "Create an agent" flow dropped a `.agent` file directly into the triggering library, not
into `AgentAssets`. `AgentAssets/Skills/...` is confirmed as the convention for native skills,
evidenced by one real pre-existing skill (`review-manual-topics/SKILL.md`) found there.

**Verification path used:** read-only existence/schema check (`Get-PnPList`), per the plan's
required staged order, satisfied "who can write" only partially — full principal-level answer is
blocked by permission scope, not absence of effort.

**Evidence:** `phase-3-0-discovery-report.json` → `AgentAssetsLibrary.Exists`,
`AgentAssetsLibrary.HasUniqueRoleAssignments`, `AgentAssetsLibrary.RoleAssignments`;
`research-summary...md` §2 ("Copilot agent creation via SharePoint UI").

**Status:** `CONFIRMED_AVAILABLE` (library exists, is a normal writable document library type) +
`NEEDS_ESCALATION` (exact write-principal list requires a Manage-Permissions-capable account or
tenant-admin confirmation).

---

## Probe 2 (Stage 3.0.2.2) — Native `SKILL.md` authoring: available on this ring? what schema does it accept?

**Finding:** `SKILL.md` files are plain Markdown-with-YAML-frontmatter files
(`---\nname: ...\ndescription: ...\n---`, body sections `# Title`, `## When to use`, `## Inputs`,
`## Steps`, `## Output format`). No PnP write cmdlet exists for skill authoring as a first-class
object type (`Get-Command -Module PnP.PowerShell -Name '*Copilot*','*Agent*','*Skill*'` returns
only `Get-PnPCopilotAgent`, `Get-PnPCopilotAdminLimitedMode`, `Set-PnPCopilotAdminLimitedMode`).
Eight custom `SKILL.md` variants were authored by hand and uploaded via generic `Add-PnPFile` to
`AgentAssets/Skills/<name>/SKILL.md` — every upload succeeded with no special content-type or
registration step, and the tested same-site custom agent **automatically discovered** at least one
of them via trigger-phrase matching, with no explicit skill reference in that agent's own `.agent`
JSON.

Important qualifier (external-review-corrected): this proves discovery **by the one tested
custom agent, on this one site, for this one trigger phrase** — not by every agent, not by the
ready-made/default agent, not across sites, and not when multiple skills compete for a trigger.
A skill's `## Output format` section was found to be a **stylistic bias, not an enforced
contract** — JSON-schema requests were honored most reliably; custom delimiter templates were
frequently ignored; an externally-referenced template file was not read literally (the agent
fabricated a plausible field name instead).

**Verification path used:** staged authoring attempt in a designated non-production
`TEST-DO-NOT-USE-*` library, per the plan's required order — satisfied.

**Evidence:** `research-summary...md` §5 ("Skill (SKILL.md) and output-template authoring"), §6
("Output-template enforcement"), §7 ("Format-compliance A/B test"), Technical Mechanics §4;
`phase-3-0-discovery-report.json` → `NativeSkills` (`DefinitionDiscovered: true`,
`AgentInvocationVerified: false` at read-only-probe time — later confirmed true via the live
chat-pane test in the write-based session).

**Status:** `CONFIRMED_AVAILABLE` (skills can be authored and uploaded as plain files, and are
discoverable by at least one tested agent), with `PROVISIONAL` scope: cross-agent/cross-site
discovery and enforced output-format compliance are unverified (see Dependency-Status Map,
follow-up Priority 3 and Priority 4).

---

## Probe 3 (Stage 3.0.2.3) — Agent creation: possible, by whom, what approval path, what write identity?

**Finding:** Agent creation is confirmed possible via two paths in this tenant/ring: (1) the
Copilot UI's "Create an agent" button in a document library's command bar (produces a `.agent`
file in that same library); (2) hand-authoring the reverse-engineered JSON schema
(`schemaVersion: "0.2.0"`, top-level `customCopilotConfig` → `conversationStarters`,
`gptDefinition.{name,description,instructions,capabilities}`,
`behavior_overrides.special_instructions.discourage_model_knowledge`) and uploading via generic
`Add-PnPFile` — no dedicated agent-creation cmdlet exists (`Get-PnPCopilotAgent` is read-only). The
hand-authored agent was confirmed fully functional: correct rendering, correct
`OneDriveAndSharePoint` source binding, and correct grounded citation of a planted test keyword.

**What was not established:** the formal tenant-admin approval path for agent creation
(Stage 3.0.2.3 explicitly calls this a read-only administrative confirmation, not a test-creation
question) — `CopilotAdmin` probe returned `Forbidden` (403) requiring the SharePoint
Administrator role, which the tested account does not hold. Write identity for both creation paths
was the same delegated user account (`richard.fremmerlid@gov.bc.ca`) via the manage-only app
registration; whether a different write identity (e.g. a service principal or automation account)
could create agents at scale is untested.

**Verification path used:** the plan calls for tenant-admin confirmation, not test-agent creation,
to answer this stage. That confirmation was **not obtained** — the two working creation paths were
discovered as a side effect of write-based probing, not as a substitute for the required admin
sign-off.

**Evidence:** `phase-3-0-discovery-report.json` → `CopilotAdmin` (`Forbidden`), `CustomAgents`
(`Empty` — no pre-existing custom agents at read-only-probe time), `ReadyMadeAgent`
(`ManualRequired` — Microsoft doc citation that the ready-made agent has no `.agent` file to
enumerate); `research-summary...md` §2, §3, §4.

**Status:** `CONFIRMED_AVAILABLE` (technically, both creation paths work end-to-end for this
account) + `DEFERRED_UNTIL_EVIDENCE` (formal admin approval path, licensing/entitlement
confirmation, and any org-wide inclusion/scope settings remain unconfirmed — see
`ManualStepsNeeded` in the discovery report and Dependency-Status Map below).

---

## Probe 4 (Stage 3.0.2.4) — Native Markdown rendering: enabled?

**Finding:** Confirmed **yes**. SharePoint's built-in Markdown viewer correctly renders headings
and turns relative Markdown links into working in-viewer navigation between topic files (tested
against real `docx-to-content` plugin output: 25 of 26 CEIS manual topic pages plus 111 images),
and surfaces contextual Copilot suggestion chips automatically. This resolves a previously-flagged
manual-only item from the read-only discovery script (`ManualStepsNeeded` entry for Stage 3.0.2.4
in `phase-3-0-discovery-report.json`, which stated the read-only script itself cannot observe
rendered output).

**Verification path used:** a rendering attempt against real content in a designated
non-production test library, per the plan's required order — satisfied, screenshot-equivalent
confirmation recorded in the findings log.

**Evidence:** `research-summary...md`, Executive Summary "Confirmed working capabilities" item 4;
§13 ("Native Markdown rendering — CONFIRMED"). `phase-3-0-discovery-report.json` →
`ManualStepsNeeded[0]` (the original open item, now closed by this finding).

**Status:** `CONFIRMED_AVAILABLE`.

---

## Probe 5 (Stage 3.0.2.5) — Metadata field types/constraints available for a pilot library

**Finding:** Field/list creation is confirmed scriptable even under the manage-only app
registration: `New-PnPList -Template DocumentLibrary -EnableVersioning -EnableContentTypes` and
`Add-PnPField -Type Note` (a "multiple lines of text" field) were both exercised successfully
against a `TEST-DO-NOT-USE-Agent-Pilot` library. This establishes that **library creation and
field/content-type creation are separate rights from permission management** (`RoleAssignments`
is `Forbidden`, but list/field creation is not).

**What was not established:** a full field-type-constraint inventory (the plan's stated
deliverable is a "field type inventory" with "observed type constraints") — only one field type
(`Note`) was exercised in this session. Choice fields, managed-metadata/taxonomy fields, lookup
fields, person/group fields, and their specific constraints (max length, required-ness,
validation formulas) were not probed. `SiteFields`/`ContentTypes` were captured in the read-only
inventory (`phase-3-0-discovery-report.json`) but have not yet been synthesized into a schema
recommendation for the pilot library's actual planned columns (Subphase 3.1's later
schema-mapping work).

**Verification path used:** partial — one field type created against an authorized
non-production test library (satisfies the plan's staged-write requirement for what was tested),
but the deliverable's full scope ("field type inventory") is incomplete.

**Evidence:** `research-summary...md` §1 ("Document library creation — scriptable"), Technical
Mechanics §1; `phase-3-0-discovery-report.json` → `SiteFields`, `ContentTypes` (raw inventory,
not yet synthesized against pilot-library requirements).

**Status:** `PARTIALLY_CONFIRMED` — the mechanism (`Add-PnPField` under a manage-only
registration) is `CONFIRMED_AVAILABLE`; the full type/constraint inventory required by the
deliverable is `DEFERRED_UNTIL_EVIDENCE` (needs a dedicated probe enumerating each field type the
pilot's actual schema will need, once Subphase 3.1 defines that schema).

---

## Overall Gating Decision

Per the plan's exit gate ("`tenant-capability-report.md` answers all five probe questions with
observed evidence; Phase 3 scope confirmed feasible or explicitly re-gated"):

- **All five probes have cited, observed evidence in this report** — the exit gate's first
  clause is met.
- **Phase 3 scope is `PROVISIONALLY CONFIRMED FEASIBLE`, not unconditionally confirmed.** Every
  probe surfaced at least one genuine open item requiring further evidence before Phase 3
  implementation planning can treat it as settled:
  - Probe 1: exact write-principal list for `AgentAssets` (`NEEDS_ESCALATION`).
  - Probe 2: cross-agent/cross-site skill discovery and output-format enforcement
    (`PROVISIONAL`).
  - Probe 3: formal tenant-admin approval path for agent creation at scale (`DEFERRED_UNTIL_EVIDENCE`).
  - Probe 5: full metadata field-type/constraint inventory for the actual pilot schema
    (`DEFERRED_UNTIL_EVIDENCE`).
- No probe returned a hard `CONFIRMED_BLOCKED` finding against core Phase 3 functionality. The one
  confirmed platform boundary found in this session — raw `.aspx` file upload to Site Pages via
  `Add-PnPFile` returning `Access denied` (§15 of the findings log) — does **not** block Phase 3,
  because the supported alternative (`Add-PnPPage` + `Add-PnPPageTextPart`) was confirmed working
  in the same session.
- **Recommendation:** proceed to Stage 3.0.3.2 (dependency-status map, produced alongside this
  report) rather than re-gating Phase 3 outright, but do not treat Phase 3 as fully
  implementation-ready until the `NEEDS_ESCALATION`/`DEFERRED_UNTIL_EVIDENCE` items above are
  resolved or explicitly accepted as residual risk by the decision owner (the initiative's
  technical lead, per the plan's Stage 3.0.3.2 decision-owner assignment).

**Decision owner:** initiative technical lead. **Tenant admin sign-off required** on: the agent
creation approval path (Probe 3), and the `AgentAssets` write-principal question (Probe 1) — both
are `CONFIRMED_BLOCKED`-adjacent findings that a non-admin account cannot resolve.
