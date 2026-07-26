# docx-to-content Phase 1 Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the self-contained `docx-to-content` Phase 1 plugin that converts the CEIS Manual from Word-authored source into cleaned, metadata-backed canonical content and proves the renderer contract with one navigable multi-page markdown renderer.

**Architecture:** The plugin is self-contained in `manual-conversion-poc/plugins/docx-to-content/`. Raw pandoc extraction is treated as transitory diagnostic input; canonical content is cleaned chunks plus metadata sidecars, manifest, validation records, and rendered output. Phase 1 proves extensibility by implementing the three-skill flow: `analyze-document -> convert-document -> render-content`.

**Tech Stack:** Python standard library, pytest, pandoc CLI, LibreOffice `soffice` CLI, markdown files, JSON manifests, Claude plugin skill structure.

## Global Constraints

- Phase 1 lives in `manual-conversion-poc/plugins/docx-to-content/`, not in the sibling `agent-plugins-skills` monorepo.
- Build exactly three skills: `analyze-document`, `convert-document`, and `render-content`.
- Raw pandoc markdown is transitory and must not be treated as canonical content.
- Canonical content is cleaned markdown chunks plus `.meta.json` sidecars, manifest, and validation report.
- Every content chunk must have exactly one metadata sidecar.
- Every metadata sidecar must point to exactly one content chunk.
- The Phase 1 renderer must consume the manifest, chunk files, metadata sidecars, and media assets.
- The only Phase 1 renderer is `multipage_markdown.py`.
- Do not implement SharePoint publishing, destination interviews, Word/PDF rendering, PowerPoint rendering, audio/script rendering, Copilot Studio export, quiz generation, or generalized template authoring in Phase 1.
- Existing working cleanup modules must be relocated with behavior preserved unless a failing test proves a defect.
- Runtime should remain as close to Python standard library only as practical.
- `pytest` is acceptable for tests.
- `pandoc` and `soffice` are external system dependencies.
- Use TDD for new code.
- CEIS Manual is the end-to-end regression fixture.
- Do not report success unless all required artifacts exist.

---

## File Structure Map

Create or modify the following files.

```text
plugins/docx-to-content/
  .claude-plugin/
    plugin.json
  plugin.yaml
  scripts/
    __init__.py
    models.py
    slugify.py
    analyze_structure.py
    chunk_metadata.py
    manifest.py
    validate_canonical.py
    docx_to_md.py
    md_to_docx.py
    emf_convert.py
    pandoc_validate.py
    pandoc_fixes/
      __init__.py
      attrs.py
      images.py
      toc.py
      tables.py
      footnotes.py
    renderers/
      __init__.py
      base.py
      multipage_markdown.py
      validate_rendered.py
  skills/
    analyze-document/
      SKILL.md
      tests/
        test_analyze_document_skill_contract.py
    convert-document/
      SKILL.md
      tests/
        test_convert_document_skill_contract.py
    render-content/
      SKILL.md
      tests/
        test_render_content_skill_contract.py
  tests/
    test_slugify.py
    test_models.py
    test_analyze_structure.py
    test_chunk_metadata.py
    test_manifest.py
    test_validate_canonical.py
    test_renderer_base.py
    test_multipage_markdown.py
    test_validate_rendered.py
    integration/
      test_ceis_end_to_end.py
    fixtures/
      minimal_manual.md
      minimal_manifest.json
  references/
    pandoc-docx-setup.md
    known-pandoc-gaps.md
  requirements.in
  requirements.txt
```

Responsibility boundaries:

- `models.py`: shared typed dictionaries/dataclasses for plans, chunks, metadata, manifests, and validation results.
- `slugify.py`: deterministic slug and `chunk_id` generation helpers.
- `analyze_structure.py`: analyze markdown structure and produce analysis reports plus conversion plans.
- `chunk_metadata.py`: split cleaned markdown into chunks and generate metadata sidecars.
- `manifest.py`: write and load manifest JSON; verify manifest references.
- `validate_canonical.py`: validate canonical content folder before rendering.
- `renderers/base.py`: renderer protocol and shared input loading.
- `renderers/multipage_markdown.py`: Phase 1 concrete renderer.
- `renderers/validate_rendered.py`: validate rendered markdown output.
- `pandoc_fixes/*`, `emf_convert.py`, `pandoc_validate.py`, `docx_to_md.py`, `md_to_docx.py`: relocated cleanup/conversion code with behavior preserved.
- Skill `SKILL.md` files: user-facing instructions and command contracts for each skill.

---

## Task 1: Scaffold Plugin and Metadata

**Files:**
- Create: `plugins/docx-to-content/.claude-plugin/plugin.json`
- Create: `plugins/docx-to-content/plugin.yaml`
- Create: `plugins/docx-to-content/requirements.in`
- Create: `plugins/docx-to-content/requirements.txt`
- Create: `plugins/docx-to-content/scripts/__init__.py`
- Create: `plugins/docx-to-content/scripts/renderers/__init__.py`
- Create: `plugins/docx-to-content/scripts/pandoc_fixes/__init__.py`

**Interfaces:**
- Consumes: none.
- Produces: plugin folder structure that all later tasks use.

- [ ] **Step 1: Create the plugin directories**

```bash
mkdir -p plugins/docx-to-content/.claude-plugin
mkdir -p plugins/docx-to-content/scripts/pandoc_fixes
mkdir -p plugins/docx-to-content/scripts/renderers
mkdir -p plugins/docx-to-content/skills/analyze-document/tests
mkdir -p plugins/docx-to-content/skills/convert-document/tests
mkdir -p plugins/docx-to-content/skills/render-content/tests
mkdir -p plugins/docx-to-content/tests/integration
mkdir -p plugins/docx-to-content/tests/fixtures
mkdir -p plugins/docx-to-content/references
```

- [ ] **Step 2: Create `.claude-plugin/plugin.json`**

```json
{
  "name": "docx-to-content",
  "version": "0.1.0",
  "description": "Convert Word-authored manuals into cleaned, metadata-backed canonical content and renderable markdown page sets.",
  "skills": [
    "analyze-document",
    "convert-document",
    "render-content"
  ]
}
```

- [ ] **Step 3: Create `plugin.yaml`**

```yaml
name: docx-to-content
version: 0.1.0
description: Convert Word-authored manuals into cleaned, metadata-backed canonical content and renderable markdown page sets.
skills:
  - analyze-document
  - convert-document
  - render-content
```

- [ ] **Step 4: Create dependency files**

`requirements.in`:

```text
pytest
```

`requirements.txt`:

```text
pytest
```

- [ ] **Step 5: Create package marker files**

```bash
touch plugins/docx-to-content/scripts/__init__.py
touch plugins/docx-to-content/scripts/pandoc_fixes/__init__.py
touch plugins/docx-to-content/scripts/renderers/__init__.py
```

- [ ] **Step 6: Commit scaffold**

```bash
git add plugins/docx-to-content/.claude-plugin/plugin.json \
        plugins/docx-to-content/plugin.yaml \
        plugins/docx-to-content/requirements.in \
        plugins/docx-to-content/requirements.txt \
        plugins/docx-to-content/scripts

git commit -m "feat: scaffold docx-to-content plugin"
```

---

## Task 2: Relocate Existing Cleanup Pipeline Without Redesign

