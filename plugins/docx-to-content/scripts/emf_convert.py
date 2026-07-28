#!/usr/bin/env python
"""
emf_convert.py
==============

Converts legacy Enhanced Metafile (.emf) / Windows Metafile (.wmf) media
extracted from an old Word document into .png, using the LibreOffice
`soffice` CLI. Browsers, GitHub, and most standard markdown viewers cannot
render .emf/.wmf directly, so these are converted at cleanup time and any
markdown image reference pointing at the old file needs to be rewritten to
the new .png (rewriting itself is the caller's job — this module only
performs the conversion and reports the old->new filename mapping).

Key Input Dependencies:
    - `soffice` (LibreOffice) must be on PATH. Verified present at version
      26.2.5.2 in this project's environment (see Task 0 baseline / DEPENDENCIES.md).

Function Index:
    - convert_legacy_media(media_dir: Path) -> dict[str, str]
        Converts every .emf/.wmf file directly inside `media_dir` to .png
        via `soffice --headless --convert-to png --outdir <dir> <input>`,
        returning a mapping of old filename -> new filename for reference
        rewriting.

Usage:
    from emf_convert import convert_legacy_media
    renamed = convert_legacy_media(Path("output/my-doc/images/media"))
"""

import subprocess
from pathlib import Path

_LEGACY_EXTENSIONS = {".emf", ".wmf"}


def convert_legacy_media(media_dir: Path) -> dict[str, str]:
    """Convert all .emf/.wmf files directly under `media_dir` to .png.

    Returns a mapping of `{old_filename: new_filename}` for every legacy
    file found, whether or not the conversion succeeded (a failed
    conversion is a caller-visible problem, not something to hide by
    omitting it from the mapping) — callers that need strict
    success/failure semantics should check that the new file actually
    exists on disk.

    If `media_dir` does not exist or contains no .emf/.wmf files, returns
    an empty mapping without invoking `soffice`.
    """
    media_dir = Path(media_dir)
    if not media_dir.is_dir():
        return {}

    legacy_files = sorted(
        p for p in media_dir.iterdir()
        if p.is_file() and p.suffix.lower() in _LEGACY_EXTENSIONS
    )
    if not legacy_files:
        return {}

    mapping: dict[str, str] = {}
    for legacy_path in legacy_files:
        new_name = legacy_path.stem + ".png"
        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to", "png",
                "--outdir", str(media_dir),
                str(legacy_path),
            ],
            check=False,
            capture_output=True,
        )
        mapping[legacy_path.name] = new_name

    return mapping
