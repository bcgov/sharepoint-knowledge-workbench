"""
sharepoint_aspx.py
===================

Phase 6 Task 0.16 -- the `render-sharepoint-pages` skill. A second concrete
`Renderer` (see `renderers/protocol.py`), producing content staged for
SharePoint's supported modern-page creation API (`Add-PnPPage` +
`Add-PnPPageTextPart`), not a raw `.aspx` file upload -- Phase 3.0 Sec.15
(`docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md`)
confirmed raw `.aspx` upload to Site Pages is `Access denied`, a platform
boundary, while `Add-PnPPage`/`Add-PnPPageTextPart` with generated HTML
pushed and rendered correctly (`tools/phase-3-sharepoint-discovery/
push-aspx-experiment.ps1`).

This renderer performs zero SharePoint tenant I/O -- it produces a
package-only, publish-ready artifact set that a later, separate skill
(`sharepoint-site-build-and-publish`'s `plan-page-publication`, Task
0.15, a different plugin -- see that plugin's package-only,
zero-tenant-I/O design) is responsible for uploading:

    rendered-output/
      page-manifest.json   <- ordered list of pages: {chunk_id, title,
                               html_file, media_refs}, the shape
                               plan-page-publication needs to call
                               Add-PnPPage/Add-PnPPageTextPart per page
      pages/
        <chunk_id>.html     <- one HTML *fragment* (body content only,
                               suitable for a single PnPPageTextPart) per
                               chunk, converted from the chunk's
                               canonical Markdown via pandoc
      media/
        <asset files>        <- copied from the loaded package's media_dir,
                               same policy as multipage_markdown.py

Design decisions mirror multipage_markdown.py wherever the same
constraint applies (manifest/publication-map ordering, no DOCX/analysis
access, staged-not-promoted output) -- see that module's docstring for
the shared reasoning. Differences specific to this renderer:

- Markdown -> HTML conversion: via `pandoc -f markdown -t html`
  (subprocess), matching the confirmed working approach from Phase 3.0
  Sec.15's experiment. Requires `pandoc` on PATH -- already a
  repository-wide dependency, see DEPENDENCIES.md.
- Local link rewriting: `chunks/<chunk_id>.md` -> `<chunk_id>.html`
  (not `.md`), since SharePoint pages, not Markdown files, are the
  rendered artifact.
- Media references are left as page-relative `../media/<name>` paths
  in the generated HTML fragment (same directory depth as
  multipage_markdown.py's pages/) -- `plan-page-publication` is
  responsible for uploading each media file and rewriting these paths
  to tenant absolute URLs before calling `Add-PnPPageTextPart`, exactly
  the pattern `push-aspx-experiment.ps1` proved: local paths first,
  tenant-URL rewrite as a separate, later step performed by the code
  that actually has a live connection.
"""

import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote, urlsplit, urlunsplit

_THIS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _THIS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import atomic_output  # noqa: E402
import render_result as contracts  # noqa: E402
# Compatibility shim (Phase 4.5 Wave 4, retire per wave-1-decisions.json):
from canonical_schema import canonical_package as _canonical_contracts  # noqa: E402

RENDERER_VERSION = "0.1.0"

# Matches `[text](target)` markdown link syntax, excluding image syntax --
# same pattern multipage_markdown.py uses, kept independent per this
# plugin's flat-scripts, no-cross-file-coupling convention.
_LINK_REF = re.compile(r"(?<!!)(\[[^\]]*\]\()([^)]+)(\))")
_IMG_SRC = re.compile(r'src="([^"]+)"')

_LOCAL_LINK_PREFIX = "chunks/"


class PandocConversionError(Exception):
    """Raised when pandoc is unavailable or fails to convert a chunk's
    Markdown to an HTML fragment."""


def _rewrite_local_links(content: str, known_chunk_ids: set) -> str:
    """Rewrite `[text](chunks/<chunk_id>.md)` to `[text](<chunk_id>.html)`
    -- a page-relative link to that chunk's rendered sibling page. Same
    policy as multipage_markdown._rewrite_local_links, but targeting
    `.html` instead of `.md` since this renderer's pages are HTML
    fragments, not Markdown files. Preserves query parameters and fragments."""

    def _replace(match: "re.Match") -> str:
        prefix, raw_target, suffix = match.group(1), match.group(2), match.group(3)
        if raw_target.startswith(("http://", "https://", "mailto:")):
            return match.group(0)
        u = urlsplit(raw_target)
        if u.scheme or u.netloc:
            return match.group(0)
        decoded_path = unquote(u.path)
        if not decoded_path.startswith(_LOCAL_LINK_PREFIX):
            return match.group(0)
        chunk_id = PurePosixPath(decoded_path).stem
        if chunk_id not in known_chunk_ids:
            return match.group(0)
        new_path = f"{quote(chunk_id)}.html"
        new_target = urlunsplit(("", "", new_path, u.query, u.fragment))
        return f"{prefix}{new_target}{suffix}"

    return _LINK_REF.sub(_replace, content)


