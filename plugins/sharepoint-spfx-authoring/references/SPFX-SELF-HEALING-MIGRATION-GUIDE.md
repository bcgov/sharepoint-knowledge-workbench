# Self-Healing GUID Migration & Resilient Property Resolution in SPFx

## Overview

When promoting modern SharePoint sites across environments (e.g. `DEV` -> `TEST` -> `PROD`) or migrating lists between sites, SharePoint generates new unique identifiers (`GUIDs`) for lists and libraries. 

If an SPFx web part stores only static `ListId` or `DocumentLibraryId` GUIDs in its property bag, migrating a page or promoting a template will break the web part, displaying "List not found" errors.

This reference details the **Self-Healing GUID Architecture**, enabling web parts to automatically recover and repair broken list bindings post-migration.

---

## 1. Dual-Key Property Storage Pattern

In your web part properties interface, persist both the **Unique GUID** (for fast REST querying) and the **Human-Readable Title** (for fallback recovery):

```typescript
export interface IEnterpriseWebPartProps {
  documentLibraryId: string;      // Primary: Fast OData queries via getById(id)
  documentLibraryTitle?: string;  // Fallback: Preserved across site migrations
  targetListId: string;
  targetListTitle?: string;
}
```

---

## 2. Dynamic Recovery Algorithm

When the web part initializes or executes its primary query, implement a fallback trap:

```text
┌──────────────────────────────────────┐
│  Query List by GUID:                 │
│  web.lists.getById(libraryId)        │
└──────────────────┬───────────────────┘
                   │
         Does list exist?
        /                \
     [YES]              [NO / 404 Error]
       │                         │
  Proceed to render       ┌──────▼───────────────────────────────────┐
                          │  Attempt Fallback Resolution by Title:   │
                          │  web.lists.getByTitle(libraryTitle)      │
                          └──────┬───────────────────────────────────┘
                                 │
                         Was list located?
                        /                 \
                    [YES]                [NO]
                      │                    │
          ┌───────────▼─────────────┐   Render Friendly Setup /
          │ 1. Recover new GUID     │   Configuration Prompt
          │ 2. Update webpart props │
          │ 3. Save property bag    │
          │ 4. Resume query         │
          └─────────────────────────┘
```

---

## 3. Implementation in TypeScript / SPFx

```typescript
export async function resolveOrRecoverListGuid(
  web: IWeb,
  currentGuid: string,
  expectedTitle?: string,
  onGuidRecovered?: (newGuid: string) => void
): Promise<{ id: string; title: string } | null> {
  // 1. Try resolving by existing GUID
  if (currentGuid) {
    try {
      const list = await web.lists.getById(currentGuid).select('Id', 'Title')();
      return { id: list.Id, title: list.Title };
    } catch (err) {
      console.warn(`[GUID Recovery] List ID ${currentGuid} not found. Attempting title fallback.`);
    }
  }

  // 2. Fallback: Try resolving by Title
  if (expectedTitle) {
    try {
      const list = await web.lists.getByTitle(expectedTitle).select('Id', 'Title')();
      console.info(`[GUID Recovery] Successfully recovered new GUID ${list.Id} for list "${expectedTitle}".`);
      
      if (onGuidRecovered) {
        onGuidRecovered(list.Id);
      }
      return { id: list.Id, title: list.Title };
    } catch (err) {
      console.error(`[GUID Recovery] Failed to locate list by title "${expectedTitle}".`, err);
    }
  }

  return null;
}
```

---

## 4. Property Pane Synchronization

Ensure that when a site administrator selects a list or library in the SPFx property pane, the web part stores **both** values:

```typescript
private _onLibrarySelectionChanged(propertyPath: string, newValue: any): void {
  const selectedOption = this._libraryDropdownOptions.find(o => o.key === newValue);
  if (selectedOption) {
    this.properties.documentLibraryId = selectedOption.key as string;
    this.properties.documentLibraryTitle = selectedOption.text;
  }
}
```