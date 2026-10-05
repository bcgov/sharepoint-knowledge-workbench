# Evolution Log — sharepoint-site-build-and-publish

Append-only record of every self-evolution event. Written by the `self-evolution` skill.
Do not edit manually except to correct a factual error.

| Date | Tier | Friction / Failure | Patch | Edit Type | Outcome |
|------|------|-------------------|-------|-----------|---------|
| 2026-10-05 | Tier 0 | Unquoted colon in SKILL.md description caused YAML frontmatter parse failure in Claude Code / agent skill loader | Quoted description in sharepoint-compare-publication-state SKILL.md using YAML folded block | Syntax fix | RESOLVED — frontmatter passes PyYAML validation |
| 2026-10-05 | Tier 1 | Lack of generic single-file download and HTML page upload skills in build-and-publish plugin | Added sharepoint-download-file (SPO/SP2016) and sharepoint-publish-html-page (M365 Roadmap 569208 native HTML rendering) with managed symlinks and evals | New Capability | RESOLVED - audit-skill --strict and plugin manifest tests pass |

## 2026-10-05 - Add PSCredential Support to spo-download-file.ps1

- **Type**: Enhancement / Fix
- **Summary**: Added [PSCredential] parameter to spo-download-file.ps1 to allow interactive or explicit domain credential passing when downloading from on-premises SharePoint 2016 instances where default Windows credentials are not passed automatically.
- **Components**: plugins/sharepoint-site-build-and-publish/scripts/content-publication/spo-download-file.ps1


## 2026-10-05 - Add Config-Driven SP2016 Auth and PSCredential to spo-download-file.ps1

- **Type**: Enhancement / Fix
- **Summary**: Aligned spo-download-file.ps1 with canonical SP2016 patterns (collect-sp2016-page-manifest.ps1). Reads Source.UseDefaultCredentials from config.psd1, supports -UseDefaultCredentials switch and -Credential parameter, and falls back to interactive Get-Credential when unauthenticated.
- **Components**: plugins/sharepoint-site-build-and-publish/scripts/content-publication/spo-download-file.ps1

