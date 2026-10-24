# Acceptance Criteria — sharepoint-develop-spfx-form-customizer

## Discovery Contract

- **Skill slug**: `sharepoint-develop-spfx-form-customizer`
- **Target plugin**: `sharepoint-spfx-development`
- **Purpose**: Scaffolds, implements, tests, packages, deploys, associates, validates, and rolls back an SPFx Form Customizer extension for custom New/Edit/Display forms with URL-driven related-item lookups (`?SelectedID=...`).
- **Trigger phrases**:
  - `create spfx form customizer`
  - `scaffold form customizer`
  - `replace sharepoint list form with custom react form`
  - `url-driven related item entry form`
  - `associate form customizer with content type`
  - `selectedid lookup form`
- **Allowed tools**: `Bash, Read, Write`

## Structural Requirements

- Skill folder exists at:
  - `plugins/sharepoint-spfx-development/skills/sharepoint-develop-spfx-form-customizer/`
- Required files exist:
  - `SKILL.md`
  - `evals/evals.json`
  - `references/acceptance-criteria.md`
  - `references/form-customizer-lifecycle.md`
  - `references/content-type-association.md`
  - `references/url-driven-related-item-pattern.md`
  - `references/validation-checklist.md`
  - `scripts/check-spfx-toolchain.ps1`
  - `scripts/associate-form-customizer.ps1`
  - `scripts/remove-form-customizer-association.ps1`
  - `scripts/validate-form-customizer-association.ps1`

## Behavioral Requirements

- Skill workflow includes:
  - Toolchain validation (`scripts/check-spfx-toolchain.ps1`)
  - Architectural suitability comparison (Web Part vs Form Customizer vs Field Customizer vs ListView Command Set vs Power Apps vs JSON formatting)
  - Scaffolding flow (`yo @microsoft/sharepoint` -> Extension -> Form Customizer)
  - Component lifecycle implementation (`BaseFormCustomizer`, `onInit`, `render`, `onDispose`, `this.context.item`, `this.formSaved()`, `this.formClosed()`)
  - URL query parameter parsing and strict positive integer validation (`/^[1-9]\d*$/`)
  - Parent item pre-fetch with minimal selective fields and access validation
  - Correct lookup field save payload (`<InternalName>Id: <integer_id>`, not text/display name)
  - Accessible UI rendering (Fluent UI, label bindings, keyboard focus on first error, double-submit protection)
  - Safe `Source` redirect validation preventing open redirects
  - Content type association via `Set-PnPContentType` with prior state backup and readback verification
  - Rollback / detachment procedure setting content type properties to `""`

## Output Quality Requirements

- `evals/evals.json` uses `should_trigger` booleans (no legacy `expected_behavior` field).
- All symlinks adhere to ADR-003 and are registered in `symlinks.json`.
- Zero broken symlinks or text-file stand-ins.
