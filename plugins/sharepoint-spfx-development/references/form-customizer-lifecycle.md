# SPFx Form Customizer Lifecycle and Architecture

## Contents

- [Overview](#overview)
- [Component Comparison Matrix](#component-comparison-matrix)
- [Core Lifecycle and Base Class](#core-lifecycle-and-base-class)
- [Essential Context APIs](#essential-context-apis)
- [Component Manifest Configuration](#component-manifest-configuration)

## Overview

An **SPFx Form Customizer** is a SharePoint Framework Extension (introduced in SPFx 1.15) that overrides the default New, Edit, or Display form experience for items in a SharePoint Online list or document library.

Unlike client-side web parts that live inside canvas zones on modern pages, Form Customizers are bound directly to **Content Types** on a list or library. When a user navigates to `NewForm.aspx`, `EditForm.aspx`, or `DispForm.aspx` (or clicks "New" / "Edit" in the modern list command bar), SharePoint renders the Form Customizer inside the dedicated form host container.

---

## Component Comparison Matrix

To prevent architectural mistakes, compare Form Customizers against sibling SharePoint customization options before starting:

| Customization Type | Scope | How It Is Attached | Best Used For | Not Suitable For |
|---|---|---|---|---|
| **SPFx Form Customizer** | Entire list item form (New/Edit/Display) | List Content Type (`*FormClientSideComponentId`) | Custom form UI/UX, multi-field validation, URL query parameter pre-population (`?SelectedID=...`), custom save/cancel navigation | Page-level dashboards, embedding anywhere on a page, simple column color formatting |
| **SPFx Web Part** | Modern page canvas zone | Added to modern page by page author | Standalone dashboards, multi-list dossiers, report viewers, master-detail pages | Overriding native SharePoint list item creation/editing dialogs |
| **SPFx Field Customizer** | Single column cell in list view | Bound to list column or site column (`ClientSideComponentId`) | Custom data rendering, badges, status bars, inline cell actions in list views | Multi-field entry forms, complete item creation |
| **SPFx ListView Command Set** | List command bar & context menu | Registered on list or site | Custom buttons, batch actions, external workflow triggers | Custom form rendering or replacing list form dialogs |
| **Power Apps Form** | List item form | Integrated via SharePoint Power Apps settings | Low-code form layout, standard Office 365 connectors | Pro-dev custom CI/CD pipelines, strict offline testing, version-controlled TypeScript codebases |
| **JSON Form Formatting** | Standard list form sections/header/footer | List form configure layout panel | Reordering fields, adding headers/footers, grouping fields into collapsible sections | Custom business logic, API calls, dynamic URL query parameter ingestion, custom field controls |

---

## Core Lifecycle and Base Class

Form Customizers inherit from `BaseFormCustomizer<TProperties>` exported by `@microsoft/sp-listview-extensibility`.

```typescript
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Log } from '@microsoft/sp-core-library';
import {
  BaseFormCustomizer,
  FormDisplayMode
} from '@microsoft/sp-listview-extensibility';

export interface ICustomFormCustomizerProperties {
  parentListTitle?: string;
  defaultLookupField?: string;
}

export default class CustomFormCustomizer
  extends BaseFormCustomizer<ICustomFormCustomizerProperties> {

  public onInit(): Promise<void> {
    Log.info('CustomFormCustomizer', 'Initializing form customizer...');
    // Asynchronous initialization: parse parameters, resolve services, prefetch
    return Promise.resolve();
  }

  public render(): void {
    // Render custom React component or DOM tree into this.domElement
    const element: React.ReactElement = React.createElement(CustomFormComponent, {
      context: this.context,
      displayMode: this.displayMode,
      onSave: this._onSave.bind(this),
      onClose: this._onClose.bind(this)
    });

    ReactDOM.render(element, this.domElement);
  }

  public onDispose(): void {
    // Clean up DOM and unmount React elements
    ReactDOM.unmountComponentAtNode(this.domElement);
    super.onDispose();
  }

  private _onSave(): void {
    // Signal completion to SharePoint host
    this.formSaved();
  }

  private _onClose(): void {
    // Signal dismissal to SharePoint host
    this.formClosed();
  }
}
```

---

## Essential Context APIs

Inside `BaseFormCustomizer`, `this.context` provides critical runtime properties:

### 1. `this.context.displayMode` (or `this.displayMode`)
Indicates the current form mode:
- `FormDisplayMode.New` (`1`): Creating a new list item. `this.context.item` is undefined/empty.
- `FormDisplayMode.Edit` (`2`): Editing an existing item. `this.context.item` contains current field values.
- `FormDisplayMode.Display` (`3`): Viewing an item in read-only mode.

### 2. `this.context.item`
Contains the existing list item data during `Edit` and `Display` modes. Provides access to field internal values and metadata.

### 3. `this.context.list`
Provides information about the hosting list:
- `this.context.list.title`: Title of the list.
- `this.context.list.guid`: Unique GUID of the list.
- `this.context.list.serverRelativeUrl`: Server-relative URL path of the list.

### 4. `this.context.pageContext`
Provides tenant, user, and web context:
- `this.context.pageContext.web.absoluteUrl`: Absolute URL of the current SharePoint site.
- `this.context.pageContext.user.loginName` / `displayName`: Current user identity.

### 5. `this.formSaved()`
Notifies the SharePoint runtime that item persistence succeeded. SharePoint will handle closing the panel/dialog or navigating back to the view / `Source` URL.

### 6. `this.formClosed()`
Notifies the SharePoint runtime that the user canceled or closed the form without saving changes.

---

## Component Manifest Configuration

Form Customizers require a manifest (`<Name>FormCustomizer.manifest.json`):

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/spfx/client-side-extension-manifest.schema.json",
  "id": "e672956c-38d7-4c8d-b778-9e55b4fa3977",
  "alias": "ReviewEntryFormCustomizer",
  "componentType": "Extension",
  "extensionType": "FormCustomizer",
  "version": "1.0.0",
  "manifestVersion": 2,
  "requiresCustomScript": false
}
```

> [!IMPORTANT]
> The `id` field in the manifest is the **Component ID** GUID used when associating the Form Customizer with list content types in PnP.PowerShell.
