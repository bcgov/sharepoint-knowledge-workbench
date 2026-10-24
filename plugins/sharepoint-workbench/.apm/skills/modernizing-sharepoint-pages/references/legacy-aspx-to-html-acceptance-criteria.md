# Legacy ASPX-to-HTML Skill Acceptance Criteria

The skill is acceptable when:

- Its description routes requests for local conversion of static legacy SharePoint ASPX files, not modern-page conversion or publication.
- The canonical converter is present at the plugin root under `scripts/` and is exposed to this skill by a managed file-level symlink.
- The skill documents single-file scope, local-only behavior, output collision handling, active-content rejection, and manual output review.
- Routing and task-success evaluations cover successful conversion, unsafe-input rejection, and the no-publication boundary.
- The focused PowerShell integration tests and repository symlink audit pass.
