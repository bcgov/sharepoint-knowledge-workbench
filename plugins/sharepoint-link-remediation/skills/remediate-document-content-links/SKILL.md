---
name: remediate-document-content-links
plugin: sharepoint-link-remediation
description: Rewrites legacy URLs embedded INSIDE Office documents (docx/xlsx/pptx, via stdlib zipfile -- no python-docx/openpyxl/python-pptx dependency) and PDFs (via an optional caller-injected handler) stored in a document library. Distinct from remediate-links, which only rewrites URLs in page/HTML body content. DRY-RUN BY DEFAULT -- applying changes requires BOTH an explicitly injected executor AND a confirmation token from the plan.
allowed-tools: Bash, Read
examples:
  - "python -c \"from document_link_remediation import plan_document_link_remediation; print(plan_document_link_remediation(documents, ruleset).to_dict())\""
---

# Remediate Document Content Links

## Trigger and Purpose

Use this skill when a page has been fully migrated to modern SPO but links
out to a Word, Excel, or PowerPoint document (or a PDF) whose own embedded
hyperlinks still point at the old classic site. `remediate-links` only
rewrites URLs in page/HTML body content -- it never opens or modifies
Office or PDF files. This skill closes that gap.

## Why no python-docx/openpyxl/python-pptx dependency

docx/xlsx/pptx are plain ZIP archives of XML parts (the Office Open XML
format). Rewriting a URL inside one of these files is a matter of finding
the right XML/`.rels` part and doing a text substitution — this module
does that directly with the standard library's `zipfile`, reusing the same
`RewriteRuleset` text-substitution `remediate-links` already uses. No new
third-party dependency is required for these three formats.

## PDF requires an injected handler

PDF hyperlink rewriting genuinely requires a real PDF parser (e.g.
`pymupdf`), which this module does not ship. A PDF document is reported
`Outcome.NOT_SUPPORTED` unless the caller passes a
`pdf_handler(content: bytes, ruleset) -> (bytes, applied_rules)` callable
— honest non-coverage, never a silent no-op mistaken for success, and
never an attempt to text-substitute a binary PDF stream (which would
corrupt it).

## Write safety -- same three-gate contract as `remediate-links`

1. **Dry-run is the default.** `apply_document_link_remediation(plan)`
   with no further arguments changes nothing.
2. **An executor must be injected.** This module ships no tenant
   transport. Without an `executor(source, content: bytes)` callable, a
   real apply raises `ExecutorRequired`.
3. **A confirmation token is required.** `dry_run=False` additionally
   requires `confirm=plan.confirmation_token`, derived from the plan's own
   content.

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `OBSERVED` | At least one document changed, all writes succeeded |
| `EMPTY` | Nothing matched the ruleset in any document |
| `NOT_SUPPORTED` | At least one document was a PDF with no injected `pdf_handler` |
| `PARTIAL` | Some writes succeeded, some failed; both lists populated |
| `FAILED` | Every write failed |

## Usage

```python
from link_rules import load_ruleset
from document_link_remediation import plan_document_link_remediation, apply_document_link_remediation

plan = plan_document_link_remediation(documents, load_ruleset("rules.json"))
print(plan.outcome, plan.change_count)

# Apply only after review, with a real executor and the plan's own confirmation token
result = apply_document_link_remediation(
    plan, executor=my_executor, dry_run=False, confirm=plan.confirmation_token
)
```

## Scripts

- `scripts/document_link_remediation.py` -- `detect_document_format`, `plan_document_link_remediation`, `apply_document_link_remediation`, `ExecutorRequired`, `ConfirmationRequired`
- `scripts/link_rules.py`, `scripts/link_outcomes.py` -- shared with `remediate-links`

## Provenance

Generalized from a source-repository design proposal
(`document-link-repair-python-solution.md`, proposing python-docx/
openpyxl/python-pptx/pymupdf for this exact problem) identified during the
Phase 9 exhaustive source audit
(`temp/phase9-source-audit/file-tracking.json`) as a real, distinct
capability gap -- what was onboarded is the approach (rewrite embedded
document hyperlinks, distinct from page-body links), not a code port; the
actual implementation here uses a dependency-free ZIP/XML approach for
Office formats instead of the proposed third-party libraries, since that
approach fully covers docx/xlsx/pptx without adding a runtime dependency.
