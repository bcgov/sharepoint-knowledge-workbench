# publication-map.json Contract

`publication-map.json` is written alongside `manifest.json` for canonical
content packages built with `strategy: "grouped"` (see
`convert-document/SKILL.md`'s Grouped Strategy section). It gives explicit,
directory-order-independent topic ordering for rendering — a renderer reads
`order` from this file rather than inferring order from manifest position
or filesystem listing order.

It is not written for `"single"`/`"chunked"` packages; its absence there is
expected, not an error.

## Shape

```json
{
  "schema_version": "1.0",
  "package_identity": "sha256:<plan_id-derived string>",
  "entries": [
    {
      "topic_id": "file-access--a1b2c3d4",
      "title": "File Access",
      "order": 0,
      "chunk_id": "chunks/file-access--a1b2c3d4.md",
      "parent_topic_id": null
    }
  ]
}
```

- `schema_version` — matches `contracts.SUPPORTED_SCHEMA_VERSION`, the same
  version field every other canonical-content contract carries.
- `package_identity` — references the canonical package's own identity
  (derived from the confirmed plan's `plan_id`), not a bare manifest hash,
  so a publication map can be checked against the specific package it was
  written for.
- `entries` — one entry per topic chunk, in the manifest's topic set
  (`entries[].topic_id` always matches some `manifest.chunks[].chunk_id`
  for a grouped manifest).
  - `topic_id` — the topic's deterministic identity
    (`identity.make_topic_id`), independent of filename or array position.
  - `title` — the topic's top-level heading text.
  - `order` — explicit integer position, contiguous `0..N-1` with no gaps
    or duplicates. This is what a renderer sorts by; it is never inferred
    from `entries` array position, directory listing, or manifest order.
  - `chunk_id` — the topic's content file path, relative to the package
    root (e.g. `chunks/<topic_id>.md`).
  - `parent_topic_id` — reserved for future topic hierarchy (a topic
    nested under another topic); `null` for every topic in Phase 1, since
    grouping is a single flat level (level-1 heading → topic).

## Where structural-anchor identity lives instead

`publication-map.json` orders **topics**, not the individual headings
folded into them. A topic's folded headings (structural anchors) are not
listed here — they live in that topic's own chunk sidecar
(`chunks/<topic_id>.meta.json`)'s `anchors` field: a list of
`{"stable_key", "source_heading_path", "occurrence", "heading_level"}`
entries, one per original heading, in source order. This keeps three
identities independent, per the Task 17-topic-grouping design: a structural
anchor's own identity (`identity.make_chunk_id`), its topic's identity
(`identity.make_topic_id`), and its position in the publication map
(`order`) — renaming or reorganizing a topic never changes the structural
anchors it contains, and reassigning which topic an anchor belongs to never
changes the anchor's own `stable_key`.

## Validation

`validate_canonical.py` enforces, for `strategy: "grouped"` packages:

- `publication-map.json` must exist (`missing_publication_map` otherwise).
- Its `entries[].topic_id` set must exactly match the manifest's chunk id
  set (`publication_map_chunk_mismatch` otherwise).
- Its `entries[].order` values must form a contiguous `0..N-1` sequence
  with no gaps or duplicates (`publication_map_order_invalid` otherwise).
- Every structural anchor in the confirmed plan must appear in exactly one
  topic chunk's `anchors` list — never zero
  (`unassigned_structural_anchor`), never more than one
  (`duplicate_structural_anchor_assignment`).

## Implementation status: implemented (Phase 1, `"grouped"` strategy only).
