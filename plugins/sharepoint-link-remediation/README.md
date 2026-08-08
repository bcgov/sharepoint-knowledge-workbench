# sharepoint-link-remediation

Generic SharePoint link extraction, rewrite-rule remediation, and
post-migration link-integrity validation.

```
plugins/sharepoint-link-remediation/
├── scripts/
│   ├── link_outcomes.py       # shared Outcome vocabulary
│   ├── link_extraction.py     # extract_links_from_text/paths, classify
│   ├── link_rules.py          # load_ruleset, RewriteRule, RewriteRuleset
│   ├── link_remediation.py    # plan_remediation, apply_remediation, rollback_remediation
│   └── link_integrity.py      # validate_link_integrity, make_local_path_resolver
├── skills/
│   ├── extract-links/
│   ├── remediate-links/
│   └── validate-link-integrity/
└── tests/
```

## Write safety

`remediate-links` is the only write-capable skill in this plugin. Three
independent gates: dry-run by default, an explicitly injected writer
required, and a plan-derived confirmation token that goes stale if the
underlying documents change. No default tenant transport ships with this
plugin.

## Rulesets are data, not code

`load_ruleset` reads a declarative JSON ruleset of `match`/`replacement`
entries. No host, tenant, or project URL is built in — every rewrite target
is supplied by the caller.

## Coverage

All 3 implemented source capabilities extracted
(`sp-extracting-links`, `sp-remediating-links`, `sp-validating-link-integrity`).
`sp-remediating-document-content-links` was not extracted — no implementation
exists in the source. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/
remaining-capability-roadmap.md` and `provenance.md`.

## Install

```bash
pip install -e plugins/sharepoint-link-remediation
python3 -m pytest plugins/sharepoint-link-remediation/tests/ -q
```
