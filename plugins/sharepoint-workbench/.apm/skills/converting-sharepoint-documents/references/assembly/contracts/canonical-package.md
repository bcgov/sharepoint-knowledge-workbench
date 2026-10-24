# `canonical-package` v1

**Producer:** `structured-content-assembly` (this plugin) — the authoritative
definition of this contract lives in this plugin's own package at
`scripts/assembly/canonical_schema/canonical_package.py`, not in a shared
top-level distribution. This plugin has zero dependency on any other
workbench distribution; it installs and runs standalone.

**Consumer:** `docx-to-content` (transitional) and future
`structured-content-rendering` (Wave 5) consume an on-disk canonical package via
`canonical_package.CanonicalPackage.load()`. A consumer plugin carries its
own plugin-local copy of the schema subset it needs — it never imports
this plugin's package at runtime.

## On-disk layout

```
<package_dir>/
├── manifest.json            # Manifest
├── validation.json          # ValidationReport
├── generator-info.json      # plugin/tool version record (atomic_output.py)
├── warning-disposition.json # only if validation status is WARN
├── publication-map.json     # only if manifest.strategy == "grouped"
├── chunks/
│   ├── <chunk_id>.md            # chunk content
│   └── <chunk_id>.meta.json     # ChunkMetadata
└── media/
    └── <media file>...
```

## `manifest.json` — `Manifest`

| Field | Type | Description |
|---|---|---|
| `schema_version` | `str` | Always `"1.0"` for this version (`MANIFEST_SCHEMA_VERSION`). |
| `generator` | `dict` | `{plugin, plugin_version}` — always `plugin: "structured-content-assembly"` for packages this plugin builds. |
| `source` | `dict` | `{path, sha256}` — the source document's fingerprint (no `size_bytes`, unlike `analysis-plan`'s `SourceFingerprint`). |
| `plan_id` | `str` | The confirmed `analysis-plan`'s `plan_id`, carried through unchanged. |
| `content_type` | `str` | Carried through from the plan. |
| `template_profile` | `str` | Carried through from the plan. |
| `strategy` | `str` | `"single"` \| `"chunked"` \| `"grouped"` — the strategy actually used to build this package. |
| `chunk_count` | `int` | `len(chunks)`. |
| `chunks` | `list[dict]` | `ManifestChunk`: `{chunk_id, content_file, metadata_file, source_order, source_heading_path}`, in manifest/render order. |
| `media` | `list[str]` | Filenames under `media/`. |
| `validation_report` | `str` | Always `"validation.json"`. |

## `chunks/<chunk_id>.meta.json` — `ChunkMetadata`

| Field | Type | Description |
|---|---|---|
| `schema_version` | `str` | Always `"1.0"` (`CHUNK_METADATA_SCHEMA_VERSION`). |
| `chunk_id` | `str` | Matches the corresponding `StructuralAnchor.stable_key` (ungrouped) or topic id (grouped). |
| `source_order` | `int` | Position in source document order. |
| `source_heading_path` | `list[str]` | Full heading path from document root. |
| `topic` | `str` | Human-readable topic/heading text. |
| `content_type` / `template_profile` | `str` | Carried through from the plan. |
| `source_sha256` | `str` | Source document fingerprint. |
| `plan_id` | `str` | Confirmed plan's `plan_id`. |
| `content_file` | `str` | Relative path to this chunk's `.md` file. |
| `content_sha256` | `str` | `hashing.content_hash` of the chunk's content bytes. |
| `local_links` | `list[str]` | Raw (pre-render-rewrite) `chunks/<id>.md`-relative links to other chunks. |
| `media_refs` | `list[str]` | Raw (pre-render-rewrite) `../media/<file>`-relative media references. |
| `anchors` | `list[dict] \| None` | Grouped strategy only: `{stable_key, source_heading_path, occurrence, heading_level}` per folded structural anchor, in source order. `None` for ungrouped chunks. |

## `validation.json` — `ValidationReport`

| Field | Type | Description |
|---|---|---|
| `status` | `str` | `"PASS"` \| `"WARN"` \| `"FAIL"`. |
| `issues` | `list[dict]` | `ValidationIssue`: `{severity, code, message, path}` (`path` optional). |
| `source_sha256` | `str` | Must match `manifest.source.sha256`. |
| `plan_id` | `str` | Must match `manifest.plan_id`. |

A `FAIL` status blocks promotion (see `atomic_output.py`); a `WARN` status
requires an accompanying `warning-disposition.json` reconciling every
warning issue before `CanonicalPackage.load()` accepts the package (see
`dispositions.py`).
