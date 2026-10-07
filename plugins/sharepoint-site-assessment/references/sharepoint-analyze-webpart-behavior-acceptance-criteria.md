# Acceptance Criteria: sharepoint-analyze-webpart-behavior

- Skill slug: `sharepoint-analyze-webpart-behavior`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Groups classic SharePoint web parts by functional behaviour (inline script, external helper scripts, text-only, empty, or unretrievable) so near-duplicate instances collapse into a reviewable set. Use when a modernization review should cover each behaviour once instead of each instance. Classification knowledge is caller-supplied via a KnowledgeBase; read-only.

## Constraints honored

- Read-only. No tenant contact and no writes outside the output directory you name. A missing input is `UNAVAILABLE` and creates no output directory.
- An unretrievable web part is `ScriptEditorMissing`: an unknown, not an empty one. Any run containing one reports `PARTIAL` with the count, never `OBSERVED`.
- Classification knowledge is caller-supplied through `KnowledgeBase` and `InlineLogicRule`. `DEFAULT_KNOWLEDGE_BASE` is deliberately generic; build in no site-specific rules.
- The per-group `businessIntent`, `enforcementLevel` and `spfxAssessment` fields are a deterministic starting point, not a disposition.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check `outcome.status` and the three output artifacts. `PARTIAL` means some web parts were unretrievable; report the count. See outcomes.
- Focused plugin tests for this skill pass.
