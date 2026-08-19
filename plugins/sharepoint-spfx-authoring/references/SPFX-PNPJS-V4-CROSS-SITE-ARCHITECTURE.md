# PnPjs v4 Cross-Site Collection & State Isolation Architecture

## Overview

In enterprise SharePoint Online architectures (e.g. Hub-and-Spoke navigation topologies), web parts deployed on child or spoke sites often need to read or write centralized data stored on a parent Hub site (such as user favourites, organizational quick links, or shared document taxonomies) while querying local site-specific document libraries.

This guide details the singleton initialization pattern, cross-site querying with `@pnp/sp` v4, and per-user data isolation.

---

## 1. Centralized PnPjs v4 Singleton: `pnpjsConfig.ts`

Avoid initializing PnPjs instances inside individual components. Establish a centralized configuration with selective modular tree-shaking and logging.

```typescript
import { WebPartContext } from '@microsoft/sp-webpart-base';
import { LogLevel, PnPLogging } from '@pnp/logging';
import { spfi, SPFI, SPFx as spSPFx } from '@pnp/sp';
import '@pnp/sp/webs';
import '@pnp/sp/lists';
import '@pnp/sp/items';
import '@pnp/sp/fields';
import '@pnp/sp/files';
import '@pnp/sp/batching';
import '@pnp/sp/security';
import { IWeb, Web } from '@pnp/sp/webs';

let _sp: SPFI | null = null;
let _context: WebPartContext | null = null;

/**
 * Initialize or retrieve the root SPFI instance bound to the web part context.
 */
export const getSP = (context?: WebPartContext): SPFI => {
  if (context) {
    _sp = spfi().using(spSPFx(context)).using(PnPLogging(LogLevel.Warning));
    _context = context;
  }
  return _sp!;
};

export const getContext = (): WebPartContext => {
  return _context!;
};

/**
 * Retrieve a scoped IWeb instance for cross-site collection queries.
 */
export const getWeb = (absUrl: string): IWeb => {
  if (!_context) {
    throw new Error('PnPjs Context not initialized. Call getSP(context) in onInit().');
  }
  return Web(absUrl).using(spSPFx(_context)).using(PnPLogging(LogLevel.Warning));
};
```

---

## 2. Hub-and-Spoke Data Topology

```text
┌────────────────────────────────────────────────────────┐
│               Enterprise Hub Site                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Central User State List (e.g. UserFavourites)    │  │
│  │ - Title, URL, Metadata                           │  │
│  │ - Filtered by Author/Id eq CurrentUserId         │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────────▲────────────────────────────┘
                            │ (Reads/Writes via getWeb(hubUrl))
┌───────────────────────────┴────────────────────────────┐
│               Spoke / Department Site                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Local Document Library / Apps Catalog            │  │
│  │ - Departmental assets, policies, tools           │  │
│  └────────────────────────▲─────────────────────────┘  │
│                           │ (Reads via sp.web)         │
│  ┌────────────────────────┴─────────────────────────┐  │
│  │ Modern SPFx Web Part                             │  │
│  │ - Merges local records with user favourites      │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Per-User State Isolation Pattern

When storing personal preferences (such as favourited apps or bookmarked documents) in a shared SharePoint list:

1. **Query by Author ID**: Always filter query by the current user's ID to ensure user isolation:
   ```typescript
   const currentUserId = context.pageContext.legacyPageContext.userId;
   const userFavorites = await hubWeb.lists
     .getById(favoritesListId)
     .items
     .filter(`AuthorId eq ${currentUserId}`)
     .select('Id', 'Title', 'TargetUrl', 'DisplayOrder', 'Created')();
   ```

2. **Auto-Incrementing Display Order**:
   ```typescript
   const maxOrder = userFavorites.reduce((max, item) => Math.max(max, item.DisplayOrder || 0), 0);
   const newDisplayOrder = maxOrder + 1;
   ```

3. **Optimistic Local UI Updates**:
   Update local component state immediately upon user click (e.g. toggling a heart/bookmark icon) while dispatching the asynchronous PnP write in the background. If the request fails, rollback the local state and display a non-blocking `MessageBar`.

---

## 4. Robust Permission & Error Handling

Cross-site requests can encounter permission boundaries (e.g. if a user has read access on a spoke site but restricted permissions on the hub favourites list):

```typescript
export function parseSpError(err: any, fallbackName: string = 'SharePoint resource'): string {
  const errorMsg = err?.['odata.error']?.message?.value || err?.message || String(err);
  
  if (errorMsg.includes('403') || errorMsg.toLowerCase().includes('access denied') || errorMsg.toLowerCase().includes('unauthorized')) {
    return `Access Denied: Unable to access ${fallbackName}. Please verify your permissions.`;
  }
  if (errorMsg.toLowerCase().includes('does not exist')) {
    return `The requested list or library in ${fallbackName} could not be found.`;
  }
  return errorMsg;
}
```