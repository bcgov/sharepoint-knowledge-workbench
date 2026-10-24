# Acceptance Criteria: sharepoint-analyze-custom-forms

- Skill slug: `sharepoint-analyze-custom-forms`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Analyses an exported classic SharePoint custom list-form inventory, classifying each form as out-of-box, script-based, or InfoPath/custom-layout, and attaches a caller-supplied modernization strategy per classification. Use when planning a classic-to-modern migration and deciding which list forms carry forward as-is. Read-only; consumes an export you provide and never contacts a tenant.

## Constraints honored

- Read-only. No tenant writes, no network access: it reads the export path you name and writes analysis artifacts to the output directory you name.
- Rules are data, not code. Strategy text per classification comes entirely from the caller-supplied rules JSON; `assets/form-classification-rules.json` is a neutral default. No site-specific migration judgement is built in.
- A missing export or rules file is `UNAVAILABLE` and creates no output directory. An empty export is `EMPTY`, never a pass. A non-array input is `FAILED`.
- Run from this skill's root with `scripts/` on `sys.path`. Python is standard library only.

## Verification passes

- Check `outcome.status` is `OBSERVED` and the output directory holds the report. `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN` and `FAILED` are honest outcomes; report them as such.
- Focused plugin tests for this skill pass.
