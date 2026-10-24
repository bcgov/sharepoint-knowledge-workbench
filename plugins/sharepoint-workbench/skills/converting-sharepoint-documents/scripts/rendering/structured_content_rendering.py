"""structured_content_rendering.py
===============================

Purpose:
    Public interface for the `structured-content-rendering` plugin: consumes an already-promoted `canonical-package` (and, for the "grouped" strategy, its `publication-map`) from disk and produces a validated, atomically-promoted `rendered-output-profile` (multipage markdown).

Key Input Dependencies:
    - sys
    - pathlib
    - canonical_package
    - renderers

Public interface for the `structured-content-rendering` plugin: consumes an
already-promoted `canonical-package` (and, for the "grouped" strategy,
its `publication-map`) from disk and produces a validated,
atomically-promoted `rendered-output-profile` (multipage markdown).

This plugin is the sole producer of `rendered-output-profile`;
`structured-content-assembly` never imports this module -- it only writes the
canonical package this function's caller loads.

Key Functions Index:
    - render()"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import canonical_package  # noqa: E402
from renderers import validate_rendered  # noqa: E402


def render(package_dir: Path, output_dir: Path) -> dict:
    """Load the accepted canonical package at `package_dir`, render it to
    a fresh staging directory under `output_dir`, validate the rendered
    output, and atomically promote it to `output_dir / "rendered-output"`
    only if validation status is PASS.

    Raises `canonical_package.CanonicalPackageError` if `package_dir`
    does not hold a valid, accepted canonical package.

    Returns a dict: `{"render_result": <RenderResult.to_dict()>,
    "validation_report": <ValidationReport.to_dict()>, "promoted": bool,
    "output_dir": str}`.
    """
    package = canonical_package.CanonicalPackage.load(Path(package_dir))
    result, report, promoted, final_dir = validate_rendered.render_and_promote(
        package, Path(output_dir)
    )
    return {
        "render_result": result.to_dict(),
        "validation_report": report.to_dict(),
        "promoted": promoted,
        "output_dir": str(final_dir),
    }
