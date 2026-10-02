# Path resolution design rationale

## Contents

- [Seam this closes](#seam-this-closes)
- [Why print, not execute](#why-print-not-execute)
- [Why plugins do not read config themselves](#why-plugins-do-not-read-config-themselves)
- [Export path convention](#export-path-convention)
- [What this does not do](#what-this-does-not-do)

Design provenance (source repository only; not needed at runtime):
`docs/architecture/sharepoint-engineering-plugin-set.md` and
`docs/superpowers/specs/2026-08-07-sharepoint-collection-and-orchestration-design.md` (Part B).

## Seam this closes

The four Phase 9 SharePoint analysis plugins (`sharepoint-discovery`, `sharepoint-schema`,
`sharepoint-link-remediation`, `sharepoint-page-modernization`) take explicit paths as
parameters and read none of `workbench-setup`'s config. This is deliberate: each stays
independently installable (plugin-architecture-policy §1.3, verified by
`isolated_install_check.py`). Nothing before this skill resolved `workbench-setup`'s config
into the concrete paths those plugins need.

The skill is that resolution layer, and only that: it reads a `DocumentId` plus
already-parsed connection, workflow-profile and publication-profile dicts, resolves them
into the export paths each downstream skill documents as its inputs, checks each against
the real filesystem, and prints the resolved invocations. It never launches a subprocess,
never imports a downstream plugin module, and never executes anything on the user's behalf.

## Why print, not execute

Per the design spec: "Print-don't-execute keeps the layer inspectable, keeps
`workbench-setup` free of any dependency on the four plugins (preserving its standalone
installability), and makes the resolution logic testable without running anything."

Adding real execution would either (a) require `workbench-setup` to import or shell out to
four plugins it has no dependency on today, breaking §1.3, or (b) turn this skill into an
orchestration or workflow engine making conditional execution decisions. Both are out of
scope (see the spec's "What this deliberately does NOT do"). A human or agent reads the
printed invocations and runs the ones they choose, using each downstream plugin's own
documented interface.

## Why plugins do not read config themselves

Resolution flows downward only: this layer reads config and emits explicit paths and
arguments to plugin invocations. It never makes a downstream plugin reach up into
`workbench-setup`'s config. That would create a shared-config coupling across all five
plugins and defeat the point of each installing and running standalone.

## Export path convention

Nothing before this skill defined where collected SharePoint exports live on disk. Part A
(`sharepoint-collection`, the plugin that would produce them) is design-only and not
authorized to build. Until a human produces exports by hand or Part A exists, the skill
resolves against the minimal convention implied by the design spec:

```text
<workbench_root>/sharepoint-exports/<DocumentId>/<skill-export-subdir>/<filename>
```

`<skill-export-subdir>` and `<filename>` per entry are fixed data in
`path_resolution.DOWNSTREAM_INVOCATIONS`, taken from each downstream skill's own `SKILL.md`
"Usage" section, not invented per call. An absent file is reported `UNAVAILABLE`, never
fabricated as if present.

## What this does not do

- Does not execute, subprocess, or import any of the four downstream plugins.
- Does not make any plugin depend on `workbench-setup`, or read shared config itself.
- Does not branch on profile contents beyond the `DocumentId` identity check: no
  conditional orchestration, no execution ordering, no state machine. If a future need
  requires that, this design has been outgrown; see the design spec's own note.
- Does not implement Part A (`sharepoint-collection`), which remains `DESIGN_ONLY` and
  `REQUIRES_HUMAN_DECISION`.
