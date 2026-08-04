# Phase 7 Prior-Research Source Ledger

> Source repository (read-only, unmodified): `/Users/richardfremmerlid/Projects/AI-Research/01-Research/topics/`.
> Full bundled contents for external review: `temp/bundles/phase-7-prior-copilot-research/payload.md`
> (not committed — a temp/ working bundle, per this repo's scratch-output convention).
> Evidence-label meanings are defined in
> `docs/superpowers/specs/2026-08-03-phase-7-cowork-copilot-studio-desk-research-design.md` Section 2:
> `CURRENT_PRIMARY_SOURCE_VERIFIED`, `BUNDLED_PRIMARY_SOURCE`, `EMPIRICALLY_OBSERVED`,
> `SECONDARY_SOURCE_CLAIM`, `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`. Freshness-status values below
> use the six-value scheme from this ledger's own instructions: `STILL_CURRENT`,
> `UPDATED_BY_CURRENT_DOCUMENTATION`, `SUPERSEDED`, `REQUIRES_FRESHNESS_CHECK`,
> `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`, `NOT_RELEVANT_TO_PHASE_7`. No current-documentation
> re-fetch has been performed yet in this pass — no entry below is `UPDATED_BY_CURRENT_DOCUMENTATION`
> until that focused verification step actually runs.

## `microsoft-copilot-cowork/`

### `README.md`
- **Title:** Copilot Cowork Conversion Sandbox (folder index)
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** whole file (orientation only)
- **Phase 7 relevance:** low — points to the substantive files below
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7`
- **Conclusions reused:** none (index only)
- **Conclusions updated/rejected:** none

### `prompt.txt`
- **Title:** Adversarial-review prompt for the "M365 Copilot & Copilot Cowork Extensibility" blueprint
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** whole file
- **Phase 7 relevance:** provenance only — explains why the `research/reviews/*` chain exists
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7`
- **Conclusions reused:** none directly; establishes review-chain context used to interpret `viable-skills-summary.md`'s revision notes
- **Conclusions updated/rejected:** none

### `viable-skills-summary.md`
- **Title:** M365 Copilot & Copilot Cowork Extensibility — Strategic Architecture & Compatibility Blueprint (v6)
- **Date:** not stated (terminus of a review chain whose earlier rounds are dated March–June 2026)
- **External sources:** PromptArmor "Securing Microsoft Copilot Cowork: A Security Practitioner's Guide"; TD SYNNEX "The Copilot Cowork Power User Guide" (both third-party/consultant, `SECONDARY_SOURCE_CLAIM`)
- **Relevant sections:** Tier Map / "Missing Middle" (Tier 2); Primitive Gap table; Claim 6 (format- vs. runtime-compatible SKILL.md); Claim 7 (delegated identity vs. Entra Agent ID); Claim 8 (Anthropic subprocessor, regional-availability retraction); §5.x Split-Runtime trade-offs
- **Phase 7 relevance:** high — directly used for portability classification (design §3a), identity comparison (§3c), split-runtime assessment (§3b), and the Tier-2 classification of the primary workflow (§2)
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` (quota/latency/pricing figures explicitly self-flagged by the source); the architectural claims (Tier Map, Primitive Gap, Claim 6/7 structure) are `BUNDLED_PRIMARY_SOURCE` pending re-check, not yet `CURRENT_PRIMARY_SOURCE_VERIFIED`
- **Conclusions reused:** Tier Map/Primitive Gap framing; Claim 6 portability distinction; Claim 7 identity framing (with the correction that this is one data point, not proof of a full identity model — see design §3c)
- **Conclusions updated/rejected:** supersedes `research/reviews/agat-sovereignty-identity.md`'s regional-disablement claim (explicitly retracted in v6) and `research/reviews/gpt55-v1.md`'s 4–6hr Dataverse refresh figure (already corrected in `opus-v2.md`, reconfirmed absent here)

### `knowledge-plugins-analysis/README.md`
- **Title:** Cowork-compatibility review of Anthropic's `knowledge-work-plugins` catalog
- **Date:** not stated
- **External sources:** Anthropic `knowledge-work-plugins` catalog (not independently verified here)
- **Relevant sections:** 🟢/🟡/🔴 classification method
- **Phase 7 relevance:** method only (direct-fit/adaptation-required/incompatible classification), reused against this repo's own workflow steps in design §4 item 3 — **the third-party plugin subjects themselves are not reused**
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` for its specific findings; the classification method is reused, tracked separately, not as a "finding"
- **Conclusions reused:** classification method only
- **Conclusions updated/rejected:** none (subjects out of scope)

### `plugin-analysis/*.md` (9 files: `agent-agentic-os.md`, `agent-loops.md`, `agent-memory.md`, `agent-scaffolders.md`, `cli-agents.md`, `dependency-management.md`, `dev-utils.md`, `exploration-cycle-plugin.md`, `obsidian-wiki-engine.md`, `plugin-manager.md`, `spec-kitty-plugin.md`)
- **Title:** Per-plugin Cowork porting-feasibility verdicts (Claude-ecosystem marketplace plugins, not this repo's own plugins)
- **Date:** not stated
- **External sources:** none beyond the plugins' own source
- **Relevant sections:** file-count/hidden-file/no-delete/no-hooks constraint pattern; consistent mitigation recommendation ("keep complex logic external, use Cowork as chat front-end")
- **Phase 7 relevance:** method/precedent only — corroborates the Split-Runtime Hybrid pattern independently of `viable-skills-summary.md`
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` as literal findings about this repo's plugins; the recurring constraint pattern is `BUNDLED_PRIMARY_SOURCE` corroboration for the Split-Runtime pattern
- **Conclusions reused:** the recurring "external MCP/API for complex logic" pattern, as corroborating evidence for design §3b
- **Conclusions updated/rejected:** none

### `experimentation/analyze-gaps.py` and `experimentation/.gitkeep`
- **Excluded from the bundle.** `.gitkeep` has no content. `analyze-gaps.py` is the audit tooling that produced `research/compatibility-report.md` — its output is fully captured there; the script itself is implementation source, not a research finding.
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7`

### `research/overview.md`
- **Title:** Cowork capability/governance/tenant-prerequisite mapping (main file)
- **Date:** not stated; content describes "June 2026" GA state
- **External sources:** none cited directly (references the tutorial transcript below as source for walkthrough sections)
- **Relevant sections:** tenant prerequisites (Anthropic subprocessor opt-in, usage-based billing); 50-custom-skills-per-conversation limit; Agent Builder two-tab flow; admin governance (Purview DLP, Unified Audit Log); network requirements
- **Phase 7 relevance:** high — tenant-enablement facts for the Cowork disposition
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` (skill-count limits, model names, subprocessor requirement all self-flagged as time-sensitive)
- **Conclusions reused:** tenant-prerequisite list, admin-governance summary
- **Conclusions updated/rejected:** none within this file; skill-count figure (50) is itself internally inconsistent with `viable-skills-summary.md`'s hedge to "20–50, depending on the doc cited" — flag both as unresolved pending freshness check

### `research/limitations.md`
- **Title:** Architectural mismatch mapping (slash commands/hooks/sub-agents vs. Cowork model)
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** whole file
- **Phase 7 relevance:** high — direct evidence for the portability classification (design §3a)
- **Freshness status:** `BUNDLED_PRIMARY_SOURCE`
- **Conclusions reused:** unsupported-feature breakdown (commands/agents/hooks/bin), auth model contrast
- **Conclusions updated/rejected:** none

### `research/cowork-limitations.md`
- **Title:** Hard limits table; cannot-edit/delete/access-encrypted findings; embedded AGAT Software audit summary
- **Date:** embedded AGAT audit dated 2026-03-18
- **External sources:** AGAT Software (2026-03-18)
- **Relevant sections:** hard-limits table (50 skills/user, 1MB SKILL.md, 20-file/10MB companion cap); cannot-edit-in-place; cannot-delete
- **Phase 7 relevance:** high — direct constraint evidence for portability and split-runtime sections
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` for the numeric limits; the embedded AGAT regional-disablement claim is `SUPERSEDED` by `viable-skills-summary.md` v6's retraction
- **Conclusions reused:** hard-limits table
- **Conclusions updated/rejected:** regional-disablement claim superseded (see above)

### `research/criticisms.md`
- **Title:** Architectural critique (orchestration lock-in, size limits, no local execution, schema rigidity)
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** whole file
- **Phase 7 relevance:** medium — corroborates `research/limitations.md`
- **Freshness status:** `BUNDLED_PRIMARY_SOURCE`
- **Conclusions reused:** no-local-execution argument (design §3a)
- **Conclusions updated/rejected:** none

### `research/compatibility-report.md`
- **Title:** Empirical compatibility-scan output (`analyze-gaps.py`'s output) across this repo's marketplace-style plugins
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** whole file
- **Phase 7 relevance:** low-to-medium — same caveat as `plugin-analysis/*.md`: about the marketplace plugin catalog, not the Phase 7 workflow's own plugins
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` as direct findings; `EMPIRICALLY_OBSERVED` as a corroborating data point for the constraint pattern
- **Conclusions reused:** none directly cited in the memo beyond the general pattern already captured via `plugin-analysis/*.md`
- **Conclusions updated/rejected:** none

### `research/whats-new.md`
- **Title:** "June 2026 General Availability (GA)" feature summary
- **Date:** self-dated "as of June 2026 GA"
- **External sources:** none
- **Relevant sections:** model selector; Local Browser Use (Edge); MCP Apps; consumption billing
- **Phase 7 relevance:** medium — GA-status claims relevant to what's actually available to evaluate
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` — explicitly self-flagged by the file's own framing
- **Conclusions reused:** none yet (pending freshness check before citing GA-status claims)
- **Conclusions updated/rejected:** none

### `research/elicitation.md`
- **Title:** Elicitation Forms JSON-RPC protocol reference
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** whole file
- **Phase 7 relevance:** medium — relevant to the "intake conversation" capability classification (design §4 item 3)
- **Freshness status:** `BUNDLED_PRIMARY_SOURCE`
- **Conclusions reused:** flat-schema/max-5–7-field constraints, for the intake-step classification
- **Conclusions updated/rejected:** none

### `research/how-to-build-custom-skills.md`
- **Title:** Practitioner tutorial on SKILL.md authoring conventions
- **Date:** not stated
- **External sources:** Shane Young (external practitioner, not a Microsoft doc)
- **Relevant sections:** naming constraints; two authoring methods; worked example
- **Phase 7 relevance:** medium — supports the portability classification (design §3a)
- **Freshness status:** `SECONDARY_SOURCE_CLAIM`
- **Conclusions reused:** authoring-method description
- **Conclusions updated/rejected:** none

### `research/mcp-apps.md`
- **Title:** MCP Apps Extension (SEP-1865) technical reference
- **Date:** not stated
- **External sources:** SEP-1865 (spec reference, not independently fetched)
- **Relevant sections:** widget/tool declaration constraints, CSP behavior
- **Phase 7 relevance:** low-to-medium — relevant only if a future pilot considered interactive UI widgets for this workflow
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** none yet
- **Conclusions updated/rejected:** none

### `research/schema-notes.md`
- **Title:** Unified Manifest v1.28 schema reference; the four packaging patterns
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** four packaging patterns (Skills-only, Skills+Remote Connector, Connector-only, Converted Claude Plugins)
- **Phase 7 relevance:** high — direct evidence that no native packaging/reconcile model exists for prompt-only skills (design §3a/§3)
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** "no reconcile-against-environment step exists" finding
- **Conclusions updated/rejected:** none

### `research/agent_365_tutorial_transcript.txt`
- **Title:** Raw YouTube tutorial transcript underlying `research/overview.md`'s walkthrough sections
- **Date:** not stated
- **External sources:** YouTube video (informal, not a Microsoft doc)
- **Relevant sections:** not independently extracted — already synthesized in `research/overview.md`
- **Phase 7 relevance:** low — primary-source backing for `overview.md`, not independently cited
- **Freshness status:** `SECONDARY_SOURCE_CLAIM` (informal video transcript)
- **Conclusions reused:** none independently (superseded in practice by `overview.md`'s synthesis)
- **Conclusions updated/rejected:** none

### `research/reviews/agat-sovereignty-identity.md`
- **Title:** AGAT Software external audit
- **Date:** 2026-03-18
- **External sources:** AGAT Software
- **Relevant sections:** identity/audit dilution; regional-disablement claim
- **Phase 7 relevance:** medium — identity-dilution finding still referenced (softened) in `viable-skills-summary.md` Claim 7
- **Freshness status:** `SUPERSEDED` on the regional-disablement claim (retracted by v6); identity-dilution finding `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** identity-dilution concern (folded into design §3c, not as a settled fact)
- **Conclusions updated/rejected:** regional-disablement claim rejected/superseded

### `research/reviews/gemini-image-analysis.md`
- **Title:** Review of the internal "Innovation Conveyor" governance model
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** whole file
- **Phase 7 relevance:** low — this repo's own architecture proposal, not a Microsoft-platform finding
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7`
- **Conclusions reused:** none
- **Conclusions updated/rejected:** none

### `research/reviews/gemini-v3.md`
- **Title:** Blueprint v3 adversarial review
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** Split-Runtime trade-offs; quota figures (later flagged for re-verification)
- **Phase 7 relevance:** medium — early version of claims later refined in `opus-v2.md`/`opus-v3.md`/v6
- **Freshness status:** `SUPERSEDED` for the quota figures specifically (refined by `opus-v2.md`/
  `viable-skills-summary.md` v6); `REQUIRES_FRESHNESS_CHECK` for the Split-Runtime trade-off
  content not yet re-verified against a live source
- **Conclusions reused:** Split-Runtime trade-off catalogue origin (refined later, cite the v6 version instead)
- **Conclusions updated/rejected:** quota figures (50 OneDrive files/25 SharePoint sites) flagged for re-verification by later rounds

### `research/reviews/gpt55-v1.md`
- **Title:** Independent balanced review
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** Split-Runtime nuance; Copilot Studio OneDrive knowledge-sync refresh-window claim
- **Phase 7 relevance:** low as a standalone source — superseded content
- **Freshness status:** `SUPERSEDED` — the "4–6hr Dataverse refresh window" claim is explicitly removed as unsubstantiated in `opus-v2.md`
- **Conclusions reused:** none (superseded)
- **Conclusions updated/rejected:** 4–6hr Dataverse refresh figure rejected

### `research/reviews/opus-v2.md`
- **Title:** Blueprint v2 revision
- **Date:** not stated
- **External sources:** none
- **Relevant sections:** retraction of the 4–6hr figure; Copilot Studio quota figures (500 knowledge sources/agent, 8,000-char instructions, 5MB/450KB connector payload, 512MB uploads, 100 skills/agent, 1,000 topics/agent); Split-Runtime trade-off catalogue; decision-tree
- **Phase 7 relevance:** high — quota figures directly relevant to Studio capacity/licensing facts
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` — the file's own quota figures are themselves flagged by `viable-skills-summary.md` v6 as needing re-verification before external publication
- **Conclusions reused:** Split-Runtime trade-off catalogue (refined into design §3b)
- **Conclusions updated/rejected:** supersedes `gpt55-v1.md`'s refresh-window claim

### `research/reviews/opus-v3.md`
- **Title:** Adversarial audit of Blueprint v3
- **Date:** references events dated 2026-05-01 (Agent 365 Wave 3), 2026-06-02 (GitHub Copilot MXC preview), 2026-06-16 (Cowork GA)
- **External sources:** none
- **Relevant sections:** GitHub Copilot MXC sandboxes; M365 Agents Playground; Agent 365; Cowork GA timeline; pricing-claim skepticism; ITSG-33 control mapping (AC-4, SC-7, SI-7)
- **Phase 7 relevance:** high — ITSG-33 mapping directly relevant to design §3b's compliance dimension; pricing skepticism directly relevant to cost-comparison claims
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` for the dated events; the "30–40% cheaper than Claude Cowork" claim is explicitly flagged `SECONDARY_SOURCE_CLAIM`/unverified vendor marketing
- **Conclusions reused:** ITSG-33 control names (design §3b); pricing-claim skepticism
- **Conclusions updated/rejected:** corrects an implicit "total rejection of local execution" framing in earlier reviews

## `microsoft-copilot-studio/`

### `HANDOFF-claude-code.md`
- **Title:** Session handoff for hands-on Copilot Studio build
- **Date:** 2026-06-20
- **External sources:** none
- **Relevant sections:** whole file (orientation)
- **Phase 7 relevance:** low directly; establishes that `agent-build-walkthrough.md`/`learnings.md` are genuinely hands-on, not synthesized
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` as a standalone finding
- **Conclusions reused:** none directly
- **Conclusions updated/rejected:** none

### `agent-build-walkthrough.md`
- **Title:** Step-by-step hands-on Copilot Studio build log
- **Date:** 2026-06-20, BC Government Shared Environment
- **External sources:** none (direct observation)
- **Relevant sections:** Step 3–3d (Instructions field is the real system prompt, Description is not); Step 4 (Message-node non-verbatim reformatting); Step 5 (blanket knowledge-connector DLP block, `DataLossPreventionViolation`); Step 6 (channel/auth restrictions, Entra App Registration requirement)
- **Phase 7 relevance:** high — directly used for design §3b (lifecycle-trigger candidates, framed as candidates only) and §3c (identity note, one connected-agent OAuth pattern only)
- **Freshness status:** `EMPIRICALLY_OBSERVED`, tenant-scoped — this ledger's account/domain finding (`gov.bc.ca`) makes this same-account-context evidence per the design's corrected Section 2 language, not proof of this project's own tenant's compliance boundary
- **Conclusions reused:** Message-node non-verbatim finding (validation-step risk); Instructions-vs-Description distinction; DLP-block observation
- **Conclusions updated/rejected:** none within this file; its Default-Environment scoping is narrowed by `learnings.md` L23 (see below)

### `generative-orchestration.md`
- **Title:** Generative orchestration architecture (decision boundaries, lifecycle triggers, Connected Agents)
- **Date:** not stated (earlier research than the hands-on session)
- **External sources:** none
- **Relevant sections:** §8 Connected Agents I/O contracts; §9 comparison table (Dataverse-solution-export-only versioning, no git-diff); Three-Layer Decision Boundaries; lifecycle interception triggers (`OnKnowledgeRequested`, `AI Response Generated`, `On Plan Complete`)
- **Phase 7 relevance:** high — direct basis for design §3 (artifact-pattern angle), §3b (lifecycle-trigger candidates), §3c (identity, one pattern only)
- **Freshness status:** `BUNDLED_PRIMARY_SOURCE`
- **Conclusions reused:** §8/§9 findings, reframed as candidates per this round's correction (not established execution semantics)
- **Conclusions updated/rejected:** none within this file; the lifecycle-trigger→workflow-step mapping is my own inference and is explicitly downgraded to "candidate" in the corrected design, not this file's own claim

### `learnings.md`
- **Title:** Distilled learnings L1–L25 from the same hands-on build
- **Date:** 2026-06-20
- **External sources:** community-sourced billing complaint (L25 only, explicitly flagged lower-confidence)
- **Relevant sections:** L1 (Instructions = system prompt); L16 (DLP is a connector allowlist, not a data-flow scanner); L19–L20 (Purview/Power-Platform-DLP governance-engine mismatch, explicitly unresolved as of June 2026); L21–L22 (root-cause confirmation of the connector block, `DataLossPreventionViolation` runtime behavior); **L23 (Default Environment vs. Custom/Dedicated Environment scoping — the source's own generalizability caveat)**; L24–L25 (cost/capacity, L25 explicitly community-sourced)
- **Phase 7 relevance:** highest-confidence empirical source in the whole corpus; L23 is the basis for the Dedicated-Environment precondition now in the design (§7)
- **Freshness status:** `EMPIRICALLY_OBSERVED` for L1–L23 (tenant/environment-scoped per L23's own caveat); L25 is `SECONDARY_SOURCE_CLAIM`
- **Conclusions reused:** L23 Dedicated-Environment precondition; L16 DLP-mechanism correction; L19 governance-mismatch finding
- **Conclusions updated/rejected:** none within this file; L23 itself narrows how far `agent-build-walkthrough.md`'s Step 5/6 findings may be generalized

## `microsoft-m365-agents/`

> Not a Phase 7 evaluation target (see design §6 non-goals) — included in the ledger only because it was bundled as Studio-interop background.

### `create-deploy-agents-sdk.md`
- **Title:** Build and deploy agents with Microsoft 365 Agents SDK
- **Date:** `ms.date: 2025-05-15`, `updated_at: 2025-12-02` (real Microsoft Learn frontmatter)
- **External sources:** Microsoft Learn
- **Relevant sections:** onboarding paths, Agents Playground
- **Phase 7 relevance:** low — background only, not an evaluation target
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` (real dated primary source, but predates mid-2026 GA claims elsewhere in the corpus; lowest freshness risk of the whole bundle)
- **Conclusions reused:** none directly cited in the design
- **Conclusions updated/rejected:** none

### `create-new-toolkit-project-vs.md`
- **Title:** Create a new Microsoft 365 Agents Toolkit project in Visual Studio
- **Date:** `ms.date: 2025-11-21`, `updated_at: 2025-11-24`
- **External sources:** Microsoft Learn
- **Relevant sections:** Weather Agent scaffolding walkthrough
- **Phase 7 relevance:** low — background only
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** none
- **Conclusions updated/rejected:** none

### `github-sdk-reference.md`
- **Title:** M365 Agents SDK GitHub repo index
- **Date:** not stated
- **External sources:** GitHub (`Microsoft/Agents`, `Microsoft/Agents-for-net`, `Microsoft/Agents-for-js`, `Microsoft/Agents-for-python`)
- **Relevant sections:** explicit confirmation that the SDK can integrate custom coded agents into Copilot Studio's generative planning graph
- **Phase 7 relevance:** medium — the clearest primary-source confirmation of SDK↔Studio interop, used only as Studio background (design §3), not as a build target
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** SDK↔Studio interop confirmation (context only)
- **Conclusions updated/rejected:** none

### `m365-agents-sdk.md`
- **Title:** When to use the Microsoft 365 Agents SDK
- **Date:** `ms.date: 2025-07-21`, `updated_at: 2025-07-22`
- **External sources:** Microsoft Learn
- **Relevant sections:** explicit constraint — "Publishing agents via the Microsoft 365 Agents Toolkit isn't supported in Microsoft 365 Government tenants"
- **Phase 7 relevance:** medium — directly relevant given the confirmed `gov.bc.ca` account context (though tenant classification itself remains `TENANT_UNKNOWN` per the design's correction); noted as background, not acted on, since the SDK is not a Phase 7 target
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` (real Microsoft Learn dates, still the lowest-risk source in the corpus)
- **Conclusions reused:** government-tenant constraint noted as a flag for any future SDK-adjacent work, not applied to this round's disposition
- **Conclusions updated/rejected:** none

## Unresolved questions carried forward from the prior research (not resolved by this ledger)

- Governance-engine mismatch between M365 Copilot Chat (Purview) and Copilot Studio (Power Platform DLP) — `learnings.md` L19–L20, explicitly unresolved by the original researcher as of June 2026.
- Whether the Default-vs-Custom/Dedicated-Environment distinction (`learnings.md` L23) actually changes the Step 5/6 DLP-blocking outcome — cannot be resolved from documentation; requires direct testing once a Dedicated Environment exists.
- Cowork regional/subprocessor availability contradiction (`agat-sovereignty-identity.md` vs. `viable-skills-summary.md` v6) — the later, hedged version is treated as authoritative per this ledger, but neither has been re-verified against current Microsoft Learn this phase.
- Whether this project's own tenant shares the compliance/regional/hosting characteristics of the BC Government Shared Environment described in `agent-build-walkthrough.md`/`learnings.md` — explicitly `TENANT_UNKNOWN` per the corrected design; not resolvable from the bundle alone.

## What Phase 7 added rather than repeated

- The three-way baseline framing (workbench + native SharePoint agent + candidate platform) — not present in the prior research, which only ever compared the marketplace plugin catalog or a generic blueprint against Cowork/Studio.
- The instructional-format-vs-executable-runtime classification applied specifically to this repository's own workflow steps (design §4 item 3) — the prior research's classification method existed, but had never been applied to this repo's actual `source-document-extraction`/`sharepoint-agents-and-skills`/etc. capabilities.
- The identity decision matrix distinguishing deployment/retrieval/user-interaction/approval/publication identity as separately evidenced fields — the prior research documented identity findings but never in this decomposed form.
- The corrected recognition that `repository-claude`'s `TooManyRelatedTopicsError` is genuinely deterministic while `native-sharepoint`'s equivalent is not — a fact from this repo's own Phase 6 evidence, not present in the AI-Research corpus at all.
