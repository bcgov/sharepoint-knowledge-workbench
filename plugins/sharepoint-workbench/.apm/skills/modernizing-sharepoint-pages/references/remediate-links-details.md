# Page link remediation details

## Contents

- [Rulesets are data](#rulesets-are-data)
- [Apply and rollback](#apply-and-rollback)
- [Real executor](#real-executor)
- [Provenance](#provenance)

## Rulesets are data

`load_ruleset(path)` reads a declarative JSON ruleset of `match` / `replacement` / `description` entries. No host, tenant or project URL is
built in: every rewrite target is supplied by you. Malformed rulesets raise `RulesetError` rather than silently matching nothing. Typical
rules: classic `/Pages/` to `/SitePages/`, or an old host to a new one.

## Apply and rollback

```python
from link_rules import load_ruleset
from link_remediation import plan_remediation, apply_remediation, rollback_remediation
plan = plan_remediation(documents, load_ruleset("rules.json"))
print(plan.outcome, plan.to_dict()["would_change"])
```

Apply only after reviewing the plan, with a real writer and `confirm=plan.confirmation_token`. `rollback_remediation` restores prior content
under the same gates. A partly-failed run is never reported as success.

## Real executor

`scripts/link-remediation/spo-remediate-page-links.ps1` resolves each changed document's `source` (a server-relative path) to a list item in `-TargetLibrary` and
overwrites `-TargetField` (default `CanvasContent1`, the modern-page body field) with `Set-PnPListItem`.

```bash
pwsh -File scripts/link-remediation/spo-remediate-page-links.ps1 -PlanPath plan.json -TargetLibrary "Site Pages" -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken REMEDIATE-SPO-LINKS
```

The plan JSON needs each changed document's `remediated_content`; see `link-pipeline-and-write-safety.md`.

## Provenance

Adapted from `sp-remediating-links` in the originating SharePoint migration repository (source repository only:
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`). The source's hardcoded tenant URLs were replaced by the
parameterized ruleset model; no project-specific literal ships as a live default.
