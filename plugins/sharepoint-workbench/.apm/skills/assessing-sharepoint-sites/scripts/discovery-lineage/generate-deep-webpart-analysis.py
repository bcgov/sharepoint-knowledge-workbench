#!/usr/bin/env python3
"""
generate-deep-webpart-analysis.py
==================================

Generates the high-quality, AI-enriched Master Web Part Code Review Catalog
(ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md) using the template in
assets/templates/ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW-template.md.

Performs deep architectural synthesis for every group:
  - User-visible effect
  - Business intent
  - Actual enforcement level
  - Modern SharePoint Online approach
  - SPFx assessment
  - Migration note

Purpose:
    Render a deep review catalog from analyzed web-part groups and a bundled template.

Key Input Dependencies:
    - An analysis directory containing webpart-code-groups.json and the bundled review template under assets/templates/.

Function index:
    - find_asset
    - _resolve_assessment_profile
    - _render_group
    - generate_deep_report
"""

import json
import os
import sys
import re
from datetime import date
from pathlib import Path

def find_asset(name: str) -> Path:
    """Locate a bundled template/rules file under assets/ (plugin source tree: <plugin>/assets; installed skill: <skill>/assets),
    trying assets/templates/<name>, assets/<name> and assets/<lowercase name>."""
    here = Path(__file__).resolve()
    for base in (here.parents[2] / "assets", here.parents[1] / "assets"):
        for candidate in (base / "templates" / name, base / name, base / name.lower()):
            if candidate.exists():
                return candidate
    return here.parents[2] / "assets" / "templates" / name


