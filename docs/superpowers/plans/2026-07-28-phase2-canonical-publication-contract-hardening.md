# Phase 2 Canonical/Publication Contract Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the `docx-to-content` plugin's canonical-content/publication-map contract so it is
provably validated (validators demonstrated, on purpose, to catch specific corruption at the specific
layer meant to catch it), provably independent of DOCX-runtime code, and internally consistent (two
confirmed identity/naming bugs fixed, `chunk_id` given real semantics, dead fields removed) — without
extracting a new plugin, renaming the repository, or building any new agent.

**Architecture:** All work happens inside `plugins/docx-to-content/`. The one structural change is
splitting `scripts/package.py` into package-*building* functions (stay in `package.py`) and the read-only
`CanonicalPackage.load()` consumer (moves to a new `scripts/canonical_package.py`), so `renderers/` can be
proven, via a transitive import-graph test, to never reach DOCX-analysis/producer code. Everything else is
additive: new mutation-test modules targeting three validation layers, a schema-version constant split, an
independent hand-authored fixture, and a golden-master comparison split into byte-identical publication
content vs. semantically-checked metadata.

**Tech Stack:** Python 3.13 stdlib only (dataclasses, `re`, `json`, `hashlib`, `ast` for the import-graph
test), `pytest` for the existing test suite.

## Global Constraints

- TDD throughout: write the failing test before the implementation, per this repo's standing rule.
- No repository rename, no new plugin, no new agent, no new renderer output format, no SharePoint code —
  per the approved spec's Section 4 non-goals.
- No schema-version migration/adapter machinery — one version per contract constant, no ranges.
- Full existing suite (449 passed/1 skipped as of the last commit before this plan) must continue passing,
  **except** tests that assert behavior this plan intentionally changes (identity value, field name,
  `chunk_id` resolution) — each such test is called out by name in the task that changes it.
- No CEIS-specific literal strings in new generalization tests.
- The golden-master baseline (Task 0, which must run FIRST, before Task 1) requires Phase 1's human
  spot-check to be complete — if it is not complete, stop and surface that to the user rather than
  proceeding. Round-3 review (both Opus and GPT 5.6, independently, as their top blocking finding) caught
  that an earlier draft of this plan captured the baseline by regenerating output with Phase 2's own
  changes already applied and then comparing that output to a copy of itself — a tautology that would
  report success even if Phase 2 changed every page. The baseline MUST be captured from the
  Phase-1-accepted, pre-Phase-2 output, before Task 1 touches any code.

---

## File Structure

| File | Responsibility after this plan |
|---|---|
| `scripts/contracts.py` | Per-contract schema-version constants; `PublicationMapEntry` without `parent_topic_id`; `RenderResult.source_content_sha256` instead of `source_manifest_hash` |
| `scripts/hashing.py` | `compute_plan_id`'s prefixing made idempotent |
| `scripts/package.py` | Package-*building* functions only (`build_canonical_package`, `build_grouped_canonical_package`, media copy/rewrite helpers); no longer defines `CanonicalPackage` |
| `scripts/canonical_package.py` (new) | The read-only `CanonicalPackage`/`LoadedChunk`/`CanonicalPackageError` family, moved verbatim (with the identity fixes applied) from `package.py` |
| `scripts/publication_map.py` | Identity-bug fix; `chunk_id` given real chunk-ID semantics, not a path; `parent_topic_id` removed; malformed-JSON/missing-field/version errors surfaced as controlled exceptions |
| `scripts/validate_canonical.py` | New lineage checks (chunk sidecar `plan_id`/`source_sha256` vs. manifest); malformed-publication-map handling; unexpected-publication-map-for-non-grouped policy; content-comparison-skip decisively enforced for producer-path packages |
| `scripts/renderers/protocol.py` | Imports `CanonicalPackage` from the new `canonical_package` module, not `package` |
| `scripts/renderers/multipage_markdown.py` | Resolves publication-map entries via `entry.chunk_id`, not `entry.topic_id`; uses `source_content_sha256` |
| `scripts/renderers/validate_rendered.py` | Uses `source_content_sha256`; check code renamed from `manifest_hash_mismatch` |
| `tests/unit/test_canonical_package_mutations.py` (new) | Layer-2 mutation suite (`CanonicalPackage.load()`) |
| `tests/unit/test_validate_canonical_mutations.py` (new) | Layer-1 mutation suite (`validate_canonical_package`) |
| `tests/unit/test_validate_rendered_mutations.py` (new) | Layer-3 mutation suite (`validate_rendered_output`) |
| `tests/unit/test_import_boundaries.py` (new) | Transitive import-graph proof |
| `tests/fixtures/independent-canonical-package/` (new) | Hand-authored canonical package, never produced by the real pipeline |
| `tests/unit/test_independent_fixture.py` (new) | Proves the renderer/validators work against the independent fixture |
| `references/extraction-triggers.md` (new) | Documents when `knowledge-publication` etc. become real extraction candidates |
| `runs/ceis-manual-v2/golden-master-baseline/` (new, Task 0) | Immutable snapshot of the Phase-1-accepted `index.md`/`pages/`/`media/`, captured BEFORE any Phase 2 code change |

---

## Task 0: Capture the Phase 1 Golden-Master Baseline — MUST Run Before Task 1

