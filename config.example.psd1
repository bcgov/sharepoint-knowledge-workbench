@{
    # Template for the local, git-ignored config-spo-{dev,test,prod}.psd1 files.
    # Each file holds exactly one SPO target and one SP2016 source:
    #   dev  -> SPO https://contoso.sharepoint.com/sites/example-site-dev   + SP2016 PROD https://sp2016.contoso.local/
    #   test -> SPO https://contoso.sharepoint.com/sites/example-site-test  + SP2016 PROD https://sp2016.contoso.local/
    #   prod -> SPO https://contoso.sharepoint.com/sites/example-site       + SP2016 PROD https://sp2016.contoso.local/
    # Fill TenantId/ClientId from the Entra app registration. Never add secrets.
    # Connection.* is the SharePoint Online target (the only site scripts connect to for SPO work).
    Connection = @{
        Environment        = "dev"
        SiteUrl            = "https://contoso.sharepoint.com/sites/example-site-dev"
        TenantId           = "00000000-0000-0000-0000-000000000000"
        ClientId           = "00000000-0000-0000-0000-000000000000"
        # Interactive, DeviceCode, or Certificate
        AuthenticationMode = "Interactive"
    }
    Authentication = @{
        # Required only when AuthenticationMode = "Certificate"
        CertificateThumbprint = ""
        # SharePoint tenant admin URL (optional, tenant-scoped operations)
        TenantAdminUrl        = "https://contoso-admin.sharepoint.com"
    }
    # SharePoint 2016 source paired with this target. Read-only; Windows authentication.
    Source = @{
        Platform              = "SharePoint2016"
        Environment           = "prod"
        SiteUrl               = "https://sp2016.contoso.local/"
        ReadOnly              = $true
        AuthenticationMode    = "Integrated"
        UseDefaultCredentials = $true
        Sites                 = @{
            Main       = "https://sp2016.contoso.local/"
            SubsiteA   = "https://sp2016.contoso.local/subsite-a/"
            SubsiteB   = "https://sp2016.contoso.local/subsite-b/"
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
