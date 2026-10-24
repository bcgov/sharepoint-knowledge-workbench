# Document workflow intake scope

## Contents

- [What the wizard asks](#what-the-wizard-asks)
- [Renderer profiles](#renderer-profiles)
- [Superseded skill](#superseded-skill)

Design provenance (source repository only; not needed at runtime):
`docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md`,
Sections 1 (Layer 1b, Layer 2) and 8.

## What the wizard asks

Ask the user across all domains, without performing any of their work:
source-document identity, new conversion vs. revision, content type/ownership,
requested processing stages, requested output formats, human-facing publication
locations, media locations, ASPX publication, agent-grounding representations,
existing-vs-new agent decisions, native-skill requirements, governance/evidence
settings, and an explicit list of unresolved decisions.

## Renderer profiles

Only implemented renderer profiles may be offered as executable choices. Currently
`multipage-markdown` and `sharepoint-aspx` (`document_workflow.IMPLEMENTED_RENDERER_PROFILES`,
kept in sync with the rendering plugin's actual registered renderers). Anything else
requested is recorded in `UnsupportedRequests`, never silently treated as executable.

## Superseded skill

`initialize-publication-profile` (a narrower, earlier-conceived skill named in the
design doc) is superseded/absorbed into this wizard's broader flow. It is not a
separate, fourth skill.
