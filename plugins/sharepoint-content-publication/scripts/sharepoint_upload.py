"""
sharepoint_upload.py
=====================

Executes a `PublishPlan` (a list of file-upload actions, built by
`sharepoint_publish_plan.py`) against SharePoint Online by delegating each
action to a caller-supplied `uploader` callable.

Inputs:
    - `plan: PublishPlan` -- the actions to execute (`document_id`, `actions`).
    - `uploader: Uploader | None` -- `Callable[[PublishAction], UploadResult]`.
      Required. This module ships no live PnP/REST client itself and performs
      zero SharePoint tenant I/O on its own -- without an `uploader`,
      `upload_pages()` raises `NotImplementedError` rather than silently
      no-op'ing or faking success. A real `uploader` should create/publish
      pages via the modern-page API (`Add-PnPPage` / `Add-PnPPageTextPart` /
      `Publish-PnPPage` or the equivalent REST calls), not a raw file upload
      -- raw `.aspx` upload is not a supported path on SharePoint Online.

Outputs:
    - `list[UploadResult]`, one per action, in plan order.

Preconditions:
    - `plan.actions` must be non-empty (`UploadError` if empty).
    - Stops and raises `UploadError` on the first action whose `uploader` call
      reports `success=False`, rather than continuing and reporting partial
      success as full success.

Example:
    from sharepoint_publish_plan import build_markdown_publish_plan
    from sharepoint_upload import upload_pages, UploadResult

    plan = build_markdown_publish_plan(document_id, source_dir, library, folder)

    def my_uploader(action):
        # call Add-PnPPage / Add-PnPPageTextPart / Publish-PnPPage (or REST)
        return UploadResult(action=action, success=True)

    results = upload_pages(plan, uploader=my_uploader)
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
