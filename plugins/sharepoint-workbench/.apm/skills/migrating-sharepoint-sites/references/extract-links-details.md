# Link extraction details

## Contents

- [API and link kinds](#api-and-link-kinds)
- [Outcomes](#outcomes)
- [Scope](#scope)
- [Provenance](#provenance)

## API and link kinds

`extract_links_from_text(content, source=...)` parses one document's content. `extract_links_from_paths(paths)` reads a set of local files
already exported from a tenant. Each returns a `LinkInventory` whose `links` are `ExtractedLink` records (`url`, `source`, `kind`) and whose
`outcome` distinguishes states that are otherwise easy to conflate. `classify(url)` reports one of `absolute`, `server_relative`,
`protocol_relative`, `mailto`, `anchor`, `malformed`.

## Outcomes

`OBSERVED` (links found), `EMPTY` (read fine, no links), `PARTIAL` (some sources failed; `problems` lists them), `FAILED` (every attempted
source failed). When `extract_links_from_paths` is given `sources_attempted`, an all-sources-failed run reports `FAILED`, not an empty
success. See `link-pipeline-and-write-safety.md`.

## Scope

Read-only. No writes and no network connections; it reads only content passed in or local paths you name. Tenant retrieval is out of scope:
export content first, then extract.

## Provenance

Adapted from `sp-extracting-links` in the originating SharePoint migration repository (`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`,
source repository only). Ported to Python and stripped of all project-specific literals; the plugin carries no dependency on that repository.
