@{
    # === AUTHORIZED TENANT ===
    TenantSite = "https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV"

    # === PHASE 3 PILOT OUTPUT LIBRARIES ===
    # These are verified from Phase 3 run-phase3-tenant-pilot.ps1
    PageLibrary = @{
        Url = "CEISPilotKnowledgePages"
        Title = "CEIS Pilot Knowledge Pages"
        Type = "WebPageLibrary"
        Description = "Phase 3 CEIS pilot topic pages (25 topics, 319 media files)"
        Location = "Site Pages/CEISPilotKnowledgePages"
    }

    AssetLibrary = @{
        Url = "CEISPilotKnowledge"
        Title = "CEIS-Pilot-Knowledge"
        Type = "DocumentLibrary"
        Description = "Phase 3 CEIS pilot media assets"
        Location = "CEISPilotKnowledge/media"
    }

    # === PHASE 4 AGENTASSETS (Native Skills Storage) ===
    # Created for Phase 4 skill provisioning
    AgentAssets = @{
        Title = "AgentAssets"
        Type = "DocumentLibrary"
        Description = "Native SharePoint skills and agent assets library"
        SkillsFolder = "AgentAssets/Skills"
        DeployedSkills = @{
            ReviewManualTopics = @{
                Name = "review-manual-topics"
                Path = "AgentAssets/Skills/review-manual-topics"
                Filename = "SKILL.md"
                RepositorySHA256 = "9586379f777d2064004e747b2d73e49a3d16680efd0dc3e2c67d5d3c5e71ce2c"
                DeployedDate = "2026-08-01 01:29:21"
                FileSize = 6409
            }
        }
    }

    # === SITEPAGES SUBFOLDER (Custom Agent Configuration) ===
    # Used by Phase 4 custom agents (commit 83c60b7 research)
    SitePages = @{
        Title = "SitePages"
        CEISPilotFolder = "SitePages/CEISPilotKnowledgePages"
        Description = "Site Pages with CEISPilotKnowledgePages subfolder containing ASPX pages"
        # Resource IDs verified in Phase 4 experiments:
        # list_id: 1a4a1eda-a2fe-4c43-8d48-4a841f07b253
        # unique_id: d260117a-79d8-4586-b9cf-9a0211634556
    }

    # === CEIS PILOT METADATA FIELDS ===
    # Expected fields on CEISPilotKnowledgePages items (Phase 3 output)
    ExpectedMetadataFields = @(
        "TopicID"
        "PublicationOrder"
        "TopicContentSHA256"
        "Status"
        "ReviewDate"
        "TransitionAction"
        "TransitionTarget"
    )

    # === KNOWN GOOD VALUES FOR TESTING ===
    # These can be retrieved once a topic is selected
    # Sample format:
    # TopicExample = @{
    #     Title = "File Creation"
    #     Filename = "file-creation--XXXXX.aspx"
    #     TopicID = "file-creation"
    #     PublicationOrder = "1"
    #     Status = "Published"
    # }
}
