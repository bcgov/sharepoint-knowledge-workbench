# Acceptance Criteria — sharepoint-setup-spfx-hosted-workbench

## Discovery Contract

- **Skill slug**: `sharepoint-setup-spfx-hosted-workbench`
- **Target plugin**: `sharepoint-spfx-development`
- **Purpose**: Set up and validate a local SPFx web part development workflow that can be tested in SharePoint Online hosted `workbench.aspx`.
- **Trigger phrases**:
  - `set up spfx workbench`
  - `configure sharepoint online workbench.aspx`
  - `prepare local spfx webpart testing`
  - `spfx hosted workbench setup`
  - `validate spfx dev environment`
- **Allowed tools**: `Bash, Read, Write`

## Structural Requirements

- Skill folder exists at:
  - `plugins/sharepoint-spfx-development/skills/sharepoint-setup-spfx-hosted-workbench/`
- Required files exist:
  - `SKILL.md`
  - `evals/evals.json`
  - `references/acceptance-criteria.md`

## Behavioral Requirements

- Skill workflow includes:
  - SPFx toolchain validation
  - Hosted SharePoint Online `workbench.aspx` URL composition
  - Debug URL composition with `loadSPFX=true` and `debugManifestsFile`
  - Dev certificate trust step for localhost
  - Clear handoff to run `gulp serve --nobrowser`
- Skill must direct SharePoint connectivity validation via:
  - `plugins/sharepoint-workbench-setup/skills/workbench-validate-sharepoint-connection/scripts/test-spo-connection.ps1`

## Output Quality Requirements

- `evals/evals.json` uses `should_trigger` booleans (no legacy `expected_behavior` field).
- Positive evals map to hosted workbench setup intent.
- Negative evals avoid overlapping existing SPFx packaging/deployment skills.
