---
name: generate-sharepoint-wave-scripts
plugin: sharepoint-migration-planning
status: design-scaffold
description: >
  NOT YET IMPLEMENTED. Will read dependency-matrix.json (from
  analyze-sharepoint-dependency-graph) plus this plugin's template assets,
  and synthesize new, site-specific wave deployment scripts and a human
  wave guide -- one script per computed wave, calling into
  sharepoint-provisioning's plan/apply functions. Explicitly agent-assisted,
  not a pure deterministic function: the same dependency graph can be
  expressed as reasonable deployment code many ways.
allowed-tools: Bash, Read, Write
---

# Generate SharePoint Wave Scripts

> **Status: design scaffold, not implemented.**

## Trigger and Purpose (planned)

Stage 3b — the **AI-model-assisted half**. Deliberately not a pure function: turning a dependency
graph into well-structured deployment code and a readable runbook is a synthesis task with more
than one reasonable output, unlike stage 3a's deterministic wave computation.

## Planned behavior

1. Read `dependency-matrix.json` (stage 3a's output).
2. Read `../../assets/wave-script-template.example.py` and
   `../../assets/wave-guide-template.md` as style/shape references — **templates to follow, not
   values to copy**. No project-specific content from either template should ever appear in a
   generated script; every generated script's actual object names/fields come only from the
   dependency matrix.
3. Synthesize one script per computed wave, each calling `sharepoint-provisioning`'s existing
   `list_provisioning`/`content_type_provisioning`/`field_provisioning` plan/apply functions —
   **never a new, parallel write path**. This skill must not introduce any tenant-write capability
   of its own; it only assembles calls into the already three-gate-safe provisioning plugin.
4. Synthesize a wave guide document: the human runbook (test → deploy → retest, one wave at a
   time, stop on first fail) — see `../../rules/test-driven-wave-deployment.md` for why this
   sequencing discipline is treated as this repo's TDD rule applied to infrastructure, not a
   separate convention.

## Explicit non-goal

This skill never executes a generated script itself. It produces scripts and a guide for a human
to run, wave by wave, through the existing three-gate-safe `sharepoint-provisioning` plugin.

## Provenance

New design work, generalizing the *shape* of hand-written wave scripts observed in a separate
SharePoint migration repository (e.g. `wave1-zero-deps.ps1`) — those were written by hand, one at a
time, by a person; this automates that authoring step, it does not port their content.
