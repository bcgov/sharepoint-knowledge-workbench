# ============================================================
# TRIAL TENANCY config (local copy) — for the demo1 SPFx web part's scratch
# provisioning script (create-applications-list.ps1). Same isolated Microsoft
# 365 trial tenant sandbox used by
# jag-csb-cmat-sharepoint-online\trial-tenancy-testing\config-trial.psd1 and
# its books-authors-spfx-poc — copied here so demo1's scripts are
# self-contained and don't reach into a sibling repo path by default.
#
# If these values drift from the source-of-truth config-trial.psd1 in
# jag-csb-cmat-sharepoint-online, resync from there.
# ============================================================

@{
    # ============================================================
    # App registration #1 — delegated (interactive) auth
    # Use for: diagnostic scripts, interactive PnP operations, page migration
    # ============================================================
    ClientId  = "d7231fef-4a83-4b4f-85ba-b210d1d36018"
    TenantId  = "2321de1b-bcfa-4353-a8a3-63718910e698"  # Directory (tenant) GUID

    # ============================================================
    # App registration #3 — admin utility app for site grants
    # Use for: Grant-PnPAzureADAppSitePermission / Get-PnPAzureADAppSitePermission
    # Requires: Microsoft Graph -> Sites.FullControl.All (Delegated)
    # ============================================================
    AdminClientId  = "c94798ed-d61a-44c3-8ab8-9410a34153b7"

    # ============================================================
    # App registration #2 — app-only unattended certificate auth
    # Use for: nightly ORDS ETL, unattended site automation
    # ============================================================
    ETLClientId    = "4e01bef9-a82d-4f50-8ea7-346af73ddf1d"
    CertThumbprint = "0720482C853D6699ED6AA16C658DF219F0A9DEB1"

    # ============================================================
    # Trial tenant: BCGovernmentTrial400.onmicrosoft.com
    # SharePoint Online root domain for this tenant is
    # bcgovernmenttrial400.sharepoint.com
    # ============================================================
    SiteUrl   = "https://bcgovernmenttrial400.sharepoint.com/sites/AppRegistrationTests"
}
