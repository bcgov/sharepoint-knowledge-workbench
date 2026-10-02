# Field provisioning details

## Contents

- [The calculated-column workaround](#the-calculated-column-workaround)
- [Deployable-field filtering](#deployable-field-filtering)
- [Usage](#usage)
- [Scripts](#scripts)
- [Provenance](#provenance)

## The calculated-column workaround

Typed field-creation APIs generally accept a type but no formula parameter, so a Calculated column has to be created through raw Field XML. `build_calculated_field_xml` builds that XML, escaping every caller-supplied
string: attribute values (display name, static name, group) with the full XML attribute-escaping set (`&` `<` `>` `"` `'`), and the formula body (element text) with the text-escaping subset (`&` `<` `>`). A call with a
non-Calculated `FieldDef` or a missing formula raises `FieldDefinitionError` rather than emitting malformed or misleading XML. `build_lookup_field_xml` and `build_user_field_xml` cover Lookup/LookupMulti and
User/UserMulti the same way.

## Deployable-field filtering

`filter_deployable_fields` keeps a field only if it belongs to the `"Custom Columns"` group, is not a skip-listed system or computed type (Counter, Computed, Calculated, workflow, event and taxonomy internals, and so on), is
not `Title`, is not explicitly excluded, and is either force-included or both visible and writable. Nothing is deployed silently by default: hidden and read-only fields are excluded unless the caller opts them in by name.

## Usage

```python
from field_provisioning import FieldDef, plan_field_action

fd = FieldDef(internal_name='Widget_Count', display_name='Widget Count', type='Number')
print(plan_field_action(fd, existing_type=None))       # -> create
print(plan_field_action(fd, existing_type='Number'))    # -> exists
print(plan_field_action(fd, existing_type='Text'))       # -> repair
```

## Scripts

`scripts/field_provisioning.py`: `FieldDef`, `FieldAction`, `filter_deployable_fields`, `field_needs_type_repair`, `build_calculated_field_xml`, `build_lookup_field_xml`, `build_user_field_xml`, `plan_field_action`.

## Provenance

Adapted from `field-helpers.ps1`'s `Get-DeployableFields`, `Repair-FieldType`, `Add-FieldSafe` and `Invoke-FieldsForList` (the declared-schema-driven field-application loop), plus the calculated/lookup/user raw-XML
construction technique from `reset-and-provision-etl-target-schema.ps1`. The source performed live `Add-PnPField` / `Add-PnPFieldFromXml` writes inline; this module only plans and renders XML. Source repository only:
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
