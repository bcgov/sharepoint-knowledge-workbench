# Plugin Extraction Triggers

This document is authorization-neutral: it records the conditions under which a workstream currently
implemented inside `docx-to-content` would become a real candidate for extraction into its own plugin
(e.g. `knowledge-publication`, `knowledge-platform-delivery`, `knowledge-evaluation`, per
`docs/vision/master-initiative-plan-workstreams-and-phases.md`). Meeting a trigger does not itself
authorize extraction — it only means the question is worth raising with the user via a proper
brainstorming/spec pass, per this repo's standing workflow.

## Triggers (any one is sufficient to raise the question)

- An independently invoked consumer needs to call the capability without going through
  `docx-to-content`'s own CLI/skills.
- A second producer of canonical content exists (i.e. something other than DOCX conversion produces a
  canonical package that this capability then needs to operate on).
- The capability needs a distinct release cadence from the rest of `docx-to-content`.
- The capability needs a separate ownership or security/access boundary (e.g. downstream-platform write
  credentials that the DOCX-conversion path has no reason to ever hold).

## Current status (as of Phase 2)

None of the above are met for any workstream. `knowledge-publication`'s boundary (publication-map
ownership, renderer contracts) is hardened *inside* `docx-to-content` by this phase's work, not extracted.

## Known limitation carried forward from Phase 2 (Task 7): self-asserted fixture provenance

`validate_canonical.py`'s content-comparison-skip exemption is derived from
`manifest.generator.plugin == "hand-authored-fixture"` — a self-asserted string in the manifest, not an
independently verified signal. This is acceptable today because the only producer of canonical content is
the trusted `docx-to-content` pipeline itself (no untrusted second producer exists per the triggers above).
**If a second producer of canonical content is ever introduced** (the trigger two rows up), this provenance
mechanism must be revisited: a self-declared string is not a sufficient trust boundary once an untrusted or
semi-trusted second producer can also write `generator.plugin` values. At that point, replace it with a
verified provenance signal (e.g. a signed or separately-tracked producer identity), not a string comparison.
