# `publication-map` v1

**Producer:** `structured-content-assembly` (this plugin) — the authoritative
definition of this contract lives in this plugin's own package at
`scripts/assembly/canonical_schema/publication_map.py`, not in a shared top-level
distribution. This plugin has zero dependency on any other workbench
distribution; it installs and runs standalone.

**Consumer:** `docx-to-content` (transitional) and future
`structured-content-rendering` (Wave 5) consume `publication-map.json` (via
`canonical_package.CanonicalPackage.load()`'s `publication_map` field) to
render grouped packages in the intended topic order rather than manifest
order. A consumer plugin carries its own plugin-local copy of the schema
subset it needs — it never imports this plugin's package at runtime.

## Applicability

Only present (`publication-map.json` at the package root) when the
package's `manifest.strategy == "grouped"`. Ungrouped (`"single"` /
`"chunked"`) packages must NOT have this file — `validate_canonical.py`
and `CanonicalPackage.load()` both reject an unexpected publication map on
a non-grouped package.

## Wire format (dict, JSON-serializable)

| Field | Type | Description |
|---|---|---|
| `schema_version` | `str` | Always `"1.0"` for this version (`PUBLICATION_MAP_SCHEMA_VERSION`). |
| `package_identity` | `str` | `sha256:`-prefixed identity tying this map to one specific canonical package (rejected if it doesn't match at load time). |
| `entries` | `list[dict]` | `PublicationMapEntry`, in intended publication order. |

### `PublicationMapEntry`

| Field | Type | Description |
|---|---|---|
| `topic_id` | `str` | The grouped chunk's `chunk_id` (topic-level identity). |
| `title` | `str` | Human-readable topic title. |
| `order` | `int` | Zero-based, contiguous publication order (no gaps/duplicates). |
| `chunk_id` | `str` | Must exist among `manifest.chunks[*].chunk_id` — every entry must resolve to a real chunk, and every chunk must appear exactly once. |
