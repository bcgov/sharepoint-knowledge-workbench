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

## Agents — relocated to their own domain plugins, 2026-08-08

This plugin previously centralized 9 Claude Code routing/analysis agents for every other
plugin's domain, on top of its own actual charter (agent/native-skill lifecycle tooling). Two
independent external architecture reviews (`temp/bundles/plugins-only/reviews/{gpt,opus}.md`)
converged on the same finding: centralizing domain-routing knowledge here, physically far from
the domain skills it routes to, is exactly why a stale claim in `sharepoint-schema-agent`
(falsely denying `audit-schema` existed) went unnoticed by anyone maintaining the schema plugin.

All 9 agents moved to their own domain plugin's `agents/` folder:

| Agent | New home |
|---|---|
| `sharepoint-link-agent`, `sharepoint-link-remediation-analysis-agent` | `sharepoint-link-remediation` |
| `sharepoint-schema-agent` | `sharepoint-schema` |
| `sharepoint-modernization-agent`, `sharepoint-webpart-modernization-analysis-agent` | `sharepoint-page-modernization` |
| `sharepoint-deployment-planning-agent`, `sharepoint-deployment-sequencing-agent` | `sharepoint-migration-planning` |
| `sharepoint-content-migration-sequencing-agent` | `sharepoint-content-migration` |
| `sharepoint-validation-agent` | `sharepoint-content-publication` |

This plugin's `agents/` directory is now empty and its `plugin.yaml` carries no `agents:` key —
it owns agent/native-skill *lifecycle* tooling only (see Purpose above), not domain routing.

**The agent-contract test remains canonical here** (`tests/unit/test_agent_definitions.py`:
frontmatter schema, zero project literals, zero dangling capability references, `plugin.yaml`
agents-list drift check, mandatory `## Not available in this workbench` section) and is
symlinked into each of the 6 plugins above via `symlinks.json` — one authored file, not
reimplemented per plugin, matching this workbench's existing shared-module pattern
(`wave_planning.py`, `provisioning_outcomes.py`).

## Dependencies

`config.psd1` (git-ignored, connection/authentication context only — `SiteUrl`, `ClientId`,
`TenantId`) is required by every PowerShell script under `scripts/`. Copy
`config.psd1.example`-equivalent conventions from the Phase 4 tooling this plugin's scripts were
migrated from until this plugin's own example file is added.
