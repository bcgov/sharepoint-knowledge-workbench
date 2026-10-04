# sharepoint-document-conversion

SharePoint document conversion: extracts a source .docx into a normalized source document, analyzes
topic structure and chunking strategy, assembles a validated canonical content package, renders it
to multipage Markdown or SharePoint modern pages through local rendering templates, validates the
rendered output, and provides single-topic editorial review of rendered Markdown or published pages.
Every workflow is local or read-only; nothing in this package writes to a tenant.

## Skills by functional group

### Assemble a content package

- `content-assemble-structured-content` -- Assembles a validated structured content package from a human-confirmed conversion plan and its source document, with stable identities, source lineage, hashes, manifests and publication mappings. Use after the...

### Editorial topic review

- `content-review-manual-topic` -- Reviews exactly one explicitly selected manual topic page (rendered Markdown in the repository runtime, or the published page in the native SharePoint runtime) for content completeness, section structure,...

### Extract source content

- `content-extract-docx` -- Runs pandoc against a source .docx and produces a normalized-source-document contract (markdown text, media files, heading structure, defect signals, statistics) for downstream structure analysis. Use as the first...

### Organize topics and pages

- `content-analyze-document-structure` -- Analyzes normalized extracted document content to identify heading hierarchy, topic boundaries, cross-references, structural deficiencies, and a proposed conversion plan for human review. Use after source-document...

### Render and check output

- `content-compare-rendered-output` -- Compares a freshly produced rendered-output tree (Markdown or ASPX) against a recorded golden-master baseline for byte-identical fidelity, checking file-set completeness and byte-for-byte content while excluding...
- `content-create-markdown-rendering-template` -- Instantiates a new local Markdown rendering (page-structure) template file on disk from the plugin's canonical generic or standard-manual starter, with heading, body and media placeholders. Use when you need a new...
- `content-create-sharepoint-rendering-template` -- Instantiates a new local SharePoint modern-page (ASPX) rendering (page-structure) template file on disk from the plugin's canonical generic or standard-manual starter, backed by the confirmed Add-PnPPage and...
- `content-render-markdown-pages` -- Renders an accepted structured content package into a multipage Markdown publication output, one page per chunk with a path-aware index, rewritten media and page-relative links, validated and atomically promoted. Use...
- `content-render-sharepoint-pages` -- Renders an accepted structured content package into SharePoint modern-page-ready artifacts (an HTML fragment per chunk plus a page-manifest.json) for the confirmed Add-PnPPage and Add-PnPPageTextPart route. Use when...
- `content-validate-rendered-output` -- Validates a staged rendered-output directory (Markdown or ASPX) against the canonical package it was rendered from, and promotes it atomically on PASS. Use after rendering and before accepting or publishing a render....
- `content-validate-rendering-template` -- Validates a RenderingTemplate (from the Markdown or ASPX template-creation skills) for schema, placeholder, required-section and format-profile correctness. Use before relying on a template. Checks the template...

## Previous identities

Skill and plugin names changed in the seven-domain migration (issue #6). Old names are not retained as aliases.

| Previous skill | Current skill | Previous plugin |
|---|---|---|
| `content-analyze-document-structure` | `content-analyze-document-structure` | `content-structure-analysis` |
| `content-assemble-structured-content` | `content-assemble-structured-content` | `content-assembly` |
| `content-compare-rendered-output` | `content-compare-rendered-output` | `content-rendering` |
| `content-create-markdown-rendering-template` | `content-create-markdown-rendering-template` | `content-rendering` |
| `content-create-aspx-rendering-template` | `content-create-sharepoint-rendering-template` | `content-rendering` |
| `content-extract-docx` | `content-extract-docx` | `content-extraction` |
| `content-render-multipage-markdown` | `content-render-markdown-pages` | `content-rendering` |
| `content-render-sharepoint-aspx` | `content-render-sharepoint-pages` | `content-rendering` |
| `sharepoint-review-manual-topics` | `content-review-manual-topic` | `sharepoint-agents-and-skills` |
| `content-validate-rendered-output` | `content-validate-rendered-output` | `content-rendering` |
| `content-validate-rendering-template` | `content-validate-rendering-template` | `content-rendering` |

## Source namespaces

This package consolidates independently developed implementations. Each keeps its own flat module namespace under a
subfolder named for its original function so that same-named modules (for example `canonical_package`, `hashing`)
never collide. Skill folders live flat under `skills/`; skills reach their scripts and references through their own
file-level symlink spokes.

| Source plugin | Namespace | Scripts | Tests | References |
|---|---|---|---|---|
| `content-assembly` | `assembly` | yes | yes | yes |
| `sharepoint-agents-and-skills (editorial review cluster)` | `editorial-review` | yes | yes |  |
| `content-extraction` | `extraction` | yes | yes | yes |
| `content-rendering` | `rendering` | yes | yes | yes |
| `content-structure-analysis` | `structure-analysis` | yes | yes | yes |

Original package READMEs and manifests are preserved as provenance under `references/source-packages/<source-plugin>/`.

## Running the tests

Each namespace is tested in its own process because bare-name imports (for example `import canonical_package`) are
namespace-local:

```bash
python3 plugins/sharepoint-document-conversion/tests/run_namespaces.py
```

To run one namespace: `cd plugins/sharepoint-document-conversion && python3 -m pytest tests/<namespace>`.

## Installing

See the repository [INSTALL.md](../../INSTALL.md). Example:

```text
/plugin install sharepoint-document-conversion@sharepoint-knowledge-workbench
```
