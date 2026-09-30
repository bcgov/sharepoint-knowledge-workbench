# Acceptance Criteria: sp-discovering-web-parts

## Structural Standards

- [x] `SKILL.md` is present with valid frontmatter (`name`, `plugin`, `description`, `allowed-tools`)
- [x] Description length is under 1024 characters
- [x] `evals/evals.json` exists with at least 2 positive and 2 negative cases using `should_trigger: true/false`
- [x] Follows plugin architecture rules (relative paths, zero duplication)

## Functional Standards

- [x] **Phase 0 (Discovery Interview)**: Prompts user for target site URL, output directory, auth method, JS assets path, and scope before running scripts.
- [x] **Phase 1 (ASPX Discovery)**: Downloads `.aspx` page sources for offline inspection via `extract-all-aspx-pages.ps1`.
- [x] **Phase 2 (Live Scanning)**: Builds inventory of CEWP/SEWP instances via `scan-webparts.ps1`.
- [x] **Phase 3 (Content Extraction)**: Extracts full web part `<Content>` payloads via legacy `exportwp.aspx` endpoint using `extract-webpart-content.ps1`.
- [x] **Phase 4 (Code Analysis & Grouping)**: Runs `analyze-webpart-code.py` to cluster identical/similar web parts into functional groups and output modernization recommendations.
