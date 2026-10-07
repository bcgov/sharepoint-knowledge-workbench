"""extraction.py
=============

Purpose:
    Public interface for the `source-document-extraction` plugin: runs pandoc once against a real source `.docx` and produces a `normalized-source-document` v1 dict, validated against this plugin's own `schema.normalized_source_document` module.

Key Input Dependencies:
    - hashlib
    - subprocess
    - sys
    - pathlib
    - dependencies
    - schema.normalized_source_document
    - heading_parsing

Public interface for the `source-document-extraction` plugin: runs pandoc
once against a real source `.docx` and produces a `normalized-source-document`
v1 dict, validated against this plugin's own `schema.normalized_source_document`
module. This plugin is the sole producer of that contract; structured-content-assembly
and structured-content-rendering never import this module directly -- they consume
the dict this function returns.

Key Functions Index:
    - _run_pandoc_raw()
    - extract_and_normalize()"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import dependencies  # noqa: E402
from schema.normalized_source_document import validate as validate_normalized_source_document  # noqa: E402
from heading_parsing import (  # noqa: E402
    _counts_by_level,
    _image_stats,
    _repeated_heading_texts,
    _repeated_paths,
    compute_statistics,
    detect_defect_signals,
    detect_raw_toc,
    parse_headings,
)


def _run_pandoc_raw(source: Path, raw_dir: Path) -> Path:
    """Run pandoc once against `source`, extracting markdown + media into
    `raw_dir`, and return the path to the extracted markdown file."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    media_dir = raw_dir / "media"
    extracted_md = raw_dir / "extracted.md"
    subprocess.run(
        [
            "pandoc",
            "-t", "markdown",
            f"--extract-media={media_dir}",
            "--wrap=none",
            str(source),
            "-o", str(extracted_md),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    # extract-media only creates the directory if there is at least one
    # media file; downstream consumers expect raw/media to always exist.
    media_dir.mkdir(parents=True, exist_ok=True)
    return extracted_md


def extract_and_normalize(source: Path, output_dir: Path) -> dict:
    """Extract `source` via pandoc into `output_dir/raw/` and produce a
    `normalized-source-document` v1 dict: raw markdown text, media file
    list, source content hash, and the source-level observations
    (heading structure, statistics, defect signals) that
    `document-structure-analysis` consumes without re-parsing.

    Raises FileNotFoundError if `source` does not exist, and
    `dependencies.MissingDependencyError` if `pandoc` is not on PATH.
    """
    source = Path(source)
    output_dir = Path(output_dir)

    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"source file not found: {source}")

    pandoc_status = dependencies.probe_pandoc()
    if not pandoc_status.available:
        raise dependencies.MissingDependencyError("pandoc")

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    extracted_md_path = _run_pandoc_raw(source, raw_dir)
    markdown_text = extracted_md_path.read_text()

    source_content_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()

    media_dir = raw_dir / "media"
    media_files = sorted(
        str(p.relative_to(media_dir)) for p in media_dir.rglob("*") if p.is_file()
    )

    headings = parse_headings(markdown_text)

    normalized = {
        "schema_version": "v1",
        "source_content_sha256": source_content_sha256,
        "markdown_text": markdown_text,
        "media_files": media_files,
        "source_path": str(source),
        "source_size_bytes": source.stat().st_size,
        "dependencies": {
            "pandoc": {
                "available": pandoc_status.available,
                "version": pandoc_status.version,
                "path": pandoc_status.path,
            },
        },
        "headings": headings,
        "heading_counts_by_level": _counts_by_level(headings),
        "repeated_heading_texts": _repeated_heading_texts(headings),
        "repeated_heading_paths": [list(p) for p in _repeated_paths(headings).keys()],
        "images": _image_stats(media_dir),
        "raw_toc_detected": detect_raw_toc(markdown_text),
        "defect_signals": detect_defect_signals(markdown_text),
        "statistics": compute_statistics(markdown_text),
    }
    validate_normalized_source_document(normalized)
    return normalized
