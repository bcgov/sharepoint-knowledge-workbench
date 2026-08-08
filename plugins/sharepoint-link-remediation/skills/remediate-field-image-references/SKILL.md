---
name: remediate-field-image-references
plugin: sharepoint-link-remediation
description: Inventory-verified remediation of an embedded <img> reference inside a rich-text list field -- classifies each item against a real document-library inventory (matched / missing / broken-placeholder-no-src / no-image) and proposes a rewrite ONLY for confirmed-matched items, never a blind regex guess. Distinct from remediate-links (page-body content) and remediate-document-content-links (Office/PDF files). DRY-RUN BY DEFAULT -- applying changes requires BOTH an explicitly injected executor AND a confirmation token from the plan.
allowed-tools: Bash, Read
examples:
  - "python -c \"from field_image_remediation import plan_field_image_remediation; print(plan_field_image_remediation(items, inventory=inventory, ruleset=ruleset).to_dict())\""
---

# Remediate Field Image References

## Trigger and Purpose

Use this skill when a rich-text list field (e.g. a "Picture or Description"
column) embeds an `<img>` reference to a file that moved libraries during
migration — the field's stored HTML still points at the old library path,
so the image no longer renders even though the file itself migrated
successfully.

## Why this is inventory-verified, not a blind rewrite

`remediate-links` and `remediate-document-content-links` both apply a
rewrite rule to every match they find, on the assumption that the target
of the rewrite genuinely exists post-migration. That assumption does not
hold here: not every file referenced by an old field value necessarily
migrated. Rewriting blindly would "fix" a reference to a file that was
never migrated, silently hiding a real data-loss problem behind an
apparently successful rewrite.

Instead, `classify_field_images` cross-references each item's referenced
filename against a real library inventory BEFORE any rewrite is proposed:

| Status | Meaning | Gets a proposed fix? |
|---|---|---|
| `no_img_tag` | Field has no `<img>` tag at all (blank or plain text) | No |
| `img_no_src` | An `<img>` tag with no `src` (empty broken-image placeholder) | No — no path to fix |
| `matched` | Referenced filename exists in the inventory | Yes — rewrite the path segment |
| `missing` | Referenced filename does not exist anywhere in the inventory | No — genuinely absent, report it |

Every item is classified and reported, even ones with no proposed fix —
`missing` and `img_no_src` items are never silently dropped from the
record just because there is nothing to write for them.

## Write safety — same three-gate contract as every write-capable module here

1. **Dry-run is the default.** `apply_field_image_remediation(plan)` with
   no further arguments changes nothing.
2. **An executor must be injected.** Without an
   `executor(source_id, new_field_value)` callable, a real apply raises
   `ExecutorRequired`.
3. **A confirmation token is required.** `dry_run=False` additionally
   requires `confirm=plan.confirmation_token`.

## Usage

```python
from link_rules import load_ruleset
from field_image_remediation import plan_field_image_remediation, apply_field_image_remediation

# items: {source_id: field_value_html}, inventory: {filename.lower(): relative_url}
plan = plan_field_image_remediation(items, inventory=inventory, ruleset=load_ruleset("rules.json"))
print(plan.outcome, plan.change_count)
for source_id, classification in plan.classifications.items():
    if classification.status == "missing":
        print(f"genuinely missing: {source_id} -> {classification.extracted_filename}")

result = apply_field_image_remediation(
    plan, executor=my_executor, dry_run=False, confirm=plan.confirmation_token
)
```

## Scripts

- `scripts/field_image_remediation.py` -- `classify_field_images`, `plan_field_image_remediation`, `apply_field_image_remediation`, `ExecutorRequired`, `ConfirmationRequired`
- `scripts/link_rules.py`, `scripts/link_outcomes.py` -- shared with `remediate-links`

## Provenance

Generalized from a source-repository diagnostic script
(`analyze-persons-images-gap.py`) that cross-referenced a Persons list's
embedded picture field against a live document-library inventory to
diagnose a specific production rendering issue. Identified during the
Phase 9 exhaustive source audit (`temp/phase9-source-audit/file-tracking.json`)
as a genuinely distinct, valuable mechanism initially under-scoped in that
audit (flagged as a noted pattern, not promoted to the onboarding plan) —
corrected after direct user confirmation that the pattern was used and
valuable. The source script's hardcoded library-segment strings
(`/PublishingImages/` -> `/Images1/`) and CSV file I/O were replaced by an
injected `RewriteRuleset` (reusing `remediate-links`' existing rules-as-data
model) and pure in-memory dicts; the classification logic itself
(extract `<img src>`, decode URL-encoding, case-insensitive filename
lookup, four-way status classification) is a faithful generalization.