def _markdown_to_html_fragment(markdown_text: str) -> str:
    """Convert `markdown_text` to a bare HTML fragment (no `<html>`/
    `<head>`/`<body>` wrapper -- a single PnPPageTextPart's content) via
    pandoc."""
    try:
        proc = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "html"],
            input=markdown_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except FileNotFoundError as exc:
        raise PandocConversionError("pandoc not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        raise PandocConversionError(f"pandoc failed: {exc.stderr}") from exc
    return proc.stdout


class SharePointAspxRenderer:
    """SharePoint modern-page-ready `Renderer` (structurally satisfies
    `renderers.protocol.Renderer` -- see
    `tests/rendering/unit/test_sharepoint_aspx.py::test_renderer_satisfies_protocol`).
    One HTML fragment per chunk under `pages/`, a `page-manifest.json`
    describing page order/titles/media for the later publish step, and a
    local copy of the canonical package's media."""

    name = "sharepoint-aspx"
    supported_manifest_versions = frozenset({_canonical_contracts.MANIFEST_SCHEMA_VERSION})

    def render(self, package, output_dir: Path, template: "Any | None" = None) -> "contracts.RenderResult":
        output_dir = Path(output_dir)
        pages_dir = output_dir / "pages"
        media_dir = output_dir / "media"
        pages_dir.mkdir(parents=True, exist_ok=True)
        media_dir.mkdir(parents=True, exist_ok=True)

        output_files = []

        # Media: identical copy policy to multipage_markdown.py -- copy
        # every file from the already-loaded package's media_dir, never
        # re-read canonical-content/media/ via any other path.
        for media_file in sorted(package.media_dir.glob("*")):
            if not media_file.is_file():
                continue
            destination = media_dir / media_file.name
            destination.write_bytes(media_file.read_bytes())
            output_files.append(str(destination))

        known_chunk_ids = {chunk.metadata.chunk_id for chunk in package.chunks}

        # Render order: publication map (grouped strategy) takes explicit
        # precedence over manifest order -- same policy as
        # multipage_markdown.py.
        if package.publication_map is not None:
            chunk_by_id = {chunk.metadata.chunk_id: chunk for chunk in package.chunks}
            ordered_entries = sorted(package.publication_map.entries, key=lambda e: e.order)
            ordered_chunks = [chunk_by_id[e.chunk_id] for e in ordered_entries]
        else:
            ordered_chunks = package.chunks

        page_manifest_entries = []
        for chunk in ordered_chunks:
            rewritten_md = _rewrite_local_links(chunk.content, known_chunk_ids)
            html_fragment = _markdown_to_html_fragment(rewritten_md)
            if template is not None:
                title = chunk.metadata.topic or chunk.metadata.title or chunk.metadata.chunk_id
                tmpl_text = getattr(template, "content", str(template))
                final_html = (
                    tmpl_text
                    .replace("{{title}}", title)
                    .replace("{{body}}", html_fragment)
                    .replace("{{media_dir}}", "../media")
                )
            else:
                final_html = html_fragment

            page_path = pages_dir / f"{chunk.metadata.chunk_id}.html"
            page_path.write_text(final_html, encoding="utf-8")
            output_files.append(str(page_path))

            media_refs = sorted({
                unquote(src) for src in _IMG_SRC.findall(final_html)
                if not src.startswith(("http://", "https://"))
            })

            page_manifest_entries.append({
                "chunk_id": chunk.metadata.chunk_id,
                "title": chunk.metadata.topic,
                "html_file": f"pages/{chunk.metadata.chunk_id}.html",
                "media_refs": media_refs,
            })

        page_manifest_path = output_dir / "page-manifest.json"
        page_manifest_path.write_text(json.dumps(
            {"schema_version": "1.0", "pages": page_manifest_entries},
            indent=2, sort_keys=True,
        ))
        output_files.append(str(page_manifest_path))

        return contracts.RenderResult(
            renderer_name=self.name,
            renderer_version=RENDERER_VERSION,
            source_content_sha256=package.manifest.source.sha256,
            output_files=output_files,
            status="PASS",
            errors=[],
            warnings=[],
        )


def render_to_staging(package, output_root: Path, renderer: "SharePointAspxRenderer | None" = None):
    """Render `package` into a fresh staging directory under
    `output_root` (via `atomic_output.create_staging_dir`) and return
    `(RenderResult, staging_dir)` -- UNPROMOTED. The validator extension
    in `renderers/validate_rendered.py` (Task 0.16's
    `validate-rendered-output` skill) is expected to validate
    `staging_dir` and call `atomic_output.promote(staging_dir, final_dir)`
    itself once that validation passes -- same split as
    multipage_markdown.render_to_staging."""
    renderer = renderer or SharePointAspxRenderer()
    staging_dir = atomic_output.create_staging_dir(output_root, prefix="rendered-aspx-staging")
    result = renderer.render(package, staging_dir)
    return result, staging_dir
