# Acceptance Criteria

- Skill slug: `sharepoint-develop-spfx-listview-command-set`
- Target plugin: `sharepoint-spfx-development`
- Canonical PowerShell resides only in the plugin root `scripts` directory.
- The skill-local script is a file-level symbolic link registered in `symlinks.json`.
- The workflow distinguishes package deployment, app installation, and list registration.
- Registration matches existing actions by stable name or component ID.
- Registration is idempotent; duplicate matches fail safely.
- `-Remove` removes all matching list actions and is safe when none exist.
- The skill covers URL launchers, selected-item commands, and React dialog/panel hosts.
- Positive and negative routing evals distinguish command sets from Form Customizers and web parts.
