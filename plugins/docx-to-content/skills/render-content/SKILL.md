---
name: render-content
plugin: docx-to-content
description: Render a validated canonical content package to a named output profile through a validated renderer contract.
allowed-tools: Bash, Read, Write
examples:
  - "python -m scripts.cli render --canonical runs/Manual/canonical-content --renderer multipage-markdown --output runs/Manual/render"
---

# Render Content

## Trigger and Purpose

Use this skill after `convert-document` has produced a promoted canonical
content package. It renders that package through a named, registered
renderer (currently only `multipage-markdown`) into published output,
running renderer-specific validation before promoting the rendered result.

`cmd_render` in `scripts/cli.py` is fully wired: it resolves `--renderer`
through the Task 12 renderer registry, loads the canonical package via
`CanonicalPackage.load()` (full schema/integrity/disposition
revalidation), and calls `renderers/validate_rendered.py`'s
`render_and_promote()` (which itself drives
`renderers/multipage_markdown.py`'s `render_to_staging`). The behavior
below is the actual, tested contract of the `render` subcommand.

## Exact CLI Invocation

```bash
python -m scripts.cli render --canonical <canonical-dir> --renderer multipage-markdown --output <render-dir>
```

- `--canonical` — path to the canonical content directory (must exist).
- `--renderer` — renderer name; currently only `multipage-markdown` is
  supported (any other name is a usage error, exit code `4`).
- `--output` — directory to write rendered output to.

## Inputs and Output Artifacts

- **Input**: a canonical content package ONLY — a loaded
  `CanonicalPackage` (via `package.py`'s loader). The renderer protocol's
  `render(self, package, output_dir)` signature has no parameter through
  which a source `.docx`, an analysis directory, or a `ConversionPlan`
  could be passed; a renderer can only ever see what was already vetted
  into the canonical package.
- **Output**: `<render-dir>/` containing the rendered pages (an `index`
  page plus one page per chunk for `multipage-markdown`), a
  `render-result.json`, and a rendered-output `validation.json`.

## Preconditions

- `--canonical` must point at an existing directory.
- `--renderer` must name a renderer registered in the renderer registry
  (`renderers/protocol.py`'s `RendererRegistry`) — as of this task the
  registry contains only `multipage_markdown`.
- The canonical package's manifest `schema_version` must be one the chosen
  renderer declares support for (`supported_manifest_versions`); an
  unsupported version is rejected rather than silently rendered.

## PASS/WARN/FAIL and Exit-Code Behavior

- **PASS** (exit code `0`): rendered output built, validated, and promoted.
- **FAIL** (exit code `2`): rendered-output validation failed (e.g. broken
  index links, incomplete pages, manifest hash mismatch, lost
  traceability) — rendered output is retained in staging for diagnosis but
  not promoted.
- Dependency/precondition failure (canonical directory not found): exit
  code `3`.
- Usage error (unsupported renderer name, unsupported manifest schema
  version): exit code `4`.

## Prohibited Shortcuts

- Must not pass raw analysis output or a `.docx` source directly to a
  renderer — only a promoted canonical content package is a valid input.
- Must not promote rendered output to its final location when
  rendered-output validation reports FAIL.
- Must not register or invoke a renderer name that isn't in the renderer
  registry, and must not hand-wire a bespoke render call that skips
  `render_and_promote`'s validation step.

## Handoff to the Next Skill

Rendering is the terminal step of the Phase 1 pipeline — there is no
further skill to hand off to. The promoted rendered output under
`<render-dir>` is the published artifact.
