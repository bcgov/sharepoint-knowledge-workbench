# Content type provisioning details

## Contents

- [Reconcile, not recreate](#reconcile-not-recreate)
- [Usage](#usage)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Reconcile, not recreate

The skill plans how a declared content type should be reconciled against current live state: create it if missing, link declared fields, hide or show them per the schema, unlink fields no longer declared, and attach the
content type to target lists. Every function only computes a plan from caller-supplied inputs; nothing it returns has been executed.

- An existing content type is left alone except for the drift the schema calls out.
- A field-link's hidden flag is compared against the schema; a mismatch is reported as drift in the action's `detail` (`"... (drift: was ...)"`), not silently corrected.
- Fields in `ContentTypeDef.unlink_fields` are unlinked only if currently linked: never a no-op mistaken for success, never an error on an already-absent link.

## Usage

```python
from content_type_provisioning import ContentTypeDef, ContentTypeFieldSpec, ContentTypeState, plan_content_type

ct = ContentTypeDef(
    name='Demo_Item',
    parent='Item',
    fields=(ContentTypeFieldSpec(field_name='Widget_Count', hidden=False),),
    unlink_fields=('Deprecated_Field',),
)
current = ContentTypeState(name='Demo_Item', exists=True, field_links={'Deprecated_Field': False})
for action in plan_content_type(ct, current):
    print(action.step, action.already_correct, action.detail)
```

`plan_add_content_type_to_list('Demo_List', 'Demo_Item', ('Demo_Item',))` plans attaching a content type to a list.

## Scripts

`scripts/content_type_provisioning.py`: `ContentTypeDef`, `ContentTypeFieldSpec`, `ContentTypeState`, `ContentTypeAction`, `plan_content_type`, `plan_add_content_type_to_list`.

## Provenance

Adapted from `content-type-lib.ps1`'s six functions (`New-SiteContentTypeSafe`, `Add-FieldToContentTypeSafe`, `Hide-FieldOnContentTypeSafe`, `Show-FieldOnContentTypeSafe`, `Unlink-FieldFromContentTypeSafe`,
`Add-ContentTypeToListSafe`) in the originating SharePoint migration repository. The source performed live PnP writes inline; this module only plans. Real execution goes through `sharepoint-provision-list`'s
`apply_provisioning` with an injected executor. Source repository only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
