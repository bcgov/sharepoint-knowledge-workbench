"""
structured_content_assembly.py
================================

Public interface for the `structured-content-assembly` plugin (renamed
from `canonical-knowledge` in the post-Wave-9 naming refactor): consumes
a *confirmed* `analysis-plan` v1 dict (produced by
`document-structure-analysis`'s `recommend_from_normalized` + a human
confirmation step) and the original source `.docx`, and produces
`canonical-package` + `publication-map` v1 artifacts via
`convert.convert_and_promote`.

This plugin is the sole producer of both contracts;
`structured-content-rendering` never imports this module directly -- it
consumes the promoted package this function's caller writes to
`output_dir`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import convert  # noqa: E402
from canonical_schema.analysis_plan import ConversionPlan  # noqa: E402


def build_canonical_package(analysis_plan: dict, source_dir: Path, output_dir: Path) -> dict:
    """Build, validate, and atomically promote a canonical-content package
    from `analysis_plan` (a confirmed `analysis-plan` v1 dict) and
    `source_dir` (the source `.docx` file's path), writing the promoted
    package and its `publication-map.json` (for the "grouped" strategy)
    under `output_dir`.

    Raises `plans.PlanVerificationError` if `analysis_plan`'s
    `confirmation.status` is not `"confirmed"`, if the source file no
    longer matches the plan's recorded fingerprint, or if the plan's
    content was tampered with after confirmation.

    Returns a dict: `{"manifest": <Manifest.to_dict()>, "validation_report":
    <ValidationReport.to_dict()>, "promoted": bool, "package_dir": str}`.
    """
    plan = ConversionPlan.from_dict(analysis_plan)
    manifest, validation_report, promoted, package_dir = convert.convert_and_promote(
        Path(source_dir), plan, Path(output_dir)
    )
    return {
        "manifest": manifest.to_dict(),
        "validation_report": validation_report.to_dict(),
        "promoted": promoted,
        "package_dir": str(package_dir),
    }
