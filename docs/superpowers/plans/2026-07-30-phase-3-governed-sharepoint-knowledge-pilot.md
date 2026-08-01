# Phase 3: Governed SharePoint Knowledge Pilot — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the offline, testable Python tooling that turns an already-promoted Phase 2 canonical+rendered package into a package-only SharePoint upload artifact, validates it before any tenant write, and reconciles it against the actual state of the pilot document library after a human performs the upload — then execute the one-time human/tenant-side pilot (create library, upload, reconcile, and one republish/rollback/rename exercise) using that tooling, against the resolved decisions in `docs/superpowers/specs/phase-3-unresolved-decisions.md`.

**Architecture:** Three new pure-Python, offline modules in `plugins/docx-to-content/scripts/` — `sharepoint_package.py` (assembles an `UploadPackage` from an existing `CanonicalPackage` + rendered-output directory), `sharepoint_dry_run.py` (validates an `UploadPackage` against the target-schema contract with zero tenant I/O), and `sharepoint_reconcile.py` (diffs an `ExpectedLibraryState` derived from the `UploadPackage` against an `ActualLibraryState` supplied by whatever evidence-capture mechanism is available — CSV export is the only currently-confirmed mechanism per Phase 3.0 evidence). All three consume `contracts.py`, `canonical_package.py`, and `publication_map.py` without modification, per the spec's package-only deployment contract (Section 8). A thin CLI (`sharepoint_cli.py`) wires the three together for human operators. The tenant-side pilot execution (creating `CEIS-Pilot-Knowledge`, running one real upload, one reconciliation pass, one republish/rollback/rename exercise, one oversharing check) is manual, evidence-recorded work that this tooling supports but cannot automate — it is captured as explicit human-procedure tasks (3.4.x) using the exact templates and resolved decisions already on file.

**Tech Stack:** Python 3 (matching Phase 2), `pytest`, dataclasses + `json`, no new third-party dependencies (no Graph SDK, no `office365` package — package-only deployment means uploads happen via SharePoint's own UI/drag-and-drop, per spec Section 8 and resolved decision #10's residual openness on any *automated* `ActualLibraryState` reader).

## Global Constraints

