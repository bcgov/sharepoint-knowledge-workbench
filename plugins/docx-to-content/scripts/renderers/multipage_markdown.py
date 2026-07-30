"""
multipage_markdown.py
======================

Task 13 -- the first concrete `Renderer` (spec Section 7.3, "render-content";
Section 8, "Renderer Protocol"): multipage Markdown output. Proves the
renderer architecture built in Task 12 (`renderers/protocol.py`,
`package.CanonicalPackage.load()`) works end to end with a real renderer.

    rendered-output/
      index.md
      pages/
        <chunk_id>.md   <- one page per chunk, chunk_id-named to mirror
                            canonical-content's chunks/<chunk_id>.md
      media/
        <asset files>   <- copied from the loaded package's media/, never
                            left pointing back at canonical-content/media/

Design decisions (see spec quotes in the Task 13 brief for the exact
requirements each of these satisfies):

- Manifest ordering: pages and the index are built by iterating
  `package.chunks` (itself `CanonicalPackage.load()`'s manifest-ordered
  list) directly, via a single `for` loop -- never sorted, never
  `os.listdir()`/`glob()`-ordered.

- Single vs chunked: no special-casing. A single-strategy package is just
  a `CanonicalPackage` with one chunk in `package.chunks`; the exact same
  loop produces one page and a one-entry index.

- Hierarchical index.md: chunks are listed as a nested markdown list built
  from each chunk's `source_heading_path`. Consecutive chunks sharing a
  path prefix (e.g. two chunks both under "Section Alpha") share that
  prefix's group line instead of repeating it -- see `_build_index`.

- Media: rendered pages live under `pages/`, exactly as deep below the
  rendered-output root as `chunks/` is below the canonical-content root,
  with a sibling `media/` dir in both cases. Canonical content already
  rewrites image refs to `../media/<name>` (Task 9, `package.py`) -- since
  the directory depth is identical, that relative form is copied through
  unchanged; only the underlying files are copied (from the loaded
  `CanonicalPackage`'s `media_dir`, never by re-reading
  canonical-content/media/ independently once `package.media_dir` was
  already handed to us).

- Internal links: any markdown link target of the form `chunks/<chunk_id>.md`
  (the canonical package's local-link convention -- see
  `contracts.ChunkMetadata.local_links` / `validate_canonical.py`) is
  rewritten to `<chunk_id>.md`, a page-relative link to that chunk's
  rendered sibling page under `pages/`. External links (`http(s)://`),
  anchors (`#...`), and `mailto:` links are left untouched.

- No DOCX/analysis/plan access: `render()`'s only inputs are the
  `CanonicalPackage` object (already fully loaded/vetted by
  `CanonicalPackage.load()`) and `output_dir` -- this module never opens a
  `.docx`, an `analysis/` directory, or a `conversion-plan*.json` file,
  and never imports `analyze_structure`/`plans`/`convert`. See
  `tests/unit/test_multipage_markdown.py`'s source-inspection test.

- Staging / promotion: per the brief, this task does NOT build the render
  validator (Task 14's job) -- "validate then promote" cannot be honored
  without a validator to run. `render_to_staging()` therefore renders into
  a fresh staging directory (via `atomic_output.create_staging_dir`, the
  same reusable primitive Task 11 built) and returns it UNPROMOTED. Task
  14 is expected to run its render validator against this staging dir and
  call `atomic_output.promote()` itself once validation passes.
"""

import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote

_THIS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _THIS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import atomic_output  # noqa: E402
import contracts  # noqa: E402

RENDERER_VERSION = "0.1.0"

# Matches `[text](target)` markdown link syntax, excluding image syntax
# (`![alt](target)`, which media-ref rewriting/copying already handles as
# plain file copies -- links are the only thing this module rewrites).
_LINK_REF = re.compile(r"(?<!!)(\[[^\]]*\]\()([^)]+)(\))")

_LOCAL_LINK_PREFIX = "chunks/"


def _rewrite_local_links(content: str, known_chunk_ids: set) -> str:
    """Rewrite any `[text](chunks/<chunk_id>.md)`-shaped link target (the
    canonical package's local-link convention) to `[text](<chunk_id>.md)`
    -- a page-relative link to that chunk's rendered sibling page under
    `pages/`. Links to a chunk_id not present in this render (should not
    happen for an already-vetted package, but left untouched rather than
    guessed at) and all other link forms (external, anchor, mailto) are
    left exactly as written."""

    def _replace(match: "re.Match") -> str:
        prefix, raw_target, suffix = match.group(1), match.group(2), match.group(3)
        if raw_target.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        decoded = unquote(raw_target)
        if not decoded.startswith(_LOCAL_LINK_PREFIX):
            return match.group(0)
        chunk_id = PurePosixPath(decoded).stem
        if chunk_id not in known_chunk_ids:
            return match.group(0)
        return f"{prefix}{quote(chunk_id)}.md{suffix}"

    return _LINK_REF.sub(_replace, content)


