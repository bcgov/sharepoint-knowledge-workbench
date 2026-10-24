# Overview of Selected Permissions (Microsoft Graph) — Summary

Source: [Overview of Selected permissions in OneDrive and SharePoint](https://learn.microsoft.com/en-us/graph/permissions-selected-overview) (Microsoft Learn, updated 2024-11-07). Full article not reproduced here — summary for quick reference; read the source for complete detail.

## The four `*.Selected` scopes (not just `Sites.Selected`)

| Scope | Grants access at |
|---|---|
| `Sites.Selected` | Site collection level |
| `Lists.SelectedOperations.Selected` | A specific list |
| `ListItems.SelectedOperations.Selected` | List items/files/folders |
| `Files.SelectedOperations.Selected` | Files/library folders only |

This workbench's `REGISTRATION_TYPES` only uses `Sites.Selected` (site-collection scope) — the more granular list/item/file-level scopes exist but aren't currently used anywhere in this repo. Worth knowing about if a future need calls for narrower-than-site-collection scoping.

## Three required steps, all three or it doesn't work

1. App consented (application or delegated) for the `.Selected` scope in Entra.
2. App **granted a role on the specific resource** via `POST /sites/{siteId}/permissions` (or the PnP equivalent, `Grant-PnPAzureADAppSitePermission`).
3. App presents a token containing that scope when calling the resource.

Matches this workbench's own two-control-plane model (Entra permission + separate PnP/Graph site-level grant) exactly — this is the authoritative source that model was built from.

## ⚠️ Role-name vocabulary mismatch — Graph API vs. PnP PowerShell

**The Graph REST API and PnP PowerShell use different role vocabularies for the same underlying concept — do not assume they're the same four words:**

| Graph API role (`POST /permissions` `roles` field) | PnP PowerShell `-Permissions` value |
|---|---|
| `read` | `Read` |
| `write` | `Write` |
| `owner` | *(no direct PnP equivalent name — likely `Manage`)* |
| `fullcontrol` | `FullControl` |

Graph's official role table has **`owner`**, not `manage`. PnP's cmdlet documentation (and this workbench's own `Grant-PnPAzureADAppSitePermission` usage) uses **`Manage`**, not `owner`. These almost certainly refer to the same underlying role via PnP's own translation layer, but the two vocabularies are not identical, and no source read so far confirms the mapping explicitly. **Do not assume `Manage` (PnP) and `owner` (Graph) are interchangeable without verifying** — when reading `Get-PnPAzureADAppSitePermission` output or a Graph API response for the same grant, check which vocabulary you're looking at before comparing role names across the two APIs.

## The four roles' official definitions (Graph vocabulary)

| Role | Definition |
|---|---|
| `read` | Read the metadata and contents of the resource |
| `write` | **Read and modify the metadata and contents of the resource** |
| `owner` | "Represents the owner role" (no further detail given) |
| `fullcontrol` | "Represents full control of the resource" (no further detail given) |

**This is the authoritative source for the correction already recorded elsewhere in this plugin** (`app_registration_request.py`'s `REGISTRATION_TYPES.interactive.capability_testing_status`, `SKILL.md`'s correction history): Microsoft's own `write` definition does not exclude structural operations like list/library creation — it says "modify the metadata and contents of the resource," full stop. The stricter Write-excludes-structure mapping this workbench originally encoded was not sourced from here.

## How access is calculated — the authoritative confirmation of the intersection model

> "There are two types of tokens: application only and delegated... With delegated, the application can never exceed the current user's existing permissions... In the delegated scenario, both the application and user permissions are calculated and then intersected, which means that the application can never exceed the user's permissions, and the user can never exceed (through the application) the consented application permissions."

This is the **authoritative source** for the intersection model already cited elsewhere in this plugin (`delegated-permission-boundary-test.md`, `REGISTRATION_TYPES.interactive`'s design notes). Important nuance this source adds precisely: it's a true intersection (effectively `min(app role, user permission)`), not "the app grant becomes irrelevant once a user is present." If a delegated session's observed capability exceeds what the app's own granted role should allow, per this model that should not be possible — which points toward the app's granted role (`write`) itself permitting more than this workbench originally assumed, rather than the app's grant being bypassed entirely by the user's own permissions. Both explanations remain in `capability_testing_status` since this source doesn't fully resolve which is operative in this workbench's specific tenant — but this source shifts the weight toward "the `write` role's real definition is broader than assumed" over "the app grant doesn't matter for delegated sessions."

## What's needed to manage permissions themselves (not covered elsewhere in this plugin)

Managing (granting/revoking) permissions on a resource requires a **higher** role than the resource itself:

| Resource | Required to manage its permissions |
|---|---|
| Site | `Sites.FullControl.All` |
| List | `Sites.FullControl.All`, or `Sites.Selected` + `FullControl`, or `Sites.Selected` + `Owner` |
| List item | as above, or `Lists.SelectedOperations.Selected` + `FullControl`/`Owner` |
| File | as above, or `Lists.SelectedOperations.Selected` + `FullControl`/`Owner` |

Not currently exercised anywhere in this workbench (`test-pnp-effective-capability-probe.ps1`'s optional `-RunPermissionMutationProbe` only reads groups/role definitions, never grants/revokes permissions) — worth knowing this table exists if a future capability needs it.

## Other consent-behavior notes worth remembering

- Revoking a broader scope (e.g. `Sites.*`) does **not** revoke a narrower grant already made under a different scope (e.g. a specific `Lists.*` grant) — they're independent.
- Removing a list-level grant removes access to **all items within that list**, regardless of any item-level grants previously made.
- A higher-level scope (`Sites.*`) can be used to grant file-specific permissions, but a lower-level scope can never reach a higher-level resource.
