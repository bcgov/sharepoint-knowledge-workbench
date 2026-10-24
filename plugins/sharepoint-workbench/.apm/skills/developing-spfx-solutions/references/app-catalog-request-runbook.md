# Site Collection App Catalog request runbook

## Contents

- [Why and which path](#why-and-which-path)
- [Path A: enterprise tenancy (service-desk request)](#path-a-enterprise-tenancy-service-desk-request)
- [Path B: trial or sandbox tenancy](#path-b-trial-or-sandbox-tenancy)
- [Verification and handoff](#verification-and-handoff)

## Why and which path

Deploying custom SPFx web parts (such as the Master-Detail briefing dashboard) requires a Site Collection App Catalog on the target site. Admin permission models differ:

- **Path A, enterprise tenancy:** developers lack SharePoint Tenant Admin rights (`-admin.sharepoint.com`), so a request to your organization's SharePoint administration team is required.
- **Path B, isolated trial or sandbox tenancy:** developers hold Global or Tenant Admin rights and can provision directly through PnP PowerShell or the SharePoint Admin Center.

## Path A: enterprise tenancy (service-desk request)

Submit a request to your organization's SharePoint administration team using this template.

```text
Title: Request for Site Collection App Catalog Provisioning for Target SPO Sites

Ticket category: SharePoint Online Administration

Description:
For the following SharePoint Online sites, we require the setup of a Site Collection App Catalog to enable deployment of custom SPFx web parts for the application modernization initiative:

Target SharePoint Online Sites:
1. https://contoso.sharepoint.com/sites/TargetSite-Test (Test Environment)
2. https://contoso.sharepoint.com/sites/TargetSite-Prod (Production Environment)

Business Justification:
To enable a like-for-like migration of the legacy SharePoint application, custom SPFx web parts are required to replicate the legacy multi-list URL-filtered briefing pages (Author_Briefing.aspx). Out-of-the-box SPO List Web Parts do not support query string filtering (?SelectedID=...).

Prior Approved Reference Tickets (optional, if your organization has precedents):
- <TICKET_REFERENCE_1>
- <TICKET_REFERENCE_2>

Required Action by Tenant Administrator:
Execute `Add-PnPSiteCollectionAppCatalog` on the admin site endpoint or provision via SharePoint Admin Center -> More Features -> Apps -> Site Collection App Catalogs for both site URLs listed above.
```

## Path B: trial or sandbox tenancy

Option 1, PnP PowerShell (recommended). Connect to the tenant admin site URL (`-admin.sharepoint.com`), not the target site collection.

```powershell
Connect-PnPOnline -Url "https://contoso-admin.sharepoint.com" -ClientId "<clientId>" -Interactive
Add-PnPSiteCollectionAppCatalog -Site "https://contoso.sharepoint.com/sites/TargetSite-Test"
Add-PnPSiteCollectionAppCatalog -Site "https://contoso.sharepoint.com/sites/TargetSite-Prod"
```

Option 2, SharePoint Admin Center: open `https://contoso-admin.sharepoint.com`; More features; under Apps click Open; Site Collection App Catalogs; Add a site collection; enter the site URL; Confirm and create.
SharePoint enables the feature and provisions the catalog at `https://contoso.sharepoint.com/sites/Demo/AppCatalog` within 10 to 30 seconds.

## Verification and handoff

1. Open `https://contoso.sharepoint.com/sites/Demo/AppCatalog/AppCatalog` (or `.../AppCatalog/Forms/AllItems.aspx`).
2. Confirm the Apps for SharePoint document library exists.
3. Deploy `.sppkg` packages with the `sharepoint-deploy-spfx-solution` skill.