def _build_index(chunks: list) -> str:
    """Build a hierarchical, path-aware `index.md` from `chunks` (already
    in manifest/render order). Each chunk's `source_heading_path` becomes
    a nested list entry; consecutive chunks sharing a path prefix share
    that prefix's group line rather than repeating it, so the index
    visibly reflects heading hierarchy depth instead of being a flat,
    chunk_id-labeled list."""
    lines = ["# Index", ""]
    previous_path: list = []

    for chunk in chunks:
        meta = chunk.metadata
        path = list(meta.source_heading_path) or [meta.topic]

        common = 0
        while (
            common < len(previous_path)
            and common < len(path) - 1
            and previous_path[common] == path[common]
        ):
            common += 1

        for depth in range(common, len(path) - 1):
            lines.append(f"{'  ' * depth}- {path[depth]}")

        leaf_depth = len(path) - 1
        link_target = f"pages/{quote(meta.chunk_id)}.md"
        lines.append(f"{'  ' * leaf_depth}- [{path[-1]}]({link_target})")

        previous_path = path

    lines.append("")
    return "\n".join(lines)


class MultipageMarkdownRenderer:
    """Multipage Markdown `Renderer` (structurally satisfies
    `renderers.protocol.Renderer` -- see
    `tests/unit/test_multipage_markdown.py::test_renderer_satisfies_protocol`).
    One page per chunk under `pages/`, a hierarchical `index.md`, and a
    local copy of the canonical package's media."""

    name = "multipage-markdown"
    supported_manifest_versions = frozenset({contracts.MANIFEST_SCHEMA_VERSION})

    def render(self, package, output_dir: Path) -> "contracts.RenderResult":
        output_dir = Path(output_dir)
        pages_dir = output_dir / "pages"
        media_dir = output_dir / "media"
        pages_dir.mkdir(parents=True, exist_ok=True)
        media_dir.mkdir(parents=True, exist_ok=True)

        output_files = []

        # Media: copy every file from the already-loaded package's
        # media_dir -- never re-read canonical-content/media/ via any
        # other path, and never left pointing back at it.
        for media_file in sorted(package.media_dir.glob("*")):
            if not media_file.is_file():
                continue
            destination = media_dir / media_file.name
            destination.write_bytes(media_file.read_bytes())
            output_files.append(str(destination))

        known_chunk_ids = {chunk.metadata.chunk_id for chunk in package.chunks}

        # Render order: the publication map (when present -- "grouped"
        # strategy) gives explicit, directory-order-independent topic
        # order; otherwise fall back to manifest order (package.chunks is
        # already manifest-ordered by CanonicalPackage.load()), unchanged
        # from before publication maps existed.
        if package.publication_map is not None:
            chunk_by_id = {chunk.metadata.chunk_id: chunk for chunk in package.chunks}
            ordered_entries = sorted(package.publication_map.entries, key=lambda e: e.order)
            ordered_chunks = [chunk_by_id[e.chunk_id] for e in ordered_entries]
        else:
            ordered_chunks = package.chunks

        # One page per chunk, in render order.
        for chunk in ordered_chunks:
            content = _rewrite_local_links(chunk.content, known_chunk_ids)
            page_path = pages_dir / f"{chunk.metadata.chunk_id}.md"
            page_path.write_text(content)
            output_files.append(str(page_path))

        index_path = output_dir / "index.md"
        index_path.write_text(_build_index(ordered_chunks))
        output_files.append(str(index_path))

        return contracts.RenderResult(
            renderer_name=self.name,
            renderer_version=RENDERER_VERSION,
            source_content_sha256=package.manifest.source.sha256,
            output_files=output_files,
            status="PASS",
            errors=[],
            warnings=[],
        )


def render_to_staging(package, output_root: Path, renderer: "MultipageMarkdownRenderer | None" = None):
    """Render `package` into a fresh staging directory under
    `output_root` (via `atomic_output.create_staging_dir`) and return
    `(RenderResult, staging_dir)` -- UNPROMOTED. Task 14's render
    validator is expected to validate `staging_dir` and call
    `atomic_output.promote(staging_dir, final_dir)` itself once that
    validation passes; this function deliberately stops short of
    promoting, since there is no validator yet to gate it on (see module
    docstring)."""
    renderer = renderer or MultipageMarkdownRenderer()
    staging_dir = atomic_output.create_staging_dir(output_root, prefix="rendered-staging")
    result = renderer.render(package, staging_dir)
    return result, staging_dir
