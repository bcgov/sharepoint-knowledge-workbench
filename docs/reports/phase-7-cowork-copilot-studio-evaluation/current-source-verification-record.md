# Phase 7 Current-Source Verification Record

> Focused freshness-check pass against live Microsoft Learn / current web sources, per the design's
> Section 7 method requirement. Scope limited to claims material to the two dispositions, per
> instruction — not all 40 bundled files. Fetched 2026-08-03 via live web search.

## 1. Copilot Studio lifecycle triggers

**Verified current.** `OnKnowledgeRequested`, `AI Response Generated`, `Plan Complete` (note: the
bundle's `generative-orchestration.md` names it "On Plan Complete"; current Microsoft
documentation uses "Plan Complete" — a naming variant, not a substantive discrepancy), and
"Triggered by Agent" are real, currently-documented generative-orchestration lifecycle triggers.

- Sources: [Apply generative orchestration capabilities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration), [Orchestrate agent behavior with generative AI](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions), [FAQs: generative orchestration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/faqs-generative-orchestration)
- Additional current detail not in the bundle: `OnKnowledgeRequested` topics are invoked either
  when the Orchestrator determines retrieval is needed, or when a Generative Answers node is
  directly invoked; results are capped at 15 combined snippets across all knowledge topics; as of
  September 2025 this trigger required YAML code view (no UI designer support at that time).
- **Evidence type/confidence:** `CURRENT_PRIMARY_SOURCE_VERIFIED`.
- **Effect on memo:** upgrades the bundle's `BUNDLED_RESEARCH_SYNTHESIS`-tagged trigger claims to
  `CURRENT_PRIMARY_SOURCE_VERIFIED` for the triggers' existence and names; the workflow-step
  mapping itself (Section 3b of the design) remains a candidate use, not established semantics —
  unaffected by this verification.

## 2. Connected Agents input/output contracts

**Verified current.** Copilot Studio distinguishes child agents (fully owned) from connected
agents (independent, reusable). Inputs/outputs define data flow; connected-agent-side
configuration requires an `OnRedirect` topic with `inputType`/`outputType` declarations, plus a
known `botSchemaName`.

- Sources: [Add other agents overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents), [Using Inputs and Outputs in Child and Connected Agents](https://microsoft.github.io/mcscatblog/posts/copilot-studio-child-connected-agents-inputs-outputs/)
- **Evidence type/confidence:** `CURRENT_PRIMARY_SOURCE_VERIFIED`.
- **Effect on memo:** confirms the design/memo's Section 7 (agent-as-artifact angle) finding —
  Connected Agents remain the closest native primitive to a typed, callable artifact. No change to
  the "no native git-tracked reconcile workflow" conclusion (see item 3, which does add nuance).

## 3. Copilot Studio solution export / ALM

**Updates the bundle's claim.** The bundle (`generative-orchestration.md` §9) states version
control exists "only via exporting solutions as compressed XML/JSON packages... no native
git-diff/PR workflow." Current documentation confirms the Dataverse-solution-export mechanism is
real, but **adds a materially relevant nuance not in the bundle**: Copilot Studio ALM supports
CI/CD tooling with native Git integration for pro-dev setups — Azure DevOps, GitHub Actions for
Power Platform, and Pipelines in Power Platform are all named as supported ALM automation paths.

- Source: [Establish an ALM strategy — Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/alm)
- **Evidence type/confidence:** `CURRENT_PRIMARY_SOURCE_VERIFIED`.
- **Effect on memo:** `UPDATED_BY_CURRENT_DOCUMENTATION`. The claim "no native git-diff/PR
  workflow" is too strong as originally stated — Git-based CI/CD *is* a supported ALM path, though
  it wraps Dataverse-solution export/import rather than tracking human-readable source files the
  way `sharepoint-agents-and-skills`' plain-markdown-in-git model does. The underlying distinction
  (solution-package-centric vs. file-centric artifact model) still holds; the specific "no git
  integration at all" framing does not and is corrected in the memo.

## 4. Copilot Studio identity model

**Materially updates the bundle's Claim 7 framing.** The bundle (`viable-skills-summary.md` Claim
7) frames Copilot Studio/Cowork as using only delegated end-user identity, with dedicated agent
identity described as a "Primitive Gap" (platform capability exists, product surface doesn't wire
it in). Current documentation shows this gap has since been **closed for Copilot Studio
specifically**: as of the July 2026 rollout, Copilot Studio automatically provisions a Microsoft
Entra Agent ID for every new agent, and opting out is no longer possible. Two authentication flows
are confirmed to coexist: On-Behalf-Of (delegated, most connectors, token managed automatically)
and Client Credentials Flow (autonomous agents, distinct agent identity, requires an HTTP Request
node since built-in connectors default to delegated flows).