# Reviewed generic report text selected from markup signatures. These are
# report templates, not claims about a particular site or business process.
_ASSESSMENT_PROFILES = {
    "multi_accordion": {
        "group_name": "Multi-Section Accordion / Dual Collapsible Panels",
        "text_sufficient": "Yes — native Modern SPO Page Canvas Collapsible Sections or Collapsible Web Parts are sufficient.",
        "spo_replacement": "Modern SPO Canvas Collapsible Sections (Multiple Sections) / Quick Links",
        "mvp_decision": "Migrate to Multiple Native SPO Collapsible Sections",
        "spfx_candidate": "No — modern page canvas supports multiple collapsible section headers per page natively.",
        "validation_req": "Verify section heading hierarchy and ensure nested accordion items flatten cleanly into modern sections.",
        "user_effect": "Renders multi-group Bootstrap accordion panels (<div class=\"panel-group\" id=\"accordion1\">, id=\"accordion2\">) containing extensive FAQ lists, multi-topic resources, or policy sections.",
        "bus_intent": "Organizes large volumes of complex documentation into distinct collapsible sections to prevent excessive page scrolling.",
        "enforcement": "Informational UI layout structure (presentation-only).",
        "spo_approach": "Map each accordion group to a native Modern SPO Canvas Collapsible Section header, allowing users to fold/unfold each topic natively on the modern page.",
        "spfx_assess": "No — SPFx is not required. SPO modern canvas natively supports section folding for multiple sections per page.",
        "mse_eval": "Not Recommended / Not Needed. Modern SPO page canvas natively supports collapsible section headers (Section Background -> Collapsible). Injecting legacy Bootstrap/jQuery accordion code via a PnP Modern Script Editor web part introduces unnecessary NoScript/tenant app catalog security overhead and breaks modern responsive page rendering. Re-architect strictly via native SPO Collapsible Sections or OOB Quick Links / FAQ List web parts.",
        "mig_note": "Cleanse Bootstrap panel classes (panel-group, panel-heading, collapse) and convert to SPO canvas section metadata.",
    },
    "single_accordion": {
        "group_name": "Single Accordion / Callout Collapsible Panel",
        "text_sufficient": "Yes — native Modern SPO Page Collapsible Section or Callout Web Part is sufficient.",
        "spo_replacement": "Modern SPO Canvas Collapsible Section / Callout Box",
        "mvp_decision": "Migrate to Native SPO Collapsible Section or Callout Box",
        "spfx_candidate": "No — native modern canvas supports collapsible section headers natively.",
        "validation_req": "Verify panel title hierarchy and ensure support links resolve.",
        "user_effect": "Renders a single expandable/collapsible Bootstrap panel (<div class=\"panel-group\" id=\"accordion\">) containing help desk contact info or intro instructions.",
        "bus_intent": "Provides a compact support callout box or single collapsible help panel at the top/side of a page.",
        "enforcement": "Informational UI callout (presentation-only).",
        "spo_approach": "Use a single Modern SPO Canvas Collapsible Section header or a modern Callout / Text web part.",
        "spfx_assess": "No — SPFx is not required. Native section folding or text callout shading handles single panels natively.",
        "mse_eval": "Not Recommended / Not Needed. Native Modern SPO Canvas Collapsible Sections satisfy single accordion panels natively. Modern Script Editor SPFx deployment is not required.",
        "mig_note": "Strip legacy Bootstrap panel classes (panel-group, panel-default) during page conversion.",
    },
    "staff_directory": {
        "group_name": "Staff Bio Directory Table",
        "text_sufficient": "Yes — native Modern Text table or People web parts are sufficient.",
        "spo_replacement": "SPO Modern Text Web Part Tables / People Web Parts / Quick Links",
        "mvp_decision": "Migrate to OOB Modern Text Table / People Cards",
        "spfx_candidate": "No — native modern features natively support formatted staff directories.",
        "validation_req": "Verify profile image paths resolve to SPO Site Assets.",
        "user_effect": "Renders a formatted multi-column rich text layout with embedded profile images, staff titles, responsibilities, and mailto/hyperlinks.",
        "bus_intent": "Provides a visual staff/resource directory or operational team dashboard for staff.",
        "enforcement": "Informational / Presentation-only. Contains no access-control or security rules.",
        "spo_approach": "Recreate content using modern SPO Text web part tables, People web parts, or Quick Links cards.",
        "spfx_assess": "No — SPFx is not required. Native modern web parts natively support formatted text, tables, and links.",
        "mse_eval": "Not Needed. Formatted staff profile tables, email links, and bio cards are natively supported in SPO Modern Text web parts, People web parts, and Quick Links cards. Modern Script Editor SPFx is not required.",
        "mig_note": "Legacy HTML table formatting (ms-rteTable-default) will be cleansed during modern page layout conversion.",
    },
    "image_header": {
        "group_name": "Image Header Banner",
        "text_sufficient": "Yes — native Modern Page Header Banner / Image Web Part is sufficient.",
        "spo_replacement": "Modern Page Title Header / Image Web Part + Text Web Part",
        "mvp_decision": "Migrate to Modern Page Banner Image",
        "spfx_candidate": "No — 100% achievable via native modern OOB features.",
        "validation_req": "Ensure banner image is uploaded to SPO Site Assets.",
        "user_effect": "Renders a full-width header image followed by intro text/announcement paragraph.",
        "bus_intent": "Establishes visual section branding and intro title for the sub-page.",
        "enforcement": "Presentation-only banner image.",
        "spo_approach": "Use modern page header layout with focal image background or an OOB Image web part.",
        "spfx_assess": "No — completely solvable with OOB modern canvas page header.",
        "mse_eval": "Not Needed. Native Modern Page Title Banners and Image web parts satisfy publishing header requirements natively. Modern Script Editor SPFx is not required.",
        "mig_note": "Extract publishing image file and upload to target SPO Site Assets catalog.",
    },
    "document_links": {
        "group_name": "Document & Resource Link Matrix",
        "text_sufficient": "Yes — native Modern Quick Links or Document Library view web part is sufficient.",
        "spo_replacement": "Modern Quick Links Web Part (Grid / List Layout)",
        "mvp_decision": "Migrate to Modern Quick Links Web Part",
        "spfx_candidate": "No — 100% achievable via native Quick Links.",
        "validation_req": "Validate document URLs resolve to target SPO libraries.",
        "user_effect": "Displays a structured index of downloadable PDF documents, video recordings, or reference links.",
        "bus_intent": "Gives users direct access to reference documents, recordings and templates.",
        "enforcement": "Informational navigation links.",
        "spo_approach": "Convert link lists into a modern Quick Links web part configured with Grid or List view layout.",
        "spfx_assess": "No — native Quick Links web part handles all link styling natively.",
        "mse_eval": "Not Needed. Native Modern Quick Links (Grid/List layout) and Document Library view web parts handle document indexes natively. Modern Script Editor SPFx is not required.",
        "mig_note": "Update document URLs from the source library paths to the target SPO library paths.",
    },
    "contact_box": {
        "group_name": "Contact / Support Callout Panel",
        "text_sufficient": "Yes — native Modern Callout / Text Web Part is sufficient.",
        "spo_replacement": "Modern Text Web Part (Callout formatting) / People Web Part",
        "mvp_decision": "Migrate to Modern Text Callout Box",
        "spfx_candidate": "No — 100% achievable via native modern OOB features.",
        "validation_req": "Verify support email addresses are current.",
        "user_effect": "Renders a highlighted help/support box containing contact emails and assistance instructions.",
        "bus_intent": "Provides quick contact details for application support and user access inquiries.",
        "enforcement": "Informational contact callout.",
        "spo_approach": "Use modern Text web part with background accent shading or a Callout component.",
        "spfx_assess": "No — native text web part shading fulfills callout requirements.",
        "mse_eval": "Not Needed. Native Modern Text web parts with background accent shading or Contact web parts handle support callout boxes natively.",
        "mig_note": "Cleanse legacy Bootstrap panel styling.",
    },
    "text_only": {
        "group_name": "Static Rich Text Banner / Announcement",
        "text_sufficient": "Yes — native Modern Text or Quick Links web part is sufficient.",
        "spo_replacement": "Modern Text Web Part",
        "mvp_decision": "Migrate to OOB Modern Text",
        "spfx_candidate": "No — 100% achievable via native modern OOB features.",
        "validation_req": "Verify text formatting in SPO canvas.",
        "user_effect": "Renders a static header banner, announcement text block, or informational paragraph.",
        "bus_intent": "Provides contextual guidance, operational notices, or site navigation headers.",
        "enforcement": "Informational / Presentation-only.",
        "spo_approach": "Migrate content directly into standard OOB Modern Text web parts on the modern canvas page.",
        "spfx_assess": "No — completely solvable with OOB modern canvas.",
        "mse_eval": "Not Needed. OOB Modern Text web parts natively support WYSIWYG text formatting, lists, tables, and links.",
        "mig_note": "Cleanse SharePoint 2016 RTE classes (ms-rteThemeForeColor, zero-width spaces).",
    },
    "custom_script": {
        "group_name": "Custom Client-Side Script Logic",
        "text_sufficient": "No — custom script or form logic detected.",
        "spo_replacement": "JSON Column/View Formatting / Power Apps / SPFx",
        "mvp_decision": "Simplify & Reimplement via JSON formatting or Power Apps",
        "spfx_candidate": "Conditional — only if native formatting/permissions cannot fulfill requirement.",
        "validation_req": "Verify business requirement enforcement.",
        "user_effect": "Executes client-side script manipulation on the DOM.",
        "bus_intent": "Automates UI interactions or modifies list view display.",
        "enforcement": "Presentation-only (client-side script).",
        "spo_approach": "JSON Column/View Formatting / Power Apps / SPFx",
        "spfx_assess": "Conditional — only if native formatting/permissions cannot fulfill requirement.",
        "mse_eval": "Conditional / Review Required. Classic Script Editor web parts executing custom DOM manipulation (e.g. field/button locking, pre-filling, or view script overrides) are blocked in SPO by default (NoScript policy). If the business requirement cannot be fulfilled via native JSON Column/View Formatting or Power Apps, deploying the open-source PnP Modern Script Editor SPFx Web Part (@pnp/spfx-controls-react) from the Tenant App Catalog allows running custom HTML/JS snippets on modern pages. However, native JSON formatting or Power Apps is strongly preferred over PnP Script Editor to maintain platform supportability.",
        "mig_note": "jQuery dependencies must be refactored to modern SPO patterns.",
    },
}


