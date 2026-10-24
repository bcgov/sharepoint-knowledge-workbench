# Acceptance Criteria: sharepoint-request-site-collection-app-catalog

- Skill slug: `sharepoint-request-site-collection-app-catalog`.
- Target plugin: `sharepoint-spfx-development`.
- Purpose: Guides the setup of Site Collection App Catalogs through service-desk ticket requests in an enterprise tenancy, or through direct Admin Center and PnP PowerShell execution in trial and sandbox environments. Use before deploying custom SPFx web parts to a site that has no App Catalog.

## Constraints honored

- Path A (enterprise tenancy): developers lack Tenant Admin rights (`-admin.sharepoint.com`), so submit a request to your organization's SharePoint administration team (for example through its ticketing system); do not attempt direct provisioning.
- Path B (trial or sandbox tenancy): the developer holds Global or Tenant Admin. Connect to the tenant admin site URL (`-admin.sharepoint.com`), not the target site collection, before `Add-PnPSiteCollectionAppCatalog -Site`.
- Provisioning is a tenant write the user (or administrator) performs. Do not run it unprompted.

## Verification passes

- `https://contoso.sharepoint.com/sites/Demo/AppCatalog/AppCatalog` opens and the Apps for SharePoint document library exists. Then deploy packages with `sharepoint-deploy-spfx-solution`.
- Focused plugin tests for this skill pass.
