# Acceptance Criteria

- Skill slug: `sharepoint-plan-migration-waves`.
- Target plugin: `sharepoint-site-migration`.
- The planner accepts caller-supplied objects and named dependencies and performs no tenant I/O.
- A valid graph returns a computed order in which each dependency is in an earlier stage.
- Cycles and unresolved dependencies return `FAILED` findings instead of a guessed order.
- Empty input returns the documented `EMPTY` outcome.
- Focused wave-planning tests pass.
