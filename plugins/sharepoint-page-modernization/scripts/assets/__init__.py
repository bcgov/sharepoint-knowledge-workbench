"""
assets
======

Packaged, non-Python data assets for `sharepoint-page-modernization`.

This directory is a real Python package (it has this `__init__.py`) purely so
setuptools recognises it and ships its data files in a built wheel. A plain,
non-package directory under `package-dir` is silently dropped from a wheel --
`pip install -e` never surfaces that, only an isolated wheel-install check
does (the packaging defect Phase 6 caught for `structured-content-rendering`).

Resolve an asset with `assets_dir()` rather than hardcoding a relative path,
so the same code works from an editable install, a wheel install, and a
skill-directory symlink.
"""

from pathlib import Path

__all__ = ["assets_dir", "asset_path"]


def assets_dir() -> Path:
    """Absolute path to this packaged assets directory."""
    return Path(__file__).resolve().parent


def asset_path(name: str) -> Path:
    """
    Absolute path to a named packaged asset.

    Args:
        name: File name inside this package, e.g. "layout-rules.json".

    Returns:
        Absolute `Path` to the asset (existence is NOT asserted here --
        callers report a missing asset through their own outcome contract).
    """
    return assets_dir() / name
