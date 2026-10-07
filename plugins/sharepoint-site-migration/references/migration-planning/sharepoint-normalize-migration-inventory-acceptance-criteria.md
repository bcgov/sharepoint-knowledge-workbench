# Acceptance Criteria

- Skill slug: `sharepoint-normalize-migration-inventory`.
- Target plugin: `sharepoint-site-migration`.
- The validator reads an existing export only and performs no live discovery or tenant I/O.
- Missing files, malformed JSON, missing arrays, and duplicate names produce specific failures.
- Lookup targets are preserved when present and never fabricated when absent.
- `OBSERVED`, `EMPTY`, `UNAVAILABLE`, and `FAILED` outcomes reflect actual export coverage.
- The documented schema link resolves from the skill's installed asset path.
- Focused inventory-validation tests pass.
