# Use Case: Link & Embedded-Reference Remediation

Generic SharePoint link extraction, rewrite-rule-driven remediation, and post-migration
link-integrity validation — including embedded field image references, not just page/document
links.

## When to use this

Content has moved (site migration, library restructuring, modernization) and links/embedded
references need to be found and rewritten to point at the new location, then verified as actually
resolving.

## Workflow at a glance

- `extract-links` — finds and classifies every link in a content set.
- `remediate-links` / `remediate-document-content-links` / `remediate-field-image-references` —
  apply caller-supplied rewrite rules. The only write-capable skills here, gated by dry-run
  default + injected writer + a plan-derived confirmation token that goes stale if the plan
  changes underneath it.
- `validate-link-integrity` — confirms links resolve after remediation. Note: absolute
  `http(s)://` links are always classified `External` and counted healthy regardless of an
  injected resolver — this plugin validates relative/internal links, not external reachability.

## Full detail

[`plugins/sharepoint-link-remediation/README.md`](../../plugins/sharepoint-link-remediation/README.md)
