# Resource Specific Consent (RSC) for Microsoft Graph and SharePoint Online — Summary

Source: [Understanding Resource Specific Consent for Microsoft Graph and SharePoint Online](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins-modernize/understanding-rsc-for-msgraph-and-sharepoint-online) (Microsoft Learn, updated 2024-02-21). Full article not reproduced here — this is a summary for quick reference; read the source for complete detail.

## What RSC is, and why it replaced ACS

Classic SharePoint (on-prem and online) let you register apps in Azure Access Control
Services (ACS) with permissions scoped to specific site collections only — read/write/
manage/full control on just the sites you named. ACS is no longer the recommended path;
the replacement is Microsoft Entra app registration + OAuth. But a default Entra
registration's Graph permissions (`Sites.Read.All`, `Sites.ReadWrite.All`,
`Sites.Manage.All`, `Sites.FullControl.All`) all target **every** site collection in the
tenant — the `All` in the name is literal. For enterprises with many site collections,
that's too broad.

**`Sites.Selected`** is the RSC permission that restores per-site scoping on top of
modern Entra app registrations — this is exactly the permission model this workbench's
`request-app-registration` skill documents for both registration types
(`REGISTRATION_TYPES`).

## Two-step model this confirms

1. **Request/grant `Sites.Selected`** (Application permission) — on Microsoft Graph, on
   SharePoint Online (for REST), or both. This alone grants **no site access** — it only
   makes the app eligible to be granted specific sites next.
2. **Grant access to specific sites** — requires a tenant global admin, or an app that
   already holds `Sites.FullControl.All`. Two equivalent mechanisms:
   - **Microsoft Graph REST**: `POST https://graph.microsoft.com/v1.0/sites/{siteId}/permissions`
     with a body naming `roles` (`read`/`write`/`manage`/`fullcontrol`) and the target
     app's `clientId`.
   - **PnP PowerShell**: `Grant-PnPAzureADAppSitePermission -AppId <id> -DisplayName
     <name> -Permissions <Read|Write|Manage|FullControl> -Site <site>` — the mechanism
     this workbench's `test-grant-tier-probe.ps1` and `SETUP_STEPS` step 6 already use.
     Companion cmdlets: `Get-PnPAzureADAppSitePermission` (read current grants),
     `Set-PnPAzureADAppSitePermission` (change an existing grant's tier),
     `Revoke-PnPAzureADAppSitePermission` (remove a grant).

## The four permission tiers (confirms this workbench's own tier table)

| Tier | Grants |
|---|---|
| `Read` | Read metadata and content only |
| `Write` | Read + modify metadata and content |
| `Manage` | Write + **manage the site** |
| `FullControl` | Full control of the site and its content |

Matches `app_registration_request.py`'s `SETUP_STEPS` tier table and the real,
tested boundary this workbench already encodes (list creation requires `Manage`, not
just `Write`) — this Microsoft Learn description of "manage the site" as the delta
between `Write` and `Manage` is consistent with the empirical list-creation finding,
not just directionally similar.

## Practical notes for this workbench

- Once granted, an app can only reach sites it was explicitly granted — targeting any
  other site fails with an `Access denied` exception. Matches the empirically-proven
  boundary in `REGISTRATION_TYPES.interactive.design_notes` and
  `delegated-permission-boundary-test.md`.
- Granting is per-site and does not propagate — same point already made in
  `SETUP_STEPS` step 6.
- `Set-PnPAzureADAppSitePermission` (change an existing grant's tier without revoking
  first) and `Get-PnPAzureADAppSitePermission` (audit current grants) aren't currently
  used anywhere in this workbench's scripts/skills — worth knowing they exist if a
  future need arises (e.g. auditing which sites an app registration currently reaches,
  or upgrading a `Write` grant to `Manage` without a revoke/re-grant round trip).
