# Acceptance Criteria

- Skill slug: `sharepoint-validate-link-integrity`.
- Validation is read-only and uses an injected resolver; the skill ships no hidden network transport.
- Links are classified as `RESOLVED`, `BROKEN`, `UNRESOLVABLE`, or `SKIPPED` with an honest overall outcome.
- An empty inventory returns `EMPTY`, not a successful validation.
- Unresolvable targets are not counted as passing, and every finding is retained in the report.
- Focused link-integrity tests pass.
