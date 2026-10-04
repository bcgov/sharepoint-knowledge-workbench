# Document content link remediation details

## Contents

- [Why this exists](#why-this-exists)
- [No python-docx, openpyxl or python-pptx](#no-python-docx-openpyxl-or-python-pptx)
- [PDF needs an injected handler](#pdf-needs-an-injected-handler)
- [Usage](#usage)
- [Real executor and design seam](#real-executor-and-design-seam)
- [Provenance](#provenance)

## Why this exists

A page can be fully migrated to modern SPO yet link out to a Word, Excel or PowerPoint document (or a PDF) whose own embedded hyperlinks still
point at the old classic site. `sharepoint-update-page-links` only rewrites URLs in page and HTML body content; it never opens Office or PDF files.

## No python-docx, openpyxl or python-pptx

docx, xlsx and pptx are ZIP archives of XML parts (Office Open XML). Rewriting a URL means finding the right XML or `.rels` part and doing a text
substitution. This module does that with the standard library's `zipfile`, reusing the `RewriteRuleset` text substitution `update-page-links` uses.
No third-party dependency is needed for these three formats.

## PDF needs an injected handler

PDF hyperlink rewriting needs a real PDF parser (for example `pymupdf`), which this module does not ship. A PDF is reported `Outcome.NOT_SUPPORTED`
unless the caller passes `pdf_handler(content: bytes, ruleset) -> (bytes, applied_rules)`. That is honest non-coverage, never a silent no-op
mistaken for success, and never a text substitution of a binary PDF stream (which would corrupt it).

## Usage

```python
from link_rules import load_ruleset
from document_link_remediation import plan_document_link_remediation, apply_document_link_remediation

plan = plan_document_link_remediation(documents, load_ruleset("rules.json"))
print(plan.outcome, plan.change_count)
result = apply_document_link_remediation(plan, executor=my_executor, dry_run=False, confirm=plan.confirmation_token)
```

## Real executor and design seam

`scripts/link-remediation/spo-remediate-document-content-links.ps1` checks out the target file (`Set-PnPFileCheckedOut`), uploads the new content (`Add-PnPFile`), and
checks it back in (`Set-PnPFileCheckedIn -CheckinType MajorCheckIn`).

```bash
pwsh -File scripts/link-remediation/spo-remediate-document-content-links.ps1 -PlanPath plan.json -TargetLibrary "Shared Documents" -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken REMEDIATE-SPO-DOCUMENT-LINKS
```

The OOXML zipfile and XML-part rewrite is Python-only logic that PowerShell does not reimplement. The plan JSON must be augmented, on each changed
document, with `remediated_content_path` (an absolute local path to the already-rewritten file bytes, written by the Python caller). See the script's
comment-based help.

## Provenance

Generalized from a source-repository design proposal (`document-link-repair-python-solution.md`, which proposed python-docx, openpyxl, python-pptx and
pymupdf) identified in the Phase 9 exhaustive source audit (`temp/phase9-source-audit/file-tracking.json`) as a real, distinct capability gap.
Onboarded is the approach (rewrite embedded document hyperlinks, distinct from page-body links), not a code port; the implementation uses a
dependency-free ZIP/XML approach for Office formats. Source repository only.
