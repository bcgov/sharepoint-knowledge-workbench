"""
sharepoint_publish_plan.py
============================

Produces human-actionable publish/rollback PLANS for Markdown/ASPX artifacts and prior
publications -- never performs any SharePoint tenant I/O itself, matching this plugin's
established Phase 3 package-only architecture (see sharepoint_package.py's own module
docstring). Real automated tenant writes for this plugin remain gated behind Stage 3.4.3's
approved-write-identity decision (docs/vision/master-initiative-plan-workstreams-and-phases.md),
which is not yet approved -- this module does not attempt to bypass that gate.

A future authorized-write skill (not built here) would consume these plans once Stage 3.4.3 is
approved; today, a human executes the plan manually, same as sharepoint_package.py's existing
"human-performed upload" pattern (Stage 3.2.3).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


class PlanError(Exception):
    """Raised when a plan cannot be constructed from the given inputs."""


@dataclass
class PublishAction:
    source_path: str
    target_library: str
    target_folder: str
    target_filename: str

    def to_dict(self) -> dict:
        return {
            "source_path": self.source_path,
            "target_library": self.target_library,
            "target_folder": self.target_folder,
            "target_filename": self.target_filename,
        }


@dataclass
class PublishPlan:
    document_id: str
    actions: list = field(default_factory=list)  # list[PublishAction]

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "action_count": len(self.actions),
            "actions": [a.to_dict() for a in self.actions],
        }


def build_markdown_publish_plan(document_id: str, source_dir: Path, target_library: str,
                                 target_folder: str) -> PublishPlan:
    """Build a plan to publish rendered Markdown + media to a target library/folder.
    No tenant I/O -- reads only from the local source_dir."""
    source_dir = Path(source_dir)
    if not source_dir.exists():
        raise PlanError(f"source_dir '{source_dir}' does not exist -- nothing to plan.")

    actions = []
    for path in sorted(source_dir.rglob("*")):
        if path.is_file():
            rel = path.relative_to(source_dir)
            actions.append(PublishAction(
                source_path=str(path),
                target_library=target_library,
                target_folder=f"{target_folder}/{rel.parent}".rstrip("/."),
                target_filename=rel.name,
            ))

    if not actions:
        raise PlanError(f"source_dir '{source_dir}' contains no files -- refusing to build an empty plan.")

    return PublishPlan(document_id=document_id, actions=actions)


def build_aspx_publish_plan(document_id: str, source_dir: Path, target_site_relative_path: str) -> PublishPlan:
    """Build a plan to publish rendered ASPX/page artifacts. No tenant I/O. Per Phase 3.0 section
    15's confirmed finding, raw .aspx upload is blocked (Access denied) -- any future authorized-
    write execution of this plan must use the Add-PnPPage/Add-PnPPageTextPart API, not a raw file
    upload; this plan records the source content, not a specific upload mechanism."""
    source_dir = Path(source_dir)
    if not source_dir.exists():
        raise PlanError(f"source_dir '{source_dir}' does not exist -- nothing to plan.")

    actions = []
    for path in sorted(source_dir.glob("*.md")):
        actions.append(PublishAction(
            source_path=str(path),
            target_library="SitePages",
            target_folder=target_site_relative_path,
            target_filename=path.stem + ".aspx",
        ))

    if not actions:
        raise PlanError(f"source_dir '{source_dir}' contains no .md files to convert to page plan entries.")

    return PublishPlan(document_id=document_id, actions=actions)


@dataclass
class RollbackAction:
    target_url: str
    reason: str

    def to_dict(self) -> dict:
        return {"target_url": self.target_url, "reason": self.reason}


@dataclass
class RollbackPlan:
    document_id: str
    actions: list = field(default_factory=list)  # list[RollbackAction]

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "action_count": len(self.actions),
            "actions": [a.to_dict() for a in self.actions],
        }


def build_rollback_plan(document_id: str, previous_publish_plan: PublishPlan) -> RollbackPlan:
    """Build a rollback plan (what to remove) from a prior PublishPlan's recorded actions.
    Package-scoped: only reverses this document_id's own actions, never another document's."""
    if previous_publish_plan.document_id != document_id:
        raise PlanError(
            f"document_id mismatch: rollback requested for {document_id!r} but the supplied "
            f"publish plan is for {previous_publish_plan.document_id!r} -- refusing to build a "
            "cross-document rollback plan."
        )

    actions = [
        RollbackAction(
            target_url=f"{a.target_library}/{a.target_folder}/{a.target_filename}".replace("//", "/"),
            reason=f"reverses publish action from document {document_id}",
        )
        for a in previous_publish_plan.actions
    ]
    return RollbackPlan(document_id=document_id, actions=actions)
