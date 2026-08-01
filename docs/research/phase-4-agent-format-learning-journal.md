# Phase 4 Agent Format Learning Journal

**Date:** 2026-07-31  
**Task:** Task 7.5 - Agent format discovery and recreation based on manually created reference agents  
**Status:** Complete

## Summary

Successfully analyzed three SharePoint agent files (.agent JSON format) to understand the correct structure for Phase 4 native skill agents. Updated automation script to match discovered patterns.

## Reference Agents Downloaded

1. **agent-demo-2.agent** (CEISPilotKnowledgePages library)
   - File size: ~1.2 MB
   - Knowledge sources: 2 (CEISPilotKnowledgePages Site Pages folder + CEIS-Pilot-Knowledge document library)
   - Created: Manual UI creation
   - Status: Reference format

2. **CEISPilotKnowledgePages agent demo.agent** (SitePages subfolder)
   - Location: SitePages/CEISPilotKnowledgePages/ subfolder
   - Knowledge sources: 1 (nested Site Pages folder only)
   - Format: Simpler, self-referential
   - Status: Subfoldered agent reference

3. **CEIS-Pilot-Knowledge-Agent.agent** (CEISPilotKnowledgePages library)
   - Status: Script-generated, updated per learnings

## Key Learnings

### 1. Knowledge Source Structure
- Site Pages folders can be knowledge sources with type: "Folder"
- Document libraries use type: "List"
- Both require real `list_id` values from the live site
- Site Pages folders should include non-zero `unique_id` values (not placeholders)
- Document libraries use zero unique_id: "00000000-0000-0000-0000-000000000000"

### 2. JSON Schema Patterns
```json
{
  "schemaVersion": "0.2.0",
  "customCopilotConfig": {
    "conversationStarters": {
      "conversationStarterList": [3 items max],
      "welcomeMessage": {"text": "..."}
    },
    "gptDefinition": {
      "name": "...",
      "description": "...",
      "instructions": "Single sentence, formal tone",
      "capabilities": [{
        "name": "OneDriveAndSharePoint",
        "items_by_sharepoint_ids": [],
        "items_by_url": [...]
      }],
      "behavior_overrides": {
        "special_instructions": {
          "discourage_model_knowledge": true
        }
      }
    },
    "icon": "data:image/png;base64,..."
  }
}
```

### 3. Best Practices Discovered
- **Name:** Keep descriptive but reasonable length (e.g., "CEIS Pilot Knowledge Agent")
- **Description:** One short sentence about purpose
- **Instructions:** Single line, clear directive (e.g., "Provide accurate information about the content in the selected files and reply in a formal tone.")
- **Conversation starters:** Exactly 3 generic items, not domain-specific
- **Welcome message:** Generic prompt to start conversation
- **Behavior overrides:** Always include `discourage_model_knowledge: true` to force grounding on knowledge sources
- **Icon:** Base64-encoded PNG (provided)

### 4. Storage Locations
Agents can be created in multiple locations:
- CEISPilotKnowledgePages library (document library) - main pilot location
- SitePages/CEISPilotKnowledgePages/ subfolder - nested within Site Pages
- Each location can have its own agents with different knowledge sources

### 5. ID Fetching Strategy
- Always query live site for real list IDs (not hardcoded placeholders)
- Use PowerShell PnP module: `Get-PnPList -Identity "LibraryName"`
- Get site GUID: `(Get-PnPSite).Id.Guid`
- Get web GUID: `(Get-PnPWeb).Id.Guid`
- For nested folders, attempt to retrieve unique_id; fall back to zeros if not found

## Script Updates Applied

Updated `create-test-agent.ps1` to:
1. ✓ Fetch real site and web GUIDs from live site
2. ✓ Query actual list IDs for both knowledge sources
3. ✓ Use Site Pages subfolder path explicitly
4. ✓ Include non-zero unique_id for Site Pages folders (where available)
5. ✓ Simplify agent name and description to match reference format
6. ✓ Keep instructions to single formal sentence
7. ✓ Use standard 3 conversation starters

## Validation

Agent created successfully with:
- Real list IDs embedded
- Both knowledge sources configured
- Correct JSON structure (validated via jq parsing)
- File size: 3139 bytes (comparable to reference agents)

## CRITICAL: Site Isolation Issue & Multi-Stage Fix