- Package-only deployment: this plan MUST NOT write code that performs autonomous SharePoint writes (no Graph API write calls, no PnP PowerShell upload scripts as part of the automated pipeline) — all tenant writes are human-performed through the SharePoint UI (spec Section 8).
- All three new modules (`sharepoint_package.py`, `sharepoint_dry_run.py`, `sharepoint_reconcile.py`) MUST consume `contracts.py`, `canonical_package.py`, and `publication_map.py` as-is — no modification to Phase 2 contract/loader code (spec Section 1, non-goals).
- TDD throughout: every new function gets a failing test committed before its implementation, per `.agent/rules/test-driven-development.md`.
- New code lives in `plugins/docx-to-content/scripts/`, tests in `plugins/docx-to-content/tests/unit/`, matching the existing plugin's layout (`tests/conftest.py` already adds `scripts/` to `sys.path`).
- Pilot scope is fixed: all 25 rendered CEIS topics from `runs/ceis-manual-v2/` (resolved decision #3) — no subset selection logic.
- Pilot site/library: existing site `AG-CSB-INTRANET-DEV`, new library `CEIS-Pilot-Knowledge` (resolved decision #1) — do not parameterize a different default.
- Republish policy: block-until-reviewed is the only policy this plan implements (resolved decision #2) — no auto-republish code path.
- No `PublishedVersion` SharePoint column: rely on native SharePoint versioning + `TopicContentSHA256` + a publication-event log entry (resolved decision #5) — reconciliation code must not invent or expect such a column.
- `PublicationID` is rejected terminology; the identity concept is `PackageIdentity` (`manifest.plan_id` / `publication-map.json`'s `package_identity`), already produced by Phase 2 (resolved decision #11).
- `Sensitivity` is a custom Choice column, populated by a human reviewer per topic, not inferred by code; all 25 pilot topics are pre-confirmed non-Protected-B (resolved decision #6) — code must still carry the field through untouched, never hardcode "non-sensitive."
- Structural anchors (`stable_key`, `source_heading_path`) stay inside the evidence package only; they are never written as a SharePoint column (resolved decision #7).

---

## Reference: Target Schema (spec Section 6, field-authority matrix)

The pilot document library (`CEIS-Pilot-Knowledge`) has these columns beyond the built-ins (`Name`, `Modified`, `Modified By`):

| Column | Type | Source of truth | Populated by |
|---|---|---|---|
| `TopicId` | Single line text | `publication-map.json` entry `topic_id` (== `chunk_id` for this grouped package) | package builder |
| `Title` | Single line text (native) | `publication-map.json` entry `title` | package builder |
| `PackageIdentity` | Single line text | `manifest.json` `plan_id` (`publication-map.json` `package_identity` — same value) | package builder |
| `PublicationOrder` | Number | `publication-map.json` entry `order` | package builder |
| `TopicContentSHA256` | Single line text | `manifest.json` chunk's sidecar `content_sha256` | package builder |
| `SourceDocumentSHA256` | Single line text | `manifest.json` `source.sha256` | package builder |
| `Sensitivity` | Choice (`Public`, `Internal`, `Protected-B`) | human reviewer, not code | manual (reviewer, at upload time) |
| `LifecycleState` | Choice (`Draft`, `Reviewed`, `Published`, `Superseded`, `Retired`) | SharePoint-side workflow (Model A) | SharePoint content-approval workflow |

## Reference: `UploadPackage` on-disk layout (produced by Task 1)

```
<output_dir>/
  upload-manifest.json          # schema_version, package_identity, source_sha256, entries[]
  topics/
    <topic_id>.md                # copy of the rendered page content
  media/
    <same filenames as render_dir/media>
```

---

### Task 1: `UploadPackage` builder (`sharepoint_package.py`)

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_package.py`
- Create: `plugins/docx-to-content/tests/unit/test_sharepoint_package.py`

**Interfaces:**
- Consumes: `canonical_package.CanonicalPackage.load(package_dir: Path) -> CanonicalPackage` (fields: `.manifest: contracts.Manifest`, `.publication_map: contracts.PublicationMap | None`, `.chunks: list[LoadedChunk]` each with `.metadata: contracts.ChunkMetadata`, `.content: str`); rendered-output directory layout `render_dir/pages/<topic_id>.md`, `render_dir/media/<filename>`.
- Produces (for Task 2 and Task 3 to consume):
  - `@dataclass UploadEntry: topic_id: str, title: str, order: int, package_identity: str, topic_content_sha256: str, source_document_sha256: str, content_path: str` (path relative to the `UploadPackage`'s root, e.g. `"topics/data-capture-standards--d1d8e601.md"`)
  - `@dataclass UploadPackage: schema_version: str, package_identity: str, source_document_sha256: str, entries: list[UploadEntry], root_dir: Path` with method `.to_dict() -> dict` and classmethod `.load(root_dir: Path) -> "UploadPackage"` (reads `upload-manifest.json` back)
  - `def build_upload_package(canonical_dir: Path, render_dir: Path, output_dir: Path) -> UploadPackage` — writes `output_dir/upload-manifest.json`, copies each topic's rendered markdown into `output_dir/topics/`, copies `render_dir/media/` into `output_dir/media/` verbatim, and returns the in-memory `UploadPackage`.
  - Raises `class SharePointPackageError(Exception)` if `canonical_dir`'s manifest has `strategy != "grouped"` (pilot scope is fixed to the grouped 25-topic package; anything else is out of scope for this plan) or if a topic's rendered page file is missing from `render_dir/pages/`.

- [ ] **Step 1: Write the failing test for `UploadEntry`/`UploadPackage` dataclasses round-tripping**

```python
"""
test_sharepoint_package.py
===========================

Tests for scripts/sharepoint_package.py — assembles an UploadPackage
(SharePoint-ready topic files + manifest) from an already-promoted
CanonicalPackage and its rendered-output sibling. Package-only: this
module never talks to a SharePoint tenant. Task 3.2.1 (Phase 3 plan).
"""

import json
from pathlib import Path

import pytest

import sharepoint_package as sp


def test_upload_entry_round_trips_through_dict():
    entry = sp.UploadEntry(
        topic_id="widget-setup--aaaa1111",
        title="WIDGET SETUP",
        order=0,
        package_identity="sha256:deadbeef",
        topic_content_sha256="cccc2222",
        source_document_sha256="dddd3333",
        content_path="topics/widget-setup--aaaa1111.md",
    )
    data = entry.to_dict()
    assert sp.UploadEntry.from_dict(data) == entry


def test_upload_package_to_dict_has_schema_version_and_entries():
    entry = sp.UploadEntry(
        topic_id="widget-setup--aaaa1111",
        title="WIDGET SETUP",
        order=0,
        package_identity="sha256:deadbeef",
        topic_content_sha256="cccc2222",
        source_document_sha256="dddd3333",
        content_path="topics/widget-setup--aaaa1111.md",
    )
    pkg = sp.UploadPackage(
        schema_version=sp.UPLOAD_MANIFEST_SCHEMA_VERSION,
        package_identity="sha256:deadbeef",
        source_document_sha256="dddd3333",
        entries=[entry],
        root_dir=Path("/tmp/does-not-matter"),
    )
    data = pkg.to_dict()
    assert data["schema_version"] == sp.UPLOAD_MANIFEST_SCHEMA_VERSION
    assert data["entries"] == [entry.to_dict()]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_package.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sharepoint_package'`

- [ ] **Step 3: Write the dataclasses**

```python
"""
sharepoint_package.py
======================

Assembles a package-only SharePoint UploadPackage from an already
ACCEPTED Phase 2 canonical-content package plus its rendered-output
sibling. Never performs any SharePoint tenant I/O -- output is a plain
directory a human uploads through the SharePoint UI. Phase 3 plan Task
3.2.1. See docs/superpowers/specs/phase-3-governed-sharepoint-knowledge-pilot-spec.md
Section 6 (target schema) and Section 8 (package-only deployment contract).
"""

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import canonical_package

UPLOAD_MANIFEST_SCHEMA_VERSION = "1.0"


class SharePointPackageError(Exception):
    """Raised when the source canonical/rendered pair cannot be assembled
    into an UploadPackage (wrong strategy, missing rendered page, etc.)."""


@dataclass
class UploadEntry:
    topic_id: str
    title: str
    order: int
    package_identity: str
    topic_content_sha256: str
    source_document_sha256: str
    content_path: str

    @classmethod
    def from_dict(cls, data: dict) -> "UploadEntry":
        return cls(
            topic_id=data["topic_id"],
            title=data["title"],
            order=data["order"],
            package_identity=data["package_identity"],
            topic_content_sha256=data["topic_content_sha256"],
            source_document_sha256=data["source_document_sha256"],
            content_path=data["content_path"],
        )

    def to_dict(self) -> dict:
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "order": self.order,
            "package_identity": self.package_identity,
            "topic_content_sha256": self.topic_content_sha256,
            "source_document_sha256": self.source_document_sha256,
            "content_path": self.content_path,
        }


@dataclass
class UploadPackage:
    schema_version: str
    package_identity: str
    source_document_sha256: str
    entries: list  # list[UploadEntry], in publication order
    root_dir: Path

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "package_identity": self.package_identity,
            "source_document_sha256": self.source_document_sha256,
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def load(cls, root_dir: Path) -> "UploadPackage":
        root_dir = Path(root_dir)
        manifest_path = root_dir / "upload-manifest.json"
        data = json.loads(manifest_path.read_text())
        return cls(
            schema_version=data["schema_version"],
            package_identity=data["package_identity"],
            source_document_sha256=data["source_document_sha256"],
            entries=[UploadEntry.from_dict(e) for e in data["entries"]],
            root_dir=root_dir,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_package.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_package.py plugins/docx-to-content/tests/unit/test_sharepoint_package.py
git commit -m "feat(phase3): add UploadEntry/UploadPackage dataclasses"
```

- [ ] **Step 6: Write the failing test for `build_upload_package` against a fabricated grouped canonical+rendered pair**

```python
def _write_grouped_fixture(tmp_path):
    """Fabricates a minimal grouped CanonicalPackage + matching rendered
    render_dir, mirroring runs/ceis-manual-v2/'s real layout (25-topic
    grouped strategy, topic_id == chunk_id, page file <topic_id>.md)."""
    canonical_dir = tmp_path / "canonical-content"
    render_dir = tmp_path / "render" / "rendered-output"
    (canonical_dir / "chunks").mkdir(parents=True)
    (canonical_dir / "media").mkdir(parents=True)
    (render_dir / "pages").mkdir(parents=True)
    (render_dir / "media").mkdir(parents=True)

    source_sha = "d" * 64
    chunk_id = "widget-setup--aaaa1111"
    content = "# Widget Setup\n\nHow to set up a widget.\n"
    content_sha = __import__("hashlib").sha256(content.encode()).hexdigest()

    (canonical_dir / "chunks" / f"{chunk_id}.md").write_text(content)
    (canonical_dir / "chunks" / f"{chunk_id}.json").write_text(json.dumps({
        "schema_version": "1.0",
        "chunk_id": chunk_id,
        "source_order": 0,
        "source_heading_path": ["Widget Setup"],
        "topic": "Widget Setup",
        "content_type": "procedure",
        "template_profile": "default",
        "source_sha256": source_sha,
        "plan_id": "sha256:" + "e" * 64,
        "content_file": f"chunks/{chunk_id}.md",
        "content_sha256": content_sha,
        "local_links": [],
        "media_refs": [],
    }))
    (canonical_dir / "manifest.json").write_text(json.dumps({
        "schema_version": "1.0",
        "generator": {"plugin": "docx-to-content", "plugin_version": "test"},
        "source": {"path": "intake/widget.docx", "sha256": source_sha},
        "plan_id": "sha256:" + "e" * 64,
        "content_type": "manual",
        "template_profile": "default",
        "strategy": "grouped",
        "chunk_count": 1,
        "chunks": [{
            "chunk_id": chunk_id,
            "content_file": f"chunks/{chunk_id}.md",
            "metadata_file": f"chunks/{chunk_id}.json",
            "source_order": 0,
            "source_heading_path": ["Widget Setup"],
        }],
        "media": [],
        "validation_report": "validation.json",
    }))
    (canonical_dir / "validation.json").write_text(json.dumps({
        "status": "PASS",
        "issues": [],
        "source_sha256": source_sha,
        "plan_id": "sha256:" + "e" * 64,
    }))
    (canonical_dir / "publication-map.json").write_text(json.dumps({
        "schema_version": "1.0",
        "package_identity": "sha256:" + "e" * 64,
        "entries": [{
            "chunk_id": chunk_id, "title": "WIDGET SETUP", "order": 0, "topic_id": chunk_id,
        }],
    }))
    (render_dir / "pages" / f"{chunk_id}.md").write_text(
        "# WIDGET SETUP\n\nHow to set up a widget.\n"
    )
    return canonical_dir, render_dir, chunk_id


def test_build_upload_package_produces_one_entry_per_topic(tmp_path):
    canonical_dir, render_dir, chunk_id = _write_grouped_fixture(tmp_path)
    output_dir = tmp_path / "upload-package"

    pkg = sp.build_upload_package(canonical_dir, render_dir, output_dir)

    assert len(pkg.entries) == 1
    entry = pkg.entries[0]
    assert entry.topic_id == chunk_id
    assert entry.title == "WIDGET SETUP"
    assert entry.order == 0
    assert entry.package_identity == pkg.package_identity
    assert (output_dir / "topics" / f"{chunk_id}.md").exists()
    assert (output_dir / "upload-manifest.json").exists()

    reloaded = sp.UploadPackage.load(output_dir)
    assert reloaded.entries[0].topic_id == chunk_id


def test_build_upload_package_rejects_non_grouped_strategy(tmp_path):
    canonical_dir, render_dir, chunk_id = _write_grouped_fixture(tmp_path)
    manifest_path = canonical_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["strategy"] = "single"
    manifest_path.write_text(json.dumps(manifest))
    (canonical_dir / "publication-map.json").unlink()

    with pytest.raises(sp.SharePointPackageError, match="grouped"):
        sp.build_upload_package(canonical_dir, render_dir, tmp_path / "out")


def test_build_upload_package_raises_on_missing_rendered_page(tmp_path):
    canonical_dir, render_dir, chunk_id = _write_grouped_fixture(tmp_path)
    (render_dir / "pages" / f"{chunk_id}.md").unlink()

    with pytest.raises(sp.SharePointPackageError, match="rendered page"):
        sp.build_upload_package(canonical_dir, render_dir, tmp_path / "out")
```

- [ ] **Step 7: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_package.py -v`
Expected: FAIL with `AttributeError: module 'sharepoint_package' has no attribute 'build_upload_package'`

- [ ] **Step 8: Implement `build_upload_package`**

```python
def build_upload_package(canonical_dir: Path, render_dir: Path, output_dir: Path) -> UploadPackage:
    """Assemble an UploadPackage at output_dir from an already-ACCEPTED
    canonical package at canonical_dir and its rendered-output sibling at
    render_dir (the render/rendered-output directory, containing
    pages/<topic_id>.md and media/). Raises SharePointPackageError if the
    canonical package isn't the grouped, publication-map-backed strategy
    this pilot targets, or if a topic's rendered page is missing."""
    canonical_dir = Path(canonical_dir)
    render_dir = Path(render_dir)
    output_dir = Path(output_dir)

    loaded = canonical_package.CanonicalPackage.load(canonical_dir)
    if loaded.manifest.strategy != "grouped" or loaded.publication_map is None:
        raise SharePointPackageError(
            f"{canonical_dir} has strategy={loaded.manifest.strategy!r} -- "
            "the Phase 3 pilot only supports the grouped, "
            "publication-map-backed strategy"
        )

    chunks_by_id = {chunk.metadata.chunk_id: chunk for chunk in loaded.chunks}

    topics_dir = output_dir / "topics"
    media_dir = output_dir / "media"
    topics_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for pub_entry in sorted(loaded.publication_map.entries, key=lambda e: e.order):
        chunk = chunks_by_id.get(pub_entry.chunk_id)
        if chunk is None:
            raise SharePointPackageError(
                f"publication-map.json references chunk_id "
                f"{pub_entry.chunk_id!r} not present in manifest.json"
            )

        rendered_page = render_dir / "pages" / f"{pub_entry.topic_id}.md"
        if not rendered_page.exists():
            raise SharePointPackageError(
                f"topic {pub_entry.topic_id!r}: missing rendered page "
                f"{rendered_page}"
            )

        dest_content_path = f"topics/{pub_entry.topic_id}.md"
        shutil.copyfile(rendered_page, output_dir / dest_content_path)

        entries.append(UploadEntry(
            topic_id=pub_entry.topic_id,
            title=pub_entry.title,
            order=pub_entry.order,
            package_identity=loaded.publication_map.package_identity,
            topic_content_sha256=chunk.metadata.content_sha256,
            source_document_sha256=loaded.manifest.source.sha256,
            content_path=dest_content_path,
        ))

    render_media_dir = render_dir / "media"
    if render_media_dir.exists():
        shutil.copytree(render_media_dir, media_dir, dirs_exist_ok=True)

    pkg = UploadPackage(
        schema_version=UPLOAD_MANIFEST_SCHEMA_VERSION,
        package_identity=loaded.publication_map.package_identity,
        source_document_sha256=loaded.manifest.source.sha256,
        entries=entries,
        root_dir=output_dir,
    )
    (output_dir / "upload-manifest.json").write_text(
        json.dumps(pkg.to_dict(), indent=2, sort_keys=True)
    )
    return pkg
```

- [ ] **Step 9: Run test to verify it passes**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_package.py -v`
Expected: PASS (5 tests)

- [ ] **Step 10: Verify against the real Phase 2 pilot output (`runs/ceis-manual-v2/`)**

```bash
cd plugins/docx-to-content
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from pathlib import Path
import sharepoint_package as sp
pkg = sp.build_upload_package(
    Path('../../runs/ceis-manual-v2/canonical-content'),
    Path('../../runs/ceis-manual-v2/render/rendered-output'),
    Path('/tmp/ceis-upload-package'),
)
print(len(pkg.entries), 'entries')
assert len(pkg.entries) == 25
print('OK')
"
```

Expected: `25 entries` then `OK` — confirms the builder works against the real, already-promoted pilot content, not just the fabricated fixture.

- [ ] **Step 11: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_package.py plugins/docx-to-content/tests/unit/test_sharepoint_package.py
git commit -m "feat(phase3): implement build_upload_package"
```

---

### Task 2: Dry-run validator (`sharepoint_dry_run.py`)

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_dry_run.py`
- Create: `plugins/docx-to-content/tests/unit/test_sharepoint_dry_run.py`

**Interfaces:**
- Consumes: `sharepoint_package.UploadPackage` (Task 1's `entries: list[UploadEntry]`, each with `.topic_id`, `.title`, `.order`, `.content_path`).
- Produces (for Task 3's CLI and Task 3.4's manual upload procedure to consume):
  - `@dataclass DryRunIssue: severity: str, code: str, message: str, topic_id: str | None = None` with `.to_dict()`
  - `@dataclass DryRunReport: status: str, issues: list, package_identity: str` (`status` is `"PASS"` or `"FAIL"`; there is no `"WARN"` tier for dry-run — every issue here is upload-blocking, unlike `ValidationReport`) with `.to_dict()`
  - `def validate_upload_package(pkg: "sharepoint_package.UploadPackage") -> DryRunReport`

Checks implemented (spec Section 9, "Dry-Run Validation"):
1. Every `entry.title` is non-empty and ≤ 255 characters (SharePoint's `Title` column limit).
2. No two entries share the same `order` value (publication order must be a strict, gapless-not-required but unique sequence).
3. No two entries share the same `topic_id`.
4. Every `entry.content_path` resolves to an existing file under the package root.
5. `pkg.entries` is non-empty (an empty upload package is always a FAIL, never a silent no-op).

- [ ] **Step 1: Write the failing tests**

```python
"""
test_sharepoint_dry_run.py
============================

Tests for scripts/sharepoint_dry_run.py -- the pre-upload validator that
runs entirely offline against an UploadPackage, with zero SharePoint
tenant I/O. Phase 3 plan Task 3.2.2.
"""

from pathlib import Path

import sharepoint_dry_run as dr
from sharepoint_package import UploadEntry, UploadPackage


def _entry(**overrides):
    base = dict(
        topic_id="widget-setup--aaaa1111",
        title="WIDGET SETUP",
        order=0,
        package_identity="sha256:deadbeef",
        topic_content_sha256="c" * 64,
        source_document_sha256="d" * 64,
        content_path="topics/widget-setup--aaaa1111.md",
    )
    base.update(overrides)
    return UploadEntry(**base)


def _package(tmp_path, entries):
    for e in entries:
        p = tmp_path / e.content_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("content")
    return UploadPackage(
        schema_version="1.0",
        package_identity="sha256:deadbeef",
        source_document_sha256="d" * 64,
        entries=entries,
        root_dir=tmp_path,
    )


def test_pass_for_a_well_formed_single_entry_package(tmp_path):
    pkg = _package(tmp_path, [_entry()])
    report = dr.validate_upload_package(pkg)
    assert report.status == "PASS"
    assert report.issues == []


def test_fails_on_empty_title(tmp_path):
    pkg = _package(tmp_path, [_entry(title="")])
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "EMPTY_TITLE" for i in report.issues)


def test_fails_on_title_over_255_chars(tmp_path):
    pkg = _package(tmp_path, [_entry(title="x" * 256)])
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "TITLE_TOO_LONG" for i in report.issues)


def test_fails_on_duplicate_order(tmp_path):
    e1 = _entry(topic_id="a--1111", content_path="topics/a--1111.md", order=0)
    e2 = _entry(topic_id="b--2222", content_path="topics/b--2222.md", order=0)
    pkg = _package(tmp_path, [e1, e2])
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "DUPLICATE_ORDER" for i in report.issues)


def test_fails_on_duplicate_topic_id(tmp_path):
    e1 = _entry(order=0, content_path="topics/a.md")
    e2 = _entry(order=1, content_path="topics/b.md")
    pkg = _package(tmp_path, [e1, e2])
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "DUPLICATE_TOPIC_ID" for i in report.issues)


def test_fails_on_missing_content_file(tmp_path):
    e = _entry(content_path="topics/does-not-exist.md")
    pkg = UploadPackage(
        schema_version="1.0", package_identity="sha256:deadbeef",
        source_document_sha256="d" * 64, entries=[e], root_dir=tmp_path,
    )
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "MISSING_CONTENT_FILE" for i in report.issues)


def test_fails_on_empty_package(tmp_path):
    pkg = UploadPackage(
        schema_version="1.0", package_identity="sha256:deadbeef",
        source_document_sha256="d" * 64, entries=[], root_dir=tmp_path,
    )
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "EMPTY_PACKAGE" for i in report.issues)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_dry_run.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sharepoint_dry_run'`

- [ ] **Step 3: Implement `sharepoint_dry_run.py`**

```python
"""
sharepoint_dry_run.py
=======================

Pre-upload validator for a Phase 3 UploadPackage (scripts/sharepoint_package.py).
Runs entirely offline -- no SharePoint tenant I/O -- so it can gate a
human upload before any tenant write happens. See
docs/superpowers/specs/phase-3-governed-sharepoint-knowledge-pilot-spec.md
Section 9. Phase 3 plan Task 3.2.2.
"""

from dataclasses import dataclass, field

TITLE_MAX_LENGTH = 255


@dataclass
class DryRunIssue:
    severity: str  # always "error" -- dry-run has no warning tier
    code: str
    message: str
    topic_id: str = None

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "topic_id": self.topic_id,
        }


@dataclass
class DryRunReport:
    status: str  # "PASS" | "FAIL"
    issues: list  # list[DryRunIssue]
    package_identity: str

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "issues": [i.to_dict() for i in self.issues],
            "package_identity": self.package_identity,
        }


def validate_upload_package(pkg) -> DryRunReport:
    issues = []

    if not pkg.entries:
        issues.append(DryRunIssue("error", "EMPTY_PACKAGE",
                                   "UploadPackage has no entries"))
        return DryRunReport(status="FAIL", issues=issues,
                             package_identity=pkg.package_identity)

    seen_orders = {}
    seen_topic_ids = {}
    for entry in pkg.entries:
        if not entry.title:
            issues.append(DryRunIssue("error", "EMPTY_TITLE",
                                       f"topic {entry.topic_id!r} has an empty title",
                                       topic_id=entry.topic_id))
        elif len(entry.title) > TITLE_MAX_LENGTH:
            issues.append(DryRunIssue(
                "error", "TITLE_TOO_LONG",
                f"topic {entry.topic_id!r} title is {len(entry.title)} chars "
                f"(max {TITLE_MAX_LENGTH})",
                topic_id=entry.topic_id,
            ))

        if entry.order in seen_orders:
            issues.append(DryRunIssue(
                "error", "DUPLICATE_ORDER",
                f"order {entry.order} used by both "
                f"{seen_orders[entry.order]!r} and {entry.topic_id!r}",
                topic_id=entry.topic_id,
            ))
        else:
            seen_orders[entry.order] = entry.topic_id

        if entry.topic_id in seen_topic_ids:
            issues.append(DryRunIssue(
                "error", "DUPLICATE_TOPIC_ID",
                f"topic_id {entry.topic_id!r} appears more than once",
                topic_id=entry.topic_id,
            ))
        else:
            seen_topic_ids[entry.topic_id] = True

        content_path = pkg.root_dir / entry.content_path
        if not content_path.exists():
            issues.append(DryRunIssue(
                "error", "MISSING_CONTENT_FILE",
                f"topic {entry.topic_id!r}: {content_path} does not exist",
                topic_id=entry.topic_id,
            ))

    status = "FAIL" if issues else "PASS"
    return DryRunReport(status=status, issues=issues,
                         package_identity=pkg.package_identity)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_dry_run.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Verify against the real pilot upload package built in Task 1's Step 10**

```bash
cd plugins/docx-to-content
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from pathlib import Path
from sharepoint_package import UploadPackage
import sharepoint_dry_run as dr
pkg = UploadPackage.load(Path('/tmp/ceis-upload-package'))
report = dr.validate_upload_package(pkg)
print(report.status, len(report.issues))
assert report.status == 'PASS'
"
```

Expected: `PASS 0` — the real 25-topic pilot package passes dry-run cleanly.

- [ ] **Step 6: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_dry_run.py plugins/docx-to-content/tests/unit/test_sharepoint_dry_run.py
git commit -m "feat(phase3): add dry-run UploadPackage validator"
```

---

### Task 3: Reconciliation comparator (`sharepoint_reconcile.py`)

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_reconcile.py`
- Create: `plugins/docx-to-content/tests/unit/test_sharepoint_reconcile.py`
- Create: `plugins/docx-to-content/docs/sharepoint-actual-state-csv-format.md` (documents the exact CSV export column names expected by `load_actual_state_from_csv`, per Phase 3.0's confirmed evidence-capture mechanism)

**Interfaces:**
- Consumes: `sharepoint_package.UploadPackage` (Task 1); no dependency on `sharepoint_dry_run.py`.
- Produces:
  - `@dataclass ActualLibraryItem: topic_id: str, title: str, package_identity: str, publication_order: int, topic_content_sha256: str, source_document_sha256: str`
  - `def load_actual_state_from_csv(csv_path: Path) -> list` returning `list[ActualLibraryItem]` — reads a CSV with header columns `TopicId,Title,PackageIdentity,PublicationOrder,TopicContentSHA256,SourceDocumentSHA256` (this is the confirmed, currently-available evidence mechanism per `docs/superpowers/specs/phase-3-tenant-capability-report.md` — a manual "export to CSV" from the SharePoint library view; resolved-decision item #10 leaves the door open for a future Graph/PnP-based reader, but does not block this pilot on one).
  - `@dataclass ReconciliationIssue: severity: str, code: str, message: str, topic_id: str | None = None` with `.to_dict()`
  - `@dataclass ReconciliationReport: status: str, issues: list, package_identity: str` (`status` is `"MATCH"` or `"MISMATCH"`) with `.to_dict()`
  - `def reconcile(pkg: "sharepoint_package.UploadPackage", actual_items: list) -> ReconciliationReport`

Checks implemented (spec Section 11, "Reconciliation Contract"):
1. Every `UploadEntry.topic_id` in the package has exactly one matching `ActualLibraryItem` (missing → `MISSING_IN_LIBRARY`; more than one → `DUPLICATE_IN_LIBRARY`).
2. Every `ActualLibraryItem.topic_id` present in the library but absent from the package is flagged `UNEXPECTED_IN_LIBRARY` (catches stray/leftover items).
3. For matched pairs: `title`, `package_identity`, `publication_order`, `topic_content_sha256`, `source_document_sha256` must all be equal; any mismatch is `FIELD_MISMATCH` naming the field.

- [ ] **Step 1: Write the failing tests**

```python
"""
test_sharepoint_reconcile.py
===============================

Tests for scripts/sharepoint_reconcile.py -- diffs an UploadPackage
(expected state) against an ActualLibraryState (evidence captured from
the real SharePoint library, currently via CSV export -- see
docs/sharepoint-actual-state-csv-format.md). Phase 3 plan Task 3.3.1.
"""

from pathlib import Path

import sharepoint_reconcile as rec
from sharepoint_package import UploadEntry, UploadPackage


def _entry(**overrides):
    base = dict(
        topic_id="widget-setup--aaaa1111",
        title="WIDGET SETUP",
        order=0,
        package_identity="sha256:deadbeef",
        topic_content_sha256="c" * 64,
        source_document_sha256="d" * 64,
        content_path="topics/widget-setup--aaaa1111.md",
    )
    base.update(overrides)
    return UploadEntry(**base)


def _package(entries):
    return UploadPackage(
        schema_version="1.0", package_identity="sha256:deadbeef",
        source_document_sha256="d" * 64, entries=entries, root_dir=Path("/unused"),
    )


def _actual(**overrides):
    base = dict(
        topic_id="widget-setup--aaaa1111", title="WIDGET SETUP",
        package_identity="sha256:deadbeef", publication_order=0,
        topic_content_sha256="c" * 64, source_document_sha256="d" * 64,
    )
    base.update(overrides)
    return rec.ActualLibraryItem(**base)


def test_match_when_package_and_library_agree():
    pkg = _package([_entry()])
    report = rec.reconcile(pkg, [_actual()])
    assert report.status == "MATCH"
    assert report.issues == []


def test_missing_in_library():
    pkg = _package([_entry()])
    report = rec.reconcile(pkg, [])
    assert report.status == "MISMATCH"
    assert any(i.code == "MISSING_IN_LIBRARY" for i in report.issues)


def test_unexpected_in_library():
    pkg = _package([])
    report = rec.reconcile(pkg, [_actual()])
    assert report.status == "MISMATCH"
    assert any(i.code == "UNEXPECTED_IN_LIBRARY" for i in report.issues)


def test_duplicate_in_library():
    pkg = _package([_entry()])
    report = rec.reconcile(pkg, [_actual(), _actual()])
    assert report.status == "MISMATCH"
    assert any(i.code == "DUPLICATE_IN_LIBRARY" for i in report.issues)


def test_field_mismatch_on_content_hash_drift():
    pkg = _package([_entry()])
    report = rec.reconcile(pkg, [_actual(topic_content_sha256="f" * 64)])
    assert report.status == "MISMATCH"
    mismatch = next(i for i in report.issues if i.code == "FIELD_MISMATCH")
    assert "topic_content_sha256" in mismatch.message


def test_csv_loader_reads_expected_columns(tmp_path):
    csv_path = tmp_path / "actual-state.csv"
    csv_path.write_text(
        "TopicId,Title,PackageIdentity,PublicationOrder,"
        "TopicContentSHA256,SourceDocumentSHA256\n"
        "widget-setup--aaaa1111,WIDGET SETUP,sha256:deadbeef,0,"
        + "c" * 64 + "," + "d" * 64 + "\n"
    )
    items = rec.load_actual_state_from_csv(csv_path)
    assert len(items) == 1
    assert items[0].topic_id == "widget-setup--aaaa1111"
    assert items[0].publication_order == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_reconcile.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sharepoint_reconcile'`

- [ ] **Step 3: Implement `sharepoint_reconcile.py`**

```python
"""
sharepoint_reconcile.py
=========================

Diffs an UploadPackage (expected state, scripts/sharepoint_package.py)
against ActualLibraryState evidence captured from the real SharePoint
library. Phase 3.0 confirmed CSV export as the only currently-available
evidence-capture mechanism (docs/superpowers/specs/phase-3-tenant-capability-report.md);
a future Graph/PnP-based reader is explicitly left open by resolved
decision #10 in docs/superpowers/specs/phase-3-unresolved-decisions.md
but is not required for this pilot. Phase 3 plan Task 3.3.1.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

_COMPARED_FIELDS = (
    "title", "package_identity", "publication_order",
    "topic_content_sha256", "source_document_sha256",
)


@dataclass
class ActualLibraryItem:
    topic_id: str
    title: str
    package_identity: str
    publication_order: int
    topic_content_sha256: str
    source_document_sha256: str


@dataclass
class ReconciliationIssue:
    severity: str
    code: str
    message: str
    topic_id: str = None

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "topic_id": self.topic_id,
        }


@dataclass
class ReconciliationReport:
    status: str  # "MATCH" | "MISMATCH"
    issues: list  # list[ReconciliationIssue]
    package_identity: str

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "issues": [i.to_dict() for i in self.issues],
            "package_identity": self.package_identity,
        }


def load_actual_state_from_csv(csv_path: Path) -> list:
    csv_path = Path(csv_path)
    items = []
    with csv_path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            items.append(ActualLibraryItem(
                topic_id=row["TopicId"],
                title=row["Title"],
                package_identity=row["PackageIdentity"],
                publication_order=int(row["PublicationOrder"]),
                topic_content_sha256=row["TopicContentSHA256"],
                source_document_sha256=row["SourceDocumentSHA256"],
            ))
    return items


def reconcile(pkg, actual_items: list) -> ReconciliationReport:
    issues = []

    actual_by_id = {}
    for item in actual_items:
        actual_by_id.setdefault(item.topic_id, []).append(item)

    expected_ids = {e.topic_id for e in pkg.entries}

    for entry in pkg.entries:
        matches = actual_by_id.get(entry.topic_id, [])
        if not matches:
            issues.append(ReconciliationIssue(
                "error", "MISSING_IN_LIBRARY",
                f"topic {entry.topic_id!r} is in the upload package but "
                "not found in the library",
                topic_id=entry.topic_id,
            ))
            continue
        if len(matches) > 1:
            issues.append(ReconciliationIssue(
                "error", "DUPLICATE_IN_LIBRARY",
                f"topic {entry.topic_id!r} appears {len(matches)} times "
                "in the library (expected exactly once)",
                topic_id=entry.topic_id,
            ))
            continue

        actual = matches[0]
        expected_values = {
            "title": entry.title,
            "package_identity": entry.package_identity,
            "publication_order": entry.order,
            "topic_content_sha256": entry.topic_content_sha256,
            "source_document_sha256": entry.source_document_sha256,
        }
        for field_name in _COMPARED_FIELDS:
            expected_key = "order" if field_name == "publication_order" else field_name
            expected_val = expected_values[field_name]
            actual_val = getattr(actual, field_name)
            if expected_val != actual_val:
                issues.append(ReconciliationIssue(
                    "error", "FIELD_MISMATCH",
                    f"topic {entry.topic_id!r}: {field_name} expected "
                    f"{expected_val!r}, library has {actual_val!r}",
                    topic_id=entry.topic_id,
                ))

    for topic_id in actual_by_id:
        if topic_id not in expected_ids:
            issues.append(ReconciliationIssue(
                "error", "UNEXPECTED_IN_LIBRARY",
                f"library has topic {topic_id!r} not present in the "
                "upload package",
                topic_id=topic_id,
            ))

    status = "MISMATCH" if issues else "MATCH"
    return ReconciliationReport(status=status, issues=issues,
                                 package_identity=pkg.package_identity)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_reconcile.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Write the CSV format doc**

```markdown
# SharePoint Actual-Library-State CSV Format

`sharepoint_reconcile.load_actual_state_from_csv()` reads a CSV export of
the `CEIS-Pilot-Knowledge` document library's default view, with these
column headers (exact names, case-sensitive):

| Column | Type | Notes |
|---|---|---|
| `TopicId` | text | must match the `TopicId` column values as uploaded |
| `Title` | text | |
| `PackageIdentity` | text | |
| `PublicationOrder` | integer | |
| `TopicContentSHA256` | text | |
| `SourceDocumentSHA256` | text | |

## How to produce this file (manual, per pilot run)

1. Open the `CEIS-Pilot-Knowledge` library in SharePoint.
2. Ensure the view includes all six columns above (add them to the view
   if not already present — Library Settings > Views).
3. Use "Export to Excel" (or "Export to CSV" if available in the tenant's
   ribbon), save as `.csv`, and ensure the header row matches the table
   above exactly (SharePoint's export sometimes uses internal column
   names — rename the header row if needed before running reconciliation).
4. Pass the resulting file to `sharepoint_cli.py reconcile --actual-state <file>.csv`.

This is the only actual-library-state evidence mechanism confirmed
available during Phase 3.0 tenant-capability discovery (see
`docs/superpowers/specs/phase-3-tenant-capability-report.md`). A future,
more automated reader (Microsoft Graph or PnP PowerShell) is an accepted
open item (`docs/superpowers/specs/phase-3-unresolved-decisions.md`,
item 10) but is not required for this pilot to proceed.
```

- [ ] **Step 6: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_reconcile.py plugins/docx-to-content/tests/unit/test_sharepoint_reconcile.py plugins/docx-to-content/docs/sharepoint-actual-state-csv-format.md
git commit -m "feat(phase3): add reconciliation comparator + CSV evidence format doc"
```

---

### Task 4: CLI wrapper (`sharepoint_cli.py`)

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_cli.py`
- Create: `plugins/docx-to-content/tests/unit/test_sharepoint_cli.py`

**Interfaces:**
- Consumes: `sharepoint_package.build_upload_package`, `sharepoint_dry_run.validate_upload_package`, `sharepoint_reconcile.load_actual_state_from_csv`, `sharepoint_reconcile.reconcile` (all from Tasks 1–3).
- Produces: a `main(argv: list[str]) -> int` entry point with three subcommands:
  - `package --canonical-dir <dir> --render-dir <dir> --output-dir <dir>` → builds the `UploadPackage`, prints `entries=<N>`, exits 0.
  - `dry-run --package-dir <dir>` → loads `UploadPackage.load()`, runs `validate_upload_package`, prints the report as JSON, exits 0 if `status == "PASS"` else 1.
  - `reconcile --package-dir <dir> --actual-state <csv>` → loads the package, loads CSV, runs `reconcile`, prints the report as JSON, exits 0 if `status == "MATCH"` else 1.

- [ ] **Step 1: Write the failing tests**

```python
"""
test_sharepoint_cli.py
=========================

Tests for scripts/sharepoint_cli.py -- the human-facing CLI wrapping
sharepoint_package/sharepoint_dry_run/sharepoint_reconcile. Phase 3 plan
Task 3.3.6.
"""

import json
from pathlib import Path

import sharepoint_cli as cli


def test_dry_run_subcommand_exits_zero_on_pass(tmp_path, capsys):
    topics_dir = tmp_path / "pkg" / "topics"
    topics_dir.mkdir(parents=True)
    (topics_dir / "a--1111.md").write_text("content")
    manifest = {
        "schema_version": "1.0",
        "package_identity": "sha256:deadbeef",
        "source_document_sha256": "d" * 64,
        "entries": [{
            "topic_id": "a--1111", "title": "A", "order": 0,
            "package_identity": "sha256:deadbeef",
            "topic_content_sha256": "c" * 64,
            "source_document_sha256": "d" * 64,
            "content_path": "topics/a--1111.md",
        }],
    }
    (tmp_path / "pkg" / "upload-manifest.json").write_text(json.dumps(manifest))

    exit_code = cli.main(["dry-run", "--package-dir", str(tmp_path / "pkg")])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert '"status": "PASS"' in out


def test_dry_run_subcommand_exits_one_on_fail(tmp_path, capsys):
    manifest = {
        "schema_version": "1.0",
        "package_identity": "sha256:deadbeef",
        "source_document_sha256": "d" * 64,
        "entries": [],
    }
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "upload-manifest.json").write_text(json.dumps(manifest))

    exit_code = cli.main(["dry-run", "--package-dir", str(tmp_path / "pkg")])

    assert exit_code == 1
    out = capsys.readouterr().out
    assert '"status": "FAIL"' in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sharepoint_cli'`

- [ ] **Step 3: Implement `sharepoint_cli.py`**

```python
"""
sharepoint_cli.py
====================

Human-facing CLI for the Phase 3 package-only SharePoint pilot tooling:
build an UploadPackage, dry-run validate it, and reconcile it against
actual-library-state CSV evidence after a human uploads it. No
SharePoint tenant I/O happens in this module or anything it calls. Phase
3 plan Task 3.3.6.
"""

import argparse
import json
import sys
from pathlib import Path

import sharepoint_dry_run as dry_run
import sharepoint_package as pkg_mod
import sharepoint_reconcile as reconcile_mod


def _cmd_package(args) -> int:
    pkg = pkg_mod.build_upload_package(
        Path(args.canonical_dir), Path(args.render_dir), Path(args.output_dir),
    )
    print(f"entries={len(pkg.entries)}")
    return 0


def _cmd_dry_run(args) -> int:
    pkg = pkg_mod.UploadPackage.load(Path(args.package_dir))
    report = dry_run.validate_upload_package(pkg)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.status == "PASS" else 1


def _cmd_reconcile(args) -> int:
    pkg = pkg_mod.UploadPackage.load(Path(args.package_dir))
    actual_items = reconcile_mod.load_actual_state_from_csv(Path(args.actual_state))
    report = reconcile_mod.reconcile(pkg, actual_items)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.status == "MATCH" else 1


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(prog="sharepoint_cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    package_parser = subparsers.add_parser("package")
    package_parser.add_argument("--canonical-dir", required=True)
    package_parser.add_argument("--render-dir", required=True)
    package_parser.add_argument("--output-dir", required=True)
    package_parser.set_defaults(func=_cmd_package)

    dry_run_parser = subparsers.add_parser("dry-run")
    dry_run_parser.add_argument("--package-dir", required=True)
    dry_run_parser.set_defaults(func=_cmd_dry_run)

    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument("--package-dir", required=True)
    reconcile_parser.add_argument("--actual-state", required=True)
    reconcile_parser.set_defaults(func=_cmd_reconcile)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/unit/test_sharepoint_cli.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: End-to-end smoke test against the real pilot output**

```bash
cd plugins/docx-to-content
python3 scripts/sharepoint_cli.py package \
  --canonical-dir ../../runs/ceis-manual-v2/canonical-content \
  --render-dir ../../runs/ceis-manual-v2/render/rendered-output \
  --output-dir /tmp/ceis-upload-package-cli
python3 scripts/sharepoint_cli.py dry-run --package-dir /tmp/ceis-upload-package-cli
```

Expected: `entries=25`, then a `"status": "PASS"` JSON report, exit code 0 (`echo $?`).

- [ ] **Step 6: Run the full existing test suite to confirm no regressions**

Run: `cd plugins/docx-to-content && python3 -m pytest tests/ -q`
Expected: all previously-passing tests still pass (509 passed, 1 skipped, plus this plan's ~20 new tests).

- [ ] **Step 7: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_cli.py plugins/docx-to-content/tests/unit/test_sharepoint_cli.py
git commit -m "feat(phase3): add sharepoint_cli.py wrapping package/dry-run/reconcile"
```

---

### Task 5: Human-performed pilot execution (tenant-side, evidence-recorded)

These steps cannot be automated — they require a human with SharePoint access to `AG-CSB-INTRANET-DEV`. They are not placeholders: each cites the exact resolved decision or tool from Tasks 1–4 to use, and the exact evidence artifact to produce. Do this task only after Tasks 1–4 are merged and the CLI smoke test in Task 4 Step 5 has been run.

**Files:**
- Create: `docs/superpowers/plans/evidence/phase-3-pilot-execution-log.md` (running log of what was done, when, by whom, with links/screenshots)

- [ ] **Step 1: Create the pilot library**

In `AG-CSB-INTRANET-DEV`, create a new document library named `CEIS-Pilot-Knowledge` (resolved decision #1). Add the 6 custom columns from this plan's "Reference: Target Schema" table (`TopicId`, `PackageIdentity`, `PublicationOrder`, `TopicContentSHA256`, `SourceDocumentSHA256`, `Sensitivity`) plus configure content approval (`LifecycleState`: Draft/Reviewed/Published/Superseded/Retired) per spec Section 7 (Model A: SharePoint-side workflow). Record the library URL and column configuration screenshot in `phase-3-pilot-execution-log.md`.

- [ ] **Step 2: Build and dry-run the upload package**

```bash
cd plugins/docx-to-content
python3 scripts/sharepoint_cli.py package \
  --canonical-dir ../../runs/ceis-manual-v2/canonical-content \
  --render-dir ../../runs/ceis-manual-v2/render/rendered-output \
  --output-dir ../../runs/ceis-manual-v2/sharepoint-upload-package
python3 scripts/sharepoint_cli.py dry-run \
  --package-dir ../../runs/ceis-manual-v2/sharepoint-upload-package
```

Confirm `"status": "PASS"` before proceeding. Append the dry-run report JSON to `phase-3-pilot-execution-log.md`.

- [ ] **Step 3: Upload all 25 topics through the SharePoint UI**

For each entry in `runs/ceis-manual-v2/sharepoint-upload-package/upload-manifest.json`, upload `topics/<topic_id>.md` (or its rendered HTML/Page equivalent per the tenant's actual page-creation UI — clarify at execution time which upload path the tenant supports for Markdown, since this was not directly tested during Phase 3.0 per `phase-3-tenant-capability-report.md`) and manually populate `TopicId`, `Title`, `PackageIdentity`, `PublicationOrder`, `TopicContentSHA256`, `SourceDocumentSHA256` from the manifest, and set `Sensitivity` to `Public` (all 25 pilot topics are pre-confirmed non-Protected-B per resolved decision #6 — still requires human selection in the column, never hardcoded by tooling). Leave `LifecycleState` at `Draft`.

- [ ] **Step 4: Export actual state and reconcile**

Follow `docs/sharepoint-actual-state-csv-format.md` to export the library view to CSV, then run:

```bash
cd plugins/docx-to-content
python3 scripts/sharepoint_cli.py reconcile \
  --package-dir ../../runs/ceis-manual-v2/sharepoint-upload-package \
  --actual-state <path-to-exported-csv>
```

Confirm `"status": "MATCH"`. If not, fix the mismatched items in SharePoint and re-export/re-reconcile until `MATCH`. Append the final `MATCH` report to `phase-3-pilot-execution-log.md`.

- [ ] **Step 5: Move all 25 topics through Draft → Reviewed → Published**

Using the SharePoint content-approval workflow configured in Step 1 (same reviewer/publisher person, `richard.fremmerlid`, accepted as the pilot exception per resolved decision #8), advance each item to `Published`. Record start/end timestamps in the execution log.

- [ ] **Step 6: Run one republish exercise (block-until-reviewed policy)**

Pick one topic (e.g. the first entry in the upload manifest). Edit its source `.docx` locally in a scratch copy (non-committed), re-run it through the Phase 2 `convert`/`render` pipeline to get updated content and a new `TopicContentSHA256`, rebuild the upload package for that single topic, and attempt to upload the change directly to the `Published` item. Confirm SharePoint's approval workflow blocks it from going live until re-reviewed (this is the resolved block-until-reviewed policy, decision #2) — i.e. the change lands in `Draft`/pending-approval, not immediately visible as `Published`. Record the observed behavior (pass/fail against the policy) in the execution log.

- [ ] **Step 7: Run one rollback exercise**

Using SharePoint's native version history on the same item from Step 6, revert to the prior version. Confirm the reverted content's hash matches the original `TopicContentSHA256` recorded in the upload manifest. Record the result.

- [ ] **Step 8: Run one rename and one retirement exercise**

For a second topic, rename its `Title` and record an explicit `RENAMED` transition entry (per spec's rename/retirement contract — resolved decision: explicit human-confirmed transition record required, no inference from a missing ID). For a third topic, set `LifecycleState` to `Retired` and record an explicit `RETIRED` transition entry. Append both transition records to the execution log.

- [ ] **Step 9: Run the oversharing/permissions check**

Using the pilot site's 3 standard SharePoint groups (Members/Owners/Visitors — resolved decision #9), confirm each group's actual access to `CEIS-Pilot-Knowledge` matches the intended governance model (e.g. Visitors read-only, Members read-only unless explicitly granted contribute, Owners full control). Record findings, and flag any oversharing discovered as a residual risk item in `start-here.md` if found (per Phase 3.0's already-accepted residual-risk item on this exact topic).

- [ ] **Step 10: Commit the evidence log**

```bash
git add docs/superpowers/plans/evidence/phase-3-pilot-execution-log.md runs/ceis-manual-v2/sharepoint-upload-package
git commit -m "docs(phase3): record pilot execution evidence (upload, reconcile, republish/rollback/rename/retire, oversharing check)"
```

---

### Task 6: Exit gate and `start-here.md` update

**Files:**
- Modify: `start-here.md`

- [ ] **Step 1: Verify exit criteria from spec Section 18**

Confirm: all 25 topics uploaded and reconciled to `MATCH`; Draft→Reviewed→Published exercised for all 25; one republish blocked correctly; one rollback verified; one rename and one retirement recorded with explicit transition entries; oversharing check completed with no unresolved findings (or findings explicitly logged as accepted residual risk); all automated tests (Tasks 1–4) passing.

- [ ] **Step 2: Update `start-here.md`**

Add a "Phase 3 — Governed SharePoint Knowledge Pilot: COMPLETE" section summarizing what was built (`sharepoint_package.py`, `sharepoint_dry_run.py`, `sharepoint_reconcile.py`, `sharepoint_cli.py`), where the pilot evidence lives (`docs/superpowers/plans/evidence/phase-3-pilot-execution-log.md`, `runs/ceis-manual-v2/sharepoint-upload-package/`), any residual risks carried forward, and the next-phase resume pointer per `docs/vision/master-initiative-plan-workstreams-and-phases.md`.

- [ ] **Step 3: Commit**

```bash
git add start-here.md
git commit -m "docs: close Phase 3 exit gate in start-here.md"
```

- [ ] **Step 4: Push branch and open PR**

```bash
git push -u origin phase-3-governed-sharepoint-pilot
gh pr create --title "Phase 3: Governed SharePoint Knowledge Pilot" \
  --body "Implements sharepoint_package/sharepoint_dry_run/sharepoint_reconcile/sharepoint_cli, executes the CEIS-Pilot-Knowledge pilot, closes the Phase 3 exit gate."
```
