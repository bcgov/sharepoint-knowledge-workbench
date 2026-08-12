# sharepoint-link-remediation

Generic SharePoint link extraction, rewrite-rule remediation, and
post-migration link-integrity validation.

```
plugins/sharepoint-link-remediation/
├── scripts/
│   ├── link_outcomes.py                          # shared Outcome vocabulary
│   ├── link_extraction.py                        # extract_links_from_text/paths, classify
│   ├── link_rules.py                              # load_ruleset, RewriteRule, RewriteRuleset
│   ├── link_remediation.py                        # plan_remediation, apply_remediation, rollback_remediation
│   ├── link_integrity.py                          # validate_link_integrity, make_local_path_resolver
│   ├── document_link_remediation.py                # plan/apply_document_link_remediation (docx/xlsx/pptx OOXML rewrite)
│   ├── field_image_remediation.py                  # classify/plan/apply_field_image_remediation
│   ├── spo-remediate-page-links.ps1                # real PnP executor for remediate-links
│   ├── spo-remediate-document-content-links.ps1    # real PnP executor for remediate-document-content-links
│   └── spo-remediate-field-image-references.ps1    # real PnP executor for remediate-field-image-references
├── skills/
│   ├── extract-links/                        # read-only
│   ├── remediate-links/                       # write-capable, real executor
│   ├── remediate-document-content-links/      # write-capable, real executor
│   ├── remediate-field-image-references/      # write-capable, real executor
│   └── validate-link-integrity/               # read-only/local-only
└── tests/
```

## Write safety

`remediate-links`, `remediate-document-content-links`, and
`remediate-field-image-references` are the write-capable skills in this
plugin (`extract-links` and `validate-link-integrity` are read-only/
local-only by design). Every write-capable module uses the same three
independent gates: dry-run by default, an explicitly injected
writer/executor required, and a plan-derived confirmation token that goes
stale if the underlying documents change. No default tenant transport ships
with the Python modules themselves.

Each of the three write-capable skills now has a real `.ps1` executor
(`scripts/spo-remediate-page-links.ps1`,
`scripts/spo-remediate-document-content-links.ps1`,
`scripts/spo-remediate-field-image-references.ps1`) that reads the
corresponding plan's `to_dict()`-shaped JSON and performs the actual PnP
writes (`Get-PnPListItem`/`Set-PnPListItem` for page and field-image
remediation; `Set-PnPFileCheckedOut`/`Add-PnPFile`/`Set-PnPFileCheckedIn`
for document-content remediation). Each defaults to a dry-run summary and
requires both `-Execute` and a skill-specific `-ConfirmToken` for a real
write — see each skill's `SKILL.md` "Real executor" section for the exact
command and, for document-content remediation, a documented design seam
(the OOXML rewrite itself stays Python-only; the plan JSON must be
pre-augmented with a path to the already-rewritten file).

## Rulesets are data, not code

`load_ruleset` reads a declarative JSON ruleset of `match`/`replacement`
entries. No host, tenant, or project URL is built in — every rewrite target
is supplied by the caller.

## Coverage

All 5 skills are implemented: `extract-links`, `remediate-links`,
`validate-link-integrity` (source-extracted), plus
`remediate-document-content-links` and `remediate-field-image-references`
(generalized from source-repository designs/diagnostics not present as
working source implementations — see each skill's `SKILL.md` "Provenance"
section). See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/
remaining-capability-roadmap.md` and `provenance.md` for the original
extraction record.

## Install

```bash
pip install -e plugins/sharepoint-link-remediation
python3 -m pytest plugins/sharepoint-link-remediation/tests/ -q
```