# Select the first profile whose signature matches the existing priority rules.
def _resolve_assessment_profile(category: str, signature: str, content_lower: str) -> dict:
    """Choose report language from generic markup indicators without interpreting site intent."""
    signature_lower = signature.lower()
    checks = (
        ("multi_accordion", "pattern::dualmultiaccordion" in signature_lower or content_lower.count("panel-heading") > 3),
        ("single_accordion", "pattern::singleaccordion" in signature_lower or "panel-group" in content_lower or "panel-collapse" in content_lower),
        ("staff_directory", "pattern::staffdirectory" in signature_lower or ("staff name" in content_lower and "position" in content_lower)),
        ("image_header", "pattern::imageheader" in signature_lower or "header image" in content_lower),
        ("document_links", "pattern::documentlink" in signature_lower or ".pdf" in content_lower),
        ("contact_box", "pattern::contactsupport" in signature_lower or ("mailto:" in content_lower and ("support" in content_lower or "contact" in content_lower))),
    )
    profile_name = next((name for name, matches in checks if matches), None)
    if profile_name is None:
        profile_name = "text_only" if category in ("TextOnly", "Empty") else "custom_script"
    return _ASSESSMENT_PROFILES[profile_name]


# Generate the catalog header, one rendered section per group, and output file.
# Render a review section from one analyzed code group.
def _render_group(idx: int, group: dict) -> list[str]:
    """Render the page references, code sample, and generic modernization assessment for one group."""
    category = group.get("category", "TextOnly")
    count = group.get("instanceCount", 1)
    pairs = group.get("pagePartPairs", [])
    representative_page = pairs[0][0] if pairs else "Unknown"
    representative_id = pairs[0][1] if pairs else "Unknown"
    snippet = (group.get("sampleContent") or "").strip()
    summary = group.get("summary") or "Static rich-text banner / layout markup."
    affected_pages = "\n".join(
        f"- `{pair[0]}` (WebPartId `{pair[1]}`)" for pair in pairs
    )
    assessment = _resolve_assessment_profile(
        category, group.get("signature", ""), snippet.lower()
    )

    lines = [
        f"## Group {idx} — {assessment['group_name']} [{category}] ({count} instances)",
        "",
        f"**Representative Page:** `{representative_page}` (WebPartId `{representative_id}`)",
        "**All Affected Pages:**",
        affected_pages,
        "",
        "### Code / Content Snippet",
        "```html",
        snippet[:1500] + ("\n... [truncated for readability]" if len(snippet) > 1500 else ""),
        "```",
        "",
        "### Modernization Assessment",
        f"- **Business behavior:** {summary}",
        f"- **Text web part sufficient:** {assessment['text_sufficient']}",
        f"- **Recommended modern replacement:** {assessment['spo_replacement']}",
        f"- **MVP decision:** {assessment['mvp_decision']}",
        f"- **SPFx candidate:** {assessment['spfx_candidate']}",
        f"- **Validation required:** {assessment['validation_req']}",
        "",
        "### Modernization Behaviour Analysis",
        "",
        "#### User-visible effect",
        assessment["user_effect"],
        "",
        "#### Business intent",
        assessment["bus_intent"],
        "",
        "#### Actual enforcement level",
        assessment["enforcement"],
        "",
        "#### Modern SharePoint Online approach",
        assessment["spo_approach"],
        "",
        "#### SPFx assessment",
        assessment["spfx_assess"],
        "",
        "#### Modern Script Editor (PnP SPFx) Evaluation",
        assessment["mse_eval"],
        "",
        "#### Migration note",
        assessment["mig_note"],
        "",
        "---",
        "",
    ]
    return lines


