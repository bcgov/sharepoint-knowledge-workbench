"""
sharepoint_upload.py
=====================

Phase 9 extraction (source: CMAT repository `sp-uploading-content` skill,
commit `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f` -- see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`).

Generic modern-page/asset upload primitive for SharePoint Online, adapted from
CMAT's proven `Add-PnPPage` / `Add-PnPPageTextPart` / `Publish-PnPPage` call
pattern (`scripts/upload/upload-modern-page-rest.ps1`,
`scripts/upload/upload-modern-page.ps1`) -- the same page-creation approach
this workbench already independently confirmed as the only working mechanism
on this tenant (`docs/research/research-experimentation/tenant-discovery/
field-note-sharepoint-write-capability-discovery.md` Section 15, referenced by
`publish-aspx-to-sharepoint`'s SKILL.md).

Matches this plugin's established Phase 3 package-only architecture
(`sharepoint_publish_plan.py`, `sharepoint_package.py`): this module performs
**zero SharePoint tenant I/O by default**. `upload_pages()` requires an
explicitly injected `uploader` callable -- without one it raises
`NotImplementedError` rather than silently no-op'ing or faking success, the
same connector-injection contract `workbench-setup`'s `config_setup.
test_connection()` already uses. No live PnP/REST client ships in this
module; callers wire in their own transport (e.g. a REST client built against
`_api/sitepages/pages` and `_api/web/getfolderbyserverrelativeurl(...)/files/
add`) only when they explicitly want a real upload to run. This preserves the
plugin's existing "no autonomous production tenant writes" property.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from sharepoint_publish_plan import PublishAction, PublishPlan


class UploadError(Exception):
    """Raised when an upload plan or action is invalid."""


@dataclass
class UploadResult:
    action: PublishAction
    success: bool
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "source_path": self.action.source_path,
            "target_library": self.action.target_library,
            "target_folder": self.action.target_folder,
            "target_filename": self.action.target_filename,
            "success": self.success,
            "detail": self.detail,
        }


# uploader(action) -> UploadResult
Uploader = Callable[[PublishAction], UploadResult]


def upload_pages(plan: PublishPlan, uploader: Optional[Uploader] = None) -> list:
    """Execute every action in `plan` via the injected `uploader` callable.

    Zero tenant I/O by default -- `uploader` must be supplied explicitly.
    Without one, raises `NotImplementedError` (same contract as
    `config_setup.test_connection`), since this module ships no live
    SharePoint REST/PnP client itself.

    Stops and raises `UploadError` on the first failed action rather than
    silently reporting partial success as full success -- callers that want
    partial-failure reporting should catch per-action results from a custom
    uploader instead of relying on an exception path.
    """
    if uploader is None:
        raise NotImplementedError(
            "upload_pages() requires a live SharePoint uploader to be injected "
            "explicitly via uploader=... -- this module does not ship one "
            "(zero tenant I/O by default, matching this plugin's package-only "
            "architecture and workbench-setup's connector-injection contract)"
        )

    if not plan.actions:
        raise UploadError(f"plan for document_id={plan.document_id!r} has no actions -- nothing to upload.")

    results = []
    for action in plan.actions:
        result = uploader(action)
        results.append(result)
        if not result.success:
            raise UploadError(
                f"upload failed for {action.source_path!r} -> "
                f"{action.target_library}/{action.target_folder}/{action.target_filename}: {result.detail}"
            )
    return results
