# Page modernization pipeline and outcomes

## Contents

- [The four stages](#the-four-stages)
- [Outputs and the manifest](#outputs-and-the-manifest)
- [Honest outcomes](#honest-outcomes)
- [Boundaries](#boundaries)

## The four stages

```
analyze-aspx-pages  ->  convert-aspx-pages
  1. inventory          3. layout selection
  2. classification     4. component mapping
```

Each stage is a script CLI. All of them operate on exported files you provide and never contact a tenant.

| Stage | Script | Key flags |
|---|---|---|
| 1. inventory | `aspx_inventory.py` | `--source-html`, `--source-page`, `--views-json`, `--override`, `--output` |
| 2. classification | `component_classification.py` | `--input`, `--output` |
| 3. layout selection | `layout_selection.py` | `--input`, `--rules`, `--output` |
| 4. component mapping | `component_mapping.py` | `--components`, `--layout`, `--mapping-rules`, `--view-name-prefix`, `--output-mapping`, `--output-views` |

`conversion_report.py` (`--manifest`, `--output`) and `preview_composition.py` (`--page-folder`, `--chrome-folder`, `--output`) are separate skills' CLIs.

## Outputs and the manifest

Stage 4 writes a mapping file and a views file (`--output-mapping`, `--output-views`). The conversion **manifest** that `conversion_report.py` renders is a
`PageConversionManifest` conforming to the packaged `manifest-schema.json` (required fields: `sourcePage`, `convertedAt`, `manifestHash`, `mapping`, `environmentProfile`,
`source`, `target`, `webParts`, `layout`, `gaps`, `confidence`, `outcome`). No script in this plugin assembles that full manifest from the stage outputs; the
caller or the modernization agent does. Do not claim a script produced it.

## Honest outcomes

All stages use the shared vocabulary in `outcomes.py`: `Observed`, `Empty`, `Partial`, `Unavailable`, `Failed` (and `Forbidden`). `Unavailable`, `Failed` and `Forbidden` are
failures; `Empty`, `Observed` and `Partial` are not. Every status other than `Observed` carries a detail message. A missing input is `Unavailable`, never a clean pass; no
detectable components is `Empty`, never success; a partly readable input is `Partial` with the gaps named.

## Boundaries

- This plugin *analyses existing* legacy pages it did not create and plans their modern equivalents. The `content-rendering` plugin *renders new* pages from
  structured content the workbench owns. Different inputs and responsibility; do not conflate them.
- The plugin produces plans, never tenant writes. Deploying a converted page is a separate, explicitly authorized step: the `sharepoint-convert-page-to-modern` skill in
  `sharepoint-page-modernization-execution` (a real `ConvertTo-PnPPage` executor, dry-run by default, gated behind `-Execute -ConfirmToken`). That skill does not read
  this plugin's manifest directly; you supply its `-PageName`, `-SourceLibrary` and field-mapping parameters from the manifest's contents.
