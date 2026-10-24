# Acceptance Criteria

- Skill slug: `sharepoint-scaffold-migration-wave-scripts`.
- Target plugin: `sharepoint-site-migration`.
- Generation accepts only a non-failed dependency matrix and derives wave order from that matrix.
- Output contains one script skeleton per computed wave and one human-readable wave guide.
- Object names, types, and dependencies come from the matrix; field-level schema is not fabricated.
- The guide keeps each wave separately gated and generated scripts are not executed by this skill.
- Focused wave-generation tests pass.