**This task runs first, before any other task in this plan touches any code.** Round-3 review (Opus and
GPT 5.6, independently, both as their #1 blocking finding) caught that an earlier draft captured this
baseline by regenerating output with Phase 2's fixes already applied, then comparing that regenerated
output to a copy of itself — proving nothing, since a Phase 2 regression that changed every page
consistently would still show green. The baseline must come from the **currently accepted, pre-Phase-2**
output.

**Files:**
- Create: `runs/ceis-manual-v2/golden-master-baseline/` (copied from the current, already-accepted
  `runs/ceis-manual-v2/render/rendered-output/`)
- Create: `runs/ceis-manual-v2/golden-master-baseline/MANIFEST.sha256` (a file-inventory + hash record,
  so later comparison can detect both missing and unexpectedly-added files, not just byte mismatches in
  files that happen to exist on both sides)

**Precondition — check before doing anything else:**
Read `runs/ceis-manual-v2/evidence-report.md`'s human spot-check section. If any of its four applicable
rows are still blank, **stop this task and tell the user** — do not capture a baseline from an unaccepted
output. This is the same precondition Task 16 (below) restates for its own comparison step; it is checked
here, at capture time, because capturing too early is the actual failure mode, not comparing too early.

- [ ] **Step 1: Confirm Phase 1 is closed**

Read `runs/ceis-manual-v2/evidence-report.md`. Confirm the human spot-check rows are filled in (not blank)
and the Final Acceptance Checklist has no outstanding ❌ rows tied to human review. If not, stop here and
report this to the user — do not proceed to Step 2.

- [ ] **Step 2: Capture the baseline from the CURRENT, unmodified output**

```bash
cd /path/to/manual-conversion-poc  # repo root, not plugins/docx-to-content
cp -r runs/ceis-manual-v2/render/rendered-output runs/ceis-manual-v2/golden-master-baseline
```

- [ ] **Step 3: Write the file-inventory/hash manifest, so later comparison can detect added/removed files
  as well as changed ones**

```bash
cd runs/ceis-manual-v2/golden-master-baseline
find index.md pages media -type f | sort | xargs shasum -a 256 > MANIFEST.sha256
cd -
```

- [ ] **Step 4: Commit the baseline itself — this is a real, durable artifact, not scratch output**

```bash
git add runs/ceis-manual-v2/golden-master-baseline/
git commit -m "chore: capture Phase 1 accepted golden-master baseline before any Phase 2 code change

Captured from runs/ceis-manual-v2/render/rendered-output/ after
confirming Phase 1's human spot-check is complete (evidence-report.md).
This directory must never be regenerated or overwritten -- Task 16
compares Phase 2's regenerated output against this immutable snapshot,
not against a second copy of Phase 2's own output."
```

---

## Task 1: Fix the `package_identity` Double-Prefix Bug

**Files:**
- Modify: `scripts/package.py:478-480`
- Test: `tests/unit/test_package.py`

(`scripts/hashing.py` is deliberately NOT modified — round 3 review caught that an earlier draft listed it
here without changing it. `hashing.compute_plan_id` already returns a single, correctly `sha256:`-prefixed
value; the bug is entirely in `package.py`'s own redundant `f"sha256:{...}"` wrapping of an
already-prefixed string, fixed in Step 3 below.)

**Interfaces:**
- Consumes: `hashing.compute_plan_id(plan) -> str` (already `sha256:`-prefixed).
- Produces: `package.build_grouped_canonical_package(...)` now writes a `publication-map.json` whose
  `package_identity` equals `manifest.plan_id` exactly (no double prefix).

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_package.py` (near `test_grouped_package_writes_publication_map`):

```python
def test_grouped_package_identity_is_not_double_prefixed(tmp_path):
    anchor = _anchor(["Alpha"], level=1)
    plan = _confirmed_plan([anchor], strategy="grouped")
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()
    sliced = SlicedDocument(
        preamble="", chunks=[_slice(anchor, "# Alpha\n\nBody text.\n")]
    )
    output_dir = tmp_path / "canonical-content"
    package.build_grouped_canonical_package(plan, sliced, raw_media_dir, output_dir)

    pub_map_data = json.loads((output_dir / "publication-map.json").read_text())
    manifest_data = json.loads((output_dir / "manifest.json").read_text())
    assert pub_map_data["package_identity"] == manifest_data["plan_id"]
    assert not pub_map_data["package_identity"].startswith("sha256:sha256:")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_package.py::test_grouped_package_identity_is_not_double_prefixed -v`
Expected: FAIL — `pub_map_data["package_identity"]` starts with `"sha256:sha256:"`, not equal to `manifest_data["plan_id"]`.

- [ ] **Step 3: Fix it**

In `scripts/package.py`, change:
```python
    pub_map = publication_map.build_publication_map(
        boundaries, topic_chunk_ids, package_identity=f"sha256:{manifest.plan_id}"
    )
```
to:
```python
    pub_map = publication_map.build_publication_map(
        boundaries, topic_chunk_ids, package_identity=manifest.plan_id
    )
```
`manifest.plan_id` is already `sha256:`-prefixed by `hashing.compute_plan_id` — no further prefixing needed.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/unit/test_package.py::test_grouped_package_identity_is_not_double_prefixed -v`
Expected: PASS

- [ ] **Step 5: Run the full existing suite to confirm no other test asserted the old (buggy) value**

Run: `python3 -m pytest tests/ -q`
Expected: all pass; if any test asserted `"sha256:sha256:"` explicitly, update it — none currently do (no
existing test checks `package_identity`'s literal value, confirmed by `grep -rn "package_identity" tests/`
before this task).

- [ ] **Step 6: Commit**

```bash
git add scripts/package.py tests/unit/test_package.py
git commit -m "fix: package_identity is no longer double-prefixed with sha256:"
```

---

## Task 2: Rename `RenderResult.source_manifest_hash` to `source_content_sha256`

**Files:**
- Modify: `scripts/contracts.py:493-524`
- Modify: `scripts/renderers/multipage_markdown.py:205-213`
- Modify: `scripts/renderers/validate_rendered.py:274-304`
- Test: `tests/contract/test_contracts.py`, `tests/unit/test_multipage_markdown.py`, `tests/unit/test_validate_rendered.py`

**Interfaces:**
- Produces: `contracts.RenderResult.source_content_sha256: str` (was `source_manifest_hash`), same
  semantics (the canonical package's source-document SHA-256, not a hash of `manifest.json`).
- Produces: `validate_rendered.py`'s check code is now `source_content_stale` (was `manifest_hash_mismatch`)
  — this is the accurate name for what the check actually does (detect that the canonical package was
  reconverted from different source content since this render was staged).

- [ ] **Step 1: Write the failing test**

Add to `tests/contract/test_contracts.py`:

```python
def test_render_result_uses_source_content_sha256_not_manifest_hash():
    data = {
        "renderer_name": "multipage-markdown",
        "renderer_version": "0.1.0",
        "source_content_sha256": "a" * 64,
        "output_files": [],
        "status": "PASS",
        "errors": [],
        "warnings": [],
    }
    result = RenderResult.from_dict(data)
    assert result.source_content_sha256 == "a" * 64
    assert result.to_dict() == data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/contract/test_contracts.py::test_render_result_uses_source_content_sha256_not_manifest_hash -v`
Expected: FAIL — `RenderResult.from_dict` raises `ValueError: missing required field: 'source_manifest_hash'`
(the old field name is still required, the new one is unknown).

- [ ] **Step 3: Rename the field in the contract**

In `scripts/contracts.py`, change every occurrence in the `RenderResult` dataclass:
```python
@dataclass
class RenderResult:
    renderer_name: str
    renderer_version: str
    source_content_sha256: str  # was source_manifest_hash
    output_files: list
    status: str
    errors: list
    warnings: list

    @classmethod
    def from_dict(cls, data: dict) -> "RenderResult":
        return cls(
            renderer_name=_require(data, "renderer_name"),
            renderer_version=_require(data, "renderer_version"),
            source_content_sha256=_require(data, "source_content_sha256"),
            output_files=list(_require(data, "output_files")),
            status=_require(data, "status"),
            errors=list(_require(data, "errors")),
            warnings=list(_require(data, "warnings")),
        )

    def to_dict(self) -> dict:
        return {
            "renderer_name": self.renderer_name,
            "renderer_version": self.renderer_version,
            "source_content_sha256": self.source_content_sha256,
            "output_files": list(self.output_files),
            "status": self.status,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }
```

- [ ] **Step 4: Update the two callers**

In `scripts/renderers/multipage_markdown.py`, in `MultipageMarkdownRenderer.render`:
```python
        return contracts.RenderResult(
            renderer_name=self.name,
            renderer_version=RENDERER_VERSION,
            source_content_sha256=package.manifest.source.sha256,
            output_files=output_files,
            status="PASS",
            errors=[],
            warnings=[],
        )
```

In `scripts/renderers/validate_rendered.py`'s `_check_manifest_hash` (rename the function too, to
`_check_source_content_staleness`, and update its one caller in `validate_rendered_output`):
```python
def _check_source_content_staleness(rendered_dir: Path, package) -> list:
    result_path = rendered_dir / "render-result.json"
    if not result_path.exists():
        return [_error(
            "missing_render_result",
            "render-result.json does not exist -- cannot verify which "
            "canonical package this render was produced from",
            "render-result.json",
        )]

    try:
        recorded = contracts.RenderResult.from_dict(json.loads(result_path.read_text()))
    except (ValueError, json.JSONDecodeError) as exc:
        return [_error(
            "malformed_render_result",
            f"render-result.json failed schema validation: {exc}",
            "render-result.json",
        )]

    current_hash = package.manifest.source.sha256
    if recorded.source_content_sha256 != current_hash:
        return [_error(
            "source_content_stale",
            f"render-result.json records source_content_sha256="
            f"{recorded.source_content_sha256!r}, but the supplied canonical "
            f"package's current source content hash is {current_hash!r} -- "
            "the canonical package was reconverted after this render was "
            "staged",
            "render-result.json",
        )]
    return []
```
And in `validate_rendered_output`, change `issues.extend(_check_manifest_hash(rendered_dir, package))` to
`issues.extend(_check_source_content_staleness(rendered_dir, package))`.

- [ ] **Step 5: Update existing tests that construct a `RenderResult` or assert the old field/check name**

`grep -rn "source_manifest_hash\|manifest_hash_mismatch" tests/` and update every match to
`source_content_sha256`/`source_content_stale` respectively — this touches
`tests/unit/test_multipage_markdown.py` and `tests/unit/test_validate_rendered.py`. These are
**intentional** test changes, not regressions — the field/check being renamed is the whole point of this
task.

- [ ] **Step 6: Run test to verify it passes, then run the full suite**

Run: `python3 -m pytest tests/contract/test_contracts.py::test_render_result_uses_source_content_sha256_not_manifest_hash -v`
Expected: PASS
Run: `python3 -m pytest tests/ -q`
Expected: all pass (with the intentional renames from Step 5 applied).

- [ ] **Step 7: Commit**

```bash
git add scripts/contracts.py scripts/renderers/multipage_markdown.py scripts/renderers/validate_rendered.py tests/
git commit -m "fix: rename RenderResult.source_manifest_hash to source_content_sha256"
```

---

## Task 3: Split Schema-Version Constants Per Contract Type

**Files:**
- Modify: `scripts/contracts.py:25-42`
- Modify: `scripts/package.py` (4 call sites at lines 266, 295, 415, 445)
- Modify: `scripts/publication_map.py:38`
- Modify: `scripts/plans.py:73`
- Test: `tests/contract/test_contracts.py`

**Interfaces:**
- Produces: `contracts.CONVERSION_PLAN_SCHEMA_VERSION`, `contracts.MANIFEST_SCHEMA_VERSION`,
  `contracts.CHUNK_METADATA_SCHEMA_VERSION`, `contracts.PUBLICATION_MAP_SCHEMA_VERSION` — each `"1.0"` for
  now, each independently checked. `contracts.SUPPORTED_SCHEMA_VERSION` remains as a backward-compatible
  alias equal to `CONVERSION_PLAN_SCHEMA_VERSION` (existing tests referencing it still pass unchanged), but
  new code uses the per-contract constant.

- [ ] **Step 1: Write the failing test**

Add to `tests/contract/test_contracts.py`:

```python
def test_schema_version_constants_are_independent_per_contract():
    assert contracts.CONVERSION_PLAN_SCHEMA_VERSION == "1.0"
    assert contracts.MANIFEST_SCHEMA_VERSION == "1.0"
    assert contracts.CHUNK_METADATA_SCHEMA_VERSION == "1.0"
    assert contracts.PUBLICATION_MAP_SCHEMA_VERSION == "1.0"

    with pytest.raises(ValueError, match="schema_version"):
        contracts.Manifest.from_dict({
            "schema_version": "9.9",
            "generator": {"plugin": "p", "plugin_version": "0.1.0"},
            "source": {"path": "x", "sha256": "a" * 64},
            "plan_id": "sha256:" + "a" * 64,
            "content_type": "manual",
            "template_profile": "t",
            "strategy": "chunked",
            "chunk_count": 0,
            "chunks": [],
            "media": [],
            "validation_report": "validation.json",
        })
```

(Add `import contracts` and `import pytest` at the top of the test file if not already present — both
already are, per the existing file's imports.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/contract/test_contracts.py::test_schema_version_constants_are_independent_per_contract -v`
Expected: FAIL — `AttributeError: module 'contracts' has no attribute 'CONVERSION_PLAN_SCHEMA_VERSION'`.

- [ ] **Step 3: Implement the constant split**

In `scripts/contracts.py`, replace:
```python
SUPPORTED_SCHEMA_VERSION = "1.0"


def _require(data: dict, field_name: str) -> Any:
    if field_name not in data:
        raise ValueError(f"missing required field: {field_name!r}")
    return data[field_name]


def _check_schema_version(data: dict) -> str:
    version = _require(data, "schema_version")
    if version != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version: {version!r} "
            f"(supported: {SUPPORTED_SCHEMA_VERSION!r})"
        )
    return version
```
with:
```python
CONVERSION_PLAN_SCHEMA_VERSION = "1.0"
MANIFEST_SCHEMA_VERSION = "1.0"
CHUNK_METADATA_SCHEMA_VERSION = "1.0"
PUBLICATION_MAP_SCHEMA_VERSION = "1.0"

# Backward-compatible alias: pre-Phase-2 code (and any external caller) that
# referenced one shared SUPPORTED_SCHEMA_VERSION still resolves to a valid
# value. New code should reference the per-contract constant above instead
# -- these four are independent per Phase 2's design (a publication-map
# change no longer forces a conversion-plan version bump or vice versa), not
# migration/compatibility machinery -- each still supports exactly one
# version.
SUPPORTED_SCHEMA_VERSION = CONVERSION_PLAN_SCHEMA_VERSION


def _require(data: dict, field_name: str) -> Any:
    if field_name not in data:
        raise ValueError(f"missing required field: {field_name!r}")
    return data[field_name]


def _check_schema_version(data: dict, expected_version: str, contract_name: str) -> str:
    version = _require(data, "schema_version")
    if version != expected_version:
        raise ValueError(
            f"unsupported schema_version for {contract_name}: {version!r} "
            f"(supported: {expected_version!r})"
        )
    return version
```

Update each contract's `from_dict` to pass its own constant and name:
- `ConversionPlan.from_dict`: `schema_version = _check_schema_version(data, CONVERSION_PLAN_SCHEMA_VERSION, "ConversionPlan")`
- `ChunkMetadata.from_dict`: `schema_version = _check_schema_version(data, CHUNK_METADATA_SCHEMA_VERSION, "ChunkMetadata")`
- `Manifest.from_dict`: `schema_version = _check_schema_version(data, MANIFEST_SCHEMA_VERSION, "Manifest")`
- `PublicationMap.from_dict`: `schema_version = _check_schema_version(data, PUBLICATION_MAP_SCHEMA_VERSION, "PublicationMap")`

- [ ] **Step 4: Update construction call sites to use the matching per-contract constant**

- `scripts/package.py:266` (inside `ChunkMetadata(...)` in `build_canonical_package`):
  `schema_version=contracts.CHUNK_METADATA_SCHEMA_VERSION,`
- `scripts/package.py:295` (inside `Manifest(...)` in `build_canonical_package`):
  `schema_version=contracts.MANIFEST_SCHEMA_VERSION,`
- `scripts/package.py:415` (inside `ChunkMetadata(...)` in `build_grouped_canonical_package`):
  `schema_version=contracts.CHUNK_METADATA_SCHEMA_VERSION,`
- `scripts/package.py:445` (inside `Manifest(...)` in `build_grouped_canonical_package`):
  `schema_version=contracts.MANIFEST_SCHEMA_VERSION,`
- `scripts/publication_map.py:38` (inside `PublicationMap(...)` in `build_publication_map`):
  `schema_version=contracts.PUBLICATION_MAP_SCHEMA_VERSION,`
- `scripts/plans.py:73` (inside whichever `ConversionPlan`/`Confirmation`-adjacent construction uses it —
  read the surrounding function first to confirm it's building a `ConversionPlan`, then use
  `contracts.CONVERSION_PLAN_SCHEMA_VERSION`).

- [ ] **Step 5: Fix the renderer's version gate, which round-3 review found still re-couples the exact
  thing this task decouples**

`scripts/renderers/multipage_markdown.py` currently declares:
```python
    supported_manifest_versions = frozenset({contracts.SUPPORTED_SCHEMA_VERSION})
```
Since `SUPPORTED_SCHEMA_VERSION` is an alias for `CONVERSION_PLAN_SCHEMA_VERSION` (Step 3), this means the
renderer gates *manifest* compatibility (checked in `protocol.dispatch_render` against
`package.manifest.schema_version`) using the *conversion-plan* constant — passing today only because both
happen to equal `"1.0"`. The entire point of this task is to remove that kind of accidental coupling; left
as-is, it survives in the one place it actually runs at dispatch time. Fix:
```python
    supported_manifest_versions = frozenset({contracts.MANIFEST_SCHEMA_VERSION})
```

Add a test to `tests/unit/test_multipage_markdown.py` proving the two constants are no longer
interchangeable at this call site:
```python
def test_renderer_supported_versions_tracks_manifest_constant_not_plan_constant(monkeypatch):
    import contracts
    monkeypatch.setattr(contracts, "MANIFEST_SCHEMA_VERSION", "9.9")
    # Re-read the class attribute fresh rather than relying on import-time
    # caching -- reload the module so the frozenset is rebuilt against the
    # monkeypatched constant.
    import importlib
    import renderers.multipage_markdown as mpm
    importlib.reload(mpm)
    assert "9.9" in mpm.MultipageMarkdownRenderer.supported_manifest_versions
    assert "1.0" not in mpm.MultipageMarkdownRenderer.supported_manifest_versions
    importlib.reload(mpm)  # restore real state for any test running after this one
```

- [ ] **Step 6: Run test to verify it passes, then the full suite**

Run: `python3 -m pytest tests/contract/test_contracts.py::test_schema_version_constants_are_independent_per_contract tests/unit/test_multipage_markdown.py::test_renderer_supported_versions_tracks_manifest_constant_not_plan_constant -v`
Expected: PASS
Run: `python3 -m pytest tests/ -q`
Expected: all pass — every existing usage of `contracts.SUPPORTED_SCHEMA_VERSION` in tests still resolves
correctly via the backward-compatible alias.

- [ ] **Step 7: Commit**

```bash
git add scripts/contracts.py scripts/package.py scripts/publication_map.py scripts/plans.py scripts/renderers/multipage_markdown.py tests/contract/test_contracts.py tests/unit/test_multipage_markdown.py
git commit -m "refactor: split schema-version ownership per contract type; point renderer gate at manifest constant, not plan constant"
```

---

## Task 4: Resolve `PublicationMapEntry.chunk_id` Semantics; Remove `parent_topic_id`

**Files:**
- Modify: `scripts/contracts.py:436-462`
- Modify: `scripts/publication_map.py:20-38`
- Modify: `scripts/package.py:478` (the `build_publication_map` call site)
- Modify: `scripts/renderers/multipage_markdown.py:187-190`
- Test: `tests/unit/test_package.py`, `tests/unit/test_multipage_markdown.py`

**Interfaces:**
- Produces: `PublicationMapEntry.chunk_id` now holds the real logical chunk identifier (equal to
  `ChunkMetadata.chunk_id` for the chunk that topic consumes), not a content-file path.
  `PublicationMapEntry` no longer has a `parent_topic_id` field.
- Produces: `renderers/multipage_markdown.py` resolves publication-map entries via `entry.chunk_id`
  against `chunk.metadata.chunk_id` (previously: `entry.topic_id`).

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_package.py`:

```python
def test_grouped_publication_map_chunk_id_is_not_a_path(tmp_path):
    anchor = _anchor(["Alpha"], level=1)
    plan = _confirmed_plan([anchor], strategy="grouped")
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()
    sliced = SlicedDocument(
        preamble="", chunks=[_slice(anchor, "# Alpha\n\nBody text.\n")]
    )
    output_dir = tmp_path / "canonical-content"
    package.build_grouped_canonical_package(plan, sliced, raw_media_dir, output_dir)

    pub_map_data = json.loads((output_dir / "publication-map.json").read_text())
    entry = pub_map_data["entries"][0]
    # chunk_id must be the real chunk identifier, never a "chunks/....md" path.
    assert not entry["chunk_id"].startswith("chunks/")
    assert not entry["chunk_id"].endswith(".md")
    assert entry["chunk_id"] == entry["topic_id"]  # equal-in-practice for the grouped producer today
    assert "parent_topic_id" not in entry
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/unit/test_package.py::test_grouped_publication_map_chunk_id_is_not_a_path -v`
Expected: FAIL — `entry["chunk_id"]` is `"chunks/alpha--<hash>.md"` (a path), and `"parent_topic_id"` is
present (as `null`).

- [ ] **Step 3: Remove `parent_topic_id` and fix `chunk_id` semantics in the contract**

In `scripts/contracts.py`:
```python
@dataclass
class PublicationMapEntry:
    topic_id: str
    title: str
    order: int
    chunk_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "PublicationMapEntry":
        return cls(
            topic_id=_require(data, "topic_id"),
            title=_require(data, "title"),
            order=_require(data, "order"),
            chunk_id=_require(data, "chunk_id"),
        )

    def to_dict(self) -> dict:
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "order": self.order,
            "chunk_id": self.chunk_id,
        }
```

- [ ] **Step 4: Fix the builder**

In `scripts/publication_map.py`, `build_publication_map`'s signature drops `parent_topic_ids`:
```python
def build_publication_map(
    topic_boundaries: list,
    topic_chunk_ids: dict,
    package_identity: str,
) -> contracts.PublicationMap:
    entries = [
        contracts.PublicationMapEntry(
            topic_id=boundary.topic_id,
            title=boundary.title,
            order=index,
            chunk_id=topic_chunk_ids[boundary.topic_id],
        )
        for index, boundary in enumerate(topic_boundaries)
    ]
    return contracts.PublicationMap(
        schema_version=contracts.PUBLICATION_MAP_SCHEMA_VERSION,
        package_identity=package_identity,
        entries=entries,
    )
```

- [ ] **Step 5: Fix `package.py`'s caller to pass the real chunk_id, not the content-file path**

In `scripts/package.py`'s `build_grouped_canonical_package`, change the `topic_chunk_ids` dict to record
the logical chunk ID (which for the grouped producer is `boundary.topic_id` itself, since one topic maps
to exactly one chunk today) instead of the content-file path:
```python
        topic_chunk_ids[boundary.topic_id] = boundary.topic_id
```
(replacing the current `topic_chunk_ids[boundary.topic_id] = content_file` line) — and update the
`build_publication_map` call to drop the now-removed `parent_topic_ids` argument:
```python
    pub_map = publication_map.build_publication_map(
        boundaries, topic_chunk_ids, package_identity=manifest.plan_id
    )
```

- [ ] **Step 6: Fix the renderer's resolution logic**

In `scripts/renderers/multipage_markdown.py`, change:
```python
        if package.publication_map is not None:
            chunk_by_id = {chunk.metadata.chunk_id: chunk for chunk in package.chunks}
            ordered_entries = sorted(package.publication_map.entries, key=lambda e: e.order)
            ordered_chunks = [chunk_by_id[e.topic_id] for e in ordered_entries]
```
to:
```python
        if package.publication_map is not None:
            chunk_by_id = {chunk.metadata.chunk_id: chunk for chunk in package.chunks}
            ordered_entries = sorted(package.publication_map.entries, key=lambda e: e.order)
            ordered_chunks = [chunk_by_id[e.chunk_id] for e in ordered_entries]
```
This is the intentional behavior change flagged in the spec — resolution now goes through `chunk_id`
(the field meant to identify the chunk) rather than `topic_id` (which happened to also work only because
today's grouped producer keeps them equal).

- [ ] **Step 7: Update any test fixture that constructs a `PublicationMapEntry` with `parent_topic_id`**

`grep -rn "parent_topic_id" tests/` and remove that keyword argument from every `PublicationMapEntry(...)`
call found (this repo's Task 17-topic-grouping tests construct these directly in a few places).

- [ ] **Step 8: Run test to verify it passes, then the full suite**

Run: `python3 -m pytest tests/unit/test_package.py::test_grouped_publication_map_chunk_id_is_not_a_path -v`
Expected: PASS
Run: `python3 -m pytest tests/ -q`
Expected: all pass.

- [ ] **Step 9: Commit**

```bash
git add scripts/contracts.py scripts/publication_map.py scripts/package.py scripts/renderers/multipage_markdown.py tests/
git commit -m "fix: PublicationMapEntry.chunk_id holds a real chunk ID, not a path; remove unused parent_topic_id"
```

---

## Task 5: Add Missing Cross-Artifact Lineage Checks (Chunk `plan_id`/`source_sha256` vs. Manifest)

**Files:**
- Modify: `scripts/validate_canonical.py:311-353` (`_check_manifest_consistency`) or as a new helper called
  alongside it
- Test: `tests/unit/test_validate_canonical.py`

**Interfaces:**
- Produces: `validate_canonical_package` now also reports `_error("chunk_plan_id_mismatch", ...)` and
  `_error("chunk_source_sha256_mismatch", ...)` when a chunk sidecar's `plan_id`/`source_sha256` doesn't
  match the manifest's. This closes a real gap GPT 5.6's round-2 review found: the validator checked
  `meta.chunk_id` and `content_sha256` per chunk, but never cross-checked lineage identity fields.

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_validate_canonical.py` (mirror the existing fixture-building pattern already used
in that file for a minimal valid package, then corrupt one sidecar's `plan_id` before validating):

```python
def test_chunk_sidecar_plan_id_mismatch_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path)  # use this file's existing helper
    meta_path = next((package_dir / "chunks").glob("*.meta.json"))
    meta_data = json.loads(meta_path.read_text())
    meta_data["plan_id"] = "sha256:" + "0" * 64
    meta_path.write_text(json.dumps(meta_data))

    plan = _load_plan_used_to_build(package_dir)  # use this file's existing helper
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "chunk_plan_id_mismatch" for i in report.issues)


def test_chunk_sidecar_source_sha256_mismatch_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path)
    meta_path = next((package_dir / "chunks").glob("*.meta.json"))
    meta_data = json.loads(meta_path.read_text())
    meta_data["source_sha256"] = "f" * 64
    meta_path.write_text(json.dumps(meta_data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "chunk_source_sha256_mismatch" for i in report.issues)
```

If `_build_minimal_valid_package`/`_load_plan_used_to_build` helpers don't already exist in
`tests/unit/test_validate_canonical.py` under those exact names, read the file's existing fixture-building
tests first and either reuse whatever helper it already has for constructing a valid package + plan pair,
or write one following the exact same pattern the file's other tests already use — do not invent a
different construction path.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/unit/test_validate_canonical.py::test_chunk_sidecar_plan_id_mismatch_is_detected tests/unit/test_validate_canonical.py::test_chunk_sidecar_source_sha256_mismatch_is_detected -v`
Expected: both FAIL — `report.status` is still `"PASS"` (or whatever it currently resolves to) because
nothing checks these fields yet.

- [ ] **Step 3: Add the checks**

In `scripts/validate_canonical.py`'s `_load_and_check_chunks`, after the existing `chunk_id_mismatch` and
`content_hash_mismatch` checks (right after the `content_hash_mismatch` block, before the `empty_chunk`
check), add:

```python
        if meta.plan_id != manifest.plan_id:
            issues.append(_error(
                "chunk_plan_id_mismatch",
                f"chunk {chunk.chunk_id!r} sidecar plan_id={meta.plan_id!r} "
                f"does not match manifest plan_id={manifest.plan_id!r}",
                chunk.metadata_file,
            ))

        if meta.source_sha256 != manifest.source.sha256:
            issues.append(_error(
                "chunk_source_sha256_mismatch",
                f"chunk {chunk.chunk_id!r} sidecar source_sha256="
                f"{meta.source_sha256!r} does not match manifest source "
                f"sha256={manifest.source.sha256!r}",
                chunk.metadata_file,
            ))
```

`_load_and_check_chunks`'s signature already receives `manifest` as a parameter (confirmed from the current
function signature `_load_and_check_chunks(package_dir: "Path", manifest: "contracts.Manifest")`), so
`manifest.plan_id`/`manifest.source.sha256` are already in scope — no signature change needed.

- [ ] **Step 4: Run test to verify it passes, then the full suite**

Run: `python3 -m pytest tests/unit/test_validate_canonical.py -v`
Expected: all pass, including the two new tests.
Run: `python3 -m pytest tests/ -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_canonical.py tests/unit/test_validate_canonical.py
git commit -m "feat: validate chunk sidecar plan_id/source_sha256 lineage against manifest"
```

---

## Task 6: Malformed Publication-Map Handling and Unexpected-Present Policy

**Files:**
- Modify: `scripts/publication_map.py:50-54` (`load_publication_map`)
- Modify: `scripts/validate_canonical.py:602-639` (`_check_publication_map_consistency`)
- Test: `tests/unit/test_publication_map.py`, `tests/unit/test_validate_canonical.py`

**Interfaces:**
- Produces: `publication_map.load_publication_map(package_dir)` now raises
  `publication_map.MalformedPublicationMapError` (new exception) instead of letting
  `json.JSONDecodeError`/`ValueError` propagate uncaught, for malformed JSON, a missing required field, or
  an unsupported schema version.
- Produces: `validate_canonical.py`'s `_check_publication_map_consistency` catches that exception and
  reports it as a controlled `_error("malformed_publication_map", ...)` — never an uncaught exception.
- Produces: a `"single"`/`"chunked"`-strategy package that has an (unexpected) `publication-map.json` on
  disk now gets `_error("unexpected_publication_map", ...)` — decided policy: reject, don't silently
  ignore.

- [ ] **Step 1: Write the failing tests**

Add to `tests/unit/test_publication_map.py` (check this file's existing import/fixture style first; if it
doesn't exist yet, create it following `tests/unit/test_package.py`'s style):

```python
def test_load_publication_map_raises_controlled_error_on_malformed_json(tmp_path):
    (tmp_path / "publication-map.json").write_text("{not valid json")
    with pytest.raises(publication_map.MalformedPublicationMapError):
        publication_map.load_publication_map(tmp_path)


def test_load_publication_map_raises_controlled_error_on_missing_field(tmp_path):
    (tmp_path / "publication-map.json").write_text(json.dumps({"schema_version": "1.0"}))
    with pytest.raises(publication_map.MalformedPublicationMapError):
        publication_map.load_publication_map(tmp_path)
```

Add to `tests/unit/test_validate_canonical.py`:

```python
def test_malformed_publication_map_is_a_controlled_validation_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    (package_dir / "publication-map.json").write_text("{not valid json")

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "malformed_publication_map" for i in report.issues)


def test_unexpected_publication_map_on_non_grouped_package_is_rejected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="chunked")
    (package_dir / "publication-map.json").write_text(json.dumps({
        "schema_version": "1.0",
        "package_identity": "sha256:" + "a" * 64,
        "entries": [],
    }))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "unexpected_publication_map" for i in report.issues)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/unit/test_publication_map.py tests/unit/test_validate_canonical.py -k "malformed or unexpected" -v`
Expected: all four FAIL — `load_publication_map` raises raw `json.JSONDecodeError`/`ValueError` (not the
new controlled exception, so `pytest.raises(MalformedPublicationMapError)` fails to match), and the
canonical validator currently has no check at all for the non-grouped case.

- [ ] **Step 3: Add the controlled exception in `publication_map.py`**

```python
class MalformedPublicationMapError(Exception):
    """publication-map.json exists but is malformed JSON, missing a
    required field, or an unsupported schema version -- raised as a
    controlled exception so callers (validate_canonical.py) can report it
    as a ValidationIssue instead of letting a raw json/ValueError escape."""


