# ListView Command Set: workflow and rules

## Contents

- [When to use it](#when-to-use-it)
- [Workflow](#workflow)
- [Registration commands](#registration-commands)
- [Rules](#rules)

## When to use it

Custom commands on a modern SharePoint list or document-library command bar. Do not use a Form Customizer: command sets attach to a list-scoped custom action, not a content type.

## Workflow

1. Confirm the target is a non-production site and collect: solution and command names; the target list or library; the command label, icon, sequence and visibility rules; the action (URL launch, selected-item operation,
   or an SPFx-owned React dialog or panel); and URL context such as a case-insensitive positive-integer `SelectedID`.
2. Run `scripts/check-spfx-toolchain.ps1`.
3. Scaffold with `yo @microsoft/sharepoint`: Component type **Extension**; Extension type **ListView Command Set**; Framework **React** when the command hosts custom UI.
4. Implement `onListViewUpdated` visibility and `onExecute` dispatch. Keep SharePoint access in a service, React state in components, and scoped styles in SCSS modules.
5. For uploads, upload the file first, then update metadata. Use live field internal names and `<InternalName>Id` lookup payloads. If metadata fails, delete only the file created by that transaction.
6. Add tests for command visibility, URL parsing, validation, duplicate filenames, lookup payloads, error sanitization and dialog or panel completion.
7. Build and package with `npm run build`; deploy the `.sppkg` to the intended App Catalog and add the app to the test site.
8. Register the extension on the list using the manifest component ID (see below). Persist custom-action changes with `Invoke-PnPQuery`, then re-query the list's `UserCustomActions` and confirm the stable name and
   component ID are present. Do not treat a success message alone as proof that registration persisted.
9. Wait for propagation, hard-refresh, and verify the command, dialog or panel, permissions, metadata, URL preselection, keyboard flow and error behavior.
10. Roll back the list registration without removing documents or the package.

## Registration commands

```powershell
pwsh -File scripts/register-listview-command-set.ps1 `
  -ListName "<Library>" -Name "<StableActionName>" -Title "<Button label>" `
  -ComponentId "<manifest-guid>" -Sequence 10 -ConfigPath "<config.psd1>"

# Roll back
pwsh -File scripts/register-listview-command-set.ps1 `
  -ListName "<Library>" -Name "<StableActionName>" `
  -ComponentId "<manifest-guid>" -ConfigPath "<config.psd1>" -Remove
```

The script supports `-WhatIf` and `-Confirm` but has no `-Execute` switch: without `-WhatIf` it writes. Preview with `-WhatIf` first.

## Rules

- Package deployment does not register the command on a list.
- Never associate a ListView Command Set with a content type.
- Omit broad `elements.xml` / `ClientSideInstance.xml` registration when list-scoped activation is required.
- Keep component properties valid JSON and treat URL and query values as untrusted.
- Prefer supported Fluent UI and SharePoint APIs over command-bar CSS injection.
