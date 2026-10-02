# Managed metadata audit: provenance

Ported and generalized from `plugins/sharepoint-migration/scripts/inventory/check-managed-metadata-custom.ps1`
and `plugins/sharepoint-migration/scripts/utilities/check-managed-metadata-spo-prod.ps1` in the
originating SharePoint migration repository. All hardcoded site URLs, project codenames and output
defaults were removed in favor of explicit `-SiteUrl`, `-ParentSiteUrl` and `-TermGroupName`
parameters, and console-only (`Write-Host`/`Format-Table`) output was replaced with structured JSON
via a required `-OutputPath` parameter.