**Files:**
- Create or copy: `plugins/docx-to-content/scripts/pandoc_fixes/attrs.py`
- Create or copy: `plugins/docx-to-content/scripts/pandoc_fixes/images.py`
- Create or copy: `plugins/docx-to-content/scripts/pandoc_fixes/toc.py`
- Create or copy: `plugins/docx-to-content/scripts/pandoc_fixes/tables.py`
- Create or copy: `plugins/docx-to-content/scripts/pandoc_fixes/footnotes.py`
- Create or copy: `plugins/docx-to-content/scripts/emf_convert.py`
- Create or copy: `plugins/docx-to-content/scripts/pandoc_validate.py`
- Create or copy: `plugins/docx-to-content/scripts/docx_to_md.py`
- Create or copy: `plugins/docx-to-content/scripts/md_to_docx.py`
- Create or copy: matching existing tests under `plugins/docx-to-content/tests/`

**Interfaces:**
- Consumes: prior working cleanup modules from paused implementation.
- Produces: relocated cleanup functions used by `convert-document`.

- [ ] **Step 1: Copy the existing cleanup modules into the new plugin**

Copy the already-working files into the exact locations listed above. Preserve function names, behavior, tests, and comments unless import paths must change.

- [ ] **Step 2: Update imports only as required by the new location**

Acceptable import change example:

```python
from pandoc_fixes.attrs import strip_pandoc_attrs
```

to:

```python
from scripts.pandoc_fixes.attrs import strip_pandoc_attrs
```

Only make import/path updates needed for tests to import the relocated modules.

- [ ] **Step 3: Run the relocated cleanup tests**

```bash
cd plugins/docx-to-content
pytest tests -k "attrs or images or toc or tables or footnotes or emf or pandoc_validate or docx_to_md or md_to_docx" -v
```

Expected: existing relocated tests pass, except failures caused only by import paths. Fix import path failures directly.

- [ ] **Step 4: Commit relocation**

```bash
git add plugins/docx-to-content/scripts plugins/docx-to-content/tests
git commit -m "feat: relocate docx cleanup pipeline"
```

---

## Task 3: Add Shared Models and Stable Chunk IDs

**Files:**
- Create: `plugins/docx-to-content/scripts/models.py`
- Create: `plugins/docx-to-content/scripts/slugify.py`
- Create: `plugins/docx-to-content/tests/test_models.py`
- Create: `plugins/docx-to-content/tests/test_slugify.py`

**Interfaces:**
- Consumes: none.
- Produces:
  - `normalize_slug(text: str) -> str`
  - `chunk_id(source_order: int, heading_path: list[str], existing_ids: set[str] | None = None) -> str`
  - dataclasses: `ChunkBoundary`, `ConversionPlan`, `ChunkMetadata`, `ManifestChunk`, `Manifest`

- [ ] **Step 1: Write failing tests for slug generation**

`plugins/docx-to-content/tests/test_slugify.py`:

```python
from scripts.slugify import normalize_slug, chunk_id


def test_normalize_slug_lowercases_and_replaces_non_alphanumeric_runs():
    assert normalize_slug("How to Seal a File!") == "how-to-seal-a-file"


def test_chunk_id_uses_padded_order_and_last_heading_slug():
    result = chunk_id(7, ["FILE ACCESS", "How to Seal a File"])
    assert result == "chunk_007_how-to-seal-a-file"


def test_chunk_id_adds_collision_suffix():
    existing = {"chunk_007_how-to-seal-a-file"}
    result = chunk_id(7, ["FILE ACCESS", "How to Seal a File"], existing)
    assert result == "chunk_007_how-to-seal-a-file-2"
```

- [ ] **Step 2: Run slug tests and verify failure**

```bash
cd plugins/docx-to-content
pytest tests/test_slugify.py -v
```

Expected: FAIL because `scripts.slugify` does not exist.

- [ ] **Step 3: Implement `slugify.py`**

```python
import re


def normalize_slug(text: str) -> str:
    lowered = text.lower()
    replaced = re.sub(r"[^a-z0-9]+", "-", lowered)
    return replaced.strip("-") or "untitled"


def chunk_id(source_order: int, heading_path: list[str], existing_ids: set[str] | None = None) -> str:
    existing_ids = existing_ids or set()
    topic = heading_path[-1] if heading_path else "untitled"
    base = f"chunk_{source_order:03d}_{normalize_slug(topic)}"
    if base not in existing_ids:
        return base
    suffix = 2
    while f"{base}-{suffix}" in existing_ids:
        suffix += 1
    return f"{base}-{suffix}"
```

- [ ] **Step 4: Write failing tests for model serialization**

`plugins/docx-to-content/tests/test_models.py`:

```python
from scripts.models import ConversionPlan, ChunkBoundary, ChunkMetadata


def test_conversion_plan_to_dict_contains_template_awareness():
    plan = ConversionPlan(
        source_docx="sourcedocuments/CEIS MANUAL - working version.docx",
        strategy="chunked",
        chunk_level=2,
        chunk_boundaries=[ChunkBoundary(source_order=1, heading_path=["INTRODUCTION"], start_line=1)],
        source_toc_count=12,
        content_type="manual",
        template_id="manual-v1",
        section_mapping_mode="preserve_source_heading_structure",
        analysis_warnings=[],
    )

    data = plan.to_dict()

    assert data["content_type"] == "manual"
    assert data["template_id"] == "manual-v1"
    assert data["section_mapping_mode"] == "preserve_source_heading_structure"
    assert data["chunk_boundaries"][0]["heading_path"] == ["INTRODUCTION"]


def test_chunk_metadata_to_dict_links_to_content_file():
    metadata = ChunkMetadata(
        chunk_id="chunk_001_intro",
        source_order=1,
        source_heading_path=["INTRODUCTION"],
        topic="INTRODUCTION",
        content_type="manual",
        template_id="manual-v1",
        source_docx="source.docx",
        content_file="chunk_001_intro.md",
    )

    assert metadata.to_dict()["content_file"] == "chunk_001_intro.md"
```

- [ ] **Step 5: Implement `models.py`**

```python
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

Strategy = Literal["single", "chunked"]


@dataclass(frozen=True)
class ChunkBoundary:
    source_order: int
    heading_path: list[str]
    start_line: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ConversionPlan:
    source_docx: str
    strategy: Strategy
    chunk_level: int
    chunk_boundaries: list[ChunkBoundary]
    source_toc_count: int
    content_type: str
    template_id: str
    section_mapping_mode: str
    analysis_warnings: list[str]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["chunk_boundaries"] = [boundary.to_dict() for boundary in self.chunk_boundaries]
        return data


@dataclass(frozen=True)
class ChunkMetadata:
    chunk_id: str
    source_order: int
    source_heading_path: list[str]
    topic: str
    content_type: str
    template_id: str
    source_docx: str
    content_file: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ManifestChunk:
    chunk_id: str
    content_file: str
    metadata_file: str
    source_order: int
    source_heading_path: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Manifest:
    source_docx: str
    content_type: str
    template_id: str
    strategy: Strategy
    chunk_count: int
    chunks: list[ManifestChunk]
    media_dir: str
    validation_report: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["chunks"] = [chunk.to_dict() for chunk in self.chunks]
        return data
```

- [ ] **Step 6: Run model and slug tests**