- Sources: [Automatically create Entra Agent IDs — Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-use-entra-agent-identities), [Agent identity integration for Copilot Studio](https://learn.microsoft.com/en-us/microsoft-agent-365/builder/identity), [Recreate Copilot Studio agents with Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/migrate-copilot-studio-agents-to-agent-id)
- **Evidence type/confidence:** `CURRENT_PRIMARY_SOURCE_VERIFIED`.
- **Effect on memo:** `UPDATED_BY_CURRENT_DOCUMENTATION`. **This is the single most consequential
  freshness finding in this pass.** The bundle's Claim 7 "Primitive Gap" framing for Copilot
  Studio is dated — Studio agents built after the July 2026 rollout have a real, dedicated Entra
  Agent ID by default, not only delegated identity. This directly affects the identity decision
  matrix (design Section 3c): Copilot Studio's deployment/execution identity is no longer
  uniformly `UNKNOWN`/delegated-only — it is `CURRENT_PRIMARY_SOURCE_VERIFIED` as
  agent-service-principal-based for newly created agents, with On-Behalf-Of remaining the
  connector-execution default. **This finding does not extend to Cowork** — no current source
  found in this pass confirms or denies whether the Cowork product surface itself has adopted the
  same Entra Agent ID model; Cowork's identity claim in the memo remains `BUNDLED_RESEARCH_
  SYNTHESIS`-sourced, unresolved by this verification pass.

## 5. Power Platform DLP / default-environment connector blocking

**Corroborates the general mechanism, does not resolve the Default-vs-Dedicated-Environment
question.** Current documentation confirms DLP policies genuinely function as a connector
allowlist (matching `learnings.md` L16's correction of the "DLP" misnomer), that blocked
connectors fail at runtime, and that the default environment carries elevated risk because all
licensed users get Environment Maker access there by default — supporting the general blocking
mechanism described in the bundle.

- Source: [Data policies — Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention), [Manage data policies](https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss)
- **Evidence type/confidence:** `CURRENT_PRIMARY_SOURCE_VERIFIED` for the general DLP/connector-
  allowlist mechanism.
- **Effect on memo:** confirms the mechanism is real and current; **does not** confirm or deny
  `learnings.md` L23's specific claim that Custom/Dedicated Environments behave differently from
  the Default Environment observed in the hands-on testing — this remains
  `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`, unresolved by this pass, consistent with the Dedicated-
  Environment precondition already in the design (Section 7).

## 6. Cowork custom skills / executable-asset packaging

**Corroborates the format-not-runtime claim, with one scoped correction.** Current documentation
confirms the 20-companion-file/10MB-per-skill cap, the OneDrive-folder-based skill structure, and
that skills run as instructions to the AI. **Correction:** the bundle's "no local execution"
framing is accurate for the general skill-authoring path but is too absolute — for Excel-specific
skills, Copilot in Excel does execute JavaScript against a real Office.js runtime from a skill's
`\scripts` folder. This is a scoped, Excel-context exception, not a general capability.

- Sources: [Build plugins for Copilot Cowork](https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development), [Use Copilot Cowork](https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork), [Overview of Copilot skills for Excel (preview)](https://learn.microsoft.com/en-us/office/dev/add-ins/excel/excel-skills)
- **Evidence type/confidence:** `CURRENT_PRIMARY_SOURCE_VERIFIED`.
- **Effect on memo:** `UPDATED_BY_CURRENT_DOCUMENTATION` — the portability classification (design
  §3a) is corrected from an absolute "no executable capability" statement to "no executable
  capability for this workflow's needs (extraction/rendering/validation are not Excel-scoped
  operations)," since a scoped Excel-JS execution path does exist for a different skill category.
  This does not change either disposition — the primary workflow's actual operations are not
  Excel-based.

## 7. Cowork tenant enablement (Anthropic subprocessor, billing)

**Updates the bundle's framing from opt-in to default-on for most tenants.** Current documentation
shows Anthropic has been onboarded as a Microsoft subprocessor and, since 2026-01-07, is enabled
**by default** for most commercial M365 tenants — the admin action required is disabling it, not
enabling it, except for EU/EFTA/UK tenants where it remains default-off. Usage-based billing
(Copilot Credits, via Global/Billing Admin) is still required to use Cowork itself.

- Sources: [Copilot in Microsoft 365 apps with Anthropic models](https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-anthropic-apps), [Turning on Copilot Cowork](https://c7solutions.com/2026/06/turning-on-copilot-cowork), [How to Enable Copilot Cowork](https://www.cowork.tips/blog/how-to-enable-copilot-cowork)
- **Evidence type/confidence:** `CURRENT_PRIMARY_SOURCE_VERIFIED` for the Microsoft Learn source;
  `SECONDARY_SOURCE_CLAIM` for the two blog/community sources (corroborating, not authoritative).
- **Effect on memo:** `UPDATED_BY_CURRENT_DOCUMENTATION` — the bundle's "explicit opt-in required"
  framing (`research/overview.md`) is superseded for most regions; the actual current gate is
  billing enablement plus a *default-on, EU/EFTA/UK default-off* subprocessor toggle. This tenant's
  regional/compliance classification remains `TENANT_UNKNOWN` (per the design's correction), so
  which default applies here is not resolved by this finding alone.

## Claims not resolved by this pass (remain as previously labeled)

- Whether this project's own tenant is subject to the EU/EFTA/UK/GCC-High-equivalent default-off
  Anthropic-subprocessor category — `TENANT_UNKNOWN`.
- Whether a Custom/Dedicated Copilot Studio Environment actually resolves the observed
  Default-Environment DLP blocking — `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`.
- Whether the Cowork product surface (as distinct from Copilot Studio) has adopted Entra Agent ID
  — not found in this pass, remains `BUNDLED_RESEARCH_SYNTHESIS`-sourced only.
- Message-node non-verbatim behavior and whether it can be disabled at the topic level — not
  covered by this pass's queries, remains `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`.
