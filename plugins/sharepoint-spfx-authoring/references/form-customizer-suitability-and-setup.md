# Form Customizer: suitability, prerequisites and scaffolding

## Contents

- [What a Form Customizer is](#what-a-form-customizer-is)
- [Suitability decision](#suitability-decision)
- [Component comparison matrix](#component-comparison-matrix)
- [Toolchain and prerequisites](#toolchain-and-prerequisites)
- [Gather requirements](#gather-requirements)
- [Run the Yeoman generator](#run-the-yeoman-generator)

## What a Form Customizer is

An SPFx Form Customizer is a SharePoint Framework Extension (SPFx 1.15 and later) that replaces the standard New, Edit or Display form for items in a SharePoint Online list or library. Unlike a web part (which sits in a canvas
zone on a modern page), it attaches to a list's **content type** through client-side component properties (`NewFormClientSideComponentId`, `EditFormClientSideComponentId`, `DisplayFormClientSideComponentId`).

The lifecycle: determine suitability, validate prerequisites, run Yeoman, implement accessible React and Fluent UI components, parse URL parameters (`?SelectedID=...`) for parent-child relationships, package, deploy, associate
with the content type, validate on the tenant, and roll back safely.

## Suitability decision

Use a Form Customizer when:

- you need a customized New, Edit or Display form attached directly to a list or library;
- fields must initialize from URL query parameters (for example `NewForm.aspx?SelectedID=2411`);
- the default lookup picker is inadequate or hits performance limits against large parent lists;
- you need custom client-side validation, multi-step sections or conditional field interactions;
- you need controlled save and cancel navigation with validated return redirects (`Source=...`);
- the solution must live in a version-controlled TypeScript codebase with automated CI/CD packaging.

Do NOT use one when:

- the requirement is a standalone dashboard or multi-list dossier on a modern page (use a web part: `sharepoint-scaffold-spfx-react-app` or `sharepoint-scaffold-spfx-master-detail`);
- simple section reordering, column hiding or header/footer styling is enough (use JSON form formatting);
- a low-code Power Platform solution was explicitly chosen (use a Power Apps form);
- customization is needed only for single column cells in views (use an SPFx Field Customizer);
- customization is needed only for list command buttons or batch actions (use `sharepoint-scaffold-spfx-listview-command-set`).

## Component comparison matrix

| Approach | Attachment target | Scope | Pro-dev / code | URL context ingestion |
|---|---|---|---|---|
| SPFx Form Customizer | List content type | Entire item form | TypeScript / React | Full (`window.location.search`) |
| SPFx Web Part | Modern page canvas | Canvas zone | TypeScript / React | Via page context / URL |
| SPFx Field Customizer | List / site column | Single table cell | TypeScript / React | Cell context only |
| SPFx ListView Command | List command bar | Selected items | TypeScript | Selected items context |
| Power Apps Form | List integration | Item form | Low-code formula | Limited / connector-driven |
| JSON Form Layout | List form header/footer | Layout sections | Declarative JSON | No |

## Toolchain and prerequisites

- Node.js LTS (v18.x or v22.x).
- SPFx 1.20 or later (Heft / Webpack build toolchain); Form Customizers need SPFx 1.15 or later.
- Yeoman (`yo`) and `@microsoft/generator-sharepoint`.
- PowerShell 7 (`pwsh`) with `PnP.PowerShell`, for deployment, association and validation.
- Tenant context: a non-production test site or trial tenancy, the target list name, the target content type name, and the schema internal field names.

Verify with `pwsh -File scripts/check-spfx-toolchain.ps1`. If Node or npm is incompatible, switch to an approved LTS (for example `nvm use 22`) before proceeding.

## Gather requirements

Do not guess form requirements. Collect:

1. Solution and extension name, for example `narrative-form-customizer` / `NarrativeFormCustomizer`.
2. Target list and content type, for example list `Narratives`, content type `Item`.
3. Applicable form modes: New only, Edit only, Display only, or all.
4. URL query parameters, for example `SelectedID` for the parent item ID.
5. Parent list and lookup field, for example parent list `Persons`, child lookup field internal name `RelatedPerson` (`RelatedPersonId`).
6. Editable fields and validation rules, for example Heading (mandatory, max 100 characters), Narrative text (mandatory), Status.
7. Return navigation: a validated redirect back to the originating dossier page.

## Run the Yeoman generator

```bash
mkdir <solution-name>
cd <solution-name>
yo @microsoft/sharepoint
```

Choose: Solution name `<solution-name>` (or the folder name); Target `SharePoint Online only (latest)`; Component type `Extension`; Extension type `Form Customizer`; Form Customizer name `PascalCaseName` (for example
`NarrativeFormCustomizer`); Framework `React`.

The generator creates `src/extensions/<name>/<Name>FormCustomizer.manifest.json` (contains the component GUID `id`), `<Name>FormCustomizer.ts` (inherits `BaseFormCustomizer`) and
`components/<Name>.tsx` (the React root component).
