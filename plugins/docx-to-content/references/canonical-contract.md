# Canonical Contract

Versioned data contracts for the docx-to-content pipeline, implemented as plain
stdlib dataclasses in `scripts/contracts.py` with deterministic hashing in
`scripts/hashing.py`. These are the shapes every later stage (analyze, convert,
render, validate) reads and writes — see
`docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md`
sections 6, 8, and 9 for the authoritative narrative spec this file mirrors.

## Types

All types support `.from_dict(data: dict)` (strict — raises `ValueError` on any
missing required field, and on missing/unsupported `schema_version` where
applicable) and `.to_dict()` (returns a plain JSON-serializable dict/list tree).

| Type | Fields | Notes |
|---|---|---|
| `SourceFingerprint` | `path`, `sha256`, `size_bytes` | Used inside `ConversionPlan.source`. |
| `ManifestSourceFingerprint` | `path`, `sha256` | Manifest's `source` block omits `size_bytes` per spec Section 6.4. |
| `StructuralAnchor` | `stable_key`, `heading_text`, `heading_level`, `occurrence`, `source_heading_path` | One entry per confirmed chunk boundary. |
| `Confirmation` | `status` (`draft`\|`confirmed`), `confirmed_by`, `confirmed_at` | `confirmed_at` is excluded from `plan_id` hashing. |
| `ConversionPlan` | `schema_version`, `plan_id`, `source`, `strategy`, `chunk_level`, `chunk_anchors`, `content_type`, `template_profile`, `confirmation`, `analysis_warnings` | Section 6.2. `plan_id` is `sha256:<hex>`, computed by `hashing.compute_plan_id`. |
| `ChunkMetadata` | `schema_version`, `chunk_id`, `source_order`, `source_heading_path`, `topic`, `content_type`, `template_profile`, `source_sha256`, `plan_id`, `content_file`, `content_sha256`, `local_links`, `media_refs` | Section 6.5. One sidecar per chunk. |
| `ManifestChunk` | `chunk_id`, `content_file`, `metadata_file`, `source_order`, `source_heading_path` | Lightweight manifest-lookup projection of `ChunkMetadata`. |
| `ManifestGenerator` | `plugin`, `plugin_version` | |
| `Manifest` | `schema_version`, `generator`, `source`, `plan_id`, `content_type`, `template_profile`, `strategy`, `chunk_count`, `chunks`, `media`, `validation_report` | Section 6.4. |
| `ValidationIssue` | `severity` (`error`\|`warning`), `code`, `message`, `path` (optional) | One reportable problem. |
| `ValidationReport` | `status` (`PASS`\|`WARN`\|`FAIL`), `issues`, `source_sha256`, `plan_id` | Section 9 severity model. |
| `RenderResult` | `renderer_name`, `renderer_version`, `source_manifest_hash`, `output_files`, `status`, `errors`, `warnings` | Section 8. Shape only — the `Renderer` protocol and `CanonicalPackage` loader are built in Task 12. |

`SUPPORTED_SCHEMA_VERSION = "1.0"` is the single source of truth for the
current schema major/minor; `ConversionPlan`, `ChunkMetadata`, and `Manifest`
all check against it via `_check_schema_version`.

## Canonical JSON serialization

`hashing.canonical_json_bytes(payload)` calls
`json.dumps(payload, sort_keys=True, separators=(",", ":"))`. This is
deterministic because:

- `sort_keys=True` fixes key ordering regardless of dict insertion order (a
  dict built as `{"b": 1, "a": 2}` serializes identically to one built as
  `{"a": 2, "b": 1}`);
- the compact `separators` remove incidental whitespace variance;
- all contract `to_dict()` methods return only plain `dict`/`list`/`str`/
  `int`/`None` values, so there is no non-JSON-native type (e.g. sets,
  datetimes) whose serialization could vary.

## Hashing

- `content_hash(canonical_json_bytes) -> str` — SHA-256 hex digest (no
  prefix) over given canonical JSON bytes.
- `compute_plan_id(plan: ConversionPlan) -> str` — serializes
  `plan.to_dict()`, then:
  1. removes the `plan_id` key (a plan cannot hash its own identity field);
  2. removes `confirmation.confirmed_at` (a timestamp must not alter the
     content hash — two plans differing only in confirmation time produce
     the same `plan_id`; see
     `tests/contract/test_contracts.py::TestComputePlanId::test_plan_id_excludes_confirmed_at_timestamp`);
  3. hashes the remainder via `content_hash`/`canonical_json_bytes`;
  4. prefixes the hex digest with `sha256:` per the spec's
     `"plan_id": "sha256:..."` convention.

  All other fields — including `confirmation.status` and
  `confirmation.confirmed_by` — participate in the hash, so promoting a
  draft to confirmed (status change) legitimately changes `plan_id`.

## Compatibility policy

- `schema_version` is checked exactly (`==`) against `SUPPORTED_SCHEMA_VERSION`
  today — there is exactly one supported version, `"1.0"`.
- A future schema bump (e.g. adding a new required field) should:
  1. Introduce a new version string (e.g. `"1.1"` for additive/backward-
     compatible changes that don't remove or repurpose fields, `"2.0"` for
     breaking changes to existing required fields);
  2. Add the new version to a `SUPPORTED_SCHEMA_VERSIONS` set/frozenset
     (replacing the current single-value check) so loaders can accept either
     the old or new shape during a migration window, or reject explicitly if
     the old version is retired;
  3. Add a `from_dict` branch (or a dedicated migration function) per
     supported version rather than silently coercing an old dict into the
     new shape — the strict "no silent defaulting" rule in this module
     applies to version migrations too;
  4. Bump `plugin_version` in `Manifest.generator` alongside any schema
     change that affects manifest/chunk output, so `Manifest.generator` can
     be used to trace which plugin build produced a given package independent
     of `schema_version`.
- Renderers (Task 12+) declare `supported_manifest_versions:
  frozenset[str]` and must refuse to render a manifest whose
  `schema_version` isn't in that set, rather than attempting a best-effort
  render.