```bash
cd plugins/docx-to-content
pytest tests/test_slugify.py tests/test_models.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit shared models**

```bash
git add plugins/docx-to-content/scripts/slugify.py \
        plugins/docx-to-content/scripts/models.py \
        plugins/docx-to-content/tests/test_slugify.py \
        plugins/docx-to-content/tests/test_models.py

git commit -m "feat: add content models and stable chunk ids"
```

---

## Task 4: Implement Analyze Structure and Conversion Plan Generation

**Files:**
- Create: `plugins/docx-to-content/scripts/analyze_structure.py`
- Create: `plugins/docx-to-content/tests/test_analyze_structure.py`

**Interfaces:**
- Consumes:
  - `ConversionPlan`, `ChunkBoundary` from `scripts.models`
- Produces:
  - `parse_headings(markdown_text: str) -> list[tuple[int, str, int]]`
  - `recommend_strategy(headings: list[tuple[int, str, int]], line_count: int) -> tuple[str, int, list[str]]`
  - `build_conversion_plan(source_docx: str, markdown_text: str, content_type: str = "manual", template_id: str = "manual-v1") -> ConversionPlan`

- [ ] **Step 1: Write failing tests for heading parsing and strategy**

`plugins/docx-to-content/tests/test_analyze_structure.py`:

```python
from scripts.analyze_structure import parse_headings, recommend_strategy, build_conversion_plan


def test_parse_headings_returns_level_text_and_line_number():
    markdown = "# Title\n\n## FILE ACCESS\nText\n### How to Seal a File\n"
    assert parse_headings(markdown) == [
        (1, "Title", 1),
        (2, "FILE ACCESS", 3),
        (3, "How to Seal a File", 5),
    ]


def test_recommend_strategy_chunked_for_many_level_two_headings():
    headings = [(2, f"Section {i}", i * 10) for i in range(1, 16)]
    strategy, level, warnings = recommend_strategy(headings, line_count=1200)
    assert strategy == "chunked"
    assert level == 2
    assert warnings == []


def test_recommend_strategy_single_for_small_document():
    headings = [(1, "Title", 1), (2, "Overview", 5)]
    strategy, level, warnings = recommend_strategy(headings, line_count=80)
    assert strategy == "single"
    assert level == 1
    assert warnings == []


def test_build_conversion_plan_preserves_manual_template_identity():
    markdown = "# CEIS Manual\n\n## FILE ACCESS\nBody\n## DATA CAPTURE\nBody\n"
    plan = build_conversion_plan("source.docx", markdown)
    data = plan.to_dict()
    assert data["content_type"] == "manual"
    assert data["template_id"] == "manual-v1"
    assert data["section_mapping_mode"] == "preserve_source_heading_structure"
    assert data["chunk_boundaries"][0]["heading_path"] == ["FILE ACCESS"]
```

- [ ] **Step 2: Run tests and verify failure**

```bash
cd plugins/docx-to-content
pytest tests/test_analyze_structure.py -v
```

Expected: FAIL because `scripts.analyze_structure` does not exist.

- [ ] **Step 3: Implement `analyze_structure.py`**

```python
from __future__ import annotations

import re

from scripts.models import ChunkBoundary, ConversionPlan

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def parse_headings(markdown_text: str) -> list[tuple[int, str, int]]:
    headings: list[tuple[int, str, int]] = []
    for index, line in enumerate(markdown_text.splitlines(), start=1):
        match = HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append((level, text, index))
    return headings


def recommend_strategy(headings: list[tuple[int, str, int]], line_count: int) -> tuple[str, int, list[str]]:
    warnings: list[str] = []
    level_two_count = sum(1 for level, _text, _line in headings if level == 2)
    if level_two_count >= 6 or line_count >= 500:
        return "chunked", 2, warnings
    return "single", 1, warnings


def _heading_path_for_level_two(headings: list[tuple[int, str, int]], index: int) -> list[str]:
    level, text, _line = headings[index]
    if level == 2:
        return [text]
    path: list[str] = [text]
    for prior_level, prior_text, _prior_line in reversed(headings[:index]):
        if prior_level < level:
            path.insert(0, prior_text)
        if prior_level == 1:
            break
    return path


def build_conversion_plan(
    source_docx: str,
    markdown_text: str,
    content_type: str = "manual",
    template_id: str = "manual-v1",
) -> ConversionPlan:
    headings = parse_headings(markdown_text)
    strategy, chunk_level, warnings = recommend_strategy(headings, len(markdown_text.splitlines()))
    boundaries: list[ChunkBoundary] = []

    if strategy == "chunked":
        selected = [(i, h) for i, h in enumerate(headings) if h[0] == chunk_level]
    else:
        selected = [(0, headings[0])] if headings else [(0, (1, "Document", 1))]

    for source_order, (heading_index, (_level, text, line_number)) in enumerate(selected, start=1):
        if strategy == "chunked":
            heading_path = _heading_path_for_level_two(headings, heading_index)
        else:
            heading_path = [text]
        boundaries.append(ChunkBoundary(source_order=source_order, heading_path=heading_path, start_line=line_number))

    return ConversionPlan(
        source_docx=source_docx,
        strategy=strategy,
        chunk_level=chunk_level,
        chunk_boundaries=boundaries,
        source_toc_count=0,
        content_type=content_type,
        template_id=template_id,
        section_mapping_mode="preserve_source_heading_structure",
        analysis_warnings=warnings,
    )
```

- [ ] **Step 4: Run analyze tests**

```bash
cd plugins/docx-to-content
pytest tests/test_analyze_structure.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit analysis logic**

```bash
git add plugins/docx-to-content/scripts/analyze_structure.py \
        plugins/docx-to-content/tests/test_analyze_structure.py

git commit -m "feat: add document structure analysis"
```

---

## Task 5: Implement Canonical Chunk and Metadata Generation

**Files:**
- Create: `plugins/docx-to-content/scripts/chunk_metadata.py`
- Create: `plugins/docx-to-content/tests/test_chunk_metadata.py`

**Interfaces:**
- Consumes:
  - `ConversionPlan`, `ChunkMetadata` from `scripts.models`
  - `chunk_id()` from `scripts.slugify`
- Produces:
  - `split_markdown_by_plan(markdown_text: str, plan: ConversionPlan) -> list[tuple[str, str]]`
  - `metadata_for_chunk(plan: ConversionPlan, source_order: int, heading_path: list[str], content_file: str, existing_ids: set[str]) -> ChunkMetadata`

- [ ] **Step 1: Write failing tests for chunk splitting and metadata**

`plugins/docx-to-content/tests/test_chunk_metadata.py`:

```python
from scripts.chunk_metadata import split_markdown_by_plan, metadata_for_chunk
from scripts.models import ConversionPlan, ChunkBoundary


def make_plan():
    return ConversionPlan(
        source_docx="source.docx",
        strategy="chunked",
        chunk_level=2,
        chunk_boundaries=[
            ChunkBoundary(1, ["FILE ACCESS"], 1),
            ChunkBoundary(2, ["DATA CAPTURE"], 4),
        ],
        source_toc_count=0,
        content_type="manual",
        template_id="manual-v1",
        section_mapping_mode="preserve_source_heading_structure",
        analysis_warnings=[],
    )


def test_split_markdown_by_plan_returns_named_chunks():
    markdown = "## FILE ACCESS\nA\nB\n## DATA CAPTURE\nC\nD\n"
    chunks = split_markdown_by_plan(markdown, make_plan())
    assert chunks == [
        ("chunk_001_file-access.md", "## FILE ACCESS\nA\nB\n"),
        ("chunk_002_data-capture.md", "## DATA CAPTURE\nC\nD"),
    ]


def test_metadata_for_chunk_links_to_content_file():
    meta = metadata_for_chunk(make_plan(), 1, ["FILE ACCESS"], "chunk_001_file-access.md", set())
    assert meta.chunk_id == "chunk_001_file-access"
    assert meta.topic == "FILE ACCESS"
    assert meta.content_file == "chunk_001_file-access.md"
    assert meta.template_id == "manual-v1"
```

- [ ] **Step 2: Run tests and verify failure**

```bash
cd plugins/docx-to-content
pytest tests/test_chunk_metadata.py -v
```

Expected: FAIL because `scripts.chunk_metadata` does not exist.

- [ ] **Step 3: Implement `chunk_metadata.py`**

```python
from __future__ import annotations

from scripts.models import ChunkMetadata, ConversionPlan
from scripts.slugify import chunk_id, normalize_slug


def split_markdown_by_plan(markdown_text: str, plan: ConversionPlan) -> list[tuple[str, str]]:
    lines = markdown_text.splitlines()
    chunks: list[tuple[str, str]] = []

    if plan.strategy == "single":
        heading_path = plan.chunk_boundaries[0].heading_path if plan.chunk_boundaries else ["Document"]
        filename = f"chunk_001_{normalize_slug(heading_path[-1])}.md"
        return [(filename, markdown_text)]

    boundaries = sorted(plan.chunk_boundaries, key=lambda item: item.start_line)
    for index, boundary in enumerate(boundaries):
        start = boundary.start_line - 1
        end = boundaries[index + 1].start_line - 1 if index + 1 < len(boundaries) else len(lines)
        body = "\n".join(lines[start:end])
        if index + 1 < len(boundaries):
            body = body + "\n"
        filename = f"chunk_{boundary.source_order:03d}_{normalize_slug(boundary.heading_path[-1])}.md"
        chunks.append((filename, body))
    return chunks


def metadata_for_chunk(
    plan: ConversionPlan,
    source_order: int,
    heading_path: list[str],
    content_file: str,
    existing_ids: set[str],
) -> ChunkMetadata:
    cid = chunk_id(source_order, heading_path, existing_ids)
    existing_ids.add(cid)
    return ChunkMetadata(
        chunk_id=cid,
        source_order=source_order,
        source_heading_path=heading_path,
        topic=heading_path[-1] if heading_path else "Document",
        content_type=plan.content_type,
        template_id=plan.template_id,
        source_docx=plan.source_docx,
        content_file=content_file,
    )
```

- [ ] **Step 4: Run chunk metadata tests**

```bash
cd plugins/docx-to-content
pytest tests/test_chunk_metadata.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit chunk metadata logic**

```bash
git add plugins/docx-to-content/scripts/chunk_metadata.py \
        plugins/docx-to-content/tests/test_chunk_metadata.py

git commit -m "feat: add canonical chunk metadata generation"
```

---

## Task 6: Implement Manifest Writer and Canonical Validator

**Files:**
- Create: `plugins/docx-to-content/scripts/manifest.py`
- Create: `plugins/docx-to-content/scripts/validate_canonical.py`
- Create: `plugins/docx-to-content/tests/test_manifest.py`
- Create: `plugins/docx-to-content/tests/test_validate_canonical.py`

**Interfaces:**
- Consumes:
  - `Manifest`, `ManifestChunk`, `ChunkMetadata` from `scripts.models`
- Produces:
  - `build_manifest(source_docx: str, content_type: str, template_id: str, strategy: str, metadata_items: list[ChunkMetadata], media_dir: str, validation_report: str) -> Manifest`
  - `write_json(path: Path, data: dict) -> None`
  - `validate_canonical_folder(root: Path) -> dict`

- [ ] **Step 1: Write failing tests for manifest generation**

`plugins/docx-to-content/tests/test_manifest.py`:

```python
from scripts.manifest import build_manifest
from scripts.models import ChunkMetadata


def test_build_manifest_records_chunks_and_validation_report():
    meta = ChunkMetadata(
        chunk_id="chunk_001_intro",
        source_order=1,
        source_heading_path=["INTRODUCTION"],
        topic="INTRODUCTION",
        content_type="manual",
        template_id="manual-v1",
        source_docx="source.docx",
        content_file="chunk_001_intro.md",
    )

    manifest = build_manifest("source.docx", "manual", "manual-v1", "chunked", [meta], "media", "validation.json")
    data = manifest.to_dict()

    assert data["chunk_count"] == 1
    assert data["chunks"][0]["metadata_file"] == "chunk_001_intro.meta.json"
    assert data["validation_report"] == "validation.json"
```

- [ ] **Step 2: Implement `manifest.py`**

```python
from __future__ import annotations

import json
from pathlib import Path

from scripts.models import ChunkMetadata, Manifest, ManifestChunk


