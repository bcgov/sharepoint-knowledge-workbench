# Phase 7 Prior-Research Source Ledger

> Source repository (read-only, unmodified): `/Users/richardfremmerlid/Projects/AI-Research/01-Research/topics/`.
> Full bundled contents for external review: `temp/bundles/phase-7-prior-copilot-research/payload.md`
> (not committed — a temp/ working bundle, per this repo's scratch-output convention).
>
> **Two separate fields per entry, per design Section 4a — never conflated:**
> - **Evidence type/confidence** — one of `CURRENT_PRIMARY_SOURCE_VERIFIED`,
>   `BUNDLED_PRIMARY_SOURCE` (actual captured Microsoft doc content only),
>   `BUNDLED_RESEARCH_SYNTHESIS` (internally authored analysis/blueprint/notes),
>   `EMPIRICALLY_OBSERVED`, `REPOSITORY_VERIFIED`, `SECONDARY_SOURCE_CLAIM`,
>   `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`.
> - **Freshness status** — one of `STILL_CURRENT`, `UPDATED_BY_CURRENT_DOCUMENTATION`,
>   `SUPERSEDED`, `REQUIRES_FRESHNESS_CHECK`, `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`,
>   `NOT_RELEVANT_TO_PHASE_7`.
>
> Current-documentation results referenced below are recorded in full in
> `current-source-verification-record.md`.

## `microsoft-copilot-cowork/`

### `README.md`
- **Title:** Copilot Cowork Conversion Sandbox (folder index)
- **Date:** not stated · **External sources:** none · **Relevant sections:** whole file (orientation)
- **Phase 7 relevance:** low — points to substantive files below
- **Evidence type/confidence:** n/a (index, not a finding)
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7`
- **Conclusions reused/updated:** none

### `prompt.txt`
- **Title:** Adversarial-review prompt for the Cowork blueprint · **Date:** not stated
- **Phase 7 relevance:** provenance only — explains why `research/reviews/*` exists
- **Evidence type/confidence:** n/a · **Freshness status:** `NOT_RELEVANT_TO_PHASE_7`
- **Conclusions reused/updated:** none

### `viable-skills-summary.md`
- **Title:** M365 Copilot & Copilot Cowork Extensibility — Strategic Architecture & Compatibility Blueprint (v6)
- **Date:** not stated (terminus of a review chain dated March–June 2026)
- **External sources:** PromptArmor, TD SYNNEX (both third-party/consultant)
- **Relevant sections:** Tier Map/Primitive Gap table; Claim 6 (format- vs. runtime-compatible); Claim 7 (identity); Claim 8 (subprocessor/regional); §5.x Split-Runtime trade-offs
- **Phase 7 relevance:** high — portability (§3a), identity (§3c), split-runtime (§3b), Tier-2 classification
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from an earlier
  mislabeling as `BUNDLED_PRIMARY_SOURCE`.** This is an internally authored blueprint document
  citing third-party consultant sources, not captured Microsoft documentation.
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` for quota/latency/pricing figures (self-flagged
  by the source); Claim 7 (identity) is now `UPDATED_BY_CURRENT_DOCUMENTATION` for Copilot Studio
  specifically per current-source item 4 (Studio agents now get automatic Entra Agent ID as of the
  July 2026 rollout) — **this update does not extend to Cowork**, which remains unverified
- **Conclusions reused:** Tier Map/Primitive Gap framing (Cowork only); Claim 6 portability distinction
- **Conclusions updated/rejected:** Claim 7's "delegated-only" framing is outdated for Copilot
  Studio (see current-source item 4); supersedes `research/reviews/agat-sovereignty-identity.md`'s
  regional-disablement claim; supersedes `research/reviews/gpt55-v1.md`'s Dataverse-refresh figure

### `knowledge-plugins-analysis/README.md`
- **Title:** Cowork-compatibility review of Anthropic's `knowledge-work-plugins` catalog
- **Phase 7 relevance:** method only (🟢/🟡/🔴 classification), reused against this repo's own
  workflow steps — **the third-party plugin subjects themselves are not reused as findings**
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` · **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` (subjects); method itself not date-sensitive
- **Conclusions reused:** classification method only

### `plugin-analysis/*.md` — **11 files** (corrected from an earlier miscount of 9): `agent-agentic-os.md`, `agent-loops.md`, `agent-memory.md`, `agent-scaffolders.md`, `cli-agents.md`, `dependency-management.md`, `dev-utils.md`, `exploration-cycle-plugin.md`, `obsidian-wiki-engine.md`, `plugin-manager.md`, `spec-kitty-plugin.md`
- **Title:** Per-plugin Cowork porting-feasibility verdicts (Claude-ecosystem marketplace plugins, not this repo's own plugins)
- **Phase 7 relevance:** method/precedent only — corroborates the Split-Runtime pattern independently of `viable-skills-summary.md`
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` · **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` as literal findings about this repo's plugins
- **Conclusions reused:** the recurring "external MCP/API for complex logic" pattern, as corroboration only

### `experimentation/analyze-gaps.py`, `experimentation/.gitkeep`
- Excluded from the bundle — tooling script (output fully captured in `research/compatibility-report.md`) and an empty placeholder. **Freshness status:** `NOT_RELEVANT_TO_PHASE_7`.

### `research/overview.md`
- **Title:** Cowork capability/governance/tenant-prerequisite mapping · **Date:** not stated, describes "June 2026" GA state
- **Relevant sections:** tenant prerequisites; 50-skills-per-conversation limit; Agent Builder; admin governance
- **Phase 7 relevance:** high — tenant-enablement facts
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**
- **Freshness status:** `UPDATED_BY_CURRENT_DOCUMENTATION` for the subprocessor-enablement claim
  (current-source item 7: default-on for most tenants as of 2026-01-07, not admin opt-in as
  originally stated); `REQUIRES_FRESHNESS_CHECK` for skill-count limits and model names
- **Conclusions reused:** tenant-prerequisite list (with the above update applied)
- **Conclusions updated/rejected:** subprocessor-enablement direction corrected (see above)

### `research/limitations.md`
- **Title:** Architectural mismatch mapping (slash commands/hooks/sub-agents vs. Cowork)
- **Phase 7 relevance:** high — portability classification (§3a)
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** unsupported-feature breakdown, corroborated current-source item 6 (Cowork execution model, with the Excel-scoped exception noted there)

### `research/cowork-limitations.md`
- **Title:** Hard limits table; embedded AGAT Software audit (2026-03-18)
- **Phase 7 relevance:** high — portability/split-runtime constraint evidence
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**; the embedded AGAT audit summary within it is `SECONDARY_SOURCE_CLAIM`
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` for the numeric limits (current-source item 6
  confirms the 20-file/10MB cap as `CURRENT_PRIMARY_SOURCE_VERIFIED`, superseding this entry for
  that specific figure — `UPDATED_BY_CURRENT_DOCUMENTATION` for that figure only); `SUPERSEDED`
  for the embedded regional-disablement claim (retracted by `viable-skills-summary.md` v6)
- **Conclusions reused:** hard-limits table (companion-file cap now current-verified)
- **Conclusions updated/rejected:** regional-disablement claim superseded

### `research/criticisms.md`
- **Title:** Architectural critique (orchestration lock-in, size limits, no local execution)
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** no-local-execution argument, with current-source item 6's Excel-scoped exception noted

### `research/compatibility-report.md`
- **Title:** Empirical compatibility-scan output across the marketplace plugin catalog
- **Phase 7 relevance:** low-to-medium — same caveat as `plugin-analysis/*.md`
- **Evidence type/confidence:** `EMPIRICALLY_OBSERVED` (script-run output) · **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` as direct findings
- **Conclusions reused:** none directly cited beyond the general pattern

### `research/whats-new.md`
- **Title:** "June 2026 GA" feature summary
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` — self-flagged by the source itself
- **Conclusions reused:** none yet

### `research/elicitation.md`
- **Title:** Elicitation Forms JSON-RPC protocol reference
- **Phase 7 relevance:** medium — "intake conversation" capability classification
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** flat-schema/field-count constraints

### `research/how-to-build-custom-skills.md`
- **Title:** Practitioner tutorial on SKILL.md authoring · **External sources:** Shane Young (external practitioner)
- **Evidence type/confidence:** `SECONDARY_SOURCE_CLAIM` · **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** authoring-method description, corroborated by current-source item 6

### `research/mcp-apps.md`
- **Title:** MCP Apps Extension (SEP-1865) technical reference
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** none yet — low priority for this workflow

### `research/schema-notes.md`
- **Title:** Unified Manifest v1.28 schema reference; four packaging patterns
- **Phase 7 relevance:** high — no reconcile-against-environment step exists
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** "no reconcile step" finding

### `research/agent_365_tutorial_transcript.txt`
- **Title:** Raw YouTube tutorial transcript underlying `research/overview.md`
- **Evidence type/confidence:** `SECONDARY_SOURCE_CLAIM` (informal video, not a Microsoft doc)
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` (superseded in practice by `overview.md`'s synthesis)
- **Conclusions reused:** none independently

### `research/reviews/agat-sovereignty-identity.md`
- **Title:** AGAT Software external audit · **Date:** 2026-03-18 · **External sources:** AGAT Software
- **Evidence type/confidence:** `SECONDARY_SOURCE_CLAIM`
- **Freshness status:** `SUPERSEDED` on the regional-disablement claim; `REQUIRES_FRESHNESS_CHECK` on identity-dilution concern
- **Conclusions reused:** identity-dilution concern (folded into §3c as unresolved, not settled)
- **Conclusions updated/rejected:** regional-disablement claim rejected

### `research/reviews/gemini-image-analysis.md`
- **Title:** Review of the internal "Innovation Conveyor" governance model — this repo's own architecture proposal
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` · **Freshness status:** `NOT_RELEVANT_TO_PHASE_7`
- **Conclusions reused:** none

### `research/reviews/gemini-v3.md`
- **Title:** Blueprint v3 adversarial review
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS`
- **Freshness status:** `SUPERSEDED` for the quota figures specifically (refined by `opus-v2.md`/`viable-skills-summary.md` v6); `REQUIRES_FRESHNESS_CHECK` for the Split-Runtime trade-off content not yet re-verified against a live source
- **Conclusions reused:** Split-Runtime trade-off catalogue origin (cite v6 instead)
- **Conclusions updated/rejected:** quota figures flagged for re-verification by later rounds

### `research/reviews/gpt55-v1.md`
- **Title:** Independent balanced review
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS`
- **Freshness status:** `SUPERSEDED` — 4–6hr Dataverse refresh claim explicitly removed in `opus-v2.md`
- **Conclusions reused:** none (superseded)

### `research/reviews/opus-v2.md`
- **Title:** Blueprint v2 revision — retraction, Studio quota figures, Split-Runtime catalogue
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS`
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` — quota figures self-flagged by `viable-skills-summary.md` v6 as needing re-verification
- **Conclusions reused:** Split-Runtime trade-off catalogue (refined into design §3b)
- **Conclusions updated/rejected:** supersedes `gpt55-v1.md`'s refresh-window claim

### `research/reviews/opus-v3.md`
- **Title:** Adversarial audit of Blueprint v3 · **Date:** references events 2026-05-01/06-02/06-16
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS`
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` for dated events; pricing claim explicitly `SECONDARY_SOURCE_CLAIM`/unverified marketing
- **Conclusions reused:** ITSG-33 control names (§3b); pricing-claim skepticism

## `microsoft-copilot-studio/`

### `HANDOFF-claude-code.md`
- **Title:** Session handoff for hands-on Copilot Studio build · **Date:** 2026-06-20
- **Evidence type/confidence:** `EMPIRICALLY_OBSERVED` (establishes the hands-on session is genuine)
- **Freshness status:** `NOT_RELEVANT_TO_PHASE_7` as a standalone finding
- **Conclusions reused:** none directly

### `agent-build-walkthrough.md`
- **Title:** Step-by-step hands-on Copilot Studio build log · **Date:** 2026-06-20, BC Government Shared Environment
- **Relevant sections:** Instructions-vs-Description; Message-node non-verbatim behavior; blanket knowledge-connector DLP block; channel/auth restrictions
- **Phase 7 relevance:** high — §3b (candidates), §3c (identity, one pattern)
- **Evidence type/confidence:** `EMPIRICALLY_OBSERVED`, tenant-scoped
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` narrowed by `learnings.md` L23's own Default-vs-Dedicated caveat; general DLP-allowlist mechanism `UPDATED_BY_CURRENT_DOCUMENTATION`-corroborated per current-source item 5
- **Conclusions reused:** Message-node non-verbatim finding; Instructions-vs-Description distinction; DLP-block observation
- **Conclusions updated/rejected:** none within this file; its Default-Environment scoping is narrowed by L23

### `generative-orchestration.md`
- **Title:** Generative orchestration architecture — decision boundaries, lifecycle triggers, Connected Agents
- **Phase 7 relevance:** high — §3 (artifact-pattern angle), §3b (candidates), §3c (identity, one pattern)
- **Evidence type/confidence:** `BUNDLED_RESEARCH_SYNTHESIS` — **corrected from `BUNDLED_PRIMARY_SOURCE`**; this is internally authored research notes about the platform, not captured Microsoft doc content
- **Freshness status:** the lifecycle-trigger names and Connected-Agents I/O contract are now
  `UPDATED_BY_CURRENT_DOCUMENTATION`/effectively `CURRENT_PRIMARY_SOURCE_VERIFIED` per
  current-source items 1–2; the §9 "no git integration" versioning claim is
  `UPDATED_BY_CURRENT_DOCUMENTATION` per current-source item 3 (Git-based CI/CD *is* a supported
  ALM path); the identity claim is `UPDATED_BY_CURRENT_DOCUMENTATION` per current-source item 4
- **Conclusions reused:** §8/§9 findings, reframed as candidates and corrected per current-source verification
- **Conclusions updated/rejected:** three separate corrections applied — see current-source-verification-record.md items 1, 3, 4

### `learnings.md`
- **Title:** Distilled learnings L1–L25 · **Date:** 2026-06-20 · **External sources:** community billing complaint (L25 only)
- **Relevant sections:** L1, L16, L19–L20, L21–L22, **L23**, L24–L25
- **Phase 7 relevance:** highest-confidence empirical source in the corpus; L23 is the basis for the Dedicated-Environment precondition
- **Evidence type/confidence:** `EMPIRICALLY_OBSERVED` for L1–L23; `SECONDARY_SOURCE_CLAIM` for L25
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`, tenant/environment-scoped per L23's own caveat; general DLP mechanism corroborated current per item 5, but the Default-vs-Dedicated question itself remains `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`
- **Conclusions reused:** L23 Dedicated-Environment precondition; L16 DLP-mechanism correction; L19 governance-mismatch finding

## `microsoft-m365-agents/`

> Not a Phase 7 evaluation target (design §6 non-goals) — bundled only as Studio-interop background.

### `create-deploy-agents-sdk.md`
- **Date:** `ms.date: 2025-05-15`, `updated_at: 2025-12-02` — real Microsoft Learn frontmatter
- **Evidence type/confidence:** `BUNDLED_PRIMARY_SOURCE` (genuinely captured Microsoft doc content, correctly labeled)
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` — real dated source, but predates the mid-2026 GA claims elsewhere
- **Conclusions reused:** none directly cited in the memo (background only)

### `create-new-toolkit-project-vs.md`
- **Date:** `ms.date: 2025-11-21`, `updated_at: 2025-11-24`
- **Evidence type/confidence:** `BUNDLED_PRIMARY_SOURCE`
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** none (background only)

### `github-sdk-reference.md`
- **External sources:** GitHub (`Microsoft/Agents*` repos)
- **Evidence type/confidence:** `BUNDLED_PRIMARY_SOURCE` (repo index content, directly captured)
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK`
- **Conclusions reused:** SDK↔Studio interop confirmation (context only, not a build target)

### `m365-agents-sdk.md`
- **Date:** `ms.date: 2025-07-21`, `updated_at: 2025-07-22`
- **Relevant sections:** explicit Government-tenant Agents Toolkit publishing constraint
- **Evidence type/confidence:** `BUNDLED_PRIMARY_SOURCE`
- **Freshness status:** `REQUIRES_FRESHNESS_CHECK` — lowest freshness risk of the corpus, real dated Learn source
- **Conclusions reused:** government-tenant constraint noted as background flag only, not applied to this round's disposition (SDK is not a Phase 7 target)

## Unresolved questions carried forward (not resolved by this ledger)

- Governance-engine mismatch between M365 Copilot Chat (Purview) and Copilot Studio (Power
  Platform DLP) — `learnings.md` L19–L20, explicitly unresolved by the original researcher.
- Whether the Default-vs-Custom/Dedicated-Environment distinction (`learnings.md` L23) actually
  changes the observed DLP-blocking outcome — corroborated as a real mechanism by current-source
  item 5, but the specific environment-type distinction is not resolved without direct testing.
- Whether this project's own tenant shares the compliance/regional/hosting characteristics of the
  BC Government Shared Environment — `TENANT_UNKNOWN`.
- Whether the Cowork product surface (as distinct from Copilot Studio) has adopted Entra Agent ID
  — not found in this pass; Cowork's identity claim remains `BUNDLED_RESEARCH_SYNTHESIS`-sourced.

## What Phase 7 added rather than repeated

- The three-way baseline framing (workbench + native SharePoint agent + candidate platform).
- The instructional-format-vs-executable-runtime classification applied to this repo's own workflow steps.
- The decomposed identity matrix (deployment/retrieval/user-interaction/approval/publication as separate fields).
- The corrected deterministic-vs-instruction-level distinction, from this repo's own Phase 6 code
  and passing test (`test_more_than_two_related_topics_is_rejected`), not present in the AI-Research corpus at all.
- This focused current-source verification pass (`current-source-verification-record.md`), which
  the prior AI-Research corpus explicitly had not performed for several of its own central claims.
