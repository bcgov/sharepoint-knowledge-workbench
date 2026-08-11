"""
spo_page_copy_plan.py
=====================

Builds a tenant-safe plan for promoting an existing SharePoint Online Site Page
from one SPO site to another. This module performs no SharePoint tenant I/O.

Key Input Dependencies:
- Caller-supplied source SharePoint site URL, target SharePoint site URL, and
  `.aspx` page name.
- No files, network connections, SharePoint tenant credentials, or external
  Python packages are required.

Usage:
- Call build_copy_page_plan(...) to produce a JSON-serializable plan for human
  review and execution outside this module.

Index:
- CopyPagePlanError: invalid page-copy plan request.
- CopyPagePlanRequest: normalized immutable request values.
- _require_non_empty: shared required-string validator.
- build_copy_page_plan: public plan builder.
"""
from __future__ import annotations

from dataclasses import dataclass


# Exception type used by callers/tests to distinguish validation failures from
# unexpected runtime failures.
class CopyPagePlanError(ValueError):
    """Raised when a requested SPO page copy plan is invalid."""


# Immutable request object keeps normalized inputs together while preserving a
# plain-dict public output contract.
@dataclass(frozen=True)
class CopyPagePlanRequest:
    """Normalized inputs for an SPO page-copy plan."""

    source_site_url: str
    target_site_url: str
    page_name: str
    page_library: str = "Site Pages"
    overwrite: bool = False


# Shared validator keeps public plan-building errors consistent across fields.
def _require_non_empty(value: str, field_name: str) -> str:
    """Return a stripped required string or raise CopyPagePlanError."""

    cleaned = (value or "").strip()
    if not cleaned:
        raise CopyPagePlanError(f"{field_name} is required.")
    return cleaned


# Public helper used by the copy-spo-page-between-sites skill and tests.
def build_copy_page_plan(
    source_site_url: str,
    target_site_url: str,
    page_name: str,
    page_library: str = "Site Pages",
    overwrite: bool = False,
) -> dict:
    """Return a JSON-serializable plan for copying an SPO Site Page.

    The plan deliberately avoids raw `.aspx` file upload guidance. For modern
    SPO pages, use page APIs such as Add-PnPPage/Add-PnPPageTextPart or a
    reviewed PnP page transform/export/import flow rather than Add-PnPFile.
    """
    request = CopyPagePlanRequest(
        source_site_url=_require_non_empty(source_site_url, "source_site_url"),
        target_site_url=_require_non_empty(target_site_url, "target_site_url"),
        page_name=_require_non_empty(page_name, "page_name"),
        page_library=_require_non_empty(page_library, "page_library"),
        overwrite=overwrite,
    )

    if not request.page_name.lower().endswith(".aspx"):
        raise CopyPagePlanError("page_name must end with .aspx.")

    return {
        "operation": "copy-spo-page",
        "source": {
            "site_url": request.source_site_url,
            "library": request.page_library,
        },
        "target": {
            "site_url": request.target_site_url,
            "library": request.page_library,
            "overwrite": request.overwrite,
        },
        "page": {
            "name": request.page_name,
            "library": request.page_library,
        },
        "safety": {
            "tenant_io": "none",
            "raw_aspx_upload": "avoid",
            "human_runs_write_command": True,
        },
        "recommended_execution": (
            "Use reviewed SPO page APIs/PnP page commands for modern page promotion "
            "(for example Add-PnPPage/Add-PnPPageTextPart/Set-PnPPage metadata), "
            "not raw Add-PnPFile .aspx upload."
        ),
    }
