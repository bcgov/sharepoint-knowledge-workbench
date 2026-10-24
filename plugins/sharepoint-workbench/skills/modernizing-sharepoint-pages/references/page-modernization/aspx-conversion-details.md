# ASPX conversion details (stages 3-4)

## Contents

- [Layout rules are data, evaluated safely](#layout-rules-are-data-evaluated-safely)
- [Gaps are named, never hidden](#gaps-are-named-never-hidden)
- [Usage](#usage)
- [Packaged assets](#packaged-assets)
- [Deployment is separate](#deployment-is-separate)
- [Provenance](#provenance)

## Layout rules are data, evaluated safely

`layout_selection.py` reads declarative rules from the packaged `assets/layout-rules.json` (or a caller-supplied `--rules` override). Rule conditions are evaluated by a
restricted AST evaluator that permits only name lookups, constants, comparisons, boolean operators and arithmetic. Any call expression is rejected: a rule containing
`__import__(...)`, `open(...)` or any other call raises `UnsafeConditionError`, and the offending rule is recorded in `skippedRules` instead of executed. Rule files are data,
so they are treated as untrusted input (verified by test).

## Gaps are named, never hidden

Not every classic component has a modern equivalent. Connected-consumer web parts cannot be reproduced. Rather than dropping them or emitting a plausible substitute,
`component_mapping.py` renders an explicit gap notice from `assets/gap-notice.template.html` that names the specific lists that were not migrated. Unsupported web-part
types are surfaced explicitly, never silently discarded. A connected consumer is recorded `NOT_MIGRATED` with its relationship preserved; a Primary list view maps to a
`ListWebPart` section plus a view-provisioning entry (CAML lives in the view, not the page).

## Usage

```bash
python3 scripts/page-modernization/layout_selection.py --input classified.json --output layout.json

python3 scripts/page-modernization/component_mapping.py \
  --components classified.json --layout layout.json \
  --output-mapping mapping.json --output-views views.json
```

`--rules` (layout selection), `--mapping-rules` and `--view-name-prefix` (component mapping) are optional overrides.

## Packaged assets

`assets/layout-rules.json`, `assets/webpart-mapping.json`, `assets/manifest-schema.json`, `assets/preview-template.html`, `assets/gap-notice.template.html`. In this plugin the
canonical copies live in `scripts/page-modernization/assets/` (packaged data) and each skill links the ones it uses.

## Deployment is separate

The skill plans; it does not create, publish or modify anything in SharePoint. Hand the source page name, library and target metadata to the
`sharepoint-convert-page-to-modern` skill in `sharepoint-site-migration`, supplying its parameters from the manifest's contents yourself.

## Provenance

Adapted from `sp-converting-aspx-pages` in the originating SharePoint migration repository, the richest single artifact in the source audit (32 files). The source's
organisation-specific layout thresholds and web-part mapping entries were replaced by the packaged, caller-overridable rule files. Source repository only:
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
