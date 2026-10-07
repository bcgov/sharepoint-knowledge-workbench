# Acceptance Criteria

- Skill slug: `sharepoint-analyze-classic-pages`.
- Target plugin: `sharepoint-site-migration`.
- Analysis uses exported files only and makes no tenant or network calls.
- Inventory and classification are distinct stages with explicit outcomes.
- Unknown components remain `Unknown`; missing, empty, and partial inputs are not reported as complete.
- Each classified component retains its role, type, and variant for the planning stage.
- Focused page-modernization tests pass.
