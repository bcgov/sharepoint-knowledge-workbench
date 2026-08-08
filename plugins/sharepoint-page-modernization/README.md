# sharepoint-page-modernization

Analyses and converts legacy classic SharePoint pages into modern-page
conversion manifests, and composes offline previews of the result.

```
plugins/sharepoint-page-modernization/
├── scripts/
│   ├── outcomes.py                    # shared status vocabulary
│   ├── aspx_inventory.py              # stage 1: parse classic page content
│   ├── component_classification.py    # stage 2: Role/Type/Variant classification
│   ├── layout_selection.py            # stage 3: data-driven layout rules, restricted AST evaluator
│   ├── component_mapping.py           # stage 4: map to modern sections, gap notices
│   ├── preview_composition.py         # offline chrome+content preview composer
│   └── assets/
│       ├── layout-rules.json
│       ├── webpart-mapping.json
│       ├── webpart-migration-rules.json
│       ├── manifest-schema.json
│       ├── preview-template.html
│       └── gap-notice.template.html
├── skills/
│   ├── analyze-aspx-pages/
│   ├── convert-aspx-pages/
│   └── compose-page-preview/
└── tests/
```

## Pipeline

```
analyze-aspx-pages           convert-aspx-pages
  1. inventory        ->       3. layout selection    -> compose-page-preview
  2. classification            4. component mapping
```

## No tenant writes

The pipeline produces a conversion *manifest* conforming to
`assets/manifest-schema.json`. It does not create, publish, or modify
anything in SharePoint.

## Security hardening beyond the source

Layout-rule conditions are evaluated by a restricted AST evaluator
(`safe_eval_condition`) permitting only names, constants, comparisons,
boolean operators, and arithmetic. Any call expression — `__import__(...)`,
`open(...)`, etc. — raises `UnsafeConditionError` rather than executing.
Rule files are data and are therefore treated as untrusted input.

## Gaps are named, never hidden

Components with no modern equivalent (e.g. connected-consumer web parts) are
not dropped silently — a gap notice names the specific lists that were not
migrated.

## Boundary vs `structured-content-rendering`

That plugin renders **new** pages from structured content this workbench
owns. This plugin analyses and converts **existing** legacy pages it did not
create. Different responsibilities — see
`docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md`
§4a.

## Coverage

`sp-analysing-aspx-pages`, `sp-converting-aspx-pages` extracted, plus the
zero-tenant-I/O, zero-ShareGate `combine-preview.ps1` component of
`sp-running-sharegate-jobs`. `sp-converting-wiki-pages` was evaluated and
**rejected** — it is a live-tenant collector (`New-ClientContextSafe`,
`$SourceSiteUrl`), out of scope for a zero-tenant-I/O plugin. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/
remaining-capability-roadmap.md` and `provenance.md`.

## Install

```bash
pip install -e plugins/sharepoint-page-modernization
python3 -m pytest plugins/sharepoint-page-modernization/tests/ -q
```
