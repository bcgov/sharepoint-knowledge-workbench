# Dependency Matrix — Reference

> **Design scaffold.** Describes the schema in `dependency-matrix-schema.json`, which is itself a
> draft. Update both together if the shape changes during real implementation.

## Fields

- **`objects`** — every deployable object (list, content type, site column, field — the type
  vocabulary is caller-defined, not fixed) discovered in the source site, plus its declared
  dependencies.
- **`name`** — must be unique across the whole matrix.
- **`objectType`** — free text describing what kind of thing this is. No built-in assumption about
  what types exist; a caller migrating a different kind of SharePoint object should be able to use
  a type name this schema has never seen.
- **`dependsOn`** — names of other objects, by name, that must exist before this one can be
  deployed. **Never a wave number.** Referring to "wave 2" instead of "the `Persons` list" is
  exactly the kind of coupling that silently breaks when stages are renumbered or split — see
  `../rules/schema-driven-sharepoint-deployment.md`.
- **`waves`** — the *computed* output: an ordered list of stages, each a list of object names ready
  to deploy once every earlier stage is done. Produced by this plugin's own
  `wave_planning.plan_waves()`, never hand-authored.

## What this deliberately does not carry over from the observed source pattern

The source repository's equivalent file mixed two different kinds of `dependsOn` entry — sometimes
an object name, sometimes a bare wave-number string. That ambiguity is not reproduced here: a
dependency must always name a specific object. See
`plugins/sharepoint-migration-planning/scripts/wave_planning.py`'s module docstring for the full
reasoning.
