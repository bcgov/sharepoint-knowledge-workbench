# `rendered-output-profile` v1

**Producer:** `structured-content-rendering` (this plugin) — the authoritative
definition of this contract (`RenderResult`) lives in this plugin's own
package at `scripts/rendering/render_result.py`, not in a shared top-level
distribution. This plugin has zero dependency on any other workbench
distribution; it installs and runs standalone.

**Consumer:** `docx-to-content` (transitional) consumes `RenderResult` via
its own bare `render_result` compatibility-shim import.

## On-disk layout (staging/promoted render output)

```
<output_dir>/
├── index.md              # hierarchical, path-aware index
├── pages/
│   └── <chunk_id>.md          # one rendered page per chunk
├── media/
│   └── <media file>...
├── render-result.json    # RenderResult
├── render-validation.json  # ValidationReport (renderer-side)
└── generator-info.json   # plugin/tool version record (atomic_output.py)
```

## `render-result.json` — `RenderResult`

| Field | Type | Description |
|---|---|---|
| `renderer_name` | `str` | e.g. `"multipage-markdown"`. |
| `renderer_version` | `str` | e.g. `"0.1.0"`. |
| `source_content_sha256` | `str` | The rendered package's manifest source fingerprint — **not** a hash of the manifest file itself; ties the render back to the original source document. |
| `output_files` | `list[str]` | Every file this render wrote. |
| `status` | `str` | `"PASS"` \| `"WARN"` \| `"FAIL"`. |
| `errors` | `list[str]` | Renderer-level errors, if any. |
| `warnings` | `list[str]` | Renderer-level warnings, if any. |

A `FAIL` status blocks promotion (see `atomic_output.py`): the prior
accepted `rendered-output/` (if any) is left untouched, and the failed
staging directory is retained for diagnosis.
