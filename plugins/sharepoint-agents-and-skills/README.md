# sharepoint-agents-and-skills

**Status: Phase 6 Task 0, `AUTHORIZED_AND_IN_PROGRESS`.** Not yet complete — see
`docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md` Task 0 for the
full task breakdown and current progress, and
`docs/architecture/complete-plugin-skill-catalog-after-phase-9.md` for this plugin's complete
skill inventory.

## Purpose

Owns SharePoint Copilot agent and native-skill lifecycle capability: `AgentAssets` inventory and
validation, agent lifecycle (create/update/knowledge-configuration/backup/restore/templates), and
native-skill lifecycle (create/deploy/verify/rollback/backup/restore).

## Non-responsibilities

Content rendering (owned by `structured-content-rendering`), SharePoint content publication
(owned by `sharepoint-content-publication`), workbench connection/config setup (owned by
`workbench-setup`).

## Ownership decision

Per `docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-plugin-design.md`'s "Ownership
decision" section (resolved 2026-08-03):
`PLUGIN_MAY_CONTAIN_REUSABLE_PLATFORM_CAPABILITIES_AND_CONFIGURED_SOLUTION_SKILLS`. This plugin
holds both generic platform tooling and clearly labeled `CONFIGURED_SOLUTION_SKILL` /
`CEIS_SPECIFIC` skills side by side — `review-manual-topics` is the current example of the
latter.

## Skills

- `review-manual-topics` — **implemented (native SharePoint runtime)**, migrated from Phase 4
  (`git mv`), real deployed skill, hash-verified. **Not yet built (repository/Claude runtime)** —
  Task 0.3.

The remaining 14 skill names (Task 0.4–0.7) are scoped in the Phase 6 plan; scripts for several are
already moved/generalized under `scripts/` but not yet packaged as their own `SKILL.md`-wrapped
skills. See the plan for exact per-skill status.

## Agents

`agents/` holds Claude Code routing agents — orchestration artifacts that decide *which*
capability to run for a request, and that report honestly when no capability exists. Four were
extracted in Phase 9 Wave 2 (see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`, Records 3–6); two more
were added generalizing findings from the Phase 9 exhaustive source audit
(`temp/phase9-source-audit/file-tracking.json`):

- `sharepoint-link-agent` — enforces extract → remediate → validate ordering for link work.
- `sharepoint-modernization-agent` — separates "render modern page artifacts" from "convert an
  existing classic page" (only the former is supported here).
- `sharepoint-schema-agent` — read-only schema conformance before any mapping question.
- `sharepoint-validation-agent` — routes post-stage validation by artifact under test.
- `sharepoint-deployment-planning-agent` — routes matrix-completeness questions before any
  deployment-order question is asked.
- `sharepoint-deployment-sequencing-agent` — routes deployment-order questions to the
  deterministic dependency-graph/topological-sort computation, never a hand-maintained sequence.

Every agent carries a mandatory `## Not available in this workbench` section. The contract
(frontmatter schema, zero project literals, zero dangling capability references, manifest
registration) is enforced by `tests/unit/test_agent_definitions.py`.

## Dependencies

`config.psd1` (git-ignored, connection/authentication context only — `SiteUrl`, `ClientId`,
`TenantId`) is required by every PowerShell script under `scripts/`. Copy
`config.psd1.example`-equivalent conventions from the Phase 4 tooling this plugin's scripts were
migrated from until this plugin's own example file is added.
