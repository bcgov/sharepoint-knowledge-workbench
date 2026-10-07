# Acceptance Criteria: workbench-initialize-document-workflow

- Skill slug: `workbench-initialize-document-workflow`.
- Target plugin: `sharepoint-workbench-setup`.
- Purpose: "Interactive intake wizard that records a source document's identity, processing stages, output formats (only implemented renderer profiles are executable choices), publication locations, agent-grounding representations and governance settings, then writes document-workflows/{DocumentId}.workflow.psd1 and publication-profiles/{DocumentId}.publication.psd1. Use when setting up a new document or revision for conversion or publication. Ask, propose defaults, validate, display, write, stop; never extracts, renders, or connects to SharePoint."

## Constraints honored

- Execution boundary for this version: Must **not**: extract documents; confirm topic boundaries; render content; connect to or modify SharePoint; upload files; create pages; create agents; deploy native skills. Each stays a separate, explicitly invoked domain-plugin capability. Offer only implemented renderer profiles (`multipage-markdown`, `sharepoint-aspx`) as executable choices. Record anything else in `UnsupportedRequests`. Run from this skill's root: the helpers are `scripts/document_workflow.py` and `scripts/psd1_writer.py`. Standard library only; no other plugin is required.

## Verification passes

- Confirm both files exist at `document-workflows/<id>.workflow.psd1` and `publication-profiles/<id>.publication.psd1`, and that every requested renderer outside the allowlist appears under `UnsupportedRequests`. Confirm no extraction, rendering or SharePoint call was made.
- Focused plugin tests for this skill pass.
