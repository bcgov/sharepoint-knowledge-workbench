# Mode: Static ASPX File Migration & Publication

Feature-parity implementation for migrating static SharePoint document-library ASPX files into reviewed HTML in SharePoint Online document libraries.

## Overview

Use when migrating static HTML-like `.aspx` files stored in document libraries (not modern `SitePages`). Converts the document to clean, modern HTML with inline CSS design tokens and uploads it to the target SPO library folder.

## Constraints

- **Classify Before Conversion**: Verify the source file is indeed a static document-library ASPX file and not a dynamic page with editable Web Parts.
- **Preserve Source File**: Never modify the source file or upload raw `.aspx`.
- **Inline Styling**: Inline standard design tokens CSS directly into the HTML so SharePoint library document preview renders correctly.
- **Link Rewriting**: Rewrite source links using `scripts/rewrite_page_links.py`. Unresolved links must be flagged for human review.
- **Explicit Overwrite**: Never overwrite an existing destination file without explicit confirmation (`Reject`, `Approve`, or `Skip`).

## Workflow

1. **Verify Static Nature**:
   Confirm file has no webpart definitions or dynamic server tags.
2. **Convert to HTML with Design System Styling**:
   Extract body, flatten layout tables, retain text, lists, and links. Substitute header, breadcrumb, and standard footer.
3. **Validate Converted Page**:
   ```bash
   python3 scripts/validate_design_system_page.py temp/page.html --source temp/page.aspx
   ```
4. **Rewrite Links**:
   ```bash
   python3 scripts/rewrite_page_links.py --page temp/page.html --ledger-map temp/library-map.csv
   ```
5. **Dry-Run Upload**:
   ```powershell
   pwsh -File scripts/spo-upload-file.ps1 -ConfigPath <target-config.psd1> -SourceFilePath temp/page.html -TargetLibrary <TargetLibrary> -TargetFolder <Folder>
   ```
6. **Execute Upload (Human Gate)**:
   Add `-Execute -ConfirmToken UPLOAD-STATIC-PAGE` to commit the file upload.
7. **Verify**: Open the target library in SharePoint and verify file rendering and link navigation.
