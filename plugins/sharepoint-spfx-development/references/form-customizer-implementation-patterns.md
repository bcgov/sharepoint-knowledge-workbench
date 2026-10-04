# Form Customizer: implementation patterns

## Contents

- [Project structure](#project-structure)
- [Lifecycle host](#lifecycle-host)
- [URL-driven related-item forms](#url-driven-related-item-forms)
- [Accessibility and UI discipline](#accessibility-and-ui-discipline)
- [Safe return and redirect handling](#safe-return-and-redirect-handling)
- [Large-list lookup guidance](#large-list-lookup-guidance)
- [Worked example](#worked-example)

## Project structure

Keep data access, state management and UI rendering cleanly separated:

```
src/extensions/<name>/
├── <Name>FormCustomizer.manifest.json   # Extension manifest & Component ID
├── <Name>FormCustomizer.ts             # Lifecycle host (onInit, render, onDispose)
├── components/
│   ├── <Name>.tsx                      # Main React Form container
│   ├── <Name>.module.scss              # Scoped Fluent UI styling
│   └── ParentSummaryBanner.tsx         # Parent lookup display card
├── models/
│   └── IFormModels.ts                  # Form state and DTO interfaces
├── services/
│   ├── FormValidationService.ts        # Input validation & schema rules
│   └── SharePointDataService.ts        # SPHttpClient / PnPjs list operations
└── utils/
    └── UrlNavigationHelper.ts          # URL parameter & Source redirect validation
```

## Lifecycle host

`<Name>FormCustomizer.ts`:

```typescript
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Log } from '@microsoft/sp-core-library';
import {
  BaseFormCustomizer,
  FormDisplayMode
} from '@microsoft/sp-listview-extensibility';
import { ReviewFormComponent } from './components/ReviewFormComponent';
import { IReviewFormProps } from './models/IFormModels';

export default class ReviewFormCustomizer extends BaseFormCustomizer<Record<string, unknown>> {

  public onInit(): Promise<void> {
    Log.info('ReviewFormCustomizer', `Initialized for list: ${this.context.list.title}`);
    return Promise.resolve();
  }

  public render(): void {
    const element: React.ReactElement<IReviewFormProps> = React.createElement(
      ReviewFormComponent,
      {
        context: this.context,
        displayMode: this.displayMode,
        onSave: () => this.formSaved(),
        onClose: () => this.formClosed()
      }
    );

    ReactDOM.render(element, this.domElement);
  }

  public onDispose(): void {
    ReactDOM.unmountComponentAtNode(this.domElement);
    super.onDispose();
  }
}
```

## URL-driven related-item forms

When creating a child item linked to a parent through `NewForm.aspx?SelectedID=2411`:

1. **Parse and validate URL parameters.** Treat them as untrusted input and enforce a positive integer:

   ```typescript
   export function getValidatedSelectedId(searchQuery: string): number | null {
     const params = new URLSearchParams(searchQuery);
     const rawId = params.get('SelectedID');

     if (!rawId) return null;

     // Enforce positive non-zero integer
     if (!/^[1-9]\d*$/.test(rawId.trim())) {
       return null;
     }

     const parsed = parseInt(rawId.trim(), 10);
     if (isNaN(parsed) || parsed <= 0 || parsed > 2147483647) {
       return null;
     }

     return parsed;
   }
   ```

2. **Query the parent item by ID**, fetching only the required fields with `SPHttpClient`:

   ```typescript
   export async function getParentSummary(
     spHttpClient: SPHttpClient,
     webUrl: string,
     parentListTitle: string,
     parentId: number
   ): Promise<{ id: number; title: string; displayName: string }> {
     const endpoint = `${webUrl}/_api/web/lists/getByTitle('${encodeURIComponent(parentListTitle)}')/items(${parentId})?$select=Id,Title`;

     const res = await spHttpClient.get(endpoint, SPHttpClient.configurations.v1, {
       headers: { 'Accept': 'application/json;odata=nometadata' }
     });

     if (!res.ok) {
       if (res.status === 404) throw new Error(`Parent record (ID ${parentId}) not found.`);
       if (res.status === 403) throw new Error(`Access denied to parent record (ID ${parentId}).`);
       throw new Error(`Failed to load parent record (HTTP ${res.status}).`);
     }

     const data = await res.json();
     return {
       id: data.Id,
       title: data.Title,
       displayName: `${data.Title} (ID: ${data.Id})`
     };
   }
   ```

3. **Save with the integer lookup ID**, using the internal field name postfixed with `Id` (`RelatedAuthorId`):

   ```typescript
   export async function createReviewItem(
     spHttpClient: SPHttpClient,
     webUrl: string,
     listTitle: string,
     itemData: { title: string; body: string; relatedPersonId: number }
   ): Promise<void> {
     const endpoint = `${webUrl}/_api/web/lists/getByTitle('${encodeURIComponent(listTitle)}')/items`;

     const body = JSON.stringify({
       Title: itemData.title,
       ReviewText: itemData.body,
       RelatedAuthorId: itemData.relatedPersonId // Integer ID, NOT display text
     });

     const res = await spHttpClient.post(endpoint, SPHttpClient.configurations.v1, {
       headers: {
         'Accept': 'application/json;odata=nometadata',
         'Content-Type': 'application/json;odata=nometadata'
       },
       body: body
     });

     if (!res.ok) {
       const errText = await res.text();
       throw new Error(`Failed to save item: ${errText}`);
     }
   }
   ```

Never pass display names, person titles or GUID strings to SharePoint REST lookup properties. Lookups must receive the integer `Id` of the parent list item.

## Accessibility and UI discipline

- Heading structure: a visible `<h1>` / `<h2>` form title and a parent summary banner near the top.
- Labels and ARIA: Fluent UI `TextField` and `Label`, with `aria-required="true"`.
- Validation focus: move keyboard focus to the first invalid control when validation fails.
- Save state and double-submit protection: disable Save immediately on submission and render a `Spinner`.
- Cancel and dismissal: accessible Cancel and Close buttons calling `this.context.formClosed()`.
- Safe output rendering: never inject unescaped strings into `innerHTML`; use React JSX bindings.

## Safe return and redirect handling

Sanitize the `Source` query parameter before navigating, to prevent open-redirect vulnerabilities:

```typescript
export function navigateToSafeSource(webUrl: string, fallbackUrl?: string): void {
  const params = new URLSearchParams(window.location.search);
  const rawSource = params.get('Source');

  if (!rawSource) {
    window.location.href = fallbackUrl || `${webUrl}/SitePages/Home.aspx`;
    return;
  }

  try {
    const decoded = decodeURIComponent(rawSource);
    // Relative path or same tenant origin only
    if (decoded.startsWith('/') && !decoded.startsWith('//')) {
      window.location.href = decoded;
      return;
    }

    const currentOrigin = new URL(webUrl).origin.toLowerCase();
    const parsed = new URL(decoded, webUrl);
    if (parsed.origin.toLowerCase() === currentOrigin) {
      window.location.href = parsed.href;
      return;
    }
  } catch {
    // Fall through to default
  }

  window.location.href = fallbackUrl || `${webUrl}/SitePages/Home.aspx`;
}
```

## Large-list lookup guidance

Why this pattern matters for enterprise environments:

1. **Bypasses large dropdowns.** Instead of a lookup dropdown with 10,000+ options (which degrades the browser or hits thresholds), the form resolves only the single target parent item by ID.
2. **Threshold limits remain.** It does not bypass List View Threshold limits on unindexed views; index the lookup column if querying views by lookup.
3. **Permission boundaries.** If the user lacks Read on the parent item, the API returns HTTP 403; catch it and show an accessible permission error rather than crashing.

## Worked example

Scenario: Authors dossier to Review entry. Parent list `Authors` (item ID `2411`, Title `Dr. Evelyn Reed`); child list `Reviews`; lookup field `RelatedAuthor` (`RelatedAuthorId`).

1. The operator views `https://tenant.sharepoint.com/sites/ops/SitePages/Author.aspx?SelectedID=2411` and clicks "Add Review".
2. The browser opens `https://tenant.sharepoint.com/sites/ops/Lists/Reviews/NewForm.aspx?SelectedID=2411&Source=<encoded Author.aspx URL>`.
3. The form extracts `SelectedID=2411`, verifies a positive integer, queries `Authors` for item 2411, and shows a read-only banner "Related Author: Dr. Evelyn Reed (ID: 2411)".
4. The operator enters Heading `Initial Assessment` and a review, and clicks Save.
5. The form POSTs `{ Title: "Initial Assessment", ReviewText: "...", RelatedAuthorId: 2411 }`, then calls `this.context.formSaved()` and navigates safely back to the `Source` URL.