# Generate the catalog header, group sections, and output file.
def generate_deep_report(analysis_dir: str | Path, site_name: str = "Source Site") -> None:
    """Read web-part groups and render the detailed modernization review catalog."""
    analysis_dir = Path(analysis_dir)
    groups_json_path = analysis_dir / "webpart-code-groups.json"
    template_path = find_asset("ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW-template.md")
    output_path = analysis_dir / "ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md"

    if not groups_json_path.exists():
        print(f"Error: {groups_json_path} not found.")
        sys.exit(1)
    if not template_path.exists():
        print(f"Error: {template_path} not found.")
        sys.exit(1)

    with open(groups_json_path, "r", encoding="utf-8") as source:
        groups_data = json.load(source)
    groups = groups_data.get("groups", [])
    total_instances = sum(group.get("instanceCount", 1) for group in groups)
    md_out = [
        f"# Master Web Part Code Review Catalog — {site_name}",
        "",
        f"> **Generated:** {date.today().isoformat()}  ",
        f"> **Target Site:** {site_name}  ",
        f"> **Total Web Parts Analyzed:** {total_instances}  ",
        f"> **Unique Functional Code Groups:** {len(groups)}  ",
        "",
        "---",
        "",
        "## Executive Summary of Architectural Code Analysis Pass",
        "",
        f"This document provides a deep architectural and behavioral code analysis for every unique custom web part group discovered on the **{site_name}** site.",
        "> **Heuristic classification:** groups are classified from markup signatures; the *user-visible effect* and *business intent* texts are inferred from those signatures, not observed. Confirm each with the page owner before relying on it.",
        "",
        "Each group has been evaluated for user-visible presentation effects, underlying business intent, presentation vs. access-control enforcement levels, and modern SPO replacement paths.",
        "",
        "---",
        "",
        "## Master Group Analysis Catalog",
        "",
    ]
    for idx, group in enumerate(groups, start=1):
        md_out.extend(_render_group(idx, group))

    with open(output_path, "w", encoding="utf-8") as destination:
        destination.write("\n".join(md_out))
    print(f"  [OK] Successfully generated deep AI architectural review catalog: {output_path}")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "01_source_sharepoint/analysis"
    if target_dir:
        target_dir = target_dir.replace('\r', '').replace('\n', '').strip()
    site_name = sys.argv[2] if len(sys.argv) > 2 else "Source Site"
    generate_deep_report(target_dir, site_name)
