# `analysis-plan` v1

**Producer:** `document-structure-analysis` (this plugin) — the authoritative
definition of this contract lives in this plugin's own package at
`scripts/structure-analysis/plan_schema/analysis_plan.py`, not in a shared top-level
distribution. This plugin has zero dependency on any other workbench
distribution; it installs and runs standalone.

**Consumer:** `structured-content-assembly` (Wave 4) consumes a *confirmed*
analysis-plan to build the `canonical-package`/`publication-map`
contracts. A consumer plugin carries its own plugin-local copy of the
schema subset it needs — it never imports this plugin's package at
runtime.

## Wire format (dict, JSON-serializable)

The `ConversionPlan` shape (see `plan_schema/analysis_plan.py`):

| Field | Type | Description |
|---|---|---|
| `schema_version` | `str` | Always `"1.0"` for this version. |
| `plan_id` | `str` | `sha256:`-prefixed content hash over the plan's normalized content (excludes `plan_id` itself and `confirmation.confirmed_at`). |
| `source` | `dict` | `{path, sha256, size_bytes}` — the source document's fingerprint. |
| `strategy` | `str` | `"single"` \| `"chunked"` \| `"grouped"` — advisory only; `chunk_anchors` determines actual chunk boundaries. |
| `chunk_level` | `int` | Advisory candidate chunk level. |
| `chunk_anchors` | `list[dict]` | `{stable_key, heading_text, heading_level, occurrence, source_heading_path}` per heading — never raw line offsets. |
| `content_type` | `str` | e.g. `"manual"`. |
| `template_profile` | `str` | e.g. `"source-structure-v1"`. |
| `confirmation` | `dict` | `{status, confirmed_by, confirmed_at}` — `status` is `"draft"` until a human confirms it. |
| `analysis_warnings` | `list[str]` | Human-reviewable warnings (defect signals, mixed topic-root levels, promoted/ambiguous roots, media-review-required). |
| `confirmed_topic_roots` | `list[dict] \| None` | `{source_heading_path, occurrence}` per topic-root physical boundary, for the "grouped" strategy. |
| `media_decisions` | `list[dict] \| None` | Preamble media classification/disposition records — proposed here as `None`; merged in by the caller (see below). |

Additional informational fields on `recommend_from_normalized`'s output
(not part of `ConversionPlan.to_dict()`, included for human review before
confirmation):

| Field | Type | Description |
|---|---|---|
| `proposed_topics` | `list[dict]` | `{topic_id, title, first_anchor_path, anchor_count, child_heading_count, approx_size_chars, source_level, classification}` per detected topic. |
| `recommendation` | `dict` | `{strategy, reasons, candidate_chunk_level, chunk_level_note}`. |

## Producing this contract

```python
from analysis import recommend_from_normalized

# normalized: a normalized-source-document v1 dict from
# source-document-extraction's extract_and_normalize()
analysis_plan = recommend_from_normalized(normalized)
```

`media_decisions` is deliberately `None` on this function's output:
proposing preamble media decisions requires filesystem access to the
extracted media directory, which this function's dict-only input doesn't
carry. The caller (currently `docx-to-content`'s compatibility
orchestrator) merges media proposals in afterward and recomputes
`plan_id` via `plan_hashing.compute_plan_id`.

## Validating

```python
from plan_schema.analysis_plan import validate

validate(analysis_plan)  # raises ValueError on missing/mismatched required fields
```
