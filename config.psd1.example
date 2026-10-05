@{
    # Template for the local, git-ignored config-spo-{dev,test,prod}.psd1 files.
    # Each file holds exactly one SPO target and one SP2016 source:
    #   dev  -> SPO https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV   + SP2016 PROD https://csb.jag.gov.bc.ca/
    #   test -> SPO https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-TEST  + SP2016 PROD https://csb.jag.gov.bc.ca/
    #   prod -> SPO https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET       + SP2016 PROD https://csb.jag.gov.bc.ca/
    # Fill TenantId/ClientId from the Entra app registration. Never add secrets.
    # Connection.* is the SharePoint Online target (the only site scripts connect to for SPO work).
    Connection = @{
        Environment        = "dev"
        SiteUrl            = "https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV"
        TenantId           = "00000000-0000-0000-0000-000000000000"
        ClientId           = "00000000-0000-0000-0000-000000000000"
        # Interactive, DeviceCode, or Certificate
        AuthenticationMode = "Interactive"
    }
    Authentication = @{
        # Required only when AuthenticationMode = "Certificate"
        CertificateThumbprint = ""
        # SharePoint tenant admin URL (optional, tenant-scoped operations)
        TenantAdminUrl        = "https://bcgov-admin.sharepoint.com"
    }
    # SharePoint 2016 source paired with this target. Read-only; Windows authentication.
    Source = @{
        Platform              = "SharePoint2016"
        Environment           = "prod"
        SiteUrl               = "https://csb.jag.gov.bc.ca/"
        ReadOnly              = $true
        AuthenticationMode    = "Integrated"
        UseDefaultCredentials = $true
        Sites                 = @{
            Main       = "https://csb.jag.gov.bc.ca/"
            Sheriff    = "https://csb.jag.gov.bc.ca/Sheriff/"
            CourtAdmin = "https://csb.jag.gov.bc.ca/CourtAdmin/"
        }
    }
    Safety = @{
        ReadOnly = $true
    }
    Defaults = @{
        DefaultHumanPublicationLibrary = "KnowledgePublications"
        DefaultAgentGroundingLibrary   = "AgentGrounding"
        DefaultAgentAssetsLibrary      = "AgentAssets"
        DefaultSitePagesLibrary        = "Site Pages"
    }
}
