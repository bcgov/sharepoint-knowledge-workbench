# Site Collection App Catalog request runbook

## Contents

- [Why and which path](#why-and-which-path)
- [Path A: enterprise tenancy (ServiceNow request)](#path-a-enterprise-tenancy-servicenow-request)
- [Path B: trial or sandbox tenancy](#path-b-trial-or-sandbox-tenancy)
- [Verification and handoff](#verification-and-handoff)

## Why and which path

Deploying custom SPFx web parts (such as the Master-Detail briefing dashboard) requires a Site Collection App Catalog on the target site. Admin permission models differ:

- **Path A, enterprise tenancy:** developers lack SharePoint Tenant Admin rights (`-admin.sharepoint.com`), so a ServiceNow ticket to MySc / CSBC is required.
- **Path B, isolated trial or sandbox tenancy:** developers hold Global or Tenant Admin rights and can provision directly through PnP PowerShell or the SharePoint Admin Center.

## Path A: enterprise tenancy (ServiceNow request)

Submit a ServiceNow request to MySc / CSBC using this template.

```text
Title: Request for Site Collection App Catalog Provisioning for Target SPO Sites

ServiceNow Category: MySc / CSBC / SharePoint Online Administration

Description:
For the following SharePoint Online sites, we require the setup of a Site Collection App Catalog to enable deployment of custom SPFx web parts for the application modernization initiative:

Target SharePoint Online Sites:
1. https://contoso.sharepoint.com/sites/TargetSite-Test (Test Environment)
2. https://contoso.sharepoint.com/sites/TargetSite-Prod (Production Environment)

Business Justification:
To enable a like-for-like migration of the legacy SharePoint application, custom SPFx web parts are required to replicate the legacy multi-list URL-filtered briefing pages (Dossier_Briefing.aspx). Out-of-the-box SPO List Web Parts do not support query string filtering (?SelectedID=...).

Prior Approved Reference Tickets:
We understand similar requests were previously approved and submitted to MySc for BCPS with the following references:
- REQ0841030 (Request Item Number: RITM1239070)
- REQ0855248 (Request Item Number: RITM1259346)

Required Action by Tenant Administrator:
Execute `Add-PnPSiteCollectionAppCatalog` on the admin site endpoint or provision via SharePoint Admin Center -> More Features -> Apps -> Site Collection App Catalogs for both site URLs listed above.
```

## Path B: trial or sandbox tenancy

Option 1, PnP PowerShell (recommended). Connect to the tenant admin site URL (`-admin.sharepoint.com`), not the target site collection.

```powershell
Connect-PnPOnline -Url "https://<tenant>-admin.sharepoint.com" -ClientId "<clientId>" -Interactive
Add-PnPSiteCollectionAppCatalog -Site "https://contoso.sharepoint.com/sites/TargetSite-Test"
Add-PnPSiteCollectionAppCatalog -Site "https://contoso.sharepoint.com/sites/TargetSite-Prod"
```

Option 2, SharePoint Admin Center: open `https://<tenant>-admin.sharepoint.com`; More features; under Apps click Open; Site Collection App Catalogs; Add a site collection; enter the site URL; Confirm and create.
SharePoint enables the feature and provisions the catalog at `https://<tenant>.sharepoint.com/sites/<SiteName>/AppCatalog` within 10 to 30 seconds.

## Verification and handoff

1. Open `https://<tenant>.sharepoint.com/sites/<SiteName>/AppCatalog/AppCatalog` (or `.../AppCatalog/Forms/AllItems.aspx`).
2. Confirm the Apps for SharePoint document library exists.
3. Deploy `.sppkg` packages with the `sharepoint-deploy-spfx-solution` skill.
