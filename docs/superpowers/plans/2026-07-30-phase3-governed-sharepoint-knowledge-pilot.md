# Phase 3 — Governed SharePoint Knowledge Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Publish the complete 25-topic CEIS rendered publication into one governed, non-production
SharePoint pilot library (`CEIS-Pilot-Knowledge` on `AG-CSB-ITAU-CMAT-DEV`) via package-only deployment,
proving metadata schema, source-of-truth, reconciliation, republish, rollback, rename/retirement, and
governance behavior — with zero autonomous writes.

**Architecture:** A local package-builder reads the confirmed canonical package + publication map
(`runs/ceis-manual-v2/`) and produces an upload-ready package (content + metadata sidecar + validation
result) entirely offline; a human publisher (richard.fremmerlid, accepted pilot exception covering both
reviewer and publisher roles) performs every SharePoint-side action manually; a local reconciliation tool
compares expected (publication-map-derived) state against actual SharePoint state using data the publisher
exports.

**Tech Stack:** Python (matching `plugins/docx-to-content`'s existing stack), the existing
`docx-to-content` plugin's `contracts.py`/`package.py`/`validate_canonical.py` modules (no reimplementation),
pytest for repository-side unit tests. SharePoint-side tooling (PnP PowerShell) is used only for human-
performed, staged, reversible actions per the write-exploration findings — never an autonomous write from
this plan's code.

## Global Constraints

- Package-only deployment only — no task in this plan implements an autonomous SharePoint write.
- New code lives inside `plugins/docx-to-content/` (existing plugin boundary; no new plugin created this
  phase).
- TDD throughout: failing test first, per `.agent/rules/test-driven-development.md`.
- Every SharePoint-side action a human performs is staged and reversible (`TEST-DO-NOT-USE-*` naming where
  applicable), per the write-exploration findings' staged-write protocol.
- Site: `https://bcgov.sharepoint.com/sites/AG-CSB-ITAU-CMAT-DEV`. Pilot library: `CEIS-Pilot-Knowledge`
  (does not exist yet — created in Task 2 below). Reviewer/publisher: richard.fremmerlid (accepted pilot
  exception, both roles).
- Real fixture package for all tests: `runs/ceis-manual-v2/canonical-content/` (manifest.json, 25 chunks,
  319 media files, `package_identity = sha256:041e1186682322ba11d64abdafbc547dfb793083b9c22a6663aad3008a53d9d3`)
  and `runs/ceis-manual-v2/render/rendered-output/` (rendered Markdown + media). No synthetic fixtures —
  this repo's Task 18 lesson is that synthetic fixtures previously masked real defects.

---

## Task 1: Schema-mapping document

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/schema-mapping.md`

**Interfaces:**
- Consumes: `phase-3-governed-sharepoint-knowledge-pilot-spec.md` Section 7 (field-authority matrix),
  `phase-3-tenant-capability-report.md` §1 (confirmed tenant-wide field/versioning facts).
- Produces: the canonical/publication contract → SharePoint column mapping Task 4 (package builder) and
  Task 8 (dry-run validation) read.

- [ ] **Step 1:** Create `docs/reports/phase-3-sharepoint-pilot/schema-mapping.md` with a short pointer to
  spec Section 7 (cite the exact commit hash of the spec at time of writing via `git log -1 --format=%H
  docs/superpowers/specs/phase-3-governed-sharepoint-knowledge-pilot-spec.md`), then a table extracting only
  the columns needed for traceability: business name, proposed SharePoint column name, proposed type,
  exact source field in `contracts.py`. Use this table:

```markdown
| Business name | SharePoint column | Type | Source field (contracts.py) |
|---|---|---|---|
| Topic identity | `TopicID` | Single line text | `PublicationMapEntry.topic_id` |
| Chunk identity | `ChunkID` | Single line text | `PublicationMapEntry.chunk_id` |
| Package identity | `PackageIdentity` | Single line text | `PublicationMap.package_identity` |
| Topic content hash | `TopicContentSHA256` | Single line text | `ChunkMetadata.content_sha256` |
| Source document fingerprint | `SourceDocumentSHA256` | Single line text | `ManifestSourceFingerprint.sha256` |
| Source package validation status | `SourcePackageValidationStatus` | Choice (PASS/WARN/FAIL) | `ValidationReport.status` |
| Title | `Title` | Single line text | `PublicationMapEntry.title` |
| Publication order | `PublicationOrder` | Number | `PublicationMapEntry.order` |
| Owner | `Owner` | Person | Human decision (richard.fremmerlid for pilot) |
| Status | `Status` | Choice (Draft/Reviewed/Published/Retired) | Section 14 workflow |
| Review date | `ReviewDate` | Date | Human decision |
| Publication event | `PublishedAt`/`PublishedBy` | Date/Person, or native versioning columns if confirmed | Generated at upload |
| Sensitivity | `Sensitivity` | Choice (custom, not tenant MIP label — resolved 2026-07-30) | Human decision |
| Transition record | `TransitionAction` (Choice: RENAMED/RETIRED/SUPERSEDED), `TransitionTarget` (text), `TransitionReason` (text), `TransitionDate` (Date) | — | Section 13 |
```

- [ ] **Step 2:** Note explicitly under the table: "Structural anchor IDs (`ChunkMetadata.anchors`) are
  `NOT_MAPPED` — retained in the evidence package/sidecar (Task 5), not a SharePoint column. `PublicationID`
  was considered and rejected — `PackageIdentity` + `PublicationOrder` is used instead (spec Section 7,
  Option A)."
- [ ] **Step 3:** Commit.

```bash
git add docs/reports/phase-3-sharepoint-pilot/schema-mapping.md
git commit -m "docs(phase3): add schema-mapping document (Task 1)"
```

---

## Task 2: Create the pilot library (human-performed, staged)

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/pilot-library-creation-log.md`

**Interfaces:**
- Consumes: schema-mapping.md (Task 1).
- Produces: a real `CEIS-Pilot-Knowledge` document library with the 14 columns from Task 1's table, which
  every later task's real-tenant steps depend on.

- [ ] **Step 1 (human-performed, via PnP PowerShell — reuse the existing
  `tools/phase-3-sharepoint-discovery/phase-3-0-tenant-discovery.ps1` connection pattern, i.e.
  `Connect-PnPOnline -Url https://bcgov.sharepoint.com/sites/AG-CSB-ITAU-CMAT-DEV -Interactive
  -ForceAuthentication`):** Run `New-PnPList -Title "CEIS-Pilot-Knowledge" -Template DocumentLibrary`, then
  `Add-PnPField` once per column in Task 1's table (14 fields), matching the exact name/type from that
  table.
- [ ] **Step 2:** Record the exact commands run, their output, and the resulting list's `Id`/`Title` in
  `pilot-library-creation-log.md`.
- [ ] **Step 3:** Commit the log (not any tenant-specific script output beyond what's already the convention
  for this repo — see `.gitignore`'s existing `tools/phase-3-sharepoint-discovery/config.psd1` exclusion).

```bash
git add docs/reports/phase-3-sharepoint-pilot/pilot-library-creation-log.md
git commit -m "docs(phase3): record CEIS-Pilot-Knowledge library creation (Task 2)"
```

---

## Task 3: Upload-ready package builder

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_package.py`
- Test: `plugins/docx-to-content/tests/unit/test_sharepoint_package.py`

**Interfaces:**
- Consumes: `contracts.Manifest`, `contracts.PublicationMap`, `contracts.ChunkMetadata`,
  `contracts.ValidationReport` (all in `plugins/docx-to-content/scripts/contracts.py`); real fixture at
  `runs/ceis-manual-v2/canonical-content/` and `runs/ceis-manual-v2/render/rendered-output/`.
- Produces: `build_upload_package(canonical_dir: Path, render_dir: Path) -> UploadPackage` — new dataclasses
  in `sharepoint_package.py`:
  ```python
  @dataclass
  class UploadPackageTopic:
      topic_id: str
      chunk_id: str
      title: str
      publication_order: int
      content_path: Path          # rendered Markdown file under render_dir
      media_paths: list           # list[Path]
      package_identity: str
      topic_content_sha256: str
      source_document_sha256: str

  @dataclass
  class UploadPackage:
      topics: list                # list[UploadPackageTopic]
      metadata_sidecar_path: Path
      source_package_validation_status: str
  ```
  Consumed by Task 8 (`validate_upload_package`).

- [ ] **Step 1: Write the failing test**

```python
# plugins/docx-to-content/tests/unit/test_sharepoint_package.py
from pathlib import Path
from sharepoint_package import build_upload_package

CANONICAL_DIR = Path(__file__).resolve().parents[3] / "runs" / "ceis-manual-v2" / "canonical-content"
RENDER_DIR = Path(__file__).resolve().parents[3] / "runs" / "ceis-manual-v2" / "render" / "rendered-output"


def test_build_upload_package_produces_25_topics_with_required_fields():
    pkg = build_upload_package(CANONICAL_DIR, RENDER_DIR)

    assert len(pkg.topics) == 25
    for topic in pkg.topics:
        assert topic.topic_id
        assert topic.chunk_id
        assert topic.package_identity
        assert topic.topic_content_sha256
        assert topic.publication_order is not None
        assert topic.content_path.exists()

    assert pkg.source_package_validation_status == "PASS"
    assert pkg.metadata_sidecar_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_package.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sharepoint_package'`

- [ ] **Step 3: Write minimal implementation**

```python
# plugins/docx-to-content/scripts/sharepoint_package.py
"""Builds an upload-ready package for the Phase 3 SharePoint pilot from a
confirmed canonical package + publication map. Package-only: this module
performs zero SharePoint I/O."""

import json
from dataclasses import dataclass, field
from pathlib import Path

import contracts


@dataclass
class UploadPackageTopic:
    topic_id: str
    chunk_id: str
    title: str
    publication_order: int
    content_path: Path
    media_paths: list
    package_identity: str
    topic_content_sha256: str
    source_document_sha256: str


@dataclass
class UploadPackage:
    topics: list
    metadata_sidecar_path: Path
    source_package_validation_status: str


def _load_manifest(canonical_dir: Path) -> contracts.Manifest:
    with open(canonical_dir / "manifest.json", encoding="utf-8") as f:
        return contracts.Manifest.from_dict(json.load(f))


def _load_publication_map(canonical_dir: Path) -> contracts.PublicationMap:
    with open(canonical_dir / "publication-map.json", encoding="utf-8") as f:
        return contracts.PublicationMap.from_dict(json.load(f))


def _load_validation_report(canonical_dir: Path, manifest: contracts.Manifest) -> contracts.ValidationReport:
    with open(canonical_dir / manifest.validation_report, encoding="utf-8") as f:
        return contracts.ValidationReport.from_dict(json.load(f))


def _load_chunk_metadata(canonical_dir: Path, chunk: contracts.ManifestChunk) -> contracts.ChunkMetadata:
    with open(canonical_dir / chunk.metadata_file, encoding="utf-8") as f:
        return contracts.ChunkMetadata.from_dict(json.load(f))


def build_upload_package(canonical_dir: Path, render_dir: Path) -> UploadPackage:
    manifest = _load_manifest(canonical_dir)
    pub_map = _load_publication_map(canonical_dir)
    validation = _load_validation_report(canonical_dir, manifest)

    chunks_by_id = {c.chunk_id: c for c in manifest.chunks}
    topics = []
    for entry in pub_map.entries:
        chunk = chunks_by_id[entry.chunk_id]
        chunk_meta = _load_chunk_metadata(canonical_dir, chunk)
        content_path = render_dir / "pages" / f"{entry.topic_id}.md"
        media_paths = [render_dir / "media" / m for m in chunk_meta.media_refs]
        topics.append(
            UploadPackageTopic(
                topic_id=entry.topic_id,
                chunk_id=entry.chunk_id,
                title=entry.title,
                publication_order=entry.order,
                content_path=content_path,
                media_paths=media_paths,
                package_identity=pub_map.package_identity,
                topic_content_sha256=chunk_meta.content_sha256,
                source_document_sha256=manifest.source.sha256,
            )
        )

    sidecar_path = canonical_dir.parent / "sharepoint-upload-metadata.json"
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "topic_id": t.topic_id,
                    "chunk_id": t.chunk_id,
                    "title": t.title,
                    "publication_order": t.publication_order,
                    "package_identity": t.package_identity,
                    "topic_content_sha256": t.topic_content_sha256,
                    "source_document_sha256": t.source_document_sha256,
                }
                for t in topics
            ],
            f,
            indent=2,
        )

    return UploadPackage(
        topics=topics,
        metadata_sidecar_path=sidecar_path,
        source_package_validation_status=validation.status,
    )
```

- [ ] **Step 4: Run test to verify it passes; fix `content_path`/`media_paths` resolution if the real
  rendered-output file naming doesn't match `{topic_id}.md` exactly**

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_package.py -v`
Expected: PASS. If it fails on `content_path.exists()`, inspect the real filenames under
`runs/ceis-manual-v2/render/rendered-output/pages/` (they include a content-hash suffix, e.g.
`ceis-training--94f8aa2a.md`) and adjust the lookup to match on a glob of `{topic_id}--*.md` instead of an
exact name — do not hardcode a filename pattern without first confirming it against the real fixture
directory listing.

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_package.py plugins/docx-to-content/tests/unit/test_sharepoint_package.py
git commit -m "feat(phase3): add upload-ready package builder (Task 3)"
```

---

## Task 4: Dry-run validation

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_dry_run.py`
- Test: `plugins/docx-to-content/tests/unit/test_sharepoint_dry_run.py`

**Interfaces:**
- Consumes: `UploadPackage`, `UploadPackageTopic` from Task 3 (`sharepoint_package.py`).
- Produces:
  ```python
  @dataclass
  class DryRunReport:
      status: str          # "PASS" | "BLOCKED" | "FAIL"
      issues: list          # list[str]
  ```
  `validate_upload_package(pkg: UploadPackage) -> DryRunReport`, consumed by Task 5's upload-log step as a
  precondition check.

- [ ] **Step 1: Write the failing test**

```python
# plugins/docx-to-content/tests/unit/test_sharepoint_dry_run.py
from pathlib import Path
from sharepoint_dry_run import validate_upload_package
from sharepoint_package import UploadPackage, UploadPackageTopic


def _topic(topic_id="t1", chunk_id="c1", order=1, sha="a" * 64):
    return UploadPackageTopic(
        topic_id=topic_id,
        chunk_id=chunk_id,
        title="Title",
        publication_order=order,
        content_path=Path(__file__),  # any file that exists
        media_paths=[],
        package_identity="sha256:abc",
        topic_content_sha256=sha,
        source_document_sha256="sha256:def",
    )


def test_all_pass_package_reports_pass():
    pkg = UploadPackage(topics=[_topic()], metadata_sidecar_path=Path(__file__), source_package_validation_status="PASS")
    report = validate_upload_package(pkg)
    assert report.status == "PASS"
    assert report.issues == []


def test_non_pass_validation_status_reports_fail():
    pkg = UploadPackage(topics=[_topic()], metadata_sidecar_path=Path(__file__), source_package_validation_status="FAIL")
    report = validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any("validation" in i.lower() for i in report.issues)


def test_duplicate_topic_id_reports_fail():
    pkg = UploadPackage(
        topics=[_topic(topic_id="dup"), _topic(topic_id="dup", chunk_id="c2")],
        metadata_sidecar_path=Path(__file__),
        source_package_validation_status="PASS",
    )
    report = validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any("duplicate" in i.lower() for i in report.issues)


def test_missing_content_file_reports_fail():
    pkg = UploadPackage(
        topics=[_topic()],
        metadata_sidecar_path=Path(__file__),
        source_package_validation_status="PASS",
    )
    pkg.topics[0].content_path = Path("/nonexistent/file.md")
    report = validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any("content" in i.lower() for i in report.issues)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_dry_run.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sharepoint_dry_run'`

- [ ] **Step 3: Write minimal implementation**

```python
# plugins/docx-to-content/scripts/sharepoint_dry_run.py
"""Offline dry-run validation for an UploadPackage before manual SharePoint
upload. Zero SharePoint I/O."""

from dataclasses import dataclass

from sharepoint_package import UploadPackage


@dataclass
class DryRunReport:
    status: str
    issues: list


def validate_upload_package(pkg: UploadPackage) -> DryRunReport:
    issues = []

    if pkg.source_package_validation_status != "PASS":
        issues.append(
            f"Source canonical package validation status is "
            f"'{pkg.source_package_validation_status}', not PASS — package not eligible for upload."
        )

    seen_topic_ids = set()
    for topic in pkg.topics:
        if topic.topic_id in seen_topic_ids:
            issues.append(f"Duplicate topic_id: {topic.topic_id}")
        seen_topic_ids.add(topic.topic_id)

        if not topic.topic_id or not topic.chunk_id or not topic.package_identity or not topic.topic_content_sha256:
            issues.append(f"Topic {topic.topic_id!r} is missing a required field.")

        if not topic.content_path.exists():
            issues.append(f"Content file for topic {topic.topic_id!r} does not exist: {topic.content_path}")

        for media_path in topic.media_paths:
            if not media_path.exists():
                issues.append(f"Media reference for topic {topic.topic_id!r} does not resolve: {media_path}")

    if any("validation status" in i or "missing a required field" in i or "does not exist" in i
           or "does not resolve" in i or "Duplicate" in i for i in issues):
        status = "FAIL"
    else:
        status = "PASS"

    return DryRunReport(status=status, issues=issues)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_dry_run.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_dry_run.py plugins/docx-to-content/tests/unit/test_sharepoint_dry_run.py
git commit -m "feat(phase3): add dry-run validation (Task 4)"
```

---

## Task 5: Manual upload log template + execution (human-performed)

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/upload-log-template.md`
- Create: `docs/reports/phase-3-sharepoint-pilot/upload-log-2026-07-30.md` (or the actual execution date)

**Interfaces:**
- Consumes: `UploadPackage` (Task 3), `DryRunReport` (Task 4) — dry-run must report `PASS` before Step 3
  below proceeds.

- [ ] **Step 1:** Create `upload-log-template.md` with these fields per spec Section 11: date/time,
  publisher identity (richard.fremmerlid), pilot library target (`CEIS-Pilot-Knowledge`), topics uploaded
  in order (25 rows: topic_id, title, publication_order), every manual step performed, deviations from
  plan, screenshot/export confirmation reference.
- [ ] **Step 2:** Run `build_upload_package` (Task 3) then `validate_upload_package` (Task 4) against the
  real fixture; confirm `DryRunReport.status == "PASS"` before proceeding. If not PASS, stop and fix the
  underlying issue — do not upload a package that fails its own dry run.
- [ ] **Step 3 (human-performed):** Using the metadata sidecar (Task 3's `metadata_sidecar_path`) and the
  25 rendered Markdown files + 319 media files, manually create one SharePoint list item per topic in
  `CEIS-Pilot-Knowledge`, in `publication_order`, filling every column from Task 1's schema-mapping table,
  setting `Status = Draft`.
- [ ] **Step 4:** Fill in `upload-log-2026-07-30.md` from the template with the real upload's details.
- [ ] **Step 5:** Commit the completed log.

```bash
git add docs/reports/phase-3-sharepoint-pilot/upload-log-template.md docs/reports/phase-3-sharepoint-pilot/upload-log-2026-07-30.md
git commit -m "docs(phase3): record pilot upload execution (Task 5)"
```

---

## Task 6: Reconciliation comparator

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_reconcile.py`
- Test: `plugins/docx-to-content/tests/unit/test_sharepoint_reconcile.py`

**Interfaces:**
- Consumes: `UploadPackage` (Task 3) as "expected state"; a new `ActualLibraryState`/`ActualLibraryItem`
  input (below) representing what the publisher manually exports from SharePoint (a CSV/JSON export of the
  `CEIS-Pilot-Knowledge` list — the exact export mechanism is a human step performed at Task 7 time, not
  built by this task).
- Produces:
  ```python
  @dataclass
  class TransitionRecord:
      action: str            # "RENAMED" | "RETIRED" | "SUPERSEDED"
      target_topic_id: str    # "" if none
      reason: str
      date: str

  @dataclass
  class ActualLibraryItem:
      topic_id: str
      chunk_id: str
      package_identity: str
      topic_content_sha256: str
      publication_order: int
      source_package_validation_status: str
      status: str             # "Draft" | "Reviewed" | "Published" | "Retired"
      transition_record: object  # TransitionRecord | None

  @dataclass
  class ActualLibraryState:
      items: list             # list[ActualLibraryItem]

  @dataclass
  class ReconciliationReport:
      missing: list
      duplicate: list
      stale: list
      unexpected_active: list
      unexpected_retired: list
      retired_expected: list
      mismatched_package_identity: list
      mismatched_publication_identity: list
      mismatched_validation_lineage: list
      transitions: list
  ```
  `reconcile(expected: UploadPackage, actual: ActualLibraryState) -> ReconciliationReport`, consumed by
  Task 7's `--dry-run` CLI wrapper and Tasks 8-10's republish/rollback/rename exercises.

- [ ] **Step 1: Write the failing test** — one case per issue category (spec Section 12), using the real
  25-topic `UploadPackage` from Task 3 as the expected side, and hand-built `ActualLibraryState` fixtures
  for the actual side:

```python
# plugins/docx-to-content/tests/unit/test_sharepoint_reconcile.py
from pathlib import Path

from sharepoint_package import build_upload_package
from sharepoint_reconcile import ActualLibraryItem, ActualLibraryState, TransitionRecord, reconcile

CANONICAL_DIR = Path(__file__).resolve().parents[3] / "runs" / "ceis-manual-v2" / "canonical-content"
RENDER_DIR = Path(__file__).resolve().parents[3] / "runs" / "ceis-manual-v2" / "render" / "rendered-output"


def _matching_actual_items(expected):
    return [
        ActualLibraryItem(
            topic_id=t.topic_id,
            chunk_id=t.chunk_id,
            package_identity=t.package_identity,
            topic_content_sha256=t.topic_content_sha256,
            publication_order=t.publication_order,
            source_package_validation_status="PASS",
            status="Published",
            transition_record=None,
        )
        for t in expected.topics
    ]


def test_clean_no_issues_case():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual = ActualLibraryState(items=_matching_actual_items(expected))
    report = reconcile(expected, actual)
    assert report.missing == []
    assert report.duplicate == []
    assert report.stale == []
    assert report.unexpected_active == []
    assert report.mismatched_package_identity == []


def test_missing_item():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)[1:]  # drop the first expected topic
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert expected.topics[0].topic_id in report.missing


def test_duplicate_item():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items.append(actual_items[0])  # duplicate the first item
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert expected.topics[0].topic_id in report.duplicate


def test_stale_content_hash():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items[0].topic_content_sha256 = "0" * 64  # drifted content hash
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert expected.topics[0].topic_id in report.stale


def test_unexpected_active_item():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items.append(
        ActualLibraryItem(
            topic_id="not-in-publication-map",
            chunk_id="c-x",
            package_identity=expected.topics[0].package_identity,
            topic_content_sha256="1" * 64,
            publication_order=999,
            source_package_validation_status="PASS",
            status="Published",
            transition_record=None,
        )
    )
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert "not-in-publication-map" in report.unexpected_active


def test_unexpected_retired_item():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items.append(
        ActualLibraryItem(
            topic_id="ghost-retired",
            chunk_id="c-y",
            package_identity=expected.topics[0].package_identity,
            topic_content_sha256="2" * 64,
            publication_order=998,
            source_package_validation_status="PASS",
            status="Retired",
            transition_record=None,
        )
    )
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert "ghost-retired" in report.unexpected_retired


def test_retired_expected_item():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items[0].status = "Retired"  # expected topic marked retired in SharePoint
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert expected.topics[0].topic_id in report.retired_expected


def test_mismatched_package_identity():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items[0].package_identity = "sha256:different"
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert expected.topics[0].topic_id in report.mismatched_package_identity


def test_mismatched_publication_identity():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items[0].publication_order = actual_items[0].publication_order + 100
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert expected.topics[0].topic_id in report.mismatched_publication_identity


def test_mismatched_validation_lineage():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items[0].source_package_validation_status = "WARN"
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert expected.topics[0].topic_id in report.mismatched_validation_lineage


def test_transition_record_is_carried_through():
    expected = build_upload_package(CANONICAL_DIR, RENDER_DIR)
    actual_items = _matching_actual_items(expected)
    actual_items[0].status = "Retired"
    actual_items[0].transition_record = TransitionRecord(
        action="SUPERSEDED", target_topic_id="replacement-topic", reason="content merged", date="2026-07-30"
    )
    report = reconcile(expected, ActualLibraryState(items=actual_items))
    assert any("SUPERSEDED" in t for t in report.transitions)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_reconcile.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sharepoint_reconcile'`

- [ ] **Step 3: Write minimal implementation**

```python
# plugins/docx-to-content/scripts/sharepoint_reconcile.py
"""Pure reconciliation comparator: expected (UploadPackage) vs actual
(ActualLibraryState, however the publisher exported it). Zero SharePoint
I/O — the export mechanism is a separate, human-performed concern."""

from dataclasses import dataclass

from sharepoint_package import UploadPackage


@dataclass
class TransitionRecord:
    action: str
    target_topic_id: str
    reason: str
    date: str


@dataclass
class ActualLibraryItem:
    topic_id: str
    chunk_id: str
    package_identity: str
    topic_content_sha256: str
    publication_order: int
    source_package_validation_status: str
    status: str
    transition_record: object


@dataclass
class ActualLibraryState:
    items: list


@dataclass
class ReconciliationReport:
    missing: list
    duplicate: list
    stale: list
    unexpected_active: list
    unexpected_retired: list
    retired_expected: list
    mismatched_package_identity: list
    mismatched_publication_identity: list
    mismatched_validation_lineage: list
    transitions: list


def reconcile(expected: UploadPackage, actual: ActualLibraryState) -> ReconciliationReport:
    expected_by_id = {t.topic_id: t for t in expected.topics}

    seen_ids = set()
    duplicate_ids = set()
    actual_by_id = {}
    for item in actual.items:
        if item.topic_id in seen_ids:
            duplicate_ids.add(item.topic_id)
        seen_ids.add(item.topic_id)
        actual_by_id[item.topic_id] = item  # last-seen wins for field comparisons

    missing = [tid for tid in expected_by_id if tid not in actual_by_id]
    unexpected_active = [
        item.topic_id for item in actual.items
        if item.topic_id not in expected_by_id and item.status != "Retired"
    ]
    unexpected_retired = [
        item.topic_id for item in actual.items
        if item.topic_id not in expected_by_id and item.status == "Retired"
    ]

    stale = []
    retired_expected = []
    mismatched_package_identity = []
    mismatched_publication_identity = []
    mismatched_validation_lineage = []
    transitions = []

    for tid, expected_topic in expected_by_id.items():
        actual_item = actual_by_id.get(tid)
        if actual_item is None:
            continue
        if actual_item.status == "Retired":
            retired_expected.append(tid)
        if actual_item.topic_content_sha256 != expected_topic.topic_content_sha256:
            stale.append(tid)
        if actual_item.package_identity != expected_topic.package_identity:
            mismatched_package_identity.append(tid)
        if actual_item.publication_order != expected_topic.publication_order:
            mismatched_publication_identity.append(tid)
        if actual_item.source_package_validation_status != "PASS":
            mismatched_validation_lineage.append(tid)
        if actual_item.transition_record is not None:
            tr = actual_item.transition_record
            transitions.append(f"{tid}: {tr.action} -> {tr.target_topic_id} ({tr.reason}, {tr.date})")

    return ReconciliationReport(
        missing=missing,
        duplicate=list(duplicate_ids),
        stale=stale,
        unexpected_active=unexpected_active,
        unexpected_retired=unexpected_retired,
        retired_expected=retired_expected,
        mismatched_package_identity=mismatched_package_identity,
        mismatched_publication_identity=mismatched_publication_identity,
        mismatched_validation_lineage=mismatched_validation_lineage,
        transitions=transitions,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_reconcile.py -v`
Expected: PASS (12 tests)

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_reconcile.py plugins/docx-to-content/tests/unit/test_sharepoint_reconcile.py
git commit -m "feat(phase3): add reconciliation comparator (Task 6)"
```

---

## Task 7: Reconciliation CLI + lineage trace record

**Files:**
- Modify: `plugins/docx-to-content/scripts/sharepoint_reconcile.py` (add `main()`/CLI entry point)
- Test: extend `plugins/docx-to-content/tests/unit/test_sharepoint_reconcile.py`
- Create: `docs/reports/phase-3-sharepoint-pilot/lineage-trace-template.md`

**Interfaces:**
- Consumes: `reconcile` (Task 6).
- Produces: a `--dry-run` CLI that reads an actual-state export (JSON, matching `ActualLibraryState`'s
  shape) and the real `UploadPackage`, prints a human-readable `ReconciliationReport`, performs zero writes.

- [ ] **Step 1: Write the failing test**

```python
def test_cli_dry_run_prints_report_and_writes_nothing(tmp_path, capsys):
    import json
    from sharepoint_reconcile import main

    actual_state_path = tmp_path / "actual.json"
    actual_state_path.write_text(json.dumps({"items": []}), encoding="utf-8")

    exit_code = main(["--dry-run", "--actual-state", str(actual_state_path),
                       "--canonical-dir", str(CANONICAL_DIR), "--render-dir", str(RENDER_DIR)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "missing" in captured.out.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_reconcile.py -v -k cli_dry_run`
Expected: FAIL with `ImportError: cannot import name 'main'`

- [ ] **Step 3: Implement the CLI wrapper** — append to `sharepoint_reconcile.py`:

```python
def main(argv=None) -> int:
    import argparse
    import json
    from pathlib import Path

    from sharepoint_package import build_upload_package

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--actual-state", type=Path, required=True)
    parser.add_argument("--canonical-dir", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    with open(args.actual_state, encoding="utf-8") as f:
        raw = json.load(f)
    actual = ActualLibraryState(
        items=[
            ActualLibraryItem(
                topic_id=i["topic_id"], chunk_id=i["chunk_id"], package_identity=i["package_identity"],
                topic_content_sha256=i["topic_content_sha256"], publication_order=i["publication_order"],
                source_package_validation_status=i["source_package_validation_status"],
                status=i["status"], transition_record=None,
            )
            for i in raw.get("items", [])
        ]
    )
    expected = build_upload_package(args.canonical_dir, args.render_dir)
    report = reconcile(expected, actual)

    print(f"missing: {report.missing}")
    print(f"duplicate: {report.duplicate}")
    print(f"stale: {report.stale}")
    print(f"unexpected_active: {report.unexpected_active}")
    print(f"unexpected_retired: {report.unexpected_retired}")
    print(f"retired_expected: {report.retired_expected}")
    print(f"mismatched_package_identity: {report.mismatched_package_identity}")
    print(f"mismatched_publication_identity: {report.mismatched_publication_identity}")
    print(f"mismatched_validation_lineage: {report.mismatched_validation_lineage}")
    print(f"transitions: {report.transitions}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_reconcile.py -v`
Expected: PASS (13 tests)

- [ ] **Step 5:** Create `lineage-trace-template.md`: given one published item, show the chain SharePoint
  item → `TopicID`/`ChunkID` → `PackageIdentity` → confirmed canonical package (`plan_id`) → source DOCX
  fingerprint (`SourceDocumentSHA256`, evidence-only).
- [ ] **Step 6 (human-performed, requires Task 5's completed upload):** trace one real published item
  through the chain above using the actual `CEIS-Pilot-Knowledge` data and the sidecar from Task 3; fill the
  template with real values.
- [ ] **Step 7: Commit**

```bash
git add plugins/docx-to-content/scripts/sharepoint_reconcile.py plugins/docx-to-content/tests/unit/test_sharepoint_reconcile.py docs/reports/phase-3-sharepoint-pilot/lineage-trace-template.md
git commit -m "feat(phase3): add reconciliation CLI + lineage trace record (Task 7)"
```

---

## Task 8: Republish, rollback, rename/retirement exercises (human-performed)

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/republish-exercise.md`
- Create: `docs/reports/phase-3-sharepoint-pilot/rollback-exercise.md`
- Create: `docs/reports/phase-3-sharepoint-pilot/rename-retirement-exercise.md`

**Interfaces:**
- Consumes: `reconcile`/CLI (Task 6-7), source-of-truth lifecycle (spec Section 8's block-until-reviewed
  policy).

- [ ] **Step 1 (republish exercise):** Pick one uploaded topic. Edit its content directly in SharePoint
  (simulating manual drift). Run the Task 7 CLI against an actual-state export capturing this drift; record
  the `stale` result in `republish-exercise.md`. Re-run the package builder + republish that one item from
  canonical content (overwrite in SharePoint per the "canonical wins" rule). Re-run reconciliation; record
  the after-state showing `stale` is now empty for that topic.
- [ ] **Step 2 (rollback exercise):** Using SharePoint's native version history on the same item, restore
  the prior (drifted) version. Record before/after reconciliation output in `rollback-exercise.md`,
  demonstrating the native version history mechanism (confirmed available, 104/106 lists versioned per
  `tenant-capability-report.md` §1) is sufficient without a separate `PublishedVersion` column.
- [ ] **Step 3 (rename/retirement exercise):** Pick a second uploaded topic. Mark it Retired in SharePoint
  with a `TransitionRecord` (`action="RETIRED"`, reason, date). Run reconciliation; record the
  `retired_expected` result and the `transitions` entry in `rename-retirement-exercise.md`.
- [ ] **Step 4:** Commit all three exercise files.

```bash
git add docs/reports/phase-3-sharepoint-pilot/republish-exercise.md docs/reports/phase-3-sharepoint-pilot/rollback-exercise.md docs/reports/phase-3-sharepoint-pilot/rename-retirement-exercise.md
git commit -m "docs(phase3): record republish/rollback/rename exercises (Task 8)"
```

---

## Task 9: Governance controls — review workflow, oversharing test, authorized-write design

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/review-workflow-walkthrough.md`
- Create: `docs/reports/phase-3-sharepoint-pilot/oversharing-test-report.md`
- Create: `docs/superpowers/specs/phase-3-authorized-write-design.md`

**Interfaces:**
- Consumes: Task 5's uploaded items; `tenant-capability-report.md` §5 (standard groups as test identities).

- [ ] **Step 1 (review-workflow walkthrough, human-performed):** Record one real item's Draft → Reviewed →
  Published transition (spec Section 14 Model A): upload as Draft (already done, Task 5) → review in
  SharePoint → mark Reviewed → run reconciliation (Task 7 CLI) → mark Published. Record timestamps and that
  richard.fremmerlid performed every transition (accepted pilot exception) in
  `review-workflow-walkthrough.md`.
- [ ] **Step 2 (oversharing/permission test, human-performed):** Using the 3 standard groups (Members,
  Owners, Visitors — `tenant-capability-report.md` §5) as the test identities, check what each group can
  see on `CEIS-Pilot-Knowledge`. Record in `oversharing-test-report.md` whether Visitors (or any broader-
  than-intended group) is assigned access, and whether that matches the intended permission boundary.
- [ ] **Step 3 (authorized-write design-only document):** Write `phase-3-authorized-write-design.md` naming
  a future accountable owner/identity for an authorized-write path — design-only, **no implementation**,
  per spec Section 14/Non-goals. State explicitly: "Owner/identity not yet named — this is the correct
  Stage 3.4.3 output at this pilot stage (design-only, gated), not a plan defect."
- [ ] **Step 4:** Commit all three files.

```bash
git add docs/reports/phase-3-sharepoint-pilot/review-workflow-walkthrough.md docs/reports/phase-3-sharepoint-pilot/oversharing-test-report.md docs/superpowers/specs/phase-3-authorized-write-design.md
git commit -m "docs(phase3): governance controls - review workflow, oversharing test, authorized-write design (Task 9)"
```

---

## Task 10: Readiness-check report and retrospective

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/readiness-check-report.md`
- Create: `docs/reports/phase-3-sharepoint-pilot/phase-3-retrospective.md`

**Interfaces:**
- Consumes: every evidence artifact from Tasks 1-9, cited by exact file path.

- [ ] **Step 1:** Check every uploaded pilot item (Task 5) against the reconciled schema (Task 1) for
  completeness — every field populated, `SourcePackageValidationStatus == PASS`, no `missing`/`duplicate`
  in the final reconciliation run. Record in `readiness-check-report.md`.
- [ ] **Step 2:** Write `phase-3-retrospective.md`, citing every evidence artifact from Tasks 1-9 by file
  path (not summarized from memory) — schema-mapping.md, pilot-library-creation-log.md,
  upload-log-2026-07-30.md, lineage-trace-template.md (filled), republish/rollback/rename-retirement
  exercises, review-workflow-walkthrough.md, oversharing-test-report.md, phase-3-authorized-write-design.md.
- [ ] **Step 3:** State explicitly which Phase 4/5 requirements the pilot surfaced as real (not assumed) —
  e.g. whether native `.agent`/`SKILL.md` deployment (write-exploration findings) remains "technically
  viable, no supported deployment interface" after this pilot's evidence, or whether anything changed that
  assessment.
- [ ] **Step 4:** Commit — this document becomes the entry-gate evidence for Phase 4/5.

```bash
git add docs/reports/phase-3-sharepoint-pilot/readiness-check-report.md docs/reports/phase-3-sharepoint-pilot/phase-3-retrospective.md
git commit -m "docs(phase3): readiness check + retrospective (Task 10) - Phase 3 exit gate"
```

---

## Task 11: Update start-here.md and merge

**Files:**
- Modify: `start-here.md`

- [ ] **Step 1:** Run the full test suite for the new modules:

Run: `cd plugins/docx-to-content && python -m pytest tests/unit/test_sharepoint_package.py tests/unit/test_sharepoint_dry_run.py tests/unit/test_sharepoint_reconcile.py -v`
Expected: all PASS.

- [ ] **Step 2:** Update `start-here.md` — mark Phase 3 complete, list every evidence artifact by path
  (Tasks 1-10), note the exit-gate is `phase-3-retrospective.md` (Task 10), and record that
  `phase-3-0-tenant-capability-discovery` is the branch this was executed on.
- [ ] **Step 3:** Report `git status --short`, the full test run, and all evidence artifact paths per the
  Per-Phase Git & Session Workflow (`docs/vision/master-initiative-plan-workstreams-and-phases.md`) before
  merging to `main`.
- [ ] **Step 4:** Commit `start-here.md`, then merge this branch to `main` only once the exit-gate evidence
  (Task 10) exists.

```bash
git add start-here.md
git commit -m "docs: mark Phase 3 complete, update start-here.md (Task 11)"
```
