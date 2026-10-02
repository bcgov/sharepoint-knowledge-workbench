# ASPX analysis details (stages 1-2)

## Contents

- [Stage 1: inventory](#stage-1-inventory)
- [Stage 2: classification](#stage-2-classification)
- [Unknown is a real answer](#unknown-is-a-real-answer)
- [Usage](#usage)
- [Provenance](#provenance)

## Stage 1: inventory

`aspx_inventory.py` parses three input sources into one neutral inventory of web part zones: rendered classic HTML (content-editor zones, `--source-html`), a views export
(list-view zones, `--views-json`), and an override file (connected-consumer zones that cannot be detected from markup alone, `--override`). It never fabricates a zone when
evidence is absent. Malformed markup does not crash the stage (see the `malformed-page` test fixture).

## Stage 2: classification

`component_classification.py` assigns each component a Role, Type and Variant (`Primary`, `Secondary`, `Child`, `Banner`, `Unknown`).

## Unknown is a real answer

`Unknown` is a first-class variant. A component the classifier cannot place is reported as `Unknown` instead of being forced into a plausible-looking category: a wrong
classification is more expensive downstream than an honest gap.

## Usage

```bash
python3 scripts/aspx_inventory.py \
  --source-html classic-page.raw.html \
  --views-json classic-page.views.json \
  --override classic-page.override.json \
  --output inventory.json

python3 scripts/component_classification.py --input inventory.json --output classified.json
```

`--source-page` and `--views-json` and `--override` are optional; `--source-html` and `--output` are required.

## Provenance

Adapted from `sp-analysing-aspx-pages` and `sp-converting-aspx-pages` in the originating SharePoint migration repository (source repository only:
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`).