def build_manifest(
    source_docx: str,
    content_type: str,
    template_id: str,
    strategy: str,
    metadata_items: list[ChunkMetadata],
    media_dir: str,
    validation_report: str,
) -> Manifest:
    chunks = [
        ManifestChunk(
            chunk_id=item.chunk_id,
            content_file=item.content_file,
            metadata_file=item.content_file.replace(".md", ".meta.json"),
            source_order=item.source_order,
            source_heading_path=item.source_heading_path,
        )
        for item in metadata_items
    ]
    return Manifest(
        source_docx=source_docx,
        content_type=content_type,
        template_id=template_id,
        strategy=strategy,
        chunk_count=len(chunks),
        chunks=chunks,
        media_dir=media_dir,
        validation_report=validation_report,
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
```

- [ ] **Step 3: Write failing tests for canonical validation**

`plugins/docx-to-content/tests/test_validate_canonical.py`:

```python
import json

from scripts.validate_canonical import validate_canonical_folder


def test_validate_canonical_folder_passes_for_matching_chunk_metadata_and_manifest(tmp_path):
    root = tmp_path / "canonical-content"
    chunks = root / "chunks"
    chunks.mkdir(parents=True)
    (root / "media").mkdir()
    (chunks / "chunk_001_intro.md").write_text("## INTRODUCTION\nBody\n", encoding="utf-8")
    (chunks / "chunk_001_intro.meta.json").write_text(json.dumps({
        "chunk_id": "chunk_001_intro",
        "source_order": 1,
        "source_heading_path": ["INTRODUCTION"],
        "topic": "INTRODUCTION",
        "content_type": "manual",
        "template_id": "manual-v1",
        "source_docx": "source.docx",
        "content_file": "chunk_001_intro.md"
    }), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps({
        "source_docx": "source.docx",
        "content_type": "manual",
        "template_id": "manual-v1",
        "strategy": "chunked",
        "chunk_count": 1,
        "chunks": [{
            "chunk_id": "chunk_001_intro",
            "content_file": "chunk_001_intro.md",
            "metadata_file": "chunk_001_intro.meta.json",
            "source_order": 1,
            "source_heading_path": ["INTRODUCTION"]
        }],
        "media_dir": "media",
        "validation_report": "validation.json"
    }), encoding="utf-8")

    result = validate_canonical_folder(root)

    assert result["status"] == "PASS"
    assert result["errors"] == []
```

- [ ] **Step 4: Implement `validate_canonical.py`**

```python
from __future__ import annotations

import json
import re
from pathlib import Path

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def validate_canonical_folder(root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = root / "manifest.json"
    chunks_dir = root / "chunks"

    if not manifest_path.exists():
        errors.append("manifest.json missing")
        return {"status": "FAIL", "errors": errors, "warnings": warnings}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    seen_ids: set[str] = set()

    for chunk in manifest.get("chunks", []):
        content_path = chunks_dir / chunk["content_file"]
        meta_path = chunks_dir / chunk["metadata_file"]
        if not content_path.exists():
            errors.append(f"content file missing: {chunk['content_file']}")
            continue
        if not meta_path.exists():
            errors.append(f"metadata file missing: {chunk['metadata_file']}")
            continue

        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        chunk_id = metadata.get("chunk_id")
        if chunk_id in seen_ids:
            errors.append(f"duplicate chunk_id: {chunk_id}")
        seen_ids.add(chunk_id)
        if metadata.get("content_file") != chunk["content_file"]:
            errors.append(f"metadata content_file mismatch for {chunk['content_file']}")

        text = content_path.read_text(encoding="utf-8")
        if re.search(r"\{width=|\{height=|\{\.underline\}|\{\.mark\}", text):
            errors.append(f"pandoc artifact remains in {chunk['content_file']}")
        if re.search(r"^#{1,6}\s+!\[", text, flags=re.MULTILINE):
            errors.append(f"image embedded in heading in {chunk['content_file']}")
        for image_ref in IMAGE_RE.findall(text):
            if image_ref.startswith("http"):
                continue
            possible = (chunks_dir / image_ref).resolve()
            if not possible.exists():
                warnings.append(f"image reference unresolved from chunks dir: {image_ref}")

    status = "FAIL" if errors else "PASS"
    return {"status": status, "errors": errors, "warnings": warnings}
```

- [ ] **Step 5: Run manifest and canonical validation tests**

```bash
cd plugins/docx-to-content
pytest tests/test_manifest.py tests/test_validate_canonical.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit validation layer**

```bash
git add plugins/docx-to-content/scripts/manifest.py \
        plugins/docx-to-content/scripts/validate_canonical.py \
        plugins/docx-to-content/tests/test_manifest.py \
        plugins/docx-to-content/tests/test_validate_canonical.py

git commit -m "feat: add manifest and canonical validation"
```

---

## Task 7: Implement Renderer Contract and Multi-Page Markdown Renderer

**Files:**
- Create: `plugins/docx-to-content/scripts/renderers/base.py`
- Create: `plugins/docx-to-content/scripts/renderers/multipage_markdown.py`
- Create: `plugins/docx-to-content/scripts/renderers/validate_rendered.py`
- Create: `plugins/docx-to-content/tests/test_renderer_base.py`
- Create: `plugins/docx-to-content/tests/test_multipage_markdown.py`
- Create: `plugins/docx-to-content/tests/test_validate_rendered.py`

**Interfaces:**
- Consumes:
  - canonical content folder containing `manifest.json`, `chunks/*.md`, `chunks/*.meta.json`, and `media/`
- Produces:
  - `RendererInput.from_folder(root: Path) -> RendererInput`
  - `render_multipage_markdown(canonical_root: Path, output_root: Path) -> dict`
  - `validate_rendered_output(output_root: Path, manifest: dict) -> dict`

- [ ] **Step 1: Write failing renderer base test**

`plugins/docx-to-content/tests/test_renderer_base.py`:

```python
import json

from scripts.renderers.base import RendererInput


def test_renderer_input_loads_manifest_chunks_and_metadata(tmp_path):
    root = tmp_path / "canonical-content"
    chunks = root / "chunks"
    chunks.mkdir(parents=True)
    (root / "media").mkdir()
    (chunks / "chunk_001_intro.md").write_text("## INTRODUCTION\n", encoding="utf-8")
    (chunks / "chunk_001_intro.meta.json").write_text(json.dumps({"chunk_id": "chunk_001_intro", "content_file": "chunk_001_intro.md"}), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps({"chunks": [{"chunk_id": "chunk_001_intro", "content_file": "chunk_001_intro.md", "metadata_file": "chunk_001_intro.meta.json"}], "media_dir": "media"}), encoding="utf-8")

    renderer_input = RendererInput.from_folder(root)

    assert renderer_input.manifest["chunks"][0]["chunk_id"] == "chunk_001_intro"
    assert renderer_input.chunks[0]["content"] == "## INTRODUCTION\n"
    assert renderer_input.chunks[0]["metadata"]["chunk_id"] == "chunk_001_intro"
```

- [ ] **Step 2: Implement `renderers/base.py`**

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RendererInput:
    root: Path
    manifest: dict
    chunks: list[dict]
    media_dir: Path

    @classmethod
    def from_folder(cls, root: Path) -> "RendererInput":
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        chunks_dir = root / "chunks"
        loaded_chunks: list[dict] = []
        for chunk in manifest.get("chunks", []):
            content = (chunks_dir / chunk["content_file"]).read_text(encoding="utf-8")
            metadata = json.loads((chunks_dir / chunk["metadata_file"]).read_text(encoding="utf-8"))
            loaded_chunks.append({"manifest": chunk, "content": content, "metadata": metadata})
        return cls(root=root, manifest=manifest, chunks=loaded_chunks, media_dir=root / manifest.get("media_dir", "media"))
```

- [ ] **Step 3: Write failing multipage renderer test**

`plugins/docx-to-content/tests/test_multipage_markdown.py`:

```python
import json

from scripts.renderers.multipage_markdown import render_multipage_markdown


def test_render_multipage_markdown_writes_index_and_pages(tmp_path):
    canonical = tmp_path / "canonical-content"
    chunks = canonical / "chunks"
    chunks.mkdir(parents=True)
    (canonical / "media").mkdir()
    (chunks / "chunk_001_intro.md").write_text("## INTRODUCTION\nBody\n", encoding="utf-8")
    (chunks / "chunk_001_intro.meta.json").write_text(json.dumps({
        "chunk_id": "chunk_001_intro",
        "source_heading_path": ["INTRODUCTION"],
        "content_file": "chunk_001_intro.md"
    }), encoding="utf-8")
    (canonical / "manifest.json").write_text(json.dumps({
        "chunks": [{
            "chunk_id": "chunk_001_intro",
            "content_file": "chunk_001_intro.md",
            "metadata_file": "chunk_001_intro.meta.json",
            "source_order": 1,
            "source_heading_path": ["INTRODUCTION"]
        }],
        "media_dir": "media"
    }), encoding="utf-8")

    result = render_multipage_markdown(canonical, tmp_path / "rendered-output")

    assert result["status"] == "PASS"
    assert (tmp_path / "rendered-output" / "index.md").exists()
    assert (tmp_path / "rendered-output" / "pages" / "chunk_001_intro.md").exists()
    assert "[INTRODUCTION](pages/chunk_001_intro.md)" in (tmp_path / "rendered-output" / "index.md").read_text(encoding="utf-8")
```

- [ ] **Step 4: Implement `multipage_markdown.py`**

```python
from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.renderers.base import RendererInput
from scripts.renderers.validate_rendered import validate_rendered_output


def render_multipage_markdown(canonical_root: Path, output_root: Path) -> dict:
    renderer_input = RendererInput.from_folder(canonical_root)
    pages_dir = output_root / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    index_lines = ["# Content Index", ""]
    for chunk in renderer_input.chunks:
        manifest_chunk = chunk["manifest"]
        metadata = chunk["metadata"]
        content_file = manifest_chunk["content_file"]
        page_path = pages_dir / content_file
        page_path.write_text(chunk["content"], encoding="utf-8")
        title = " / ".join(metadata.get("source_heading_path", [manifest_chunk["chunk_id"]]))
        index_lines.append(f"- [{title}](pages/{content_file})")

    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    if renderer_input.media_dir.exists():
        destination_media = output_root / "media"
        if destination_media.exists():
            shutil.rmtree(destination_media)
        shutil.copytree(renderer_input.media_dir, destination_media)

    validation = validate_rendered_output(output_root, renderer_input.manifest)
    (output_root / "renderer-validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    return validation
```

- [ ] **Step 5: Write failing rendered validation test**

`plugins/docx-to-content/tests/test_validate_rendered.py`:

```python
from scripts.renderers.validate_rendered import validate_rendered_output


def test_validate_rendered_output_passes_when_index_links_and_pages_exist(tmp_path):
    output = tmp_path / "rendered-output"
    pages = output / "pages"
    pages.mkdir(parents=True)
    (output / "index.md").write_text("# Content Index\n\n- [INTRODUCTION](pages/chunk_001_intro.md)\n", encoding="utf-8")
    (pages / "chunk_001_intro.md").write_text("## INTRODUCTION\nBody\n", encoding="utf-8")
    manifest = {"chunks": [{"content_file": "chunk_001_intro.md"}]}

    result = validate_rendered_output(output, manifest)

    assert result["status"] == "PASS"
    assert result["errors"] == []
```

- [ ] **Step 6: Implement `validate_rendered.py`**

```python
from __future__ import annotations

import re
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def validate_rendered_output(output_root: Path, manifest: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    index_path = output_root / "index.md"
    pages_dir = output_root / "pages"

    if not output_root.exists():
        errors.append("output folder missing")
    if not index_path.exists():
        errors.append("index.md missing")
    if not pages_dir.exists():
        errors.append("pages folder missing")

    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")
        for target in LINK_RE.findall(index_text):
            if target.startswith("http"):
                continue
            if not (output_root / target).exists():
                errors.append(f"index link target missing: {target}")

    for chunk in manifest.get("chunks", []):
        page = pages_dir / chunk["content_file"]
        if not page.exists():
            errors.append(f"rendered page missing: {chunk['content_file']}")

    return {"status": "FAIL" if errors else "PASS", "errors": errors, "warnings": warnings}
```

- [ ] **Step 7: Run renderer tests**

```bash
cd plugins/docx-to-content
pytest tests/test_renderer_base.py tests/test_multipage_markdown.py tests/test_validate_rendered.py -v
```

Expected: PASS.

- [ ] **Step 8: Commit renderer contract**

```bash
git add plugins/docx-to-content/scripts/renderers \
        plugins/docx-to-content/tests/test_renderer_base.py \
        plugins/docx-to-content/tests/test_multipage_markdown.py \
        plugins/docx-to-content/tests/test_validate_rendered.py

git commit -m "feat: add multipage markdown renderer"
```

---

## Task 8: Wire the Convert Flow Into Artifacts

**Files:**
- Modify: `plugins/docx-to-content/scripts/docx_to_md.py`
- Create: `plugins/docx-to-content/tests/integration/test_ceis_end_to_end.py`

**Interfaces:**
- Consumes:
  - `build_conversion_plan()` from `scripts.analyze_structure`
  - cleanup functions from relocated modules
  - `split_markdown_by_plan()` and `metadata_for_chunk()`
  - `build_manifest()` and `write_json()`
  - `validate_canonical_folder()`
  - `render_multipage_markdown()`
- Produces:
  - `run_phase1_pipeline(source_docx: Path, work_root: Path) -> dict`

- [ ] **Step 1: Add integration test using a small markdown fixture first**

`plugins/docx-to-content/tests/integration/test_ceis_end_to_end.py`:

```python
import json

from pathlib import Path

from scripts.analyze_structure import build_conversion_plan
from scripts.chunk_metadata import metadata_for_chunk, split_markdown_by_plan
from scripts.manifest import build_manifest, write_json
from scripts.validate_canonical import validate_canonical_folder
from scripts.renderers.multipage_markdown import render_multipage_markdown


def test_phase1_pipeline_from_clean_markdown_fixture(tmp_path):
    source_docx = "source.docx"
    markdown = "## FILE ACCESS\nBody\n## DATA CAPTURE\nMore body\n"
    plan = build_conversion_plan(source_docx, markdown)
    canonical = tmp_path / "canonical-content"
    chunks_dir = canonical / "chunks"
    chunks_dir.mkdir(parents=True)
    (canonical / "media").mkdir()

    chunks = split_markdown_by_plan(markdown, plan)
    metadata_items = []
    existing_ids = set()
    for boundary, (filename, body) in zip(plan.chunk_boundaries, chunks):
        (chunks_dir / filename).write_text(body, encoding="utf-8")
        meta = metadata_for_chunk(plan, boundary.source_order, boundary.heading_path, filename, existing_ids)
        metadata_items.append(meta)
        write_json(chunks_dir / filename.replace(".md", ".meta.json"), meta.to_dict())

    manifest = build_manifest(source_docx, "manual", "manual-v1", plan.strategy, metadata_items, "media", "validation.json")
    write_json(canonical / "manifest.json", manifest.to_dict())
    validation = validate_canonical_folder(canonical)
    write_json(canonical / "validation.json", validation)

    render_validation = render_multipage_markdown(canonical, tmp_path / "rendered-output")

    assert validation["status"] == "PASS"
    assert render_validation["status"] == "PASS"
    assert (tmp_path / "rendered-output" / "index.md").exists()
```

- [ ] **Step 2: Run integration test**

```bash
cd plugins/docx-to-content
pytest tests/integration/test_ceis_end_to_end.py -v
```

Expected: PASS after prior tasks.

- [ ] **Step 3: Add `run_phase1_pipeline` to `docx_to_md.py`**

Append or integrate this public function while preserving existing conversion behavior:

```python
from __future__ import annotations

import json
from pathlib import Path

from scripts.analyze_structure import build_conversion_plan
from scripts.chunk_metadata import metadata_for_chunk, split_markdown_by_plan
from scripts.manifest import build_manifest, write_json
from scripts.validate_canonical import validate_canonical_folder
from scripts.renderers.multipage_markdown import render_multipage_markdown


def run_phase1_pipeline_from_clean_markdown(source_docx: str, markdown_text: str, work_root: Path) -> dict:
    analysis_report_path = work_root / "analysis-report.json"
    conversion_plan_path = work_root / "conversion-plan.json"
    canonical_root = work_root / "canonical-content"
    chunks_dir = canonical_root / "chunks"
    rendered_root = work_root / "rendered-output"

    chunks_dir.mkdir(parents=True, exist_ok=True)
    (canonical_root / "media").mkdir(parents=True, exist_ok=True)

    plan = build_conversion_plan(source_docx, markdown_text)
    write_json(conversion_plan_path, plan.to_dict())
    write_json(analysis_report_path, {
        "source_docx": source_docx,
        "strategy": plan.strategy,
        "chunk_level": plan.chunk_level,
        "chunk_count": len(plan.chunk_boundaries),
        "warnings": plan.analysis_warnings,
    })

    chunks = split_markdown_by_plan(markdown_text, plan)
    metadata_items = []
    existing_ids: set[str] = set()
    for boundary, (filename, body) in zip(plan.chunk_boundaries, chunks):
        (chunks_dir / filename).write_text(body, encoding="utf-8")
        meta = metadata_for_chunk(plan, boundary.source_order, boundary.heading_path, filename, existing_ids)
        metadata_items.append(meta)
        write_json(chunks_dir / filename.replace(".md", ".meta.json"), meta.to_dict())

    manifest = build_manifest(source_docx, plan.content_type, plan.template_id, plan.strategy, metadata_items, "media", "validation.json")
    write_json(canonical_root / "manifest.json", manifest.to_dict())
    canonical_validation = validate_canonical_folder(canonical_root)
    write_json(canonical_root / "validation.json", canonical_validation)

    rendered_validation = render_multipage_markdown(canonical_root, rendered_root)

    return {
        "analysis_report": str(analysis_report_path),
        "conversion_plan": str(conversion_plan_path),
        "canonical_validation": canonical_validation,
        "renderer_validation": rendered_validation,
        "canonical_root": str(canonical_root),
        "rendered_root": str(rendered_root),
    }
```

- [ ] **Step 4: Add a test for the public pipeline function**

Extend `test_ceis_end_to_end.py`:

```python
from scripts.docx_to_md import run_phase1_pipeline_from_clean_markdown


def test_run_phase1_pipeline_from_clean_markdown_writes_required_artifacts(tmp_path):
    result = run_phase1_pipeline_from_clean_markdown(
        "source.docx",
        "## FILE ACCESS\nBody\n## DATA CAPTURE\nMore body\n",
        tmp_path,
    )

    assert result["canonical_validation"]["status"] == "PASS"
    assert result["renderer_validation"]["status"] == "PASS"
    assert (tmp_path / "analysis-report.json").exists()
    assert (tmp_path / "conversion-plan.json").exists()
    assert (tmp_path / "canonical-content" / "manifest.json").exists()
    assert (tmp_path / "canonical-content" / "validation.json").exists()
    assert (tmp_path / "rendered-output" / "index.md").exists()
    assert (tmp_path / "rendered-output" / "renderer-validation.json").exists()
```

- [ ] **Step 5: Run integration tests**

```bash
cd plugins/docx-to-content
pytest tests/integration/test_ceis_end_to_end.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit pipeline wiring**

```bash
git add plugins/docx-to-content/scripts/docx_to_md.py \
        plugins/docx-to-content/tests/integration/test_ceis_end_to_end.py

git commit -m "feat: wire phase1 content pipeline"
```

---

## Task 9: Write Skill Documents and Contract Tests

**Files:**
- Create: `plugins/docx-to-content/skills/analyze-document/SKILL.md`
- Create: `plugins/docx-to-content/skills/convert-document/SKILL.md`
- Create: `plugins/docx-to-content/skills/render-content/SKILL.md`
- Create: `plugins/docx-to-content/skills/analyze-document/tests/test_analyze_document_skill_contract.py`
- Create: `plugins/docx-to-content/skills/convert-document/tests/test_convert_document_skill_contract.py`
- Create: `plugins/docx-to-content/skills/render-content/tests/test_render_content_skill_contract.py`

**Interfaces:**
- Consumes: scripts from prior tasks.
- Produces: clear skill-level user/agent instructions.

- [ ] **Step 1: Create `analyze-document/SKILL.md`**

```markdown
### name: analyze-document
plugin: docx-to-content
description: Analyze a source .docx and produce a conversion plan before canonical content is written

## Purpose

Use this skill first in the Phase 1 docx-to-content workflow.

It may run temporary pandoc extraction for analysis only. Raw pandoc markdown is transitory diagnostic input and is not canonical content.

## Inputs

- source `.docx`
- output folder for analysis artifacts
- optional content type, default `manual`
- optional template id, default `manual-v1`

## Outputs

- `analysis-report.json`
- `conversion-plan.json`

## Required Behavior

- Analyze heading structure, image count, approximate document size, and known pandoc issue signals.
- Recommend `single` or `chunked` strategy.
- Include explicit reasoning for the recommendation.
- Include `content_type`, `template_id`, and `section_mapping_mode` in the conversion plan.
- Do not write canonical content chunks.

## Success Criteria

The skill succeeds when the analysis report and conversion plan exist and the plan can be consumed by `convert-document`.
```

- [ ] **Step 2: Create `convert-document/SKILL.md`**

```markdown
### name: convert-document
plugin: docx-to-content
description: Convert a source .docx according to a confirmed plan into canonical cleaned content and metadata

## Purpose

Use this skill after `analyze-document` has produced a confirmed conversion plan.

## Inputs

- source `.docx`
- confirmed `conversion-plan.json`
- canonical content output folder

## Outputs

- `canonical-content/manifest.json`
- `canonical-content/validation.json`
- `canonical-content/chunks/*.md`
- `canonical-content/chunks/*.meta.json`
- `canonical-content/media/`

## Required Behavior

- Treat raw pandoc markdown as transitory.
- Run the cleanup pipeline in this order: attrs, images, toc, tables, footnotes, legacy image conversion.
- Generate deterministic chunk IDs.
- Generate exactly one metadata sidecar per chunk.
- Generate a manifest.
- Run canonical validation.

## Success Criteria

The skill succeeds when canonical validation status is `PASS`, or when warnings are recorded without blocking use.
```

- [ ] **Step 3: Create `render-content/SKILL.md`**

```markdown
### name: render-content
plugin: docx-to-content
description: Render canonical content through the Phase 1 multipage markdown renderer

## Purpose

Use this skill after `convert-document` has produced canonical content.

## Inputs

- canonical content folder containing `manifest.json`, `chunks/`, and `media/`
- rendered output folder

## Outputs

- `rendered-output/index.md`
- `rendered-output/pages/*.md`
- `rendered-output/media/` if media exists
- `rendered-output/renderer-validation.json`

## Required Behavior

- Consume the renderer contract: manifest, chunks, metadata sidecars, and media assets.
- Use only `multipage_markdown.py` in Phase 1.
- Generate a navigable index.
- Validate rendered output links and pages.

## Success Criteria

The skill succeeds when renderer validation status is `PASS`.
```

- [ ] **Step 4: Add contract tests for skill docs**

`plugins/docx-to-content/skills/analyze-document/tests/test_analyze_document_skill_contract.py`:

```python
from pathlib import Path


def test_analyze_document_skill_mentions_transitory_raw_markdown():
    text = Path("skills/analyze-document/SKILL.md").read_text(encoding="utf-8")
    assert "Raw pandoc markdown is transitory" in text
    assert "conversion-plan.json" in text
```

`plugins/docx-to-content/skills/convert-document/tests/test_convert_document_skill_contract.py`:

```python
from pathlib import Path


def test_convert_document_skill_mentions_metadata_sidecars_and_validation():
    text = Path("skills/convert-document/SKILL.md").read_text(encoding="utf-8")
    assert "exactly one metadata sidecar per chunk" in text
    assert "canonical validation" in text
```

`plugins/docx-to-content/skills/render-content/tests/test_render_content_skill_contract.py`:

```python
from pathlib import Path


def test_render_content_skill_mentions_only_phase1_renderer():
    text = Path("skills/render-content/SKILL.md").read_text(encoding="utf-8")
    assert "Use only `multipage_markdown.py` in Phase 1" in text
    assert "renderer-validation.json" in text
```

- [ ] **Step 5: Run skill contract tests**

```bash
cd plugins/docx-to-content
pytest skills/analyze-document/tests skills/convert-document/tests skills/render-content/tests -v
```

Expected: PASS.

- [ ] **Step 6: Commit skill docs**

```bash
git add plugins/docx-to-content/skills
git commit -m "docs: add docx-to-content skill contracts"
```

---

## Task 10: Add References and Review Gate

**Files:**
- Create: `plugins/docx-to-content/references/pandoc-docx-setup.md`
- Create: `plugins/docx-to-content/references/known-pandoc-gaps.md`
- Create: `plugins/docx-to-content/references/plan-reviewer-dispatch.md`

**Interfaces:**
- Consumes: review prompt format from plan document reviewer input.
- Produces: implementation reference docs and plan review handoff.

- [ ] **Step 1: Create `pandoc-docx-setup.md`**

```markdown
# Pandoc DOCX Setup

## Required External Tools

- `pandoc` for `.docx` to markdown extraction.
- LibreOffice `soffice` for legacy image conversion when `.emf` or `.wmf` assets are present.

## Verification Commands

```bash
pandoc --version
soffice --version
```

## Notes

On macOS Homebrew cask installs LibreOffice with the CLI name `soffice`, not `libreoffice`.
```

- [ ] **Step 2: Create `known-pandoc-gaps.md`**

```markdown
# Known Pandoc DOCX Gaps

The Phase 1 cleanup pipeline exists because raw pandoc markdown from older Word-authored manuals can contain defects that make the markdown unusable as canonical content.

## Gaps Addressed

- Raw Word table-of-contents field output.
- Images glued directly to headings or list items.
- Pandoc attribute syntax such as width and height markers.
- Legacy `.emf` and `.wmf` media references.
- Footnote and table cleanup issues.

## Rule

Raw pandoc markdown is transitory. It must be cleaned, chunked, metadata-backed, and validated before it becomes canonical content.
```

- [ ] **Step 3: Create `plan-reviewer-dispatch.md`**

```markdown
# Plan Reviewer Dispatch

Use after the implementation plan is complete and before coding begins.

## Reviewer Prompt

You are a plan document reviewer. Verify this plan is complete and ready for implementation.

**Plan to review:** docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan.md

**Spec for reference:** docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design.md

## What to Check

| Category | What to Look For |
|----------|------------------|
| Completeness | unresolved markers, incomplete tasks, missing steps |
| Spec Alignment | plan covers spec requirements, no major scope creep |
| Task Decomposition | tasks have clear boundaries, steps are actionable |
| Buildability | engineer can follow the plan without getting stuck |

## Calibration

Only flag issues that would cause real problems during implementation.

Approve unless there are serious gaps, contradictory steps, missing requirements from the spec, or tasks so vague they cannot be acted on.

## Output Format

## Plan Review

**Status:** Approved | Issues Found

**Issues:**

- [Task X, Step Y]: specific issue - why it matters for implementation

**Recommendations:**

- advisory suggestions that do not block approval
```

- [ ] **Step 4: Commit references**

```bash
git add plugins/docx-to-content/references
git commit -m "docs: add docx-to-content references and review gate"
```

---

## Task 11: Full Test Run and CEIS Regression Gate

**Files:**
- Modify only if tests reveal a real defect in a prior task.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: validated Phase 1 artifact set.

- [ ] **Step 1: Run full plugin test suite**

```bash
cd plugins/docx-to-content
pytest -v
```

Expected: PASS.

- [ ] **Step 2: Run the CEIS source through the three-skill flow**

Use the real source document path used by this repo:

```text
sourcedocuments/CEIS MANUAL - working version.docx
```

Expected artifact structure:

```text
analysis-report.json
conversion-plan.json
canonical-content/
  manifest.json
  validation.json
  chunks/
    chunk_001_*.md
    chunk_001_*.meta.json
  media/
rendered-output/
  index.md
  pages/
  renderer-validation.json
```

- [ ] **Step 3: Verify canonical validation result**

```bash
cat canonical-content/validation.json
```

Expected status: `PASS`, or documented `WARN` entries that do not block use.

- [ ] **Step 4: Verify renderer validation result**

```bash
cat rendered-output/renderer-validation.json
```

Expected status: `PASS`.

- [ ] **Step 5: Verify rendered index exists and links to pages**

```bash
test -f rendered-output/index.md
test -d rendered-output/pages
grep -n "pages/" rendered-output/index.md
```

Expected: index exists, pages folder exists, and index contains links into `pages/`.

- [ ] **Step 6: Commit final validation evidence**

```bash
git add plugins/docx-to-content output/ceis-manual
git commit -m "test: validate docx-to-content phase1 on CEIS manual"
```

---

## Self-Review

### Spec Coverage

- Three-skill flow is covered by Tasks 4, 5, 7, 8, and 9.
- Raw pandoc markdown as transitory is covered by Tasks 4, 8, 9, and 10.
- Canonical content chunks and metadata sidecars are covered by Tasks 5 and 6.
- Stable `chunk_id` generation is covered by Task 3.
- Manifest and validation records are covered by Task 6.
- Renderer contract and one concrete renderer are covered by Task 7.
- Renderer validation is covered by Task 7.
- Artifact evidence is covered by Tasks 8 and 11.
- CEIS regression fixture is covered by Tasks 8 and 11.
- Deferred future work is protected by Global Constraints and Skill docs.

### Unresolved Marker Scan

The plan avoids unresolved implementation markers and gives concrete file paths, interfaces, tests, commands, and expected results.

### Type Consistency

- `ConversionPlan`, `ChunkBoundary`, `ChunkMetadata`, `ManifestChunk`, and `Manifest` are defined in Task 3 and reused consistently.
- `chunk_id()` and `normalize_slug()` are defined in Task 3 and reused in Task 5.
- `build_conversion_plan()` is defined in Task 4 and reused in Task 8.
- `split_markdown_by_plan()` and `metadata_for_chunk()` are defined in Task 5 and reused in Task 8.
- `build_manifest()` and `write_json()` are defined in Task 6 and reused in Task 8.
- `RendererInput.from_folder()` and `render_multipage_markdown()` are defined in Task 7 and reused in Task 8.

---

## Execution Handoff

Plan complete and intended save path:

```text
docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan.md
```

Two execution options:

1. **Subagent-Driven recommended** — dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session using task-by-task checkpoints.

Recommended approach for this work: **Subagent-Driven**, because the plan has clear task boundaries, validation gates, and task-level commits.
