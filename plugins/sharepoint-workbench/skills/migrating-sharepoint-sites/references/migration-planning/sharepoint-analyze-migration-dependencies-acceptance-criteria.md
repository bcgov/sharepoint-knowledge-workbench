# Acceptance Criteria

- Skill slug: `sharepoint-analyze-migration-dependencies`.
- Target plugin: `sharepoint-site-migration`.
- Completeness checks run before dependency-matrix construction; a failed check blocks output.
- Wave order is computed by the shared topological planner from named dependencies.
- Cycles and unresolved dependencies are reported as blocking findings, never guessed around.
- Output follows the dependency-matrix schema and contains no tenant-derived side effects.
- Focused migration-planning tests pass.
