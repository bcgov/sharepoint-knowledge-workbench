# Acceptance Criteria

- Skill slug: `sharepoint-update-rich-text-image-links`.
- Target plugin: `sharepoint-site-migration`.
- Each item is classified against a caller-supplied verified inventory.
- Rewrites are proposed only for confirmed matches; missing files, placeholders, and no-image items remain explicit findings.
- Dry-run is the default; applying changes requires an injected executor and the plan confirmation token.
- The gap report accounts for every input item and distinguishes unresolved files from successful matches.
- Focused field-image remediation tests pass.
