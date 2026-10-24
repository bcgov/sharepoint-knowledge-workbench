# Web part code analysis: categories, collection and Stage 2

## Contents

- [Categories](#categories)
- [Classification knowledge is caller-supplied](#classification-knowledge-is-caller-supplied)
- [Collecting a fresh export](#collecting-a-fresh-export)
- [Stage 2: AI-reasoning pass](#stage-2-ai-reasoning-pass)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Categories

| Category | Meaning |
|---|---|
| `InlineLogic` | Contains inline script implementing real behaviour |
| `ExternalHelpersOnly` | References external helper scripts, no inline logic |
| `TextOnly` | Static content, no code |
| `Empty` | No meaningful content |
| `ScriptEditorMissing` | Content could not be retrieved: not a classification, a gap |

`ScriptEditorMissing` is deliberately distinct. An unretrievable web part is an unknown, not an
empty one, and a run containing any of them reports `PARTIAL` with the count, never `OBSERVED`.

Classic sites accumulate hundreds of web-part instances that are mostly copies of a handful of
behaviours. The skill collapses an export into distinct functional groups so a modernization review
covers each behaviour once. It produces three artifacts: a groups JSON, a Markdown analysis report
and a per-instance review CSV.

## Classification knowledge is caller-supplied

`KnowledgeBase` and `InlineLogicRule` let you supply the helper-script table and behavioural
heuristics. The source implementation hardcoded roughly thirty helper-script names and one
organisation's business-rule heuristics; all of that is removed. `DEFAULT_KNOWLEDGE_BASE` is
deliberately generic.

## Collecting a fresh export

`collect-sharepoint-webpart-content.ps1` connects to a live on-prem SharePoint 2016 site (REST plus
NTLM/Kerberos, no PnP/CSOM; see the repository's `sharepoint-ps1-authentication-convention.md`
rule) in two modes:

- `-Mode Scan` (default) enumerates pages and queries `GetLimitedWebPartManager` for every web part
  on every page, writing `webpart-scan.csv` and `.json`.
- `-Mode ExtractContent` reads that CSV and pulls each web part's full HTML/JS payload via the
  legacy `_vti_bin/exportwp.aspx` handler (the only mechanism that exposes it on SP2016; the modern
  REST `ExportWebPart` action 404s unconditionally), writing `webpart-content.json` in the shape
  `[{PageUrl, WebPartId, WebPartTitle, Content}]`.

Read-only: REST GETs only, zero tenant writes.

```bash
pwsh -File scripts/collect-sharepoint-webpart-content.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -Mode Scan -UseDefaultCredentials
pwsh -File scripts/collect-sharepoint-webpart-content.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -Mode ExtractContent -UseDefaultCredentials
```

## Stage 2: AI-reasoning pass

Stage 1 grouping is deterministic, but each group's JSON also carries `businessIntent`,
`enforcementLevel` and `spfxAssessment` fields. They are generic and structurally honest for
`Empty`/`TextOnly`, caller-supplied via `InlineLogicRule.business_intent` and `spfx_assessment` for
recognised inline logic, and an explicit "requires manual review" for everything unrecognised.
These are a deterministic starting point, not a substitute for judgment. The full disposition
(business behaviour, MVP decision, SPFx candidacy with justification, pattern-collapse across groups
sharing one mechanism, evidence gaps) is Stage 2, agent-assisted by design: route to the
`sharepoint-webpart-modernization-analysis-agent` (in `sharepoint-site-migration`) once the
grouped output exists. Its per-group analysis structure and category-level defaults are richer than
anything this module computes.

## Scripts

- `scripts/collect-sharepoint-webpart-content.ps1`: real, read-only on-prem REST collector (Scan and
  ExtractContent modes).
- `scripts/webpart_code_analysis.py`: `run`, `analyse`, `classify`, `recommend`, `generate_report`,
  `generate_instance_csv`, `KnowledgeBase`, `InlineLogicRule`.
- `scripts/discovery_inputs.py`: shared status vocabulary and input loading.
- Also bundled: `generate-deep-webpart-analysis.py`, `sample-webpart-content.ps1`.

## Provenance

Adapted from `sp-discovering-web-parts` in the originating SharePoint migration repository. Six of
that skill's 19 symlinks pointed at project analysis data outside the plugin boundary; that data was
not extracted. The Stage-2 reasoning framework those documents applied (per-group disposition
fields, category-level defaults, pattern-collapse discipline) was later generalized into
`sharepoint-webpart-modernization-analysis-agent` after a Phase 9 audit follow-up. Source repository
only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
