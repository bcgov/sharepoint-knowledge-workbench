# Acceptance Criteria

- Skill slug: `sharepoint-plan-page-modernization`.
- Target plugin: `sharepoint-site-migration`.
- Layout selection and component mapping consume classified input and perform no tenant writes.
- Rule conditions use only the documented restricted expression subset; unsafe rules are skipped and reported.
- Unsupported components and connected consumers appear in explicit gap output, never silently disappear.
- The result is a plan only and does not claim to create or publish a modern page.
- Focused page-modernization planning tests pass.
