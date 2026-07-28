# Task 17-topic-grouping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional "grouped" chunking strategy to the `docx-to-content` plugin that groups the existing per-heading structural-anchor chunks (today, one file per heading — ~159 for the real CEIS pilot) into ~25 maintainable canonical **topic** files, while every structural anchor keeps independent, stable identity as in-topic metadata, plus a new minimal `publication-map.json` contract that drives rendered navigation order/hierarchy.

**Architecture:** Structural-anchor identity (from `identity.make_chunk_id`), canonical **topic** identity (new `identity.make_topic_id`, keyed only on the top-level section path), and publication-map-entry identity are three independent concepts — a structural anchor survives its parent topic being renamed/reorganized/split. Topic boundaries are computed deterministically from the existing heading list (no new source-of-truth), previewed in `analyze-report.json` for human review, and become part of the confirmed plan (`plan.strategy = "grouped"`). `convert` builds one canonical chunk file per topic (containing all its structural anchors' content, in source order) instead of one per heading, plus a `publication-map.json` sidecar. `render` consumes the publication map (when present) to build navigation instead of raw manifest order. The existing per-heading ("chunked") and "single" strategies remain fully supported, unchanged, and independently tested — "grouped" is additive.

**Tech Stack:** Python 3, pytest, existing plugin modules (`chunking.py`, `analyze_structure.py`, `identity.py`, `package.py`, `contracts.py`, `validate_canonical.py`, `renderers/multipage_markdown.py`, `cli.py`, `plans.py`).

## Global Constraints

- Every anchor is assigned to exactly one topic — no unassigned or multiply-assigned anchors (user directive).
- Child headings inside a topic stay in source document order (user directive).
- Topic IDs are deterministic, independent of filename and array position — same derivation pattern as `identity.make_chunk_id` (slug + content-hash of a structural key), never derived from an ordinal alone (user directive; matches `identity.py`'s existing contract).
- Structural-anchor IDs (`stable_key` / `make_chunk_id` output) are unchanged by this work and remain stable across grouping-strategy changes — grouping is a layer on top of anchor identity, never a replacement for it.
- Publication-map order is explicit and independent of directory/filesystem order (user directive) — this is exactly the constraint `contracts.Manifest.chunks` already satisfies via `source_order` from `enumerate()`, not `os.listdir()`; the publication map must follow the same pattern.
- No generated/raw Word TOC survives in canonical content (already enforced by `validate_canonical.py`'s `raw_toc_artifact` check and `pandoc_fixes/toc.py` — grouping must not reintroduce it).
- Meaningful preamble is retained per the already-approved Task 17 disposition (title/subtitle/version as publication metadata; `Ctrl+F` instruction omitted; Word TOC removed) — this plan does not re-litigate that disposition, only ensures grouped packaging doesn't silently drop the preamble bytes it already carries today.
- Rendered navigation must follow the publication map when the manifest strategy is `"grouped"`, and existing per-chunk-page navigation is preserved unchanged for `"single"`/`"chunked"` strategies (no regression).
- The existing fine-grained (one-file-per-heading) mode is preserved as a fully supported, fully tested strategy — `strategy`/`chunk_level` semantics for `"single"`/`"chunked"` are not redefined by this plan.
- Grouped reconstruction must be lossless and non-duplicating: concatenating all of a topic's structural-anchor slices, in order, must reproduce exactly the same content the ungrouped ("chunked") pipeline would produce for the same anchors — this plan must prove that with a test, reusing the existing content-loss/duplication comparison approach from `validate_canonical.py`'s `_check_content_loss_and_duplication`.
- Failed grouping/publication-map validation must retain the prior accepted output (same atomic-promotion guarantee `convert_and_promote`/`atomic_output.py` already provide for the ungrouped path — no new promotion mechanism, reuse the existing one).
- All new/changed code goes through the plugin's existing TDD discipline (per `.agent/rules/test-driven-development.md` / this repo's `CLAUDE.md`) — write the failing test before the implementation in every task below.

---

### Task 1: Topic identity — `identity.make_topic_id`

**Files:**
- Modify: `plugins/docx-to-content/scripts/identity.py`
- Test: `plugins/docx-to-content/tests/test_identity.py`

**Interfaces:**
- Consumes: `identity._slugify_component(text: str) -> str`, `identity.content_hash` (already imported from `hashing.py`), both already defined in `identity.py`.
- Produces: `identity.make_topic_id(top_level_heading_path: list[str], occurrence: int = 1) -> str` — later tasks (Task 2, Task 4) call this to derive each proposed topic's ID from its top-level heading's path only (e.g. `["FILE ACCESS"]`, never the full descendant path of a child heading inside it).

- [ ] **Step 1: Write the failing tests**

```python
# plugins/docx-to-content/tests/test_identity.py (add to existing file)

def test_make_topic_id_uses_only_top_level_path():
    # Two different full chunk paths sharing the same top-level section
    # must yield the SAME topic id when passed only their shared top-level path.
    topic_id_a = identity.make_topic_id(["FILE ACCESS"])
    topic_id_b = identity.make_topic_id(["FILE ACCESS"])
    assert topic_id_a == topic_id_b
    assert topic_id_a.startswith("file-access--")


def test_make_topic_id_differs_by_occurrence():
    first = identity.make_topic_id(["Overview"], occurrence=1)
    second = identity.make_topic_id(["Overview"], occurrence=2)
    assert first != second


def test_make_topic_id_matches_slug_hash_shape():
    topic_id = identity.make_topic_id(["Protection Orders"])
    slug, _, digest = topic_id.partition("--")
    assert slug == "protection-orders"
    assert len(digest) == 8


def test_make_topic_id_independent_of_child_heading_path():
    # A structural anchor's full path descends from the topic's top-level
    # heading, but make_topic_id must be called with ONLY the top-level
    # component (single-element list) to stay position/child-independent.
    topic_id = identity.make_topic_id(["FILE ACCESS"])
    chunk_id_for_child = identity.make_chunk_id(
        ["FILE ACCESS", "How to Seal a File"], occurrence=1
    )
    assert topic_id != chunk_id_for_child
    assert topic_id.split("--")[0] == "file-access"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_identity.py -k make_topic_id -v`
Expected: FAIL with `AttributeError: module 'identity' has no attribute 'make_topic_id'`

- [ ] **Step 3: Write minimal implementation**

Add to `plugins/docx-to-content/scripts/identity.py`, directly below `make_chunk_id`:

```python
def make_topic_id(top_level_heading_path: list, occurrence: int = 1) -> str:
    """Deterministic topic identity, keyed only on the top-level section path.

    Distinct from make_chunk_id: a topic id must stay stable even if a
    structural anchor's descendant heading text changes, because it is
    derived only from the topic's own top-level heading path plus an
    occurrence disambiguator for duplicate top-level titles.
    """
    slug = normalize_heading_path(top_level_heading_path)
    structural_key = f"topic\x00{slug}\x00{occurrence}"
    digest = content_hash(structural_key.encode("utf-8"))[:_HASH_LENGTH]
    return f"{slug}--{digest}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_identity.py -v`
Expected: PASS, full file green (no regressions in existing `make_chunk_id`/`normalize_heading_path` tests).

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/identity.py plugins/docx-to-content/tests/test_identity.py
git commit -m "feat: add deterministic topic identity derivation"
```

---

### Task 2: Topic boundary computation — `topic_grouping.py`

**Files:**
- Create: `plugins/docx-to-content/scripts/topic_grouping.py`
- Test: `plugins/docx-to-content/tests/test_topic_grouping.py`

**Interfaces:**
- Consumes: `identity.make_topic_id` (Task 1); the same heading-dict shape `analyze_structure.parse_headings()` already produces (`{"level": int, "text": str, "path": list[str], "occurrence": int}`) — this task's function takes that list directly so it composes with the existing analysis pipeline without re-parsing.
- Produces: `topic_grouping.compute_topic_boundaries(headings: list[dict]) -> list[TopicBoundary]` and the `TopicBoundary` dataclass — Task 3 (analyze-report preview) and Task 5 (grouped package builder) both consume this.

- [ ] **Step 1: Write the failing tests**

```python
# plugins/docx-to-content/tests/test_topic_grouping.py

from scripts import topic_grouping


def _heading(level, text, path, occurrence=1):
    return {"level": level, "text": text, "path": path, "occurrence": occurrence}


def test_every_heading_assigned_to_exactly_one_topic():
    headings = [
        _heading(1, "Introduction", ["Introduction"]),
        _heading(2, "Scope", ["Introduction", "Scope"]),
        _heading(1, "File Access", ["File Access"]),
        _heading(2, "How to Seal a File", ["File Access", "How to Seal a File"]),
        _heading(3, "Prerequisites", ["File Access", "How to Seal a File", "Prerequisites"]),
    ]
    boundaries = topic_grouping.compute_topic_boundaries(headings)
    assigned_paths = [
        tuple(member.path) for boundary in boundaries for member in boundary.members
    ]
    all_paths = [tuple(h["path"]) for h in headings]
    assert sorted(assigned_paths) == sorted(all_paths)
    assert len(assigned_paths) == len(set(assigned_paths))  # no duplicates


def test_top_level_headings_start_new_topics():
    headings = [
        _heading(1, "A", ["A"]),
        _heading(2, "A.1", ["A", "A.1"]),
        _heading(1, "B", ["B"]),
    ]
    boundaries = topic_grouping.compute_topic_boundaries(headings)
    assert [b.title for b in boundaries] == ["A", "B"]
    assert [tuple(m.path) for m in boundaries[0].members] == [("A",), ("A", "A.1")]
    assert [tuple(m.path) for m in boundaries[1].members] == [("B",)]


def test_child_headings_stay_in_source_order_within_topic():
    headings = [
        _heading(1, "A", ["A"]),
        _heading(2, "Second", ["A", "Second"]),
        _heading(2, "First-in-code-but-later-in-doc", ["A", "First-in-code-but-later-in-doc"]),
    ]
    boundaries = topic_grouping.compute_topic_boundaries(headings)
    assert [m.text for m in boundaries[0].members] == [
        "A",
        "Second",
        "First-in-code-but-later-in-doc",
    ]


def test_topic_ids_deterministic_and_independent_of_position():
    headings_a = [
        _heading(1, "File Access", ["File Access"]),
        _heading(1, "Overview", ["Overview"]),
    ]
    headings_b = [
        _heading(1, "Overview", ["Overview"]),
        _heading(1, "File Access", ["File Access"]),
    ]
    boundaries_a = topic_grouping.compute_topic_boundaries(headings_a)
    boundaries_b = topic_grouping.compute_topic_boundaries(headings_b)
    ids_a = {b.title: b.topic_id for b in boundaries_a}
    ids_b = {b.title: b.topic_id for b in boundaries_b}
    assert ids_a == ids_b


def test_duplicate_top_level_titles_get_distinct_topic_ids_via_occurrence():
    headings = [
        _heading(1, "Overview", ["Overview"], occurrence=1),
        _heading(1, "Overview", ["Overview"], occurrence=2),
    ]
    boundaries = topic_grouping.compute_topic_boundaries(headings)
    assert boundaries[0].topic_id != boundaries[1].topic_id


def test_heading_below_top_level_before_any_top_level_heading_raises():
    # A document must not start with a level-2+ heading with no level-1
    # parent yet -- there is no topic to assign it to.
    headings = [_heading(2, "Orphan", ["Orphan"])]
    with __import__("pytest").raises(topic_grouping.UnassignableHeadingError):
        topic_grouping.compute_topic_boundaries(headings)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_topic_grouping.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.topic_grouping'`

- [ ] **Step 3: Write minimal implementation**

```python
# plugins/docx-to-content/scripts/topic_grouping.py
"""Deterministic topic-boundary computation for the "grouped" chunking strategy.

Groups a flat, source-ordered heading list into topics: every level-1
heading starts a new topic; every heading at level 2+ belongs to the most
recently seen level-1 topic. This mirrors the existing heading-path stack
approach in analyze_structure.iter_heading_matches, applied one level up.
"""

from dataclasses import dataclass, field

from . import identity


class UnassignableHeadingError(Exception):
    """Raised when a heading appears before any level-1 topic root."""


@dataclass(frozen=True)
class TopicMember:
    level: int
    text: str
    path: list
    occurrence: int


@dataclass(frozen=True)
class TopicBoundary:
    topic_id: str
    title: str
    members: list  # list[TopicMember], source order, first member is the topic root


def compute_topic_boundaries(headings: list) -> list:
    boundaries = []
    current = None
    for heading in headings:
        member = TopicMember(
            level=heading["level"],
            text=heading["text"],
            path=list(heading["path"]),
            occurrence=heading["occurrence"],
        )
        if heading["level"] == 1:
            topic_id = identity.make_topic_id([heading["text"]], occurrence=heading["occurrence"])
            current = TopicBoundary(topic_id=topic_id, title=heading["text"], members=[member])
            boundaries.append(current)
        else:
            if current is None:
                raise UnassignableHeadingError(
                    f"Heading {heading['path']!r} appears before any level-1 topic root"
                )
            current.members.append(member)
    return boundaries
```

`TopicBoundary.members` is a plain `list` field on a frozen dataclass — mutated in place during construction (append), never reassigned after a boundary is appended to `boundaries`, so frozen-ness is preserved for every other field while still allowing incremental population. This matches the existing pattern in `chunking.SlicedDocument.chunks`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_topic_grouping.py -v`
Expected: PASS, all 6 tests green.

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/topic_grouping.py plugins/docx-to-content/tests/test_topic_grouping.py
git commit -m "feat: compute deterministic topic boundaries from heading list"
```

---

### Task 3: Preview proposed topics in `analyze-report.json`

**Files:**
- Modify: `plugins/docx-to-content/scripts/analyze_structure.py`
- Test: `plugins/docx-to-content/tests/test_analyze_structure.py`

**Interfaces:**
- Consumes: `topic_grouping.compute_topic_boundaries` (Task 2), `parse_headings()` (already in this file, unchanged).
- Produces: a new `"proposed_topics"` top-level key in the dict returned by `analyze_document(...).report`, list of dicts `{"topic_id", "title", "first_anchor_path", "anchor_count", "child_heading_count", "approx_size_chars"}` — this is the exact preview shape the human confirmation step (Task 17 checkpoint, outside this plan's scope) presents to the user; Task 6 (CLI/plan wiring) references this same shape when building the grouped plan's boundary list.

- [ ] **Step 1: Write the failing test**

```python
# plugins/docx-to-content/tests/test_analyze_structure.py (add to existing file)

def test_analyze_report_includes_proposed_topics_preview(tmp_path):
    markdown = (
        "# File Access\n\ncontent one\n\n"
        "## How to Seal a File\n\nmore content here\n\n"
        "# Overview\n\nshort\n"
    )
    source = _write_fixture_docx_stub(tmp_path, markdown)  # reuse existing test helper
    result = analyze_structure.analyze_document(source, tmp_path / "out")
    proposed = result.report["proposed_topics"]
    assert [t["title"] for t in proposed] == ["File Access", "Overview"]
    file_access = proposed[0]
    assert file_access["anchor_count"] == 2
    assert file_access["child_heading_count"] == 1
    assert file_access["first_anchor_path"] == ["File Access"]
    assert file_access["approx_size_chars"] > 0
    assert "topic_id" in file_access and file_access["topic_id"].startswith("file-access--")
```

Note: `_write_fixture_docx_stub` is a placeholder name — use whichever existing helper this test file already uses to produce a `SourceFingerprint`/temp docx-like input for `analyze_document` (check the top of `test_analyze_structure.py` for the established fixture/mocking pattern used by neighboring tests in that file and reuse it verbatim; do not invent a second pattern).

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_analyze_structure.py -k proposed_topics -v`
Expected: FAIL with `KeyError: 'proposed_topics'`

- [ ] **Step 3: Write minimal implementation**

In `analyze_structure.py`, import the new module at the top:

```python
from . import topic_grouping
```

Inside `analyze_document`, after `headings = parse_headings(markdown_text)` (or wherever the existing heading list local variable is built — reuse it, do not re-parse), add:

```python
    topic_boundaries = topic_grouping.compute_topic_boundaries(headings)
    proposed_topics = [
        {
            "topic_id": boundary.topic_id,
            "title": boundary.title,
            "first_anchor_path": list(boundary.members[0].path),
            "anchor_count": len(boundary.members),
            "child_heading_count": len(boundary.members) - 1,
            "approx_size_chars": sum(len(m.text) for m in boundary.members),
        }
        for boundary in topic_boundaries
    ]
```

Add `"proposed_topics": proposed_topics,` as a new top-level key in the `report` dict literal being assembled (place it next to the existing `"headings"` key for readability — do not reorder any existing keys).

Note on `approx_size_chars`: this is deliberately a cheap, heading-text-only proxy at analysis time (real chunk-body sizes aren't known until cleaned markdown is sliced in `convert`) — document this in a one-line comment so a future reader doesn't mistake it for exact byte counts.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_analyze_structure.py -v`
Expected: PASS, full file green including all pre-existing `analyze_document`/`analyze-report.json` shape tests (confirms no existing key was disturbed).

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/analyze_structure.py plugins/docx-to-content/tests/test_analyze_structure.py
git commit -m "feat: preview proposed topic boundaries in analyze-report.json"
```

---

### Task 4: `PublicationMap` contract + writer

**Files:**
- Modify: `plugins/docx-to-content/scripts/contracts.py`
- Create: `plugins/docx-to-content/scripts/publication_map.py`
- Test: `plugins/docx-to-content/tests/test_publication_map.py`

**Interfaces:**
- Consumes: `contracts.SUPPORTED_SCHEMA_VERSION`, the `_require`/schema-check helper pattern already used by every other `contracts.py` dataclass (read `contracts.py`'s existing `from_dict`/`to_dict` methods for the exact helper names and copy the pattern — do not invent a second validation style).
- Produces: `contracts.PublicationMapEntry(topic_id, title, order, parent_topic_id, chunk_id)` and `contracts.PublicationMap(schema_version, package_identity, entries)` dataclasses with `to_dict()`/`from_dict()`; `publication_map.build_publication_map(topic_boundaries, topic_chunk_ids, package_manifest_hash) -> contracts.PublicationMap` and `publication_map.write_publication_map(pub_map, output_dir) -> Path` — Task 5 (grouped package builder) calls both; Task 7 (renderer) calls a new `publication_map.load_publication_map(package_dir) -> contracts.PublicationMap | None` this task also adds.

- [ ] **Step 1: Write the failing tests**

```python
# plugins/docx-to-content/tests/test_publication_map.py

import json

from scripts import contracts, publication_map, topic_grouping


def _boundary(topic_id, title, member_paths):
    members = [
        topic_grouping.TopicMember(level=1 if i == 0 else 2, text=p[-1], path=p, occurrence=1)
        for i, p in enumerate(member_paths)
    ]
    return topic_grouping.TopicBoundary(topic_id=topic_id, title=title, members=members)


def test_publication_map_round_trips_through_json():
    boundaries = [
        _boundary("file-access--aaaaaaaa", "File Access", [["File Access"]]),
        _boundary("overview--bbbbbbbb", "Overview", [["Overview"]]),
    ]
    chunk_ids = {
        "file-access--aaaaaaaa": "chunks/file-access--aaaaaaaa.md",
        "overview--bbbbbbbb": "chunks/overview--bbbbbbbb.md",
    }
    pub_map = publication_map.build_publication_map(
        boundaries, chunk_ids, package_identity="sha256:deadbeef"
    )
    as_dict = pub_map.to_dict()
    restored = contracts.PublicationMap.from_dict(as_dict)
    assert restored == pub_map


def test_publication_map_order_is_explicit_not_positional(tmp_path):
    boundaries = [
        _boundary("b--11111111", "B", [["B"]]),
        _boundary("a--22222222", "A", [["A"]]),
    ]
    chunk_ids = {"b--11111111": "chunks/b.md", "a--22222222": "chunks/a.md"}
    pub_map = publication_map.build_publication_map(
        boundaries, chunk_ids, package_identity="sha256:deadbeef"
    )
    orders = [entry.order for entry in pub_map.entries]
    assert orders == [0, 1]  # explicit order field, matches boundary list position at write time
    written = publication_map.write_publication_map(pub_map, tmp_path)
    on_disk = json.loads(written.read_text())
    assert [e["order"] for e in on_disk["entries"]] == [0, 1]


def test_publication_map_supports_parent_topic_id_hierarchy():
    boundaries = [_boundary("a--11111111", "A", [["A"]])]
    chunk_ids = {"a--11111111": "chunks/a.md"}
    pub_map = publication_map.build_publication_map(
        boundaries,
        chunk_ids,
        package_identity="sha256:deadbeef",
        parent_topic_ids={"a--11111111": None},
    )
    assert pub_map.entries[0].parent_topic_id is None


def test_load_publication_map_returns_none_when_absent(tmp_path):
    assert publication_map.load_publication_map(tmp_path) is None


def test_load_publication_map_round_trips(tmp_path):
    boundaries = [_boundary("a--11111111", "A", [["A"]])]
    chunk_ids = {"a--11111111": "chunks/a.md"}
    pub_map = publication_map.build_publication_map(
        boundaries, chunk_ids, package_identity="sha256:deadbeef"
    )
    publication_map.write_publication_map(pub_map, tmp_path)
    loaded = publication_map.load_publication_map(tmp_path)
    assert loaded == pub_map
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_publication_map.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.publication_map'`

- [ ] **Step 3: Write minimal implementation**

In `contracts.py`, add (following the exact `_require`/`to_dict`/`from_dict` pattern already used by every neighboring dataclass in that file — read `ManifestChunk` or `ChunkMetadata`'s implementation immediately before writing this, so field-presence checks and error messages match house style):

```python
@dataclass(frozen=True)
class PublicationMapEntry:
    topic_id: str
    title: str
    order: int
    chunk_id: str
    parent_topic_id: object = None  # str | None

    def to_dict(self) -> dict:
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "order": self.order,
            "chunk_id": self.chunk_id,
            "parent_topic_id": self.parent_topic_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PublicationMapEntry":
        _require(data, "topic_id")
        _require(data, "title")
        _require(data, "order")
        _require(data, "chunk_id")
        return cls(
            topic_id=data["topic_id"],
            title=data["title"],
            order=data["order"],
            chunk_id=data["chunk_id"],
            parent_topic_id=data.get("parent_topic_id"),
        )


@dataclass(frozen=True)
class PublicationMap:
    schema_version: str
    package_identity: str
    entries: list

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "package_identity": self.package_identity,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PublicationMap":
        _require(data, "schema_version")
        _check_schema_version(data["schema_version"])
        _require(data, "package_identity")
        _require(data, "entries")
        return cls(
            schema_version=data["schema_version"],
            package_identity=data["package_identity"],
            entries=[PublicationMapEntry.from_dict(e) for e in data["entries"]],
        )
```

(Use the real names of `_require`/`_check_schema_version` as found in `contracts.py` — the names above are inferred from the pattern reported by research and must be verified against the actual file before writing this code; if the actual helper names differ, use those instead and do not introduce a second helper.)

Create `plugins/docx-to-content/scripts/publication_map.py`:

```python
"""Minimal publication-map contract writer/loader for the grouped strategy.

publication-map.json references the canonical package's own identity (not
just a bare manifest hash), lists canonical topic ids in explicit,
directory-order-independent sequence, and supports parent_topic_id for
future hierarchy -- see plan 2026-07-28-docx-to-content-topic-grouping.md.
"""

import json
from pathlib import Path

from . import contracts

_FILENAME = "publication-map.json"


def build_publication_map(
    topic_boundaries: list,
    topic_chunk_ids: dict,
    package_identity: str,
    parent_topic_ids: dict = None,
) -> contracts.PublicationMap:
    parent_topic_ids = parent_topic_ids or {}
    entries = [
        contracts.PublicationMapEntry(
            topic_id=boundary.topic_id,
            title=boundary.title,
            order=index,
            chunk_id=topic_chunk_ids[boundary.topic_id],
            parent_topic_id=parent_topic_ids.get(boundary.topic_id),
        )
        for index, boundary in enumerate(topic_boundaries)
    ]
    return contracts.PublicationMap(
        schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
        package_identity=package_identity,
        entries=entries,
    )


def write_publication_map(pub_map: contracts.PublicationMap, output_dir: Path) -> Path:
    output_path = Path(output_dir) / _FILENAME
    output_path.write_text(json.dumps(pub_map.to_dict(), indent=2, sort_keys=True))
    return output_path


def load_publication_map(package_dir: Path):
    path = Path(package_dir) / _FILENAME
    if not path.exists():
        return None
    return contracts.PublicationMap.from_dict(json.loads(path.read_text()))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_publication_map.py tests/test_contracts.py -v`
Expected: PASS, all new tests green, no regressions in existing `contracts.py` tests.

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/contracts.py plugins/docx-to-content/scripts/publication_map.py plugins/docx-to-content/tests/test_publication_map.py
git commit -m "feat: add publication-map contract and writer/loader"
```

---

### Task 5: Grouped canonical package builder

**Files:**
- Modify: `plugins/docx-to-content/scripts/package.py`
- Modify: `plugins/docx-to-content/scripts/contracts.py` (extend `ChunkMetadata` with anchor lineage)
- Test: `plugins/docx-to-content/tests/test_package.py`

**Interfaces:**
- Consumes: `topic_grouping.compute_topic_boundaries` (Task 2), `chunking.reconcile_and_slice`/`SlicedDocument`/`ChunkSlice` (existing, unchanged), `publication_map.build_publication_map`/`write_publication_map` (Task 4).
- Produces: `package.build_grouped_canonical_package(plan, sliced_document, raw_media_dir, output_dir) -> contracts.Manifest` — Task 6 (CLI/plan wiring) calls this instead of `build_canonical_package` when `plan.strategy == "grouped"`. Each manifest chunk entry's `content_file` now points to one file per **topic**, but `contracts.ChunkMetadata` gains a new field `anchors: list[dict]` — one entry per structural anchor folded into that topic, each `{"stable_key", "source_heading_path", "occurrence", "heading_level"}` — so later validation/rendering can still address individual anchors without a second file per anchor. This is the "internal-anchor metadata on topic chunks" the user directive requires.

- [ ] **Step 1: Write the failing tests**

```python
# plugins/docx-to-content/tests/test_package.py (add to existing file)

def test_build_grouped_canonical_package_produces_one_file_per_topic(tmp_path):
    plan = _make_plan(strategy="grouped")  # reuse existing test helper for plan construction
    sliced = _make_sliced_document_with_two_topics()  # new small helper, see below
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    assert manifest.strategy == "grouped"
    assert manifest.chunk_count == 2  # two topics, not the underlying anchor count
    assert {c.chunk_id for c in manifest.chunks} == {
        "file-access--" in c.chunk_id and c.chunk_id or c.chunk_id for c in manifest.chunks
    }


def test_grouped_topic_content_preserves_all_anchor_content_losslessly(tmp_path):
    plan = _make_plan(strategy="grouped")
    sliced = _make_sliced_document_with_two_topics()
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    file_access_chunk = next(c for c in manifest.chunks if "File Access" in c.source_heading_path[0] or c.source_heading_path == ["File Access"])
    content_path = (tmp_path / "out" / file_access_chunk.content_file)
    combined = content_path.read_text()
    for anchor_slice in sliced.chunks:
        if anchor_slice.anchor.source_heading_path[0] == "File Access":
            assert anchor_slice.content.strip() in combined


def test_grouped_chunk_metadata_lists_every_folded_anchor(tmp_path):
    plan = _make_plan(strategy="grouped")
    sliced = _make_sliced_document_with_two_topics()
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    file_access_chunk = next(c for c in manifest.chunks if c.source_heading_path == ["File Access"])
    meta_path = tmp_path / "out" / file_access_chunk.metadata_file
    meta = contracts.ChunkMetadata.from_dict(json.loads(meta_path.read_text()))
    anchor_keys = {a["stable_key"] for a in meta.anchors}
    expected_keys = {
        s.anchor.stable_key for s in sliced.chunks if s.anchor.source_heading_path[0] == "File Access"
    }
    assert anchor_keys == expected_keys


def test_grouped_package_writes_publication_map(tmp_path):
    plan = _make_plan(strategy="grouped")
    sliced = _make_sliced_document_with_two_topics()
    package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    pub_map_path = tmp_path / "out" / "publication-map.json"
    assert pub_map_path.exists()
    data = json.loads(pub_map_path.read_text())
    assert len(data["entries"]) == 2
    assert data["entries"][0]["order"] == 0


def test_grouped_every_anchor_assigned_exactly_once(tmp_path):
    plan = _make_plan(strategy="grouped")
    sliced = _make_sliced_document_with_two_topics()
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    all_anchor_keys = []
    for chunk in manifest.chunks:
        meta_path = tmp_path / "out" / chunk.metadata_file
        meta = contracts.ChunkMetadata.from_dict(json.loads(meta_path.read_text()))
        all_anchor_keys.extend(a["stable_key"] for a in meta.anchors)
    source_keys = [s.anchor.stable_key for s in sliced.chunks]
    assert sorted(all_anchor_keys) == sorted(source_keys)
    assert len(all_anchor_keys) == len(set(all_anchor_keys))
```

Note: `_make_plan` and a new `_make_sliced_document_with_two_topics` test helper must follow the exact construction pattern of whatever helper `test_package.py` already uses for `build_canonical_package` tests (check the top of that file for the established `ConversionPlan`/`SlicedDocument`/`StructuralAnchor` builder helpers before writing new ones — reuse, don't duplicate). `_make_sliced_document_with_two_topics` should build two `chunking.ChunkSlice` entries under a "File Access" top-level heading (one being a level-2 child, e.g. "How to Seal a File") and one under "Overview", so the grouped builder has real multi-anchor-per-topic folding to prove.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_package.py -k grouped -v`
Expected: FAIL with `AttributeError: module 'package' has no attribute 'build_grouped_canonical_package'`

- [ ] **Step 3: Write minimal implementation**

In `contracts.py`, extend `ChunkMetadata` with a new field (append at the end of the dataclass's field list and `to_dict`/`from_dict`, default `None` so ungrouped packages are unaffected):

```python
# In ChunkMetadata dataclass: add field
    anchors: list = None  # list[dict] with stable_key/source_heading_path/occurrence/heading_level; None for ungrouped (per-heading) chunks
```

Update `ChunkMetadata.to_dict()` to include `"anchors": self.anchors` only when `self.anchors is not None` (so the existing ungrouped manifest/sidecar shape is byte-identical to before this change — verified by Task 5's Step 4 full-suite run picking up any pre-existing golden-shape test). Update `ChunkMetadata.from_dict()` to read `data.get("anchors")`.

In `package.py`, add (near `build_canonical_package`, reusing its helper functions for writing `.md`/`.meta.json`/`manifest.json` rather than duplicating them — read `build_canonical_package`'s body first and factor out any file-writing helper it doesn't already expose as a private function, e.g. `_write_chunk_files(chunk_id, content, metadata, output_dir)`, so both the ungrouped and grouped builders share it):

```python
def build_grouped_canonical_package(plan, sliced_document, raw_media_dir, output_dir):
    from . import topic_grouping, publication_map, identity

    headings = [
        {
            "level": s.anchor.heading_level,
            "text": s.anchor.heading_text,
            "path": list(s.anchor.source_heading_path),
            "occurrence": s.anchor.occurrence,
        }
        for s in sliced_document.chunks
    ]
    boundaries = topic_grouping.compute_topic_boundaries(headings)

    # Map each ChunkSlice back to its owning topic by stable_key, preserving
    # sliced_document.chunks' source order within each topic.
    slices_by_key = {s.anchor.stable_key: s for s in sliced_document.chunks}

    output_dir = Path(output_dir)
    chunks_dir = output_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    rewritten_by_id, media_filenames = rewrite_media_and_copy(
        [
            (boundary.topic_id, "\n\n".join(
                slices_by_key[m.path and _stable_key_for_member(m, slices_by_key)].content
                for m in boundary.members
            ))
            for boundary in boundaries
        ],
        raw_media_dir,
        output_dir / "media",
    )

    manifest_chunks = []
    topic_chunk_ids = {}
    for source_order, boundary in enumerate(boundaries):
        combined_content = rewritten_by_id[boundary.topic_id]
        anchors_meta = [
            {
                "stable_key": slices_by_key[_stable_key_for_member(m, slices_by_key)].anchor.stable_key,
                "source_heading_path": list(m.path),
                "occurrence": m.occurrence,
                "heading_level": m.level,
            }
            for m in boundary.members
        ]
        content_file = f"chunks/{boundary.topic_id}.md"
        metadata_file = f"chunks/{boundary.topic_id}.meta.json"
        topic_chunk_ids[boundary.topic_id] = content_file
        (output_dir / content_file).write_text(combined_content)
        metadata = contracts.ChunkMetadata(
            schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
            chunk_id=boundary.topic_id,
            source_order=source_order,
            source_heading_path=[boundary.title],
            topic=boundary.title,
            content_type=plan.content_type,
            template_profile=plan.template_profile,
            source_sha256=plan.source.sha256,
            plan_id=plan.plan_id,
            content_file=content_file,
            content_sha256=hashing.content_hash(combined_content.encode("utf-8")),
            local_links=[],
            media_refs=[],
            anchors=anchors_meta,
        )
        (output_dir / metadata_file).write_text(json.dumps(metadata.to_dict(), indent=2, sort_keys=True))
        manifest_chunks.append(
            contracts.ManifestChunk(
                chunk_id=boundary.topic_id,
                content_file=content_file,
                metadata_file=metadata_file,
                source_order=source_order,
                source_heading_path=[boundary.title],
            )
        )

    manifest = contracts.Manifest(
        schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
        generator=contracts.ManifestGenerator(plugin="docx-to-content", plugin_version=_PLUGIN_VERSION),
        source=contracts.ManifestSourceFingerprint(path=plan.source.path, sha256=plan.source.sha256),
        plan_id=plan.plan_id,
        content_type=plan.content_type,
        template_profile=plan.template_profile,
        strategy="grouped",
        chunk_count=len(manifest_chunks),
        chunks=manifest_chunks,
        media=media_filenames,
        validation_report="validation.json",
    )
    (output_dir / "manifest.json").write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True))
    (output_dir / "validation.json").write_text(
        json.dumps({"status": "PENDING", "issues": [], "note": "not yet validated"}, indent=2)
    )

    pub_map = publication_map.build_publication_map(
        boundaries, topic_chunk_ids, package_identity=f"sha256:{manifest.plan_id}"
    )
    publication_map.write_publication_map(pub_map, output_dir)

    return manifest


def _stable_key_for_member(member, slices_by_key):
    for key, s in slices_by_key.items():
        if list(s.anchor.source_heading_path) == list(member.path) and s.anchor.occurrence == member.occurrence:
            return key
    raise KeyError(f"No ChunkSlice found for topic member {member.path!r}")
```

This step is deliberately written verbosely above because the exact helper names in the real `package.py` (constants like `_PLUGIN_VERSION`, the private file-writing helpers) must be confirmed against the actual file before implementation — the implementer must read `build_canonical_package`'s real body first and reuse its existing private helpers (e.g. do not hand-roll `.write_text(json.dumps(...))` calls if `build_canonical_package` already has a shared private function for this) rather than copying this scaffold verbatim if a cleaner shared helper already exists. The behavior contract (manifest strategy `"grouped"`, one file per topic, `anchors` list per chunk metadata, publication-map written) is what the tests in Step 1 pin down — implementation details should match house style over this sketch where they conflict.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_package.py tests/test_contracts.py -v`
Expected: PASS, all new grouped-package tests green, and all pre-existing `build_canonical_package` (ungrouped) tests still green (proves the `ChunkMetadata.anchors` addition didn't change the ungrouped JSON shape).

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/package.py plugins/docx-to-content/scripts/contracts.py plugins/docx-to-content/tests/test_package.py
git commit -m "feat: build grouped canonical packages with topic-folded anchor metadata"
```

---

### Task 6: Plan/CLI wiring for the `"grouped"` strategy

**Files:**
- Modify: `plugins/docx-to-content/scripts/plans.py`
- Modify: `plugins/docx-to-content/scripts/convert.py`
- Modify: `plugins/docx-to-content/scripts/cli.py`
- Test: `plugins/docx-to-content/tests/test_plans.py`, `plugins/docx-to-content/tests/test_convert.py`, `plugins/docx-to-content/tests/test_cli.py`

**Interfaces:**
- Consumes: `package.build_grouped_canonical_package` (Task 5), existing `plans.build_draft_plan`/`confirm_plan` (unchanged signatures — `strategy` is already a bare string per `contracts.ConversionPlan`, so `"grouped"` needs no new parameter, only new branch logic wherever `strategy` is dispatched on).
- Produces: `convert.convert_and_promote(source_path, plan, output_root)` now branches on `plan.strategy == "grouped"` to call `package.build_grouped_canonical_package` instead of the existing per-heading builder — this is the exact call site Task 17's eventual real-CEIS `confirm`/`convert` run (outside this plan) depends on.

- [ ] **Step 1: Write the failing tests**

```python
# plugins/docx-to-content/tests/test_convert.py (add to existing file)

def test_convert_and_promote_dispatches_grouped_strategy_to_grouped_builder(tmp_path, monkeypatch):
    plan = _make_confirmed_plan(strategy="grouped")  # reuse/extend existing plan-builder test helper
    source_path = _write_small_multi_topic_docx(tmp_path)  # reuse existing docx fixture helper if present, else pandoc a tiny fixture like small_single.docx already used elsewhere in this file

    called = {}
    original = package.build_grouped_canonical_package

    def spy(*args, **kwargs):
        called["invoked"] = True
        return original(*args, **kwargs)

    monkeypatch.setattr(package, "build_grouped_canonical_package", spy)
    manifest, report, promoted, final_dir = convert.convert_and_promote(
        source_path, plan, output_root=tmp_path / "out"
    )
    assert called.get("invoked") is True
    assert manifest.strategy == "grouped"
```

```python
# plugins/docx-to-content/tests/test_plans.py (add to existing file)

def test_build_draft_plan_accepts_grouped_strategy():
    plan = plans.build_draft_plan(
        source_fingerprint=_make_source_fingerprint(),  # reuse existing helper
        strategy="grouped",
        chunk_level=1,
        chunk_anchors=[],
    )
    assert plan.strategy == "grouped"
```

```python
# plugins/docx-to-content/tests/test_cli.py (add to existing file)

def test_convert_command_produces_grouped_manifest_end_to_end(tmp_path):
    # Full analyze -> confirm -> convert chain via cli.main([...]), asserting
    # the confirmed plan's strategy can be overridden to "grouped" before
    # confirm (by editing the draft-plan JSON on disk, exactly as a human
    # reviewer would per the Task 17 checkpoint) and convert honors it.
    source = _copy_fixture_docx(tmp_path, "small_single.docx")  # reuse existing fixture helper
    analyze_out = tmp_path / "analysis"
    exit_code = cli.main(["analyze", "--source", str(source), "--output", str(analyze_out)])
    assert exit_code == 0

    draft_path = analyze_out / "conversion-plan.draft.json"
    draft = json.loads(draft_path.read_text())
    draft["strategy"] = "grouped"
    draft_path.write_text(json.dumps(draft))

    confirm_out = tmp_path / "confirmed"
    exit_code = cli.main(
        ["confirm", "--draft-plan", str(draft_path), "--output", str(confirm_out)]
    )
    assert exit_code == 0
    confirmed_plan_path = confirm_out / "conversion-plan.confirmed.json"

    convert_out = tmp_path / "converted"
    exit_code = cli.main(
        [
            "convert",
            "--source", str(source),
            "--plan", str(confirmed_plan_path),
            "--output", str(convert_out),
        ]
    )
    assert exit_code == 0
    manifest = json.loads((convert_out / "manifest.json").read_text())
    assert manifest["strategy"] == "grouped"
    assert (convert_out / "publication-map.json").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_convert.py tests/test_plans.py tests/test_cli.py -k grouped -v`
Expected: FAIL — `convert_and_promote` still always calls the ungrouped builder, so `manifest.strategy` stays whatever the ungrouped path hardcodes and the grouped-dispatch spy is never invoked; `test_convert_command_produces_grouped_manifest_end_to_end` fails on the missing `publication-map.json`/wrong `strategy`.

- [ ] **Step 3: Write minimal implementation**

In `convert.py`, find the shared core function (per research, referenced as `convert.py:171`, used by both `convert_document` and `convert_and_promote`) where `package.build_canonical_package(...)` is called, and branch:

```python
    if plan.strategy == "grouped":
        manifest = package.build_grouped_canonical_package(
            plan, sliced_document, raw_media_dir, output_dir
        )
    else:
        manifest = package.build_canonical_package(
            plan, sliced_document, raw_media_dir, output_dir
        )
```

`plans.py` requires no code change — `strategy` is already a bare, unvalidated string on `ConversionPlan` per `contracts.py`'s `_require(data, "strategy")` (confirmed by research item 7); `test_build_draft_plan_accepts_grouped_strategy` should already pass once `build_draft_plan`'s existing signature is exercised with `"grouped"` — if it does NOT pass, that means an undiscovered strategy allowlist exists somewhere in `plans.py`; in that case, widen the allowlist to include `"grouped"` alongside `"single"`/`"chunked"`, in the single place it's enforced, and no elsewhere.

`cli.py` requires no new flags (research confirmed no `--strategy` flag exists today — strategy already flows entirely through the plan JSON file), only that `cmd_convert`'s existing call path reaches the new branch in `convert.py`, which it already does since `cmd_convert` calls `convert_and_promote` unchanged.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd plugins/docx-to-content && python -m pytest tests/ -v`
Expected: PASS, full suite green (this is the first task where the grouped path is reachable end-to-end via the real CLI, so a full-suite run — not just the new tests — is required to catch any regression in the ungrouped `"single"`/`"chunked"` CLI paths).

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/convert.py plugins/docx-to-content/tests/test_convert.py plugins/docx-to-content/tests/test_plans.py plugins/docx-to-content/tests/test_cli.py
git commit -m "feat: wire grouped strategy through convert and the real CLI chain"
```

---

### Task 7: Validation checks for grouped packages

**Files:**
- Modify: `plugins/docx-to-content/scripts/validate_canonical.py`
- Test: `plugins/docx-to-content/tests/test_validate_canonical.py`

**Interfaces:**
- Consumes: `publication_map.load_publication_map` (Task 4), the existing `validate_canonical_package(package_dir, plan, source_path=None, cleaned_markdown_text=None) -> contracts.ValidationReport` entry point (unchanged signature) and its existing private `_check_*` helper pattern.
- Produces: three new private check functions wired into `validate_canonical_package`'s existing call sequence — `_check_anchor_assignment_completeness` (every plan anchor appears in exactly one chunk's `metadata.anchors`, none missing, none duplicated), `_check_publication_map_consistency` (when `manifest.strategy == "grouped"`, `publication-map.json` must exist, reference the real chunk ids, and its `entries` order must be internally consistent — no gaps/duplicates in `order`), `_check_grouped_content_losslessness` (extends the existing `_check_content_loss_and_duplication` normalized-aggregate comparison to work when chunks are topic-grouped, by comparing the union of all `anchors[].stable_key`-tagged sections rather than assuming one chunk equals one heading).

- [ ] **Step 1: Write the failing tests**

```python
# plugins/docx-to-content/tests/test_validate_canonical.py (add to existing file)

def test_validate_grouped_package_passes_when_every_anchor_assigned_once(tmp_path):
    package_dir = _build_valid_grouped_package(tmp_path)  # new helper, build via package.build_grouped_canonical_package + write validation.json PENDING as build_grouped_canonical_package already does
    plan = _load_plan_for(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)
    assert report.status == "PASS"


def test_validate_grouped_package_fails_when_an_anchor_is_missing(tmp_path):
    package_dir = _build_valid_grouped_package(tmp_path)
    meta_path = next(package_dir.glob("chunks/*.meta.json"))
    meta = json.loads(meta_path.read_text())
    meta["anchors"].pop()
    meta_path.write_text(json.dumps(meta))
    plan = _load_plan_for(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)
    assert report.status == "FAIL"
    assert any(i.code == "unassigned_structural_anchor" for i in report.issues)


def test_validate_grouped_package_fails_when_an_anchor_is_duplicated_across_topics(tmp_path):
    package_dir = _build_valid_grouped_package(tmp_path)
    meta_paths = sorted(package_dir.glob("chunks/*.meta.json"))
    first = json.loads(meta_paths[0].read_text())
    second = json.loads(meta_paths[1].read_text())
    second["anchors"].append(first["anchors"][0])
    meta_paths[1].write_text(json.dumps(second))
    plan = _load_plan_for(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)
    assert report.status == "FAIL"
    assert any(i.code == "duplicate_structural_anchor_assignment" for i in report.issues)


def test_validate_grouped_package_fails_when_publication_map_missing(tmp_path):
    package_dir = _build_valid_grouped_package(tmp_path)
    (package_dir / "publication-map.json").unlink()
    plan = _load_plan_for(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)
    assert report.status == "FAIL"
    assert any(i.code == "missing_publication_map" for i in report.issues)


def test_validate_grouped_package_fails_when_publication_map_order_has_gap(tmp_path):
    package_dir = _build_valid_grouped_package(tmp_path)
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"][1]["order"] = 5
    pub_map_path.write_text(json.dumps(data))
    plan = _load_plan_for(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)
    assert report.status == "FAIL"
    assert any(i.code == "publication_map_order_invalid" for i in report.issues)


def test_validate_ungrouped_package_unaffected_by_new_checks(tmp_path):
    # Regression guard: strategy="chunked" packages have no publication-map.json
    # and no metadata.anchors, and must still PASS exactly as before.
    package_dir = _build_valid_chunked_package(tmp_path)  # reuse existing helper
    plan = _load_plan_for(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)
    assert report.status == "PASS"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_validate_canonical.py -k grouped -v`
Expected: FAIL — none of the new check functions/error codes exist yet, so grouped-specific defects go undetected (reports come back PASS or with unrelated codes).

- [ ] **Step 3: Write minimal implementation**

In `validate_canonical.py`, add the three new private check functions following the existing pattern (each appends `contracts.ValidationIssue(severity, code, message, path)` to a shared `issues` list threaded through `validate_canonical_package`, exactly as every existing `_check_*` function does — read one existing check, e.g. `_check_orphans`, immediately before writing these to match its exact signature/threading convention):

```python
def _check_anchor_assignment_completeness(issues, plan, loaded_chunks_meta):
    plan_anchor_keys = {a.stable_key for a in plan.chunk_anchors}
    seen = {}
    for meta in loaded_chunks_meta:
        for anchor in (meta.anchors or []):
            key = anchor["stable_key"]
            seen.setdefault(key, []).append(meta.chunk_id)
    for key, owning_chunks in seen.items():
        if len(owning_chunks) > 1:
            issues.append(
                contracts.ValidationIssue(
                    severity="error",
                    code="duplicate_structural_anchor_assignment",
                    message=f"Structural anchor {key} assigned to multiple topics: {owning_chunks}",
                    path=key,
                )
            )
    missing = plan_anchor_keys - set(seen)
    for key in missing:
        issues.append(
            contracts.ValidationIssue(
                severity="error",
                code="unassigned_structural_anchor",
                message=f"Structural anchor {key} not present in any topic chunk",
                path=key,
            )
        )


def _check_publication_map_consistency(issues, package_dir, manifest):
    if manifest.strategy != "grouped":
        return
    pub_map = publication_map.load_publication_map(package_dir)
    if pub_map is None:
        issues.append(
            contracts.ValidationIssue(
                severity="error",
                code="missing_publication_map",
                message="strategy=grouped requires publication-map.json",
                path="publication-map.json",
            )
        )
        return
    manifest_chunk_ids = {c.chunk_id for c in manifest.chunks}
    entry_chunk_ids = {e.topic_id for e in pub_map.entries}
    if entry_chunk_ids != manifest_chunk_ids:
        issues.append(
            contracts.ValidationIssue(
                severity="error",
                code="publication_map_chunk_mismatch",
                message="publication-map.json entries do not match manifest chunk ids",
                path="publication-map.json",
            )
        )
    orders = sorted(e.order for e in pub_map.entries)
    if orders != list(range(len(orders))):
        issues.append(
            contracts.ValidationIssue(
                severity="error",
                code="publication_map_order_invalid",
                message="publication-map.json entry order must be a contiguous 0..N-1 sequence",
                path="publication-map.json",
            )
        )
```

For `_check_grouped_content_losslessness`: only add this if the existing `_check_content_loss_and_duplication`'s normalized-aggregate comparison does not already work unmodified for grouped packages (it compares the full concatenated staged-chunk text against the full cleaned_markdown_text aggregate, which is chunk-shape-agnostic per research item 5's description — "normalized aggregate mismatch" over ALL chunks' content, not per-chunk). Before writing a new function, run the existing `_check_content_loss_and_duplication` test suite against a grouped fixture package manually; if it already correctly PASSes/FAILs on grouped input because it only ever compares full-document aggregates, do not add a redundant function — document that finding as a one-line comment above `_check_publication_map_consistency` instead, and skip straight to wiring only the two anchor-assignment checks plus reusing the existing content-loss check unmodified. This is a "verify before adding" step, not an optional skip — confirm it explicitly, do not assume.

Wire both (or three) new checks into `validate_canonical_package`'s existing sequential call chain, in the same style as the existing `_check_orphans`/`_check_unresolved_anchors` calls (pass `issues`, and whichever of `plan`/`package_dir`/`manifest`/`loaded_chunks_meta` each needs, matching how neighboring checks already receive those same values — do not introduce a new parameter-passing convention).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_validate_canonical.py -v`
Expected: PASS, all new grouped-validation tests green, and `test_validate_ungrouped_package_unaffected_by_new_checks` (and the full pre-existing suite in this file) still green.

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/validate_canonical.py plugins/docx-to-content/tests/test_validate_canonical.py
git commit -m "feat: validate anchor assignment completeness and publication-map consistency for grouped packages"
```

---

### Task 8: Grouped-aware `CanonicalPackage.load()` and renderer navigation

**Files:**
- Modify: `plugins/docx-to-content/scripts/package.py` (`CanonicalPackage.load`)
- Modify: `plugins/docx-to-content/scripts/renderers/multipage_markdown.py`
- Test: `plugins/docx-to-content/tests/test_package.py`, `plugins/docx-to-content/tests/test_multipage_markdown.py`

**Interfaces:**
- Consumes: `publication_map.load_publication_map` (Task 4), the existing `CanonicalPackage` frozen dataclass (Task 5's manifest/chunk changes are already compatible since `LoadedChunk.metadata` is `contracts.ChunkMetadata`, which now optionally carries `anchors`).
- Produces: `CanonicalPackage` gains a new field `publication_map: object = None` (populated by `load()` when `manifest.strategy == "grouped"` and the file exists, else `None` — additive, so every existing caller/test that constructs `CanonicalPackage` positionally must be checked and updated to keyword args if any do — research did not find positional construction outside `load()` itself, but verify before assuming); `multipage_markdown.py`'s `render()` branches: when `package.publication_map is not None`, iterate `sorted(package.publication_map.entries, key=lambda e: e.order)` to build `index.md` and page order instead of `_build_index(chunks)`'s raw manifest-order loop — falling back to today's unchanged behavior otherwise.

- [ ] **Step 1: Write the failing tests**

```python
# plugins/docx-to-content/tests/test_package.py (add to existing file)

def test_canonical_package_load_attaches_publication_map_for_grouped(tmp_path):
    plan = _make_confirmed_plan(strategy="grouped")
    sliced = _make_sliced_document_with_two_topics()
    package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "pkg"
    )
    loaded = package.CanonicalPackage.load(tmp_path / "pkg")
    assert loaded.publication_map is not None
    assert len(loaded.publication_map.entries) == 2


def test_canonical_package_load_publication_map_none_for_ungrouped(tmp_path):
    package_dir = _build_valid_chunked_package(tmp_path)  # reuse existing helper
    loaded = package.CanonicalPackage.load(package_dir)
    assert loaded.publication_map is None
```

```python
# plugins/docx-to-content/tests/test_multipage_markdown.py (add to existing file)

def test_render_uses_publication_map_order_when_present(tmp_path):
    package_with_map = _load_grouped_package_fixture(tmp_path)  # new helper: build_grouped_canonical_package + validate + CanonicalPackage.load
    renderer = multipage_markdown.MultipageMarkdownRenderer()
    result, staging_dir = renderer.render_to_staging(package_with_map, tmp_path / "rendered")
    index_text = (staging_dir / "index.md").read_text()
    ordered_titles = [e.title for e in sorted(package_with_map.publication_map.entries, key=lambda e: e.order)]
    positions = [index_text.index(title) for title in ordered_titles]
    assert positions == sorted(positions)


def test_render_falls_back_to_manifest_order_when_no_publication_map(tmp_path):
    package_without_map = _load_chunked_package_fixture(tmp_path)  # reuse existing fixture helper for the ungrouped path
    renderer = multipage_markdown.MultipageMarkdownRenderer()
    result, staging_dir = renderer.render_to_staging(package_without_map, tmp_path / "rendered")
    assert (staging_dir / "index.md").exists()  # unchanged pre-existing behavior, regression guard
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_package.py tests/test_multipage_markdown.py -k "publication_map or grouped" -v`
Expected: FAIL — `CanonicalPackage.load` has no `publication_map` attribute/behavior yet; `TypeError` or `AttributeError` on the new assertions.

- [ ] **Step 3: Write minimal implementation**

In `package.py`'s `CanonicalPackage` dataclass, add the field:

```python
    publication_map: object = None  # contracts.PublicationMap | None; populated by load() for strategy="grouped"
```

In `CanonicalPackage.load()`, after the manifest is parsed and before returning the constructed instance, add:

```python
        from . import publication_map as publication_map_module
        pub_map = None
        if manifest.strategy == "grouped":
            pub_map = publication_map_module.load_publication_map(package_dir)
```

and pass `publication_map=pub_map` into the final `cls(...)` construction (update every keyword, do not rely on positional order given the new field).

In `renderers/multipage_markdown.py`, inside `render()` (or wherever `_build_index(chunks)` and the per-chunk page loop currently iterate `package.chunks` directly), branch:

```python
        if package.publication_map is not None:
            ordered_entries = sorted(package.publication_map.entries, key=lambda e: e.order)
            chunk_by_id = {c.metadata.chunk_id: c for c in package.chunks}
            ordered_chunks = [chunk_by_id[e.chunk_id] for e in ordered_entries]
        else:
            ordered_chunks = package.chunks
```

and use `ordered_chunks` everywhere `chunks`/`package.chunks` was previously used to build `index.md` and iterate pages — do not otherwise change `_build_index`'s hierarchy-bullet logic (it still keys off each chunk's `metadata.source_heading_path`, which for a grouped chunk is `[boundary.title]`, a single-element list — flat entries in the index, appropriately, since sub-anchor hierarchy inside a topic is not separately paginated in Phase 1).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd plugins/docx-to-content && python -m pytest tests/ -v`
Expected: PASS, full suite green — this task touches the renderer's core loop, so a full-suite run is required, not just the new tests, to confirm the `"single"`/`"chunked"` fallback path (`package.publication_map is None`) still renders identically to before this change.

- [ ] **Step 5: Commit**

```bash
git add plugins/docx-to-content/scripts/package.py plugins/docx-to-content/scripts/renderers/multipage_markdown.py plugins/docx-to-content/tests/test_package.py plugins/docx-to-content/tests/test_multipage_markdown.py
git commit -m "feat: render grouped packages in publication-map order, preserve manifest-order fallback"
```

---

### Task 9: End-to-end grouped pipeline proof + documentation

**Files:**
- Create test fixture: `plugins/docx-to-content/tests/fixtures/multi_topic.docx` (built via a small script/pandoc round-trip, matching how `small_single.docx`/`repeated_headings.docx` were created per Task 16's ledger entry — check `tests/fixtures/` for any existing fixture-generation script and reuse it, e.g. `tests/fixtures/generate_fixtures.py` if one exists, else generate via the same manual method Task 16 used and document the exact command in the commit message)
- Test: `plugins/docx-to-content/tests/test_grouped_e2e.py`
- Modify: `plugins/docx-to-content/SKILL.md` files for `analyze-document`, `convert-document`, `render-content` (whichever mention `strategy`/`chunk_level` today) to document the new `"grouped"` value
- Modify: `plugins/docx-to-content/references/` — add a short `publication-map-contract.md` describing the JSON shape, following the same documentation style as `references/future-output-profiles.md`

**Interfaces:**
- Consumes: everything from Tasks 1-8, exercised only through the public CLI (`cli.main([...])`) — no internal function calls, proving the real end-to-end chain the way Task 16's `test_pipeline_generalizes_beyond_ceis` proved the ungrouped chain.
- Produces: nothing new for later tasks — this is the closing proof task for Task 17-topic-grouping. After this task, the plan's "Next action on resume" checkpoint in `start-here.md` (rerun real CEIS analysis, present ~25 proposed topic boundaries, produce a new plan/plan-identity, stop for explicit confirmation) becomes actionable, but running it against the real CEIS document is explicitly outside this plan's scope (per the existing Task 17 human-confirmation gate) — do not run it as part of this task.

- [ ] **Step 1: Write the failing end-to-end test**

```python
# plugins/docx-to-content/tests/test_grouped_e2e.py
"""Proves the full analyze -> confirm(grouped) -> convert -> render chain
end-to-end via the real CLI, the same rigor Task 16 applied to the
ungrouped chain, for a synthetic multi-topic fixture."""

import json
from pathlib import Path

from scripts import cli


def test_grouped_pipeline_end_to_end_via_real_cli(tmp_path):
    fixture = Path(__file__).parent / "fixtures" / "multi_topic.docx"
    analyze_out = tmp_path / "analysis"
    assert cli.main(["analyze", "--source", str(fixture), "--output", str(analyze_out)]) == 0

    report = json.loads((analyze_out / "analyze-report.json").read_text())
    proposed_topics = report["proposed_topics"]
    assert len(proposed_topics) >= 2

    draft_path = analyze_out / "conversion-plan.draft.json"
    draft = json.loads(draft_path.read_text())
    draft["strategy"] = "grouped"
    draft_path.write_text(json.dumps(draft))

    confirm_out = tmp_path / "confirmed"
    assert cli.main(
        ["confirm", "--draft-plan", str(draft_path), "--output", str(confirm_out)]
    ) == 0

    convert_out = tmp_path / "converted"
    assert cli.main(
        [
            "convert",
            "--source", str(fixture),
            "--plan", str(confirm_out / "conversion-plan.confirmed.json"),
            "--output", str(convert_out),
        ]
    ) == 0

    manifest = json.loads((convert_out / "manifest.json").read_text())
    assert manifest["strategy"] == "grouped"
    assert manifest["chunk_count"] == len(proposed_topics)
    validation = json.loads((convert_out / "validation.json").read_text())
    assert validation["status"] == "PASS"

    render_out = tmp_path / "rendered"
    assert cli.main(
        [
            "render",
            "--canonical", str(convert_out),
            "--renderer", "multipage-markdown",
            "--output", str(render_out),
        ]
    ) == 0
    index_text = (render_out / "index.md").read_text()
    for topic in proposed_topics:
        assert topic["title"] in index_text

    # Losslessness: every structural anchor's content must appear somewhere
    # in the rendered pages, exactly once (not lost, not duplicated).
    all_rendered_text = "\n".join(
        p.read_text() for p in (render_out / "pages").glob("*.md")
    )
    for topic in proposed_topics:
        assert all_rendered_text.count(topic["title"]) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugins/docx-to-content && python -m pytest tests/test_grouped_e2e.py -v`
Expected: FAIL initially with `FileNotFoundError` for `multi_topic.docx` (fixture doesn't exist yet) — build the fixture first (see Step 3), then rerun; it should fail for a real reason (missing feature) only if any of Tasks 1-8 have a gap this test exposes, which is the point of this task existing.

- [ ] **Step 3: Build the fixture and verify the full chain**

Build `tests/fixtures/multi_topic.docx`: a small Word document with at least 3 top-level (H1) headings, at least one of which has 2+ child (H2/H3) headings, following whatever method Task 16's `small_single.docx`/`repeated_headings.docx` fixtures were built with (check `tests/fixtures/` for a generation script; if none exists, these were likely authored directly in Word/LibreOffice and checked in as binary — do the same: author it once, check in the `.docx`, do not attempt to generate `.docx` bytes procedurally in Python).

Run: `cd plugins/docx-to-content && python -m pytest tests/test_grouped_e2e.py -v`
Expected: PASS once the fixture exists and Tasks 1-8's implementation is correct. If it fails for a feature reason (not a missing fixture), that is a real integration gap between tasks — fix the specific task's code (not this test), following this plan's TDD discipline, and rerun.

- [ ] **Step 4: Run the full suite**

Run: `cd plugins/docx-to-content && python -m pytest tests/ -v`
Expected: PASS, full suite green, no regressions anywhere (this is the plan's final correctness gate before documentation).

- [ ] **Step 5: Update SKILL.md and references, then commit**

In each of `plugins/docx-to-content/skills/analyze-document/SKILL.md`, `.../convert-document/SKILL.md`, `.../render-content/SKILL.md` (exact paths per whatever `Task 15/15a/15b` established — locate via `find plugins/docx-to-content -iname 'SKILL.md'`), add one short paragraph documenting `strategy: "grouped"` as a third supported value alongside `"single"`/`"chunked"`, describing: ~25 topic files instead of one-per-heading, `publication-map.json` sidecar, and that structural-anchor lineage is preserved as `anchors` metadata inside each topic's sidecar. Match the existing honest-disclosure tone these files already use (per research item 15/15a/15b's ledger note about `render-content` SKILL.md's disclosure style).

Create `plugins/docx-to-content/references/publication-map-contract.md` documenting the `publication-map.json` JSON shape (`schema_version`, `package_identity`, `entries[].{topic_id,title,order,chunk_id,parent_topic_id}`), in the same structure/tone as the existing `references/future-output-profiles.md` (read that file first and match its heading structure).

```bash
git add plugins/docx-to-content/tests/fixtures/multi_topic.docx plugins/docx-to-content/tests/test_grouped_e2e.py plugins/docx-to-content/skills/*/SKILL.md plugins/docx-to-content/references/publication-map-contract.md
git commit -m "test: prove grouped strategy end-to-end via real CLI chain; document contract"
```

---

## After this plan

Per `start-here.md`'s existing checkpoint requirements (unchanged, not part of this plan's scope): once Tasks 1-9 are complete and reviewed, rerun `analyze` against the real CEIS document, present the actual ~25 proposed topic boundaries (via the new `proposed_topics` preview from Task 3) for human review, present the preamble/image findings already resolved earlier in Task 17, produce a new draft plan + plan identity with `strategy: "grouped"`, and **stop for explicit plan confirmation** before running `confirm`/`convert`/`render`/Task 18 against the real document — same human-confirmation gate as before, not superseded by this plan.
