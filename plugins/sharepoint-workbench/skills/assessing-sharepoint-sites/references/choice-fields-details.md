# Choice fields: unknown vs. empty, scripts and provenance

## Contents

- [Unknown is not empty](#unknown-is-not-empty)
- [Group filter is opt-in](#group-filter-is-opt-in)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Unknown is not empty

- A field with an empty choice list has genuinely no options defined.
- A field with no `Choices` property at all is `UNKNOWN`: the export did not carry the information.

These are reported differently and never conflated. `to_overrides_mapping` omits unknown option sets
rather than emitting an empty list for them, so a downstream consumer cannot mistake "we don't know"
for "there are none". Both the plain array form and the OData `{"results": [...]}` envelope are
supported, since SharePoint exports vary.

## Group filter is opt-in

Filtering by field group is an explicit caller parameter with no default. Nothing is silently excluded
from the inventory.

## Scripts

- `scripts/choice_fields.py`: `inventory_choice_fields`, `to_overrides_mapping`, `ChoiceField`,
  `ChoiceFieldInventory`.
- `scripts/schema_export.py`: export loading and the shared status vocabulary.

## Provenance

Adapted from `sp-extracting-choices` in the originating SharePoint migration repository. Source
repository only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
