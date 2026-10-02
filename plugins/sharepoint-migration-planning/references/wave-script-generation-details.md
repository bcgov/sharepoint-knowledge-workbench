# Wave script generation details

## Contents

- [Public interface](#public-interface)
- [What this skill never does](#what-this-skill-never-does)
- [Real executors](#real-executors)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Public interface

```python
from wave_script_generation import generate_wave_scripts

result = generate_wave_scripts(dependency_matrix_dict)
# result.outcome: Outcome.OBSERVED | Outcome.EMPTY | Outcome.FAILED
# result.scripts: one GeneratedWaveScript per wave (wave_number, object_names, source, filename) in matrix wave order
# result.guide: a single Markdown wave guide covering every wave as a discrete test -> deploy -> retest step
```

This is templating, not full schema synthesis. Each generated script's `ProvisioningSchema` / `build_schema()` body is an honest `NotImplementedError` TODO: the matrix
carries only `name`, `objectType` and `dependsOn`, not field-level schema, so full schema synthesis is not mechanically derivable and is never fabricated. Every generated
script's comment block names the wave's real objects taken directly from the matrix.

## What this skill never does

- Never generates a script from a matrix whose `outcome` is `Outcome.FAILED` (a blocked or invalid graph); it refuses and reports `Outcome.FAILED` with an explanatory issue.
- Never emits a single script that deploys every wave unattended; the wave guide presents each wave as its own gated step, per `test-driven-wave-deployment.md`.
- Never opens a new tenant-write path: each generated script's `main()` requires an explicitly injected executor and confirmation token, matching
  `sharepoint-provisioning`'s three-gate write safety. This skill never executes a generated script.
- Never copies content from `wave-script-template.example.py` or `wave-guide-template.md` verbatim; they are style and shape references only, and every real value in
  generated output comes from the matrix.

## Real executors

A generated wave script's `main()` still needs an injected executor and confirmation token, but the executor no longer has to be hand-written. Real, gated PowerShell
executors exist for the writes the planning modules compute. Each is dry-run by default and needs `-Execute` plus its exact `-ConfirmToken`; each script's own comment-based
help documents its plan JSON shape and any augmentation needed beyond the Python module's `to_dict()`.

| Script | Lives in | Consumes a plan matching | Confirm token |
|---|---|---|---|
| `spo-provision-site-columns.ps1` | `sharepoint-provisioning` | `field_provisioning.py`'s `FieldAction` list | `PROVISION-SPO-SITE-COLUMNS` |
| `spo-provision-content-types.ps1` | `sharepoint-provisioning` | `content_type_provisioning.py`'s `ContentTypeAction` list | `PROVISION-SPO-CONTENT-TYPES` |
| `spo-provision-list.ps1` | `sharepoint-provisioning` | `list_provisioning.py`'s `ProvisioningPlan` | `PROVISION-SPO-LIST` |
| `spo-provision-calendar.ps1` | this plugin | `calendar_provisioning.py`'s `CalendarProvisioningPlan` | `PROVISION-SPO-CALENDAR` |

Only `spo-provision-calendar.ps1` is a script of this plugin (with the shared `Get-WorkbenchConnectionConfig.ps1`). The other three belong to the `sharepoint-provisioning` plugin; invoke
that plugin's skills (`sharepoint-create-site-column`, `sharepoint-create-content-type`, `sharepoint-create-list`) for them rather than importing or copying their scripts. The plugin README
still lists all four as local; that is out of date. `generate_wave_scripts` has not been changed to reference these executors automatically; that remains undone follow-up if a generated
wave script should call them directly instead of leaving a `build_schema()` TODO. When running an executor from an installed copy, pass `-ConfigPath` (its default resolves to the repository
root only from the plugin's own `scripts/`).

## Scripts

- `scripts/wave_script_generation.py`: `generate_wave_scripts`, `GeneratedWaveScript`, `WaveGenerationResult`.
- `scripts/provisioning_outcomes.py`: the shared `Outcome` vocabulary.
- `scripts/spo-provision-calendar.ps1` and `scripts/Get-WorkbenchConnectionConfig.ps1`: the local executor and the shared config reader.

## Provenance

New design work, generalizing the shape of hand-written wave scripts observed in a separate SharePoint migration repository (for example `wave1-zero-deps.ps1`). Those were written
by hand, one at a time; this automates that authoring step and does not port their content.