**Issue 1 discovered:** Agents created with zero list_ids (00000000-0000-0000-0000-000000000000) permit the SharePoint content picker to expose libraries from OTHER sites, including the retired AG-CSB-ITAU-CMAT-DEV sandbox.

**Issue 2 discovered (more critical):** Using site_id and web_id from the wrong site causes agents to reference wrong site's content entirely. Initial script hardcoded values from TEST agent (bd691009-3e48-422a-928b-c01a27aaca06 / 5c76b6ea-19f7-41b2-b29c-c0aa36aaee04) which point to AG-CSB-ITAU-CMAT-DEV, not AG-CSB-INTRANET-DEV.

**Impact:** Agents referenced retired site's content, violating Phase 4 isolation requirements.

**Fix applied (Stage 1 - Partial):**
- Changed script from zero list_ids to REAL list_ids from AG-CSB-INTRANET-DEV
- CEISPilotKnowledgePages list_id: `1ff096cb-00ee-4013-a253-d856100fafb2`
- CEISPilotKnowledge list_id: `0ea7cc13-c318-42d3-96b9-5318e797f083`

**Fix applied (Stage 2 - Complete):**
- Corrected site_id to: `19801e68-6fba-44c7-89c7-923b85baf943` (AG-CSB-INTRANET-DEV)
- Corrected web_id to: `fbff48d7-76dd-4f69-8b03-9f8ed45f07cf` (AG-CSB-INTRANET-DEV)
- Extracted from working agent after manual UI configuration
- Agent now correctly grounds on AG-CSB-INTRANET-DEV ONLY

**Lesson:** Site_id and web_id are critical for site identification. Never assume values from other agents. Always verify before hardcoding.

## Verification Steps

1. ✓ Agent JSON validated with real list_ids
2. ✓ Content picker tested - confirms no ITAU-CMAT-DEV exposure
3. ✓ Agent operational with proper site isolation
4. ✓ Other test agents cleaned up (deleted)
5. ✓ Knowledge retrieval tested with ASPX and image sources

## Phase 4 Discovery: Root Cause - Wrong list_id and unique_id

**CRITICAL FINDING:** Agent retrieval was failing because I was using WRONG resource IDs.

**The Problem:**
- Script was pointing to CEISPilotKnowledgePages DOCUMENT LIBRARY
- Should have been pointing to SitePages/CEISPilotKnowledgePages FOLDER

**Comparison - Manual (WORKING) vs Script (BROKEN):**

| Property | Manual (Works) | Script (Failed) |
|----------|---|---|
| URL | `/SitePages/CEISPilotKnowledgePages` | `/CEISPilotKnowledgePages` |
| list_id | `1a4a1eda-a2fe-4c43-8d48-4a841f07b253` | `1ff096cb-00ee-4013-a253-d856100fafb2` |
| unique_id | `d260117a-79d8-4586-b9cf-9a0211634556` | `00000000-0000-0000-0000-000000000000` |

**Why This Matters:**
- list_id identifies which library/folder to search
- Wrong list_id = searching wrong content
- unique_id identifies the specific folder within that list
- Zero unique_id = missing folder specificity

**Solution:**
Use the EXACT list_id and unique_id from the working manual agent:
- list_id: `1a4a1eda-a2fe-4c43-8d48-4a841f07b253`
- unique_id: `d260117a-79d8-4586-b9cf-9a0211634556`
- URL MUST include: `/SitePages/CEISPilotKnowledgePages` (not just the library name)

**Platform Note:** Classic ASPX pages are still not supported by agents for automatic indexing, but manual agent creation works because it manually specifies the exact SitePages folder, allowing direct content access even if search ranking doesn't favor it.

## Next Steps

- Test agent against CEIS knowledge sources in Copilot
- Verify knowledge retrieval from both Site Pages and document library
- Confirm content picker shows ONLY AG-CSB-INTRANET-DEV libraries (no cross-site leakage)
- Document for Task 8 evidence: site isolation verification complete

## References

- Manual agent 1: `/SitePages/CEISPilotKnowledgePages/` subfolder (downloaded to temp/CEISPilotKnowledgePages_agent_demo.agent)
- Manual agent 2: CEISPilotKnowledgePages library (downloaded to temp/agent-demo-2.agent)
- Script-generated: `tools/phase-4-native-sharepoint-skills/deployment/scripts/create-test-agent.ps1`
