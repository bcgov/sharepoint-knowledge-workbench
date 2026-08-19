# External Tool Dependencies

Running log of system-level (non-Python) tools required for this project's document-conversion workflow. These are not covered by `.agent/rules/dependency-management.md` (which governs Python `.in`/`.txt` lockfiles) — install manually per the commands below.

| Tool | Purpose | Install (macOS) | Status |
|---|---|---|---|
| pandoc | Convert .docx to Markdown | `brew install pandoc` | Installed |
| LibreOffice (`soffice`) | Convert legacy image formats (.emf/.doc) to .png/.docx/.pdf | `brew install --cask libreoffice` | Installed — brew links the binary as `soffice`, not `libreoffice` (the `libreoffice`/`libraoffice` shell commands do not exist). Used to convert legacy .emf images to .png during extraction. |
| pdftoppm (Poppler) | Render PDF pages to images for visual verification of generated .docx files | `brew install poppler` | Not yet checked |

## Notes
- After installing LibreOffice, `soffice` should be on PATH automatically via the cask.
- Update this table whenever a new external tool is introduced by a skill or conversion step.
- **2026-07-25:** Removed the Anthropic `docx` skill from this repo. Its unique capabilities (in-place tracked-changes/redlining edits, docx-js precision authoring) aren't needed for this project's content-centric round-trip workflow — pandoc alone covers both docx→markdown and markdown→docx, which is what a new in-house skill (`pandoc-docx-convert`, authored in `agent-plugins-skills/plugins/dev-utils`) is being built to do properly. See `JOURNAL.md` for the full reasoning.