def load_publication_map(package_dir):
    path = Path(package_dir) / _FILENAME
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text())
        return contracts.PublicationMap.from_dict(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise MalformedPublicationMapError(
            f"{path} is malformed: {exc}"
        ) from exc
```

- [ ] **Step 4: Catch it in the canonical validator and add the unexpected-present check**

In `scripts/validate_canonical.py`, change `_check_publication_map_consistency`:
```python
def _check_publication_map_consistency(
    package_dir: "Path", manifest: "contracts.Manifest"
) -> list:
    if manifest.strategy != "grouped":
        try:
            unexpected = publication_map.load_publication_map(package_dir)
        except publication_map.MalformedPublicationMapError:
            # A malformed file on a non-grouped package is still an
            # "unexpected file present" problem, not this check's job to
            # diagnose further -- report the same unexpected-presence issue.
            unexpected = True
        if unexpected is not None:
            return [_error(
                "unexpected_publication_map",
                "publication-map.json is present but strategy is not "
                "'grouped' -- an unexpected file is not silently ignored",
                "publication-map.json",
            )]
        return []

    try:
        pub_map = publication_map.load_publication_map(package_dir)
    except publication_map.MalformedPublicationMapError as exc:
        return [_error("malformed_publication_map", str(exc), "publication-map.json")]

    if pub_map is None:
        return [_error(
            "missing_publication_map",
            "strategy=grouped requires publication-map.json",
            "publication-map.json",
        )]

    issues = []
    manifest_chunk_ids = {c.chunk_id for c in manifest.chunks}
    # Round-3 review (Opus) caught a load-bearing defect in an earlier draft
    # of this check: it compared `manifest_chunk_ids` against
    # `{e.topic_id for e in pub_map.entries}`, while Task 4 made the
    # RENDERER resolve entries via `entry.chunk_id` instead. That meant the
    # renderer consumed a field this validator never checked at all --
    # today harmless only because the grouped producer happens to set
    # `chunk_id == topic_id`, but the moment they diverge the renderer
    # keys off an unvalidated field. This check now validates `chunk_id`,
    # matching what the renderer actually consumes, and separately confirms
    # every `topic_id` is unique (the publication ordering identity) and
    # every `chunk_id` resolves to exactly one manifest chunk.
    entry_topic_ids = [e.topic_id for e in pub_map.entries]
    if len(set(entry_topic_ids)) != len(entry_topic_ids):
        issues.append(_error(
            "publication_map_duplicate_topic_id",
            "publication-map.json has a duplicate topic_id across entries",
            "publication-map.json",
        ))

    entry_chunk_ids = [e.chunk_id for e in pub_map.entries]
    if len(set(entry_chunk_ids)) != len(entry_chunk_ids):
        issues.append(_error(
            "publication_map_duplicate_chunk_id",
            "publication-map.json has a duplicate chunk_id across entries",
            "publication-map.json",
        ))
    if set(entry_chunk_ids) != manifest_chunk_ids:
        issues.append(_error(
            "publication_map_chunk_mismatch",
            "publication-map.json entries' chunk_id values do not match "
            "manifest chunk ids -- every entry.chunk_id must resolve to "
            "exactly one manifest chunk, and every manifest chunk must be "
            "covered exactly once",
            "publication-map.json",
        ))

    orders = sorted(e.order for e in pub_map.entries)
    if orders != list(range(len(orders))):
        issues.append(_error(
            "publication_map_order_invalid",
            "publication-map.json entry order must be a contiguous "
            "0..N-1 sequence with no gaps or duplicates",
            "publication-map.json",
        ))
    return issues
```

- [ ] **Step 5: Write the mutation test proving `chunk_id`/`topic_id` divergence is actually caught**

Add to `tests/unit/test_validate_canonical.py` (this is the test round-3 review demanded — today's grouped
producer keeps `chunk_id == topic_id`, so without this test the new check in Step 4 would be exercised only
in the equal case, never proving it actually looks at `chunk_id` independently):

```python
def test_publication_map_chunk_id_diverging_from_topic_id_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    # Deliberately break the chunk_id/topic_id equality the real producer
    # currently maintains -- chunk_id now points at a chunk that does not
    # exist in the manifest at all, proving the validator checks chunk_id
    # itself rather than trusting topic_id as a stand-in for it.
    data["entries"][0]["chunk_id"] = "nonexistent-chunk-id"
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "publication_map_chunk_mismatch" for i in report.issues)
```

- [ ] **Step 6: Run tests to verify they pass, then the full suite**

Run: `python3 -m pytest tests/unit/test_publication_map.py tests/unit/test_validate_canonical.py -k "malformed or unexpected or chunk_id_diverging" -v`
Expected: all PASS
Run: `python3 -m pytest tests/ -q`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add scripts/publication_map.py scripts/validate_canonical.py tests/unit/test_publication_map.py tests/unit/test_validate_canonical.py
git commit -m "feat: validate publication-map chunk_id (not topic_id) resolves to manifest chunks; handle malformed/unexpected publication-map.json"
```

---

## Task 7: Decisively Close the Content-Comparison-Skip Loophole

**Files:**
- Modify: `scripts/validate_canonical.py:167-220, 646-676`
- Modify: `scripts/convert.py` (the one real caller of `validate_canonical_package`)
- Test: `tests/unit/test_validate_canonical.py`

**Interfaces:**
- Produces: `validate_canonical_package(package_dir, plan, source_path=None, cleaned_markdown_text=None)` —
  **no new caller-supplied boolean parameter.** Round-3 review (GPT 5.6 blocking #3) correctly flagged that
  an earlier draft's `is_independent_fixture: bool` argument was a trust bypass — any caller could label an
  arbitrary real package "independent fixture" and suppress the required content comparison. Opus's
  round-3 refinement (adopted here) is more precise: the distinction must live in the **package's own
  recorded provenance**, not a caller argument. Concretely: `contracts.ManifestGenerator.plugin` already
  distinguishes producer identity (`"docx-to-content"` for every real conversion, confirmed in
  `package.py`'s two builders). The validator now derives independence from **that field on the loaded
  manifest itself** — a package cannot claim to be an independent fixture unless its own manifest says so,
  and that manifest is exactly what schema-validates and gets hash-checked elsewhere in this pipeline.

- [ ] **Step 1: Write the failing test**

Add to `tests/unit/test_validate_canonical.py`:

```python
def test_producer_path_content_comparison_skip_is_now_an_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path)  # generator.plugin == "docx-to-content"
    plan = _load_plan_used_to_build(package_dir)
    # cleaned_markdown_text omitted -- this package's own manifest records
    # generator.plugin == "docx-to-content", so it's a producer-path
    # package regardless of what any caller might wish were true.
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(
        i.code == "content_comparison_skipped" and i.severity == "error"
        for i in report.issues
    )


def test_fixture_provenance_content_comparison_skip_is_not_an_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, generator_plugin="hand-authored-fixture")
    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status != "FAIL" or not any(
        i.code == "content_comparison_skipped" for i in report.issues
    )
```

`_build_minimal_valid_package` needs a `generator_plugin: str = "docx-to-content"` keyword argument
(passed straight through to the `ManifestGenerator(plugin=...)` it constructs) if it doesn't already
support one — add it to the shared helper in `tests/unit/test_validate_canonical.py` if missing.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/unit/test_validate_canonical.py -k content_comparison_skip -v`
Expected: the first test FAILS (current behavior returns WARN, not error, for
`content_comparison_skipped` regardless of provenance). The second may already pass by coincidence —
confirm, don't assume.

- [ ] **Step 3: Implement the decisive, provenance-derived policy**

In `scripts/validate_canonical.py`, change `_check_content_loss_and_duplication`'s signature and the skip
branch — note it now takes `manifest` (already a parameter) and derives independence from it, no new
boolean parameter at all:
```python
_FIXTURE_GENERATOR_PLUGIN = "hand-authored-fixture"


def _check_content_loss_and_duplication(
    package_dir: "Path",
    manifest: "contracts.Manifest",
    cleaned_markdown_text: "str | None",
) -> list:
    is_independent_fixture = manifest.generator.plugin == _FIXTURE_GENERATOR_PLUGIN
    if cleaned_markdown_text is None:
        if is_independent_fixture:
            return []  # no source conversion exists to compare against; not a gap for this kind of package
        return [_error(
            "content_comparison_skipped",
            "no cleaned_markdown_text was supplied for a producer-path "
            "package (manifest.generator.plugin="
            f"{manifest.generator.plugin!r}); the normalized aggregate "
            "content-loss/duplication comparison did not run -- a "
            "producer-generated package cannot be promoted as fully "
            "accepted without this comparison having actually run and "
            "passed",
        )]
    ...  # rest unchanged
```
`validate_canonical_package`'s own signature is unchanged from today (`package_dir, plan, source_path=None,
cleaned_markdown_text=None`) — it already passes `manifest` into
`_check_content_loss_and_duplication(package_dir, manifest, cleaned_markdown_text)`, so no signature change
propagates to its callers.

Add `_FIXTURE_GENERATOR_PLUGIN` to `canonical_package.py` too (Task 8) — no, on reflection this constant is
only consumed by `validate_canonical.py`; Task 13's fixture only needs to know the literal string
`"hand-authored-fixture"` to construct its manifest with, which this task's docstring/constant makes
discoverable without duplicating the constant into a second module.

- [ ] **Step 4: Confirm `convert.py`'s real caller is unaffected**

`convert.py`'s `convert_and_promote` always supplies `cleaned_markdown_text` — confirmed directly this
session by reading `_run_conversion_pipeline`/`convert_and_promote` in full: `_run_conversion_pipeline`
unconditionally returns `(manifest, text_without_preamble)`, and `convert_and_promote` unconditionally
passes that `cleaned_text` into `validate_canonical.validate_canonical_package(package_staging_dir, plan,
source_path=source, cleaned_markdown_text=cleaned_text)` — there is no branch anywhere in that path that
omits it. So the real producer path never hits the skip branch at all; this task's error-vs-note decision
only matters for direct/test/fixture invocations of `validate_canonical_package`, exactly as intended. This
also means Task 16's real CLI-driven `convert` regeneration is unaffected by this task — the two are not
the "cross-task landmine" an earlier draft risked, precisely because this was verified against the actual
code rather than assumed.

- [ ] **Step 5: Run tests to verify they pass, then the full suite**

Run: `python3 -m pytest tests/unit/test_validate_canonical.py -k content_comparison_skip -v`
Expected: both PASS
Run: `python3 -m pytest tests/ -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_canonical.py tests/unit/test_validate_canonical.py
git commit -m "feat: producer-path canonical packages cannot skip content-comparison and still be accepted

Independence is derived from the package's own manifest.generator.plugin
provenance field, not a caller-supplied boolean -- a caller cannot label
an arbitrary real package as an independent fixture to suppress the
check."
```

---

## Task 8: Split `package.py` — Extract the Read-Only `CanonicalPackage` Loader

**Files:**
- Create: `scripts/canonical_package.py`
- Modify: `scripts/package.py` (remove everything from the "Task 12" section onward)
- Modify: `scripts/renderers/protocol.py:44`
- Test: `tests/unit/test_package_load.py` (update its import), any other test importing `CanonicalPackage`
  from `package`

**Interfaces:**
- Consumes: `publication_map.MalformedPublicationMapError` (Task 6 must run before this task — it defines
  this exception, which `load()`'s new publication-map re-validation below catches).
- Produces: `canonical_package.CanonicalPackage`, `canonical_package.LoadedChunk`,
  `canonical_package.CanonicalPackageError`, `canonical_package.CanonicalPackageValidationError`,
  `canonical_package.CanonicalPackageIntegrityError`, `canonical_package.CanonicalPackage.load(package_dir)`
  — relocated from `package.py`, but **not merely relocated**: per round-3 review, `load()` now also
  independently re-derives (rather than trusting) validation-report lineage
  (`plan_id`/`source_sha256` vs. the manifest) and full publication-map integrity (present-when-required,
  identity match, `chunk_id` resolution, order contiguity, absent-when-not-grouped) — closing the Layer-2
  trust-boundary gap round 3 found. `package.py` no longer defines any of these; it retains
  `build_canonical_package`, `build_grouped_canonical_package`, `rewrite_media_and_copy`,
  `extract_media_refs`, `MediaError` and its subclasses, `_decode_and_validate`.

- [ ] **Step 1: Write the failing test (import-location proof)**

Add to `tests/unit/test_package_load.py` at the top of the file (adjust the existing import if this file
currently does `from package import CanonicalPackage` — check first):

```python
def test_canonical_package_importable_from_new_module():
    from canonical_package import CanonicalPackage
    assert hasattr(CanonicalPackage, "load")


def test_canonical_package_no_longer_defined_in_package_module():
    import package
    assert not hasattr(package, "CanonicalPackage")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/unit/test_package_load.py::test_canonical_package_importable_from_new_module tests/unit/test_package_load.py::test_canonical_package_no_longer_defined_in_package_module -v`
Expected: the first FAILS with `ModuleNotFoundError: No module named 'canonical_package'`; the second
currently FAILS too (`package.CanonicalPackage` exists today).

- [ ] **Step 3: Create `scripts/canonical_package.py`**

Move the entire block from `package.py` starting at the comment
`# Task 12 — CanonicalPackage: renderer-side loader` (the module-level comment before
`class CanonicalPackageError`) through the end of `CanonicalPackage.load()` into the new file, with its own
imports:

```python
"""
canonical_package.py
=====================

The read-only, renderer-side consumer of a promoted canonical-content
package (moved out of package.py during Phase 2's contract hardening).
Renderers (and anything else that only needs to READ an already-promoted
package) import from HERE, never from package.py -- package.py retains
only the producer/builder functions (build_canonical_package,
build_grouped_canonical_package), which depend on topic_grouping and other
analysis-side modules. This module depends on none of that: keeping the
two responsibilities in separate files is what makes the import-boundary
test in tests/unit/test_import_boundaries.py actually mean something --
see that test's docstring for the full rationale (a renderer that
imported `package.CanonicalPackage` transitively pulled in
`topic_grouping`, a producer/analysis concern, even though the renderer
code itself never referenced it directly).

CanonicalPackage.load() is a SECOND, independent integrity check at load
time, on top of whatever validate_canonical.py already recorded in
validation.json at convert time -- defense against the promoted package
having been tampered with or corrupted on disk since promotion.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import contracts  # noqa: E402
import dispositions  # noqa: E402
import hashing  # noqa: E402
import publication_map  # noqa: E402

# Round-3 review (GPT 5.6 blocking #4/#5, confirmed independently by Opus):
# an earlier draft of this module trusted validation.json's status without
# cross-checking its OWN lineage fields against the manifest it claims to
# describe, and loaded publication-map.json without re-enforcing any of
# the same-invariants validate_canonical.py already checked at convert
# time. Both are real post-promotion tamper surfaces: a PASS report copied
# from a different package, or a publication-map.json edited/deleted after
# promotion, would otherwise silently authorize a package that never
# actually passed those checks. load() now re-derives both, independent of
# whatever validate_canonical.py recorded -- this is the whole point of
# Layer 2 existing as a SEPARATE check from Layer 1.


class CanonicalPackageError(Exception):
    """Base class for `CanonicalPackage.load()` failures. Raised, never
    swallowed into a null/error field -- a renderer receiving a
    `CanonicalPackage` instance can assume it has already been fully
    vetted."""


class CanonicalPackageValidationError(CanonicalPackageError):
    """The package's manifest/validation.json failed schema validation, or
    its validation status is FAIL, or WARN without a disposition file that
    accounts for every warning."""


class CanonicalPackageIntegrityError(CanonicalPackageError):
    """A chunk's on-disk content no longer matches its sidecar's recorded
    `content_sha256`, or a chunk's media reference does not resolve to a
    file under `media/` -- i.e. the package was tampered with or corrupted
    on disk after promotion."""


def _media_ref_to_filename(ref: str) -> str:
    """Reverse `package.rewrite_media_and_copy`'s `../media/<quoted-name>`
    rewrite back to the plain on-disk filename under `media/`."""
    prefix = "../media/"
    name = ref[len(prefix):] if ref.startswith(prefix) else ref
    return unquote(name)


@dataclass(frozen=True)
class LoadedChunk:
    """One chunk's metadata and content, already loaded into memory and
    hash-verified by `CanonicalPackage.load()`."""

    metadata: "contracts.ChunkMetadata"
    content: str


@dataclass(frozen=True)
class CanonicalPackage:
    """A fully vetted, in-memory view of an ACCEPTED canonical-content
    package. Only ever constructed via `CanonicalPackage.load()` -- never
    built by a renderer directly."""

    manifest: "contracts.Manifest"
    validation_report: "contracts.ValidationReport"
    chunks: list  # list[LoadedChunk], in manifest order
    media_dir: Path
    package_dir: Path
    publication_map: "object" = None

    @classmethod
    def load(cls, package_dir: Path) -> "CanonicalPackage":
        """Load and fully re-validate an ACCEPTED canonical package at
        `package_dir`. Raises `CanonicalPackageError` (or a subclass) on
        any failure -- never returns a partially-valid package."""
        package_dir = Path(package_dir)

        manifest_path = package_dir / "manifest.json"
        if not manifest_path.exists():
            raise CanonicalPackageValidationError(f"{manifest_path} does not exist")
        try:
            manifest = contracts.Manifest.from_dict(json.loads(manifest_path.read_text()))
        except (ValueError, json.JSONDecodeError) as exc:
            raise CanonicalPackageValidationError(
                f"manifest.json failed schema validation: {exc}"
            ) from exc

        validation_path = package_dir / "validation.json"
        if not validation_path.exists():
            raise CanonicalPackageValidationError(f"{validation_path} does not exist")
        try:
            validation_report = contracts.ValidationReport.from_dict(
                json.loads(validation_path.read_text())
            )
        except (ValueError, json.JSONDecodeError) as exc:
            raise CanonicalPackageValidationError(
                f"validation.json failed schema validation: {exc}"
            ) from exc

        if validation_report.status == "FAIL":
            raise CanonicalPackageValidationError(
                f"{package_dir} has validation status FAIL -- not renderable"
            )
        if validation_report.status == "WARN":
            disposition_path = package_dir / "warning-disposition.json"
            check = dispositions.apply_disposition(validation_report, disposition_path)
            if not check.promotable:
                undispositioned = [dispositions.disposition_key(w) for w in check.undispositioned]
                raise CanonicalPackageValidationError(
                    f"{package_dir} has validation status WARN with "
                    f"undispositioned warnings: {undispositioned}"
                )

        # Lineage cross-check: validation.json must actually describe THIS
        # manifest, not merely have a PASS/WARN status -- a validation
        # report copied or left over from a different package must not
        # silently authorize this one.
        if validation_report.plan_id != manifest.plan_id:
            raise CanonicalPackageIntegrityError(
                f"validation.json plan_id={validation_report.plan_id!r} does "
                f"not match manifest.json plan_id={manifest.plan_id!r} -- "
                "the validation report does not describe this package"
            )
        if validation_report.source_sha256 != manifest.source.sha256:
            raise CanonicalPackageIntegrityError(
                f"validation.json source_sha256={validation_report.source_sha256!r} "
                f"does not match manifest.json source.sha256="
                f"{manifest.source.sha256!r} -- the validation report does "
                "not describe this package"
            )

        loaded_chunks = []
        for manifest_chunk in manifest.chunks:
            content_path = package_dir / manifest_chunk.content_file
            metadata_path = package_dir / manifest_chunk.metadata_file
            if not content_path.exists():
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: missing content file {content_path}"
                )
            if not metadata_path.exists():
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: missing metadata file {metadata_path}"
                )

            content = content_path.read_text()
            try:
                metadata = contracts.ChunkMetadata.from_dict(json.loads(metadata_path.read_text()))
            except (ValueError, json.JSONDecodeError) as exc:
                raise CanonicalPackageValidationError(
                    f"chunk {manifest_chunk.chunk_id!r}: metadata failed schema validation: {exc}"
                ) from exc

            recomputed_hash = hashing.content_hash(content.encode("utf-8"))
            if recomputed_hash != metadata.content_sha256:
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: content hash mismatch "
                    f"(sidecar says {metadata.content_sha256}, on-disk content "
                    f"hashes to {recomputed_hash}) -- package may have been "
                    "tampered with or corrupted since promotion"
                )

            for ref in metadata.media_refs:
                media_path = package_dir / "media" / _media_ref_to_filename(ref)
                if not media_path.exists():
                    raise CanonicalPackageIntegrityError(
                        f"chunk {manifest_chunk.chunk_id!r}: media reference "
                        f"{ref!r} does not resolve to a file under "
                        f"{package_dir / 'media'}"
                    )

            loaded_chunks.append(LoadedChunk(metadata=metadata, content=content))

        pub_map = None
        if manifest.strategy == "grouped":
            try:
                pub_map = publication_map.load_publication_map(package_dir)
            except publication_map.MalformedPublicationMapError as exc:
                raise CanonicalPackageValidationError(
                    f"publication-map.json is malformed: {exc}"
                ) from exc

            if pub_map is None:
                raise CanonicalPackageValidationError(
                    f"{package_dir} has strategy='grouped' but "
                    "publication-map.json is missing -- required at load "
                    "time, not only at convert time"
                )

            if pub_map.package_identity != manifest.plan_id:
                raise CanonicalPackageIntegrityError(
                    f"publication-map.json package_identity="
                    f"{pub_map.package_identity!r} does not match "
                    f"manifest.json plan_id={manifest.plan_id!r} -- the "
                    "publication map does not describe this package"
                )

            manifest_chunk_ids = {c.chunk_id for c in manifest.chunks}
            entry_chunk_ids = [e.chunk_id for e in pub_map.entries]
            if len(set(entry_chunk_ids)) != len(entry_chunk_ids):
                raise CanonicalPackageIntegrityError(
                    "publication-map.json has a duplicate chunk_id across entries"
                )
            if set(entry_chunk_ids) != manifest_chunk_ids:
                raise CanonicalPackageIntegrityError(
                    "publication-map.json entries' chunk_id values do not "
                    "match manifest chunk ids -- may have been edited or "
                    "corrupted after promotion"
                )
            orders = sorted(e.order for e in pub_map.entries)
            if orders != list(range(len(orders))):
                raise CanonicalPackageIntegrityError(
                    "publication-map.json entry order is not a contiguous "
                    "0..N-1 sequence -- may have been edited or corrupted "
                    "after promotion"
                )
        elif publication_map.load_publication_map(package_dir) is not None:
            # Non-grouped package with an unexpected publication-map.json
            # present -- validate_canonical.py already rejects this at
            # convert time (Task 6), but load() re-checks independently
            # since the file could have been added after promotion.
            raise CanonicalPackageValidationError(
                f"{package_dir} has strategy={manifest.strategy!r} but an "
                "unexpected publication-map.json is present"
            )

        return cls(
            manifest=manifest,
            validation_report=validation_report,
            chunks=loaded_chunks,
            media_dir=package_dir / "media",
            package_dir=package_dir,
            publication_map=pub_map,
        )
```

- [ ] **Step 4: Remove the moved block from `package.py`**

Delete everything from the `# ---... Task 12 — CanonicalPackage: renderer-side loader` comment through the
end of the file in `scripts/package.py` (the `CanonicalPackageError`/`CanonicalPackageValidationError`/
`CanonicalPackageIntegrityError`/`_media_ref_to_filename`/`LoadedChunk`/`CanonicalPackage` definitions) —
`package.py` now ends after `build_grouped_canonical_package`'s `return manifest`.

- [ ] **Step 5: Update `renderers/protocol.py`'s import**

Change:
```python
from package import CanonicalPackage
```
to:
```python
from canonical_package import CanonicalPackage
```

- [ ] **Step 6: Update every other importer of `CanonicalPackage` from `package`**

Run `grep -rln "from package import CanonicalPackage\|package\.CanonicalPackage" scripts/ tests/` and update
each hit to import from `canonical_package` instead. Based on this session's earlier reads, this includes
at minimum `tests/unit/test_package_load.py` and any renderer test that constructs/loads a
`CanonicalPackage` directly (`tests/unit/test_multipage_markdown.py`,
`tests/unit/test_validate_rendered.py`) — read each file's current import line before changing it.

- [ ] **Step 7: Run tests to verify they pass, then the full suite**

Run: `python3 -m pytest tests/unit/test_package_load.py -v`
Expected: all pass, including the two new tests from Step 1. This should also hold for the new
lineage/publication-map checks added to `load()` above without any additional fixture changes: every
package a legitimate test already builds is internally self-consistent (a real `validate_canonical.py` run
or a hand-constructed fixture that matches its own manifest), so the new checks are newly *enforced*, not
newly *triggered* by anything already in the suite.
Run: `python3 -m pytest tests/ -q`
Expected: all pass. If anything now fails here, it means an existing test fixture was already
internally inconsistent (e.g. a hand-built `validation.json` with a `plan_id` that never matched its
`manifest.json`) and happened to pass only because nothing checked it before — fix the fixture to be
consistent, don't loosen the new check.

- [ ] **Step 8: Commit**

```bash
git add scripts/package.py scripts/canonical_package.py scripts/renderers/protocol.py tests/
git commit -m "refactor: extract CanonicalPackage loader into canonical_package.py; harden load() to re-derive validation-report lineage and publication-map integrity independently"
```

---

## Task 9: Transitive Import-Boundary Test

**Files:**
- Create: `tests/unit/test_import_boundaries.py`

**Interfaces:**
- Consumes: nothing new — uses only `ast` (stdlib) to statically parse import statements.
- Produces: a reusable `_transitive_imports(module_name: str, scripts_dir: Path) -> set[str]` test helper
  and a test asserting the renderer side never transitively reaches a forbidden module.

- [ ] **Step 1: Write the test (this task is the test — there's no separate "implementation" to write
  first, since the import boundary was already fixed by Task 8's module split; this test is the proof)**

```python
"""
test_import_boundaries.py
==========================

Proves, via static analysis of the actual import graph (not just each
module's own direct import statements), that renderer-side code never
transitively reaches a DOCX-analysis/producer module. A DIRECT-import-only
check would have missed the real defect this repo found: renderers/protocol.py
imports CanonicalPackage from package.py, and package.py (before Phase 2's
Task 8 split) itself imported topic_grouping -- a producer/analysis concern
-- so a check that only inspected renderers/'s own import statements would
have passed while the dependency chain still pulled in topic_grouping.

Round-3 review (GPT 5.6 issue #11, confirmed by Opus) found the first draft
of `_direct_imports` truncated every dotted import to its first component
(`node.module.split(".")[0]`), so `from renderers import multipage_markdown`
was recorded as just `"renderers"` -- silently losing the submodule. This
version resolves `from X import Y` to `X.Y` whenever `X.Y` is itself a real
local submodule (not merely an attribute defined inside `X`'s own file),
and includes a negative-control test proving the checker itself would
catch a real forbidden edge, not just happening to find none today.
"""

import ast
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _THIS_DIR.parent.parent / "scripts"

_FORBIDDEN_MODULES = {
    "analyze_structure", "pandoc_fixes", "convert", "plans", "chunking",
    "emf_convert", "topic_grouping", "package",  # package.py = builders only now
}

_ENTRY_MODULES = {
    "renderers.protocol", "renderers.multipage_markdown", "renderers.validate_rendered",
    "canonical_package",
}


def _module_path(module_name: str) -> "Path | None":
    """Resolve a dotted module name to a real .py file under scripts_dir,
    trying both `<parts>.py` and `<parts>/__init__.py` -- or None if it
    doesn't resolve locally (e.g. it's a stdlib module)."""
    parts = module_name.split(".")
    candidate = _SCRIPTS_DIR.joinpath(*parts).with_suffix(".py")
    if candidate.exists():
        return candidate
    init_candidate = _SCRIPTS_DIR.joinpath(*parts, "__init__.py")
    if init_candidate.exists():
        return init_candidate
    return None


def _direct_imports(module_path: Path) -> set:
    """Return every LOCALLY RESOLVABLE dotted module name this file
    directly imports -- e.g. {"renderers.multipage_markdown", "contracts"},
    never truncated to a package's first component when the real target is
    a submodule."""
    tree = ast.parse(module_path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            base = node.module
            for alias in node.names:
                dotted = f"{base}.{alias.name}"
                if _module_path(dotted) is not None:
                    # `from X import Y` where Y is itself a real submodule
                    # of X (e.g. `from renderers import multipage_markdown`)
                    # -- record the FULL dotted path, not just `base`.
                    names.add(dotted)
                else:
                    # Y is an attribute/name defined inside X's own file
                    # (e.g. `from contracts import RenderResult`) -- X
                    # itself is still the thing that gets imported/executed.
                    names.add(base)
    return names


def _transitive_imports(module_name: str, seen: set = None) -> set:
    seen = seen if seen is not None else set()
    if module_name in seen:
        return seen
    seen.add(module_name)
    path = _module_path(module_name)
    if path is None:
        return seen  # unresolvable locally (e.g. stdlib) -- harmless, nothing further to walk
    for imported in _direct_imports(path):
        if imported == module_name:
            continue
        _transitive_imports(imported, seen)
    return seen


def test_renderer_side_never_transitively_imports_a_forbidden_module():
    for entry in _ENTRY_MODULES:
        transitive = _transitive_imports(entry)
        forbidden_hit = transitive & _FORBIDDEN_MODULES
        assert not forbidden_hit, (
            f"{entry!r} transitively imports forbidden module(s) {forbidden_hit} "
            f"-- full transitive closure: {sorted(transitive)}"
        )


def test_checker_detects_a_synthetic_forbidden_transitive_edge(tmp_path, monkeypatch):
    """Negative control (round-3 review's explicit ask): prove this checker
    would actually catch a forbidden edge, not merely that it found none in
    the real graph today. Builds a tiny synthetic three-module chain
    (entry -> middle -> forbidden) in an isolated directory and asserts the
    transitive walk surfaces the forbidden module."""
    synthetic_scripts_dir = tmp_path / "scripts"
    synthetic_scripts_dir.mkdir()
    (synthetic_scripts_dir / "entry_module.py").write_text("from middle_module import thing\n")
    (synthetic_scripts_dir / "middle_module.py").write_text("import forbidden_module\nthing = 1\n")
    (synthetic_scripts_dir / "forbidden_module.py").write_text("x = 1\n")

    import test_import_boundaries as tib
    monkeypatch.setattr(tib, "_SCRIPTS_DIR", synthetic_scripts_dir)

    transitive = tib._transitive_imports("entry_module")
    assert "forbidden_module" in transitive


def test_checker_correctly_resolves_from_package_import_submodule(tmp_path, monkeypatch):
    """Round-3 review's exact reported bug: `from X import Y` where Y is a
    real submodule of X must resolve to `X.Y`, not truncate to `X` alone
    and silently lose which submodule was actually reached."""
    synthetic_scripts_dir = tmp_path / "scripts"
    package_dir = synthetic_scripts_dir / "pkg"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("")
    (package_dir / "sub.py").write_text("import forbidden_module\n")
    (synthetic_scripts_dir / "forbidden_module.py").write_text("x = 1\n")
    (synthetic_scripts_dir / "entry_module.py").write_text("from pkg import sub\n")

    import test_import_boundaries as tib
    monkeypatch.setattr(tib, "_SCRIPTS_DIR", synthetic_scripts_dir)

    direct = tib._direct_imports(synthetic_scripts_dir / "entry_module.py")
    assert "pkg.sub" in direct  # not truncated to just "pkg"
    transitive = tib._transitive_imports("entry_module")
    assert "forbidden_module" in transitive
```

- [ ] **Step 2: Run the tests**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_import_boundaries.py -v`
Expected: all four PASS — the two negative-control tests prove the checker itself works, and
`test_renderer_side_never_transitively_imports_a_forbidden_module` passes now that Task 8 has split
`package.py`. If the real-graph test fails, that means Task 8's split left a residual dependency — check
which forbidden module the failure names, and confirm Task 8's `canonical_package.py` doesn't import
anything beyond `contracts`, `dispositions`, `hashing`, `publication_map` (none of which import
producer/analysis modules).

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_import_boundaries.py
git commit -m "test: prove renderer-side code never transitively imports a forbidden module, with negative-control self-tests"
```

---

## Task 10: Layer-1 Mutation Suite — `validate_canonical_package`

**Files:**
- Create: `tests/unit/test_validate_canonical_mutations.py`

**Interfaces:**
- Consumes: `validate_canonical.validate_canonical_package`, the same package-construction helpers used in
  `tests/unit/test_validate_canonical.py` (reuse them; do not reinvent a second construction path).

- [ ] **Step 1: Write the mutation-matrix test module**

```python
"""
test_validate_canonical_mutations.py
======================================

Layer-1 mutation suite (Phase 2, spec Section 5.1): takes a known-good
canonical package, deliberately corrupts it one way at a time, and asserts
validate_canonical_package's status/issue-code for each -- proving the
validator actually catches each corruption, not just "doesn't currently
fail by accident." Each test name states the artifact/field mutated.
"""

import json

import pytest

import validate_canonical
# Reuse whatever helper tests/unit/test_validate_canonical.py already uses
# to build a minimal valid package + its plan -- import it directly rather
# than duplicating construction logic:
from test_validate_canonical import _build_minimal_valid_package, _load_plan_used_to_build


def test_deleted_media_file_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    media_file = next((package_dir / "media").iterdir())
    media_file.unlink()

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "broken_media_reference" for i in report.issues)


def test_absolute_media_reference_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    chunk_path = next((package_dir / "chunks").glob("*.md"))
    text = chunk_path.read_text()
    chunk_path.write_text(text.replace("../media/", "/etc/media/"))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "path_traversal_or_absolute_reference" for i in report.issues)


def test_removed_publication_map_entry_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"].pop()
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "publication_map_chunk_mismatch" for i in report.issues)


def test_duplicate_publication_map_entry_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"].append(dict(data["entries"][0]))
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(
        i.code in ("publication_map_chunk_mismatch", "publication_map_order_invalid")
        for i in report.issues
    )


def test_non_contiguous_publication_map_order_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"][0]["order"] = 99
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "publication_map_order_invalid" for i in report.issues)


def test_manifest_plan_id_mismatch_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path)
    manifest_path = package_dir / "manifest.json"
    data = json.loads(manifest_path.read_text())
    data["plan_id"] = "sha256:" + "1" * 64
    manifest_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "plan_fingerprint_mismatch" for i in report.issues)


def test_duplicate_manifest_chunk_content_path_is_detected(tmp_path):
    # Round-3 review (GPT 5.6 blocking #6) caught that a single-chunk
    # fixture makes `data["chunks"][0] == data["chunks"][-1]` the SAME
    # entry -- overwriting a path with itself introduces no duplicate and
    # proves nothing. This fixture must have >= 2 chunks with genuinely
    # different paths BEFORE the mutation, asserted explicitly.
    package_dir = _build_minimal_valid_package(tmp_path, chunk_count=2)
    manifest_path = package_dir / "manifest.json"
    data = json.loads(manifest_path.read_text())
    assert len(data["chunks"]) >= 2, "fixture must have at least 2 chunks for this test to mean anything"
    assert data["chunks"][0]["content_file"] != data["chunks"][1]["content_file"], (
        "precondition: the two chunks must start with genuinely different paths"
    )
    data["chunks"][0]["content_file"] = data["chunks"][1]["content_file"]
    manifest_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "duplicate_content_path" for i in report.issues)


def test_orphan_media_file_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    (package_dir / "media" / "orphan.png").write_bytes(b"not-referenced")

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "orphan_media_file" for i in report.issues)


def test_encoded_traversal_media_reference_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    chunk_path = next((package_dir / "chunks").glob("*.md"))
    text = chunk_path.read_text()
    chunk_path.write_text(text.replace("../media/", "../media/%2e%2e/"))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"


def test_malformed_chunk_sidecar_json_is_a_controlled_validation_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path)
    meta_path = next((package_dir / "chunks").glob("*.meta.json"))
    meta_path.write_text("{not valid json")

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "malformed_json" for i in report.issues)


def test_publication_map_order_as_string_is_a_controlled_validation_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"][0]["order"] = "zero"  # wrong type: string, not int
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"


def test_empty_publication_map_entries_for_nonempty_grouped_package_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped", chunk_count=2)
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"] = []
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "publication_map_chunk_mismatch" for i in report.issues)
```

**Decision on the unknown-field policy** (GPT 5.6's round-3 question, left genuinely open in the spec):
extra/unknown fields in any contract's JSON are permitted and silently ignored, not rejected — this
matches every `from_dict` classmethod's existing behavior (each reads only its own known fields via
`_require`/`.get`, never rejects extras) and is a deliberate forward-compatibility choice, not a gap. No
new test enforces rejection; if a future need for strict rejection arises, that is a separate, explicitly
scoped change, not implied by this task.

If `_build_minimal_valid_package` doesn't currently accept `with_media=True`/`strategy=`/`chunk_count=`
keyword arguments, extend it in `tests/unit/test_validate_canonical.py` to accept them (default
`with_media=False`, `strategy="chunked"`, `chunk_count=1`, building `chunk_count` distinctly-pathed chunks
when greater than 1) rather than writing a second, divergent helper in this new file — read that helper's
current signature first.

- [ ] **Step 2: Run tests to verify each fails for the right reason before any fix, or passes now if the
  behavior it tests was already correct**

Run: `python3 -m pytest tests/unit/test_validate_canonical_mutations.py -v`
Expected: most should already PASS at this point in the plan (Tasks 5/6 already added the lineage and
malformed-map checks; existing validator logic already covers media/orphan/traversal detection). Any that
FAIL here reveal a real gap not yet covered by earlier tasks — stop and add the missing check to
`validate_canonical.py` before proceeding, following the same pattern as Task 5/6's fixes.

- [ ] **Step 3: Prove every already-passing mutation test actually depends on its check (Opus's round-3
  finding — "most should already PASS" is exactly the wave-through this phase exists to prevent)**

A mutation test that passes without any new implementation only proves the check catches the corruption
*today* — it does not prove the test would go red if that check regressed or was accidentally deleted. For
every test in this file that passed in Step 2 without a new check being added, temporarily neutralize the
specific check it depends on and confirm the test now fails, then restore the check. Do this as a single
throwaway local script, not a permanent test (the permanent tests already assert the real behavior; this is
a one-time proof for this task, not a maintained artifact):

```python
# Run this interactively (e.g. python3 -c "..." or a scratch script under
# temp/), NOT as a committed test -- it's a one-time meta-proof, not
# ongoing coverage:
import validate_canonical

# Example for test_deleted_media_file_is_detected: temporarily make
# _check_media_references a no-op and confirm the test then fails.
original = validate_canonical._check_media_references
validate_canonical._check_media_references = lambda *a, **kw: []
try:
    # re-run test_deleted_media_file_is_detected's body here (or via
    # `pytest tests/unit/test_validate_canonical_mutations.py::test_deleted_media_file_is_detected -v`
    # with the monkeypatch applied) and confirm it now FAILS (report.status != "FAIL"
    # or the expected issue code is absent) -- if it still passes, some
    # OTHER check is also catching this corruption, which is fine, but
    # note which one in this task's commit message.
    pass
finally:
    validate_canonical._check_media_references = original
```
Repeat this pattern (neutralize → confirm red → restore) for each already-passing test's specific
underlying check (`_check_media_references`, `_check_publication_map_consistency`,
`_check_manifest_consistency`, `_check_orphans`, `_check_plan_and_source`) before considering this task
done. Record in the commit message which checks were verified this way.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/test_validate_canonical_mutations.py
git commit -m "test: layer-1 mutation suite proving validate_canonical_package catches deliberate corruption

Verified by temporarily neutralizing each of _check_media_references,
_check_publication_map_consistency, _check_manifest_consistency,
_check_orphans, and _check_plan_and_source and confirming the
corresponding test(s) go red, then restoring -- proving these tests
depend on the checks they claim to, not passing by accident."
```

---

## Task 11: Layer-2 Mutation Suite — `CanonicalPackage.load()`

**Files:**
- Create: `tests/unit/test_canonical_package_mutations.py`

- [ ] **Step 1: Write the mutation tests**

```python
"""
test_canonical_package_mutations.py
======================================

Layer-2 mutation suite (Phase 2, spec Section 5.1): CanonicalPackage.load()
is itself a validator (schema loading, content-hash verification, media
existence) and must be proven to reject corruption introduced AFTER
promotion -- this is the exact path a tampered/corrupted-on-disk package
would be caught (or not) through, independent of whatever
validate_canonical.py already recorded in validation.json at convert time.
"""

import json

import pytest

from canonical_package import CanonicalPackage, CanonicalPackageIntegrityError, CanonicalPackageValidationError
from test_validate_canonical import _build_minimal_valid_package


def test_load_rejects_media_deleted_after_promotion(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True, validated=True)
    media_file = next((package_dir / "media").iterdir())
    media_file.unlink()

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_chunk_content_altered_after_promotion(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    chunk_path = next((package_dir / "chunks").glob("*.md"))
    chunk_path.write_text(chunk_path.read_text() + "\ntampered\n")

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_fail_status_validation_report(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    validation_path = package_dir / "validation.json"
    data = json.loads(validation_path.read_text())
    data["status"] = "FAIL"
    data["issues"] = [{"severity": "error", "code": "x", "message": "x", "path": None}]
    validation_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_malformed_manifest(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    (package_dir / "manifest.json").write_text("{not valid json")

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_validation_report_plan_id_not_matching_manifest(tmp_path):
    """Round-3 review (GPT 5.6 blocking #5): a PASS report copied from a
    different package must not silently authorize this one -- Task 8's
    load() now re-derives this instead of trusting validation.json's
    status alone."""
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    validation_path = package_dir / "validation.json"
    data = json.loads(validation_path.read_text())
    data["plan_id"] = "sha256:" + "9" * 64
    validation_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_validation_report_source_sha256_not_matching_manifest(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    validation_path = package_dir / "validation.json"
    data = json.loads(validation_path.read_text())
    data["source_sha256"] = "8" * 64
    validation_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_grouped_package_missing_publication_map_after_promotion(tmp_path):
    """Round-3 review (GPT 5.6 blocking #4): validate_canonical.py already
    rejects this at CONVERT time, but load() must re-check independently,
    since the file could be deleted after promotion -- Layer 2 exists
    precisely to catch what happens between promotion and render time."""
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped", validated=True)
    (package_dir / "publication-map.json").unlink()

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_publication_map_identity_mismatch_after_promotion(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped", validated=True)
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["package_identity"] = "sha256:" + "7" * 64
    pub_map_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_publication_map_chunk_id_altered_after_promotion(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped", validated=True)
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"][0]["chunk_id"] = "nonexistent-chunk-id"
    pub_map_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_unexpected_publication_map_on_non_grouped_package(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="chunked", validated=True)
    (package_dir / "publication-map.json").write_text(json.dumps({
        "schema_version": "1.0",
        "package_identity": "sha256:" + "a" * 64,
        "entries": [],
    }))

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)
```

`_build_minimal_valid_package` needs a `validated=True` option (writes a real PASS `validation.json`
instead of the PENDING placeholder `package.py` writes by default) if it doesn't already support one — add
it to the shared helper in `tests/unit/test_validate_canonical.py` if missing, reusing
`validate_canonical.validate_canonical_package`/`write_validation_report` to produce a real PASS report
before these tests corrupt anything.

- [ ] **Step 2: Run the tests**

Run: `python3 -m pytest tests/unit/test_canonical_package_mutations.py -v`
Expected: the first four PASS given `canonical_package.py`'s pre-existing checks. The five new tests
(validation-report lineage, missing/identity-mismatched/chunk-id-altered/unexpected publication map) PASS
**only if** Task 8's `load()` additions (the lineage cross-check and hardened publication-map
re-validation block) were actually implemented — they were specified in Task 8 above precisely so these
tests have something real to prove, not left for this task to discover as a surprise gap.

- [ ] **Step 3: Prove the already-passing tests actually depend on their checks (same meta-step as Task
  10, applied to `canonical_package.py`)**

For `test_load_rejects_media_deleted_after_promotion`, `test_load_rejects_chunk_content_altered_after_promotion`,
`test_load_rejects_fail_status_validation_report`, and `test_load_rejects_malformed_manifest` — temporarily
neutralize the specific check each depends on inside `CanonicalPackage.load()` (e.g. comment out the
content-hash comparison block, or the media-existence check, one at a time in a scratch copy) and confirm
the corresponding test now fails before restoring. Record which were verified this way in the commit
message, same as Task 10.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/test_canonical_package_mutations.py
git commit -m "test: layer-2 mutation suite proving CanonicalPackage.load() catches post-promotion tampering, including publication-map and validation-report lineage attacks

Verified the pre-existing checks (media existence, content hash, FAIL
status, malformed manifest) by temporarily neutralizing each and
confirming the corresponding test goes red, then restoring."
```

---

## Task 12: Layer-3 Mutation Suite — `validate_rendered_output`

**Files:**
- Create: `tests/unit/test_validate_rendered_mutations.py`

- [ ] **Step 1: Write the mutation tests**

```python
"""
test_validate_rendered_mutations.py
======================================

Layer-3 mutation suite (Phase 2, spec Section 5.1): validate_rendered_output
must be proven to catch corruption in the staged rendered-output directory
-- an omitted-but-linked page, a page whose index link is wrong, and a
validation report whose lineage fields don't match the package it claims
to describe (the general form of the image239 lesson: a report that lies
about what it checked).
"""

import json

import pytest

from renderers import validate_rendered
from test_validate_rendered import _build_rendered_package_pair  # reuse existing helper; read its exact name/signature first


def test_index_omitting_an_existing_page_is_detected(tmp_path):
    """Neither existing check catches this: _check_index_links only checks
    links that ARE present in index.md for brokenness, and
    _check_page_completeness only checks that every chunk has a page and
    every page has a chunk -- neither checks that index.md actually links
    every page that exists. This is a real gap this task closes with a new
    check, _check_index_completeness (added to validate_rendered.py in
    Step 3 below), not a hypothetical one."""
    package, rendered_dir = _build_rendered_package_pair(tmp_path)
    index_path = rendered_dir / "index.md"
    pages_dir = rendered_dir / "pages"
    existing_page_stems = {p.stem for p in pages_dir.glob("*.md")}
    assert existing_page_stems, "fixture must have produced at least one page"

    # Remove every line in index.md that links to one specific existing
    # page, leaving that page still present on disk but unlinked.
    target_stem = sorted(existing_page_stems)[0]
    lines = index_path.read_text().splitlines()
    kept = [l for l in lines if f"pages/{target_stem}.md" not in l]
    index_path.write_text("\n".join(kept))

    report = validate_rendered.validate_rendered_output(rendered_dir, package)

    assert report.status == "FAIL"
    assert any(i.code == "page_not_linked_from_index" for i in report.issues)


def test_source_content_staleness_is_detected(tmp_path):
    # Round-3 review (GPT 5.6 blocking #7) caught that an earlier draft
    # named this test "wrong_manifest_version_claim" while it actually
    # mutates source_content_sha256 -- a source-staleness case, not a
    # renderer manifest-version-compatibility case. Renamed to match what
    # it actually tests; the real manifest-version-compatibility case is
    # test_renderer_rejects_unsupported_manifest_version below.
    package, rendered_dir = _build_rendered_package_pair(tmp_path)
    render_result_path = rendered_dir / "render-result.json"
    data = json.loads(render_result_path.read_text())
    data["source_content_sha256"] = "f" * 64
    render_result_path.write_text(json.dumps(data))

    report = validate_rendered.validate_rendered_output(rendered_dir, package)

    assert report.status == "FAIL"
    assert any(i.code == "source_content_stale" for i in report.issues)


def test_renderer_rejects_unsupported_manifest_version(tmp_path):
    """The actual 'wrong manifest version' case: protocol.dispatch_render
    must refuse to render a package whose manifest.schema_version is not
    in the renderer's own supported_manifest_versions -- this is a
    dispatch-time check (renderers/protocol.py), not a rendered-output
    validation check, so it's tested at the dispatch layer directly."""
    import dataclasses

    from renderers import protocol
    from renderers.multipage_markdown import MultipageMarkdownRenderer

    package, _rendered_dir = _build_rendered_package_pair(tmp_path)
    unsupported_manifest = dataclasses.replace(package.manifest, schema_version="9.9")
    unsupported_package = dataclasses.replace(package, manifest=unsupported_manifest)

    with pytest.raises(protocol.UnsupportedManifestVersionError):
        protocol.dispatch_render(MultipageMarkdownRenderer(), unsupported_package, tmp_path / "out")


def test_page_content_diverging_from_source_chunk_is_detected(tmp_path):
    package, rendered_dir = _build_rendered_package_pair(tmp_path)
    page_path = next((rendered_dir / "pages").glob("*.md"))
    page_path.write_text(page_path.read_text() + "\ntampered after render\n")

    report = validate_rendered.validate_rendered_output(rendered_dir, package)

    assert report.status == "FAIL"
    assert any(i.code == "page_content_not_traceable" for i in report.issues)
```

Read `tests/unit/test_validate_rendered.py`'s existing tests first to find (or add, if missing) a shared
helper that builds a real `CanonicalPackage` plus a real staged rendered-output directory pair, and import
it by its actual name rather than the placeholder name used above — `_build_rendered_package_pair` is a
description of what's needed, not a guaranteed existing name.

- [ ] **Step 2: Run the tests to confirm they fail for the right reason**

Run: `python3 -m pytest tests/unit/test_validate_rendered_mutations.py -v`
Expected: `test_wrong_manifest_version_claim_is_detected` and `test_page_content_diverging_from_source_chunk_is_detected`
already PASS given existing `validate_rendered.py` logic (confirmed by this session's read of
`_check_source_content_staleness`/`_check_page_traceability` after Task 2's rename).
`test_index_omitting_an_existing_page_is_detected` FAILS — `AssertionError` on `report.status == "FAIL"`,
since no existing check in `validate_rendered.py` verifies that `index.md` links every page that exists.

- [ ] **Step 3: Add `_check_index_completeness` to close the real gap**

In `scripts/renderers/validate_rendered.py`, add a new check function, placed after
`_check_index_links` (reusing the same `_LINK_REF` pattern already imported at module scope):

```python
def _check_index_completeness(rendered_dir: Path) -> list:
    """index.md must link every page that actually exists under pages/ --
    _check_index_links only catches links that ARE present and broken, not
    an existing page index.md silently fails to mention at all."""
    index_path = rendered_dir / "index.md"
    pages_dir = rendered_dir / "pages"
    if not index_path.exists() or not pages_dir.is_dir():
        return []

    index_text = index_path.read_text()
    linked_stems = set()
    for match in _LINK_REF.finditer(index_text):
        raw_target = match.group(1).strip()
        if raw_target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = unquote(raw_target)
        if target.startswith("pages/"):
            linked_stems.add(Path(target).stem)

    issues = []
    for page_path in sorted(pages_dir.glob("*.md")):
        if page_path.stem not in linked_stems:
            issues.append(_error(
                "page_not_linked_from_index",
                f"pages/{page_path.name} exists but index.md does not link it",
                "index.md",
            ))
    return issues
```

Wire it into `validate_rendered_output`, right after the existing `_check_index_links` call:
```python
    issues.extend(_check_index_and_pages_exist(rendered_dir))
    issues.extend(_check_index_links(rendered_dir))
    issues.extend(_check_index_completeness(rendered_dir))
    issues.extend(_check_page_completeness(rendered_dir, package))
```

- [ ] **Step 4: Add adversarial index-completeness cases (both round-3 reviewers' shared finding: a new
  check built on the same regex-based link parser can re-earn the exact image239 failure mode in a new
  spot if that parser has any gap)**

Add to `tests/unit/test_validate_rendered_mutations.py`:

```python
def test_index_completeness_survives_escaped_bracket_in_link_text(tmp_path):
    package, rendered_dir = _build_rendered_package_pair(tmp_path)
    index_path = rendered_dir / "index.md"
    pages_dir = rendered_dir / "pages"
    target_stem = sorted(p.stem for p in pages_dir.glob("*.md"))[0]

    # Rewrite the line linking target_stem to use link text containing a
    # markdown-escaped `]` -- this must NOT cause the link to become
    # unrecognized (the exact regex failure mode Phase 2 already fixed
    # once in package.py/validate_canonical.py; _LINK_REF must handle it
    # here too, since it reuses the same character-class fix).
    lines = index_path.read_text().splitlines()
    rewritten = []
    for line in lines:
        if f"pages/{target_stem}.md" in line:
            rewritten.append(f"- [Section \\[One\\]](pages/{target_stem}.md)")
        else:
            rewritten.append(line)
    index_path.write_text("\n".join(rewritten))

    report = validate_rendered.validate_rendered_output(rendered_dir, package)

    assert not any(i.code == "page_not_linked_from_index" for i in report.issues), (
        "escaped bracket in link text must not cause a correctly-linked "
        "page to be reported as unlinked"
    )


def test_index_completeness_survives_url_encoded_page_filename(tmp_path):
    package, rendered_dir = _build_rendered_package_pair(tmp_path)
    index_path = rendered_dir / "index.md"
    pages_dir = rendered_dir / "pages"
    target_stem = sorted(p.stem for p in pages_dir.glob("*.md"))[0]

    lines = index_path.read_text().splitlines()
    rewritten = []
    for line in lines:
        if f"pages/{target_stem}.md" in line:
            from urllib.parse import quote
            rewritten.append(f"- [Section One](pages/{quote(target_stem)}.md)")
        else:
            rewritten.append(line)
    index_path.write_text("\n".join(rewritten))

    report = validate_rendered.validate_rendered_output(rendered_dir, package)

    assert not any(i.code == "page_not_linked_from_index" for i in report.issues)


def test_index_completeness_detects_duplicate_link_while_another_page_is_omitted(tmp_path):
    package, rendered_dir = _build_rendered_package_pair(tmp_path)
    pages_dir = rendered_dir / "pages"
    stems = sorted(p.stem for p in pages_dir.glob("*.md"))
    assert len(stems) >= 2, "fixture must produce at least 2 pages for this test to mean anything"
    first_stem, second_stem = stems[0], stems[1]

    index_path = rendered_dir / "index.md"
    lines = index_path.read_text().splitlines()
    # Remove the line linking second_stem, and duplicate first_stem's link
    # line in its place -- proving the check flags the OMITTED page even
    # when total link count is unchanged (a naive "link count == page
    # count" check would miss this).
    rewritten = [l for l in lines if f"pages/{second_stem}.md" not in l]
    rewritten.append(f"- [Duplicate]({f'pages/{first_stem}.md'})")
    index_path.write_text("\n".join(rewritten))

    report = validate_rendered.validate_rendered_output(rendered_dir, package)

    assert report.status == "FAIL"
    assert any(
        i.code == "page_not_linked_from_index" and second_stem in i.message
        for i in report.issues
    )
```

- [ ] **Step 5: Run the tests to verify they pass, then the full suite**

Run: `python3 -m pytest tests/unit/test_validate_rendered_mutations.py -v`
Expected: all seven PASS.
Run: `python3 -m pytest tests/ -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add tests/unit/test_validate_rendered_mutations.py scripts/renderers/validate_rendered.py
git commit -m "feat: detect a rendered page that exists but is not linked from index.md, hardened against escaped-bracket/URL-encoded/duplicate-link adversarial cases"
```

---

## Task 13: Independent Hand-Authored Canonical Fixture

**Files:**
- Create: `tests/fixtures/independent-canonical-package/manifest.json`
- Create: `tests/fixtures/independent-canonical-package/chunks/intro--abc12345.md`
- Create: `tests/fixtures/independent-canonical-package/chunks/intro--abc12345.meta.json`
- Create: `tests/fixtures/independent-canonical-package/media/diagram.png`
- Create: `tests/fixtures/independent-canonical-package/validation.json`
- Test: `tests/unit/test_independent_fixture.py`

**Interfaces:**
- Consumes: `canonical_package.CanonicalPackage.load`, `renderers.multipage_markdown.MultipageMarkdownRenderer`,
  `validate_canonical.validate_canonical_package`/`write_validation_report` (Task 7).
- Produces: proof that both work against a package that was never produced by `convert.py`/`package.py` —
  hand-typed to match the documented contract shape exactly, **and actually validated by the real
  validator** (not a fabricated PASS report — round-3 review, GPT 5.6 blocking #3, caught that an earlier
  draft wrote `{"status": "PASS"}` directly and never ran the validator at all, which proves only that a
  hand-typed PASS file is accepted, not that this fixture's *provenance* was ever really checked).

- [ ] **Step 1: Hand-author the fixture files**

`tests/fixtures/independent-canonical-package/chunks/intro--abc12345.md`:
```markdown
# Introduction

This is a hand-authored canonical chunk, never produced by the real DOCX
conversion pipeline. It exists to prove the renderer and validators depend
on the documented contract shape, not on incidental producer behavior.

![a small diagram](../media/diagram.png)
```

`tests/fixtures/independent-canonical-package/media/diagram.png`: any small valid PNG byte sequence (a
1x1 transparent pixel is sufficient — write it as raw bytes in the test setup, not as a real image file
checked into git, to keep the fixture obviously synthetic; see Step 2).

- [ ] **Step 2: Write the test that builds the rest of the fixture programmatically and exercises it**

```python
"""
test_independent_fixture.py
==============================

Phase 2, spec Section 5.3: proves the renderer and validators work against
a canonical package that was NEVER produced by running the real DOCX
pipeline -- constructed directly to match the documented contract shape.
This is necessary but, per the round-1 Opus review, insufficient alone: it
proves the shape is readable, not that corruption is caught (that's what
the mutation suites in Tasks 10-12 are for).
"""

import json
from pathlib import Path

import contracts
import hashing
import validate_canonical
from canonical_package import CanonicalPackage
from renderers.multipage_markdown import MultipageMarkdownRenderer

_ONE_PX_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000100" "00000000000000000000"
)  # placeholder hex; replace with a real minimal valid PNG byte sequence
   # during implementation and confirm it round-trips through PIL-free
   # byte-level handling this codebase already uses (no image library is
   # imported anywhere in scripts/, so no format validation happens on
   # media bytes -- any non-empty bytes suffice for this fixture's purpose).


_FIXTURE_SOURCE_SHA256 = "2" * 64


def _build_fixture_plan() -> "contracts.ConversionPlan":
    """Build the ConversionPlan this fixture's manifest/chunks are
    consistent with -- needed because validate_canonical_package's own
    checks (plan-integrity, manifest-plan_id-match) apply to this fixture
    exactly as they would to a real producer-path package. Provenance is
    recorded via the MANIFEST's generator.plugin (see
    _build_independent_fixture), not by skipping these checks."""
    anchor = contracts.StructuralAnchor(
        stable_key="intro--abc12345",
        heading_text="Introduction",
        heading_level=1,
        occurrence=1,
        source_heading_path=["Introduction"],
    )
    plan = contracts.ConversionPlan(
        schema_version=contracts.CONVERSION_PLAN_SCHEMA_VERSION,
        plan_id="",  # computed below
        source=contracts.SourceFingerprint(
            path="hand-authored", sha256=_FIXTURE_SOURCE_SHA256, size_bytes=0
        ),
        strategy="chunked",
        chunk_level=1,
        chunk_anchors=[anchor],
        content_type="manual",
        template_profile="source-structure-v1",
        confirmation=contracts.Confirmation(
            status="confirmed", confirmed_by="fixture", confirmed_at="2026-01-01T00:00:00Z"
        ),
    )
    plan.plan_id = hashing.compute_plan_id(plan)
    return plan


def _build_independent_fixture(tmp_path: Path) -> Path:
    package_dir = tmp_path / "independent-canonical-package"
    chunks_dir = package_dir / "chunks"
    media_dir = package_dir / "media"
    chunks_dir.mkdir(parents=True)
    media_dir.mkdir(parents=True)

    (media_dir / "diagram.png").write_bytes(_ONE_PX_PNG)

    chunk_content = (
        "# Introduction\n\n"
        "This is a hand-authored canonical chunk, never produced by the "
        "real DOCX conversion pipeline.\n\n"
        "![a small diagram](../media/diagram.png)\n"
    )
    (chunks_dir / "intro--abc12345.md").write_text(chunk_content)
    content_sha256 = hashing.content_hash(chunk_content.encode("utf-8"))

    plan = _build_fixture_plan()
    meta = contracts.ChunkMetadata(
        schema_version=contracts.CHUNK_METADATA_SCHEMA_VERSION,
        chunk_id="intro--abc12345",
        source_order=0,
        source_heading_path=["Introduction"],
        topic="Introduction",
        content_type="manual",
        template_profile="source-structure-v1",
        source_sha256=_FIXTURE_SOURCE_SHA256,
        plan_id=plan.plan_id,
        content_file="chunks/intro--abc12345.md",
        content_sha256=content_sha256,
        local_links=[],
        media_refs=["../media/diagram.png"],
    )
    (chunks_dir / "intro--abc12345.meta.json").write_text(json.dumps(meta.to_dict()))

    manifest = contracts.Manifest(
        schema_version=contracts.MANIFEST_SCHEMA_VERSION,
        # "hand-authored-fixture" is the provenance value Task 7's
        # _FIXTURE_GENERATOR_PLUGIN checks for -- this is what makes the
        # content-comparison skip legitimate for THIS package, not a
        # caller-supplied flag.
        generator=contracts.ManifestGenerator(plugin="hand-authored-fixture", plugin_version="0.1.0"),
        source=contracts.ManifestSourceFingerprint(path="hand-authored", sha256=_FIXTURE_SOURCE_SHA256),
        plan_id=plan.plan_id,
        content_type="manual",
        template_profile="source-structure-v1",
        strategy="chunked",
        chunk_count=1,
        chunks=[
            contracts.ManifestChunk(
                chunk_id="intro--abc12345",
                content_file="chunks/intro--abc12345.md",
                metadata_file="chunks/intro--abc12345.meta.json",
                source_order=0,
                source_heading_path=["Introduction"],
            )
        ],
        media=["diagram.png"],
        validation_report="validation.json",
    )
    (package_dir / "manifest.json").write_text(json.dumps(manifest.to_dict()))

    # Run the REAL validator against this package -- do not fabricate
    # validation.json directly (round-3 review's core finding). source_path
    # is omitted (None) since there is no real source .docx for a hand-
    # authored fixture to check against; cleaned_markdown_text is also
    # omitted, which Task 7's fix now correctly treats as a non-error
    # because this manifest's generator.plugin declares fixture provenance.
    report = validate_canonical.validate_canonical_package(package_dir, plan, source_path=None)
    validate_canonical.write_validation_report(report, package_dir)
    assert report.status == "PASS", (
        f"fixture must be genuinely valid, not merely accepted by accident: {report.issues}"
    )

    return package_dir


def test_independent_fixture_loads_successfully(tmp_path):
    package_dir = _build_independent_fixture(tmp_path)
    package = CanonicalPackage.load(package_dir)
    assert package.manifest.chunk_count == 1
    assert package.chunks[0].metadata.chunk_id == "intro--abc12345"
    assert package.manifest.generator.plugin == "hand-authored-fixture"


def test_independent_fixture_renders_successfully_with_no_docx_side_code_invoked(tmp_path):
    package_dir = _build_independent_fixture(tmp_path)
    package = CanonicalPackage.load(package_dir)

    renderer = MultipageMarkdownRenderer()
    output_dir = tmp_path / "rendered-output"
    result = renderer.render(package, output_dir)

    assert result.status == "PASS"
    assert (output_dir / "index.md").exists()
    assert (output_dir / "pages" / "intro--abc12345.md").exists()
    assert (output_dir / "media" / "diagram.png").exists()
```

Replace the placeholder `_ONE_PX_PNG` hex string with an actual minimal valid PNG byte sequence during
implementation (verify by writing it to a temp file and confirming it opens, e.g. via `file <path>` at the
shell, if any doubt) — this codebase never parses media bytes as images (confirmed: no image-processing
import anywhere in `scripts/`), so any non-empty bytes technically suffice for the pipeline's own logic, but
a real minimal PNG keeps the fixture honest about what it claims to be.

- [ ] **Step 3: Run tests to verify they pass**

Run: `python3 -m pytest tests/unit/test_independent_fixture.py -v`
Expected: both PASS. The `assert report.status == "PASS"` inside `_build_independent_fixture` itself
(added in Step 2) means either test failing at fixture-construction time (before the test's own asserts
even run) tells you the fixture is genuinely invalid, not that the test's own assertions are wrong —
read the printed `report.issues` in that case rather than loosening anything.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/test_independent_fixture.py
git commit -m "test: independent hand-authored canonical fixture, validated by the real validator via manifest.generator.plugin provenance, not a fabricated PASS report"
```

---

## Task 14: Runtime-Independence — DOCX/Intake/Temp Physically Absent

**Files:**
- Create: `tests/unit/test_runtime_independence.py`

- [ ] **Step 1: Write the test**

```python
"""
test_runtime_independence.py
===============================

Phase 2, spec Section 5.4: proves rendering works when the real source
.docx, intake/, and temp/ analysis artifacts are physically absent -- not
merely unused. Complements test_import_boundaries.py's static proof with
a behavioral one.
"""

from pathlib import Path

from canonical_package import CanonicalPackage
from renderers.multipage_markdown import MultipageMarkdownRenderer
from test_independent_fixture import _build_independent_fixture


def test_render_succeeds_with_no_docx_intake_or_temp_directory_present(tmp_path, monkeypatch):
    # Build the fixture in an isolated tmp_path that has no intake/ or
    # temp/ sibling directories at all -- there is nothing to accidentally
    # fall back to.
    package_dir = _build_independent_fixture(tmp_path)
    assert not (tmp_path / "intake").exists()
    assert not (tmp_path / "temp").exists()
    assert not any(tmp_path.rglob("*.docx"))

    package = CanonicalPackage.load(package_dir)
    result = MultipageMarkdownRenderer().render(package, tmp_path / "rendered-output")
    assert result.status == "PASS"
```

- [ ] **Step 2: Run the test**

Run: `python3 -m pytest tests/unit/test_runtime_independence.py -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_runtime_independence.py
git commit -m "test: prove rendering succeeds with source docx/intake/temp physically absent"
```

---

## Task 15: Document Extraction Triggers

**Files:**
- Create: `references/extraction-triggers.md`

- [ ] **Step 1: Write the reference doc**

```markdown
# Plugin Extraction Triggers

This document is authorization-neutral: it records the conditions under which a workstream currently
implemented inside `docx-to-content` would become a real candidate for extraction into its own plugin
(e.g. `knowledge-publication`, `sharepoint-knowledge`, `knowledge-evaluation`, per
`docs/vision/master-initiative-plan-workstreams-and-phases.md`). Meeting a trigger does not itself
authorize extraction — it only means the question is worth raising with the user via a proper
brainstorming/spec pass, per this repo's standing workflow.

## Triggers (any one is sufficient to raise the question)

- An independently invoked consumer needs to call the capability without going through
  `docx-to-content`'s own CLI/skills.
- A second producer of canonical content exists (i.e. something other than DOCX conversion produces a
  canonical package that this capability then needs to operate on).
- The capability needs a distinct release cadence from the rest of `docx-to-content`.
- The capability needs a separate ownership or security/access boundary (e.g. SharePoint write
  credentials that the DOCX-conversion path has no reason to ever hold).

## Current status (as of Phase 2)

None of the above are met for any workstream. `knowledge-publication`'s boundary (publication-map
ownership, renderer contracts) is hardened *inside* `docx-to-content` by this phase's work, not extracted.
```

- [ ] **Step 2: Commit**

```bash
git add references/extraction-triggers.md
git commit -m "docs: record explicit plugin-extraction triggers, not yet met for any workstream"
```

---

## Task 16: Golden-Master Comparison Against the Task 0 Baseline

**This task ONLY compares against the baseline Task 0 already captured before any code changed. It never
captures a new baseline itself** — round-3 review's blocking finding on an earlier draft was that
regenerating output and then copying that same regenerated output as the "golden master" is a tautology:
it would report success even if Phase 2 changed every page. That failure mode is now structurally
impossible, since Task 0 already ran, before Task 1, against the unmodified Phase 1 output.

**Files:**
- Create: `tests/integration/test_golden_master.py`
- Modify: `runs/ceis-manual-v2/canonical-content/`, `runs/ceis-manual-v2/render/rendered-output/`
  (regenerated with all of Tasks 1-9's fixes applied — this OVERWRITES the working output, but never
  touches `runs/ceis-manual-v2/golden-master-baseline/`, which Task 0 made immutable)

- [ ] **Step 1: Confirm the Task 0 baseline exists**

```bash
test -f runs/ceis-manual-v2/golden-master-baseline/MANIFEST.sha256 && echo "baseline present" || echo "MISSING -- run Task 0 first, do not proceed"
```
If missing, stop — this task cannot run meaningfully without it (Task 0 was supposed to run before Task 1;
if it didn't, go back and do it now, comparing against the output as it exists RIGHT NOW only if you can
still confirm that output is Phase-1-accepted and pre-Phase-2. If Phase 2 code has already changed the
output, there is no valid baseline left to capture — escalate to the user rather than guessing.)

- [ ] **Step 2: Regenerate the real CEIS output with all of Tasks 1-9's fixes applied**

```bash
cd plugins/docx-to-content
python3 -m scripts.cli convert --source "../../intake/CEIS MANUAL - working version.docx" --plan ../../temp/ceis-manual-analysis/conversion-plan.confirmed.json --output ../../runs/ceis-manual-v2
python3 -m scripts.cli render --canonical ../../runs/ceis-manual-v2/canonical-content --renderer multipage-markdown --output ../../runs/ceis-manual-v2/render
cd ../..
```
(If `temp/ceis-manual-analysis/conversion-plan.confirmed.json` no longer exists because `temp/` was
cleared, re-run `analyze`/`confirm` fresh first, per `start-here.md`'s standing note about `temp/` being
gitignored scratch space.)

- [ ] **Step 3: Write the two-surface comparison test, with symmetric file-set equality and a correct
  repo-root locator**

Round-3 review (GPT 5.6 blocking #2) caught two more real bugs in an earlier draft: `Path(__file__).parent
.parent.parent` from a test under `plugins/docx-to-content/tests/integration/` resolves to
`plugins/docx-to-content/runs/...`, not the actual `runs/` at the repository root — three `.parent` calls
is one too few. And the comparison only checked that every *golden* file has a matching *current* file,
never the reverse (an extra file added to `current` would go undetected). Both are fixed below.

```python
"""
test_golden_master.py
========================

Phase 2, spec Section 5.5: two comparison surfaces, not one blanket
byte-identical check. Section 5.2's identity/naming fixes intentionally
change render-result.json/publication-map.json bytes -- so publication
CONTENT (index.md, pages/**, media/**) is compared byte-identical
AND file-set-identical (no missing, no extra files) against the Task 0
baseline, while control METADATA is compared semantically (the identity
still correctly identifies the same source/plan, even though its literal
bytes changed).
"""

from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    """Walk upward from this test file until a directory containing both
    `plugins/` and `runs/` is found -- more robust than counting `.parent`
    calls, which an earlier draft got wrong by one level."""
    current = start.resolve()
    for candidate in [current] + list(current.parents):
        if (candidate / "plugins").is_dir() and (candidate / "runs").is_dir():
            return candidate
    raise RuntimeError(f"could not locate repo root walking up from {start}")


_REPO_ROOT = _find_repo_root(Path(__file__))
_GOLDEN_DIR = _REPO_ROOT / "runs" / "ceis-manual-v2" / "golden-master-baseline"
_CURRENT_DIR = _REPO_ROOT / "runs" / "ceis-manual-v2" / "render" / "rendered-output"


def _require_golden_master():
    if not _GOLDEN_DIR.exists():
        pytest.skip(
            "golden-master-baseline not captured yet -- run Task 0's capture "
            "step after confirming Phase 1 is formally closed, BEFORE any "
            "other task in this plan runs"
        )


def _relative_files(root: Path, subdir: str) -> set:
    base = root / subdir if subdir else root
    if not base.is_dir():
        return set()
    return {p.relative_to(base) for p in base.rglob("*") if p.is_file()}


def test_index_is_byte_identical_to_golden_master():
    _require_golden_master()
    assert (_GOLDEN_DIR / "index.md").read_bytes() == (_CURRENT_DIR / "index.md").read_bytes()


def test_pages_are_file_set_identical_and_byte_identical_to_golden_master():
    _require_golden_master()
    golden_files = _relative_files(_GOLDEN_DIR, "pages")
    current_files = _relative_files(_CURRENT_DIR, "pages")
    missing = golden_files - current_files
    extra = current_files - golden_files
    assert not missing, f"pages present in golden master but missing from current output: {sorted(missing)}"
    assert not extra, f"pages present in current output but NOT in golden master (unexplained addition): {sorted(extra)}"
    for rel in sorted(golden_files):
        golden_bytes = (_GOLDEN_DIR / "pages" / rel).read_bytes()
        current_bytes = (_CURRENT_DIR / "pages" / rel).read_bytes()
        assert golden_bytes == current_bytes, f"pages/{rel} differs from golden master"


def test_media_is_file_set_identical_and_byte_identical_to_golden_master():
    _require_golden_master()
    golden_files = _relative_files(_GOLDEN_DIR, "media")
    current_files = _relative_files(_CURRENT_DIR, "media")
    missing = golden_files - current_files
    extra = current_files - golden_files
    assert not missing, f"media present in golden master but missing from current output: {sorted(missing)}"
    assert not extra, f"media present in current output but NOT in golden master (unexplained addition): {sorted(extra)}"
    for rel in sorted(golden_files):
        golden_bytes = (_GOLDEN_DIR / "media" / rel).read_bytes()
        current_bytes = (_CURRENT_DIR / "media" / rel).read_bytes()
        assert golden_bytes == current_bytes, f"media/{rel} differs from golden master"


def test_control_metadata_is_semantically_correct_not_byte_identical():
    _require_golden_master()
    import json
    current = json.loads((_CURRENT_DIR / "render-result.json").read_text())
    # Semantic check, not byte comparison: the renamed field is present and
    # correctly identifies the same source content -- NOT that it matches
    # the old field name/value byte-for-byte (it deliberately won't, since
    # Task 2 renamed it and the golden master predates that rename).
    assert "source_content_sha256" in current
    assert len(current["source_content_sha256"]) == 64  # a real sha256 hex digest
```

- [ ] **Step 4: Run the test**

Run: `python3 -m pytest tests/integration/test_golden_master.py -v`
Expected: PASS if Task 0's baseline exists (it must, since Task 0 runs before Task 1); SKIP (not FAIL) only
in the anomalous case where this task somehow runs without Task 0 having completed — that should not
happen in a normal execution of this plan in order.

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_golden_master.py runs/ceis-manual-v2/canonical-content/ runs/ceis-manual-v2/render/rendered-output/
git commit -m "feat: compare Phase 2's regenerated publication output against the Task 0 pre-change baseline

Byte-identical AND file-set-identical (no missing, no unexplained extra
files) for index.md/pages/media; semantic-only for control metadata
that Section 5.2's fixes intentionally changed."
```

---

## Task 17: Full Suite Run and Intentional-Change Accounting

**Files:** none new — this task is verification and documentation only.

- [ ] **Step 1: Run the full suite**

```bash
cd plugins/docx-to-content
python3 -m pytest tests/ -q
```

- [ ] **Step 2: Confirm Task 16's golden-master test did not skip**

Round-3 review (GPT 5.6, significant issue #10) caught a real conflict in an earlier draft: it let this
task declare "Phase 2 completion" even if Task 16's golden-master test had skipped rather than actually
run. Run:
```bash
python3 -m pytest tests/integration/test_golden_master.py -v
```
Confirm every test in it **PASSED**, not SKIPPED. If any skipped, **Phase 2 is not complete** — do not
proceed to Step 3's "completion" framing. Report to the user that Phase 2 remains open pending Task 0/16,
and stop here rather than writing a completion record that isn't true yet.

- [ ] **Step 3: Record exact pass/fail/skip counts and enumerate every intentionally-changed pre-existing
  test**

Update `start-here.md` with: the new total pass/skip count from the FULL suite (Step 1) — a skip here is
expected and fine only for tests genuinely unrelated to Task 16 (there should be none, since Task 0 running
first means Task 16 should never skip in a normal execution of this plan); a list of every pre-existing
test whose assertion changed because of Tasks 1, 2, or 4 (identity value, field rename, `chunk_id`
resolution) — naming each by file and test function, distinguishing "intentionally changed, here's why"
from "still passing unchanged." State explicitly whether Task 16's golden-master test passed (not skipped)
as part of this record — that is the actual completion evidence, not the aggregate pass count alone.

- [ ] **Step 4: Commit**

```bash
git add start-here.md
git commit -m "docs: record Phase 2 completion (golden-master test PASSED, not skipped), full suite counts, and intentionally-changed tests"
```

---

## Self-Review Notes (for whoever executes this plan)

- Every mandatory item from the approved spec (`docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md`)
  traces to a task above: golden-master baseline capture (Task 0, run first), package_identity (Task 1),
  source_manifest_hash rename + renderer version-gate fix (Task 2/3), schema-version split (Task 3),
  chunk_id/parent_topic_id (Task 4), lineage checks (Task 5), malformed/unexpected publication-map (Task
  6), content-comparison-skip via manifest provenance (Task 7), module split with hardened
  lineage/publication-map re-validation in `load()` (Task 8), transitive import boundary with negative
  controls (Task 9), three-layer mutation suites including the meta-proof that already-passing tests
  actually depend on their checks (Tasks 10-12), independent fixture validated by the real validator (Task
  13), runtime independence (Task 14), extraction triggers (Task 15), golden master comparison against the
  Task 0 baseline (Task 16).
- **This plan went through three rounds of external adversarial review** (Opus + GPT 5.6;
  `temp/plan-reviews/opus.md`/`gpt5.6.md`, `temp/plan-reviews/phase2/`, `temp/plan-reviews/full-plan-review/`)
  before reaching this state. Round 3 found and this revision fixed: a load-bearing `chunk_id`/`topic_id`
  validator divergence (Task 6/8), a version-gate re-coupling the renderer still had (Task 3), a golden-
  master tautology and broken path resolution (Task 0/16, the most severe finding), a fabricated-PASS
  independent fixture that proved nothing about provenance (Task 13), missing publication-map/lineage
  enforcement in `CanonicalPackage.load()` (Task 8/11), a single-chunk mutation test that mutated nothing
  (Task 10), a mislabeled mutation test (Task 12), an unproven import-graph checker (Task 9), and a
  skip/completion conflict (Task 17). This is not evidence the plan is now perfect — only that it has been
  checked harder than most plans get checked, and every concrete, verified finding was fixed rather than
  argued away.
- Several test-helper names in Tasks 10-14 (`_build_minimal_valid_package`, `_load_plan_used_to_build`,
  `_build_rendered_package_pair`) are described by what they must do, not guaranteed to already exist under
  those exact names — the task steps explicitly instruct reading the real test files first and reusing or
  extending whatever helper already exists, rather than assuming the name is correct.
- Scope note both round-3 reviewers raised: this is the Phase 2 sub-plan, not the whole-spectrum master
  plan — that document already exists separately at
  `docs/vision/master-initiative-plan-workstreams-and-phases.md` (committed earlier this session, before
  round 3's bundle was built, so round 3 didn't have it in context). No action needed here; noting it so a
  reader of this plan alone doesn't mistake it for the only planning artifact.
