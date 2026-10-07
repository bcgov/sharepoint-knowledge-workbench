"""
sharepoint_publish_plan.py
============================

Purpose:
Produces human-actionable publish/rollback PLANS for Markdown/ASPX artifacts and prior
publications -- never performs any SharePoint tenant I/O itself, matching this plugin's
established Phase 3 package-only architecture (see sharepoint_package.py's own module
docstring). Real automated tenant writes for this plugin remain gated behind Stage 3.4.3's
approved-write-identity decision (docs/vision/master-initiative-plan-workstreams-and-phases.md),
which is not yet approved -- this module does not attempt to bypass that gate.

A future authorized-write skill (not built here) would consume these plans once Stage 3.4.3 is
approved; today, a human executes the plan manually, same as sharepoint_package.py's existing
"human-performed upload" pattern (Stage 3.2.3).

Key Input Dependencies:
    - renderer output directory containing page-manifest.json and HTML fragments
    - local Markdown/ASPX source directory for legacy publish-plan functions
    - standard-library json and pathlib

Function Index:
    PublishAction.to_dict, PublishPlan.to_dict, build_markdown_publish_plan,
    build_aspx_publish_plan, _safe_relative, _load_render_manifest,
    _page_action_from_manifest, _manifest_chunk_id, _manifest_media_refs,
    build_page_publish_plan_from_render,
    RollbackAction.to_dict, RollbackPlan.to_dict, build_rollback_plan
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath


class PlanError(Exception):
    """Raised when a plan cannot be constructed from the given inputs."""


@dataclass
class PublishAction:
    source_path: str
    target_library: str
    target_folder: str
    target_filename: str
    title: str = ""
    media_refs: list = field(default_factory=list)  # page-relative media paths the fragment still references

    def to_dict(self) -> dict:
        """Serialize required publish fields and optional page metadata."""
        data = {
            "source_path": self.source_path,
            "target_library": self.target_library,
            "target_folder": self.target_folder,
            "target_filename": self.target_filename,
        }
        # optional keys are emitted only when set, so Markdown-flow plans keep their original shape
        if self.title:
            data["title"] = self.title
        if self.media_refs:
            data["media_refs"] = list(self.media_refs)
        return data


@dataclass
class PublishPlan:
    document_id: str
    actions: list = field(default_factory=list)  # list[PublishAction]
    # What every action's source_path contains: "html-fragment" (renderer output; the only format spo-publish-modern-page.ps1
    # accepts), "markdown" (the legacy Markdown->page plan; the HTML executor refuses it), or "" (unspecified/legacy).
    source_format: str = ""

    def to_dict(self) -> dict:
        """Serialize a publish plan while omitting legacy-empty source_format."""
        data = {
            "document_id": self.document_id,
            "action_count": len(self.actions),
            "actions": [a.to_dict() for a in self.actions],
        }
        if self.source_format:
            data["source_format"] = self.source_format
        return data


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

    # Source files are Markdown. spo-publish-modern-page.ps1 publishes HTML fragments and refuses this plan; use
    # build_page_publish_plan_from_render for the renderer's real output.
    return PublishPlan(document_id=document_id, actions=actions, source_format="markdown")


MANIFEST_NAME = "page-manifest.json"
SUPPORTED_MANIFEST_VERSIONS = frozenset({"1.0"})


def _safe_relative(value, what: str) -> PurePosixPath:
    """Validate one manifest path as a relative path without traversal."""
    if not isinstance(value, str) or not value.strip():
        raise PlanError(f"{what} must be a non-empty string, got {value!r}.")
    rel = PurePosixPath(value.replace("\\", "/"))
    if rel.is_absolute() or ".." in rel.parts or (rel.parts and ":" in rel.parts[0]):
        raise PlanError(f"{what} {value!r} must be a relative path inside the rendered output directory.")
    return rel


# Validate and read the renderer manifest before validating individual pages.
def _load_render_manifest(rendered_dir: Path) -> list[dict]:
    """Load and validate the renderer manifest before page-level processing."""
    if not rendered_dir.is_dir():
        raise PlanError(f"rendered_dir '{rendered_dir}' does not exist -- nothing to plan.")
    manifest_path = rendered_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        raise PlanError(
            f"rendered_dir '{rendered_dir}' has no {MANIFEST_NAME}: it is not sharepoint-aspx renderer output. "
            "Markdown renderer output is published with build_markdown_publish_plan, not as pages."
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PlanError(f"{manifest_path} is not readable JSON: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") not in SUPPORTED_MANIFEST_VERSIONS:
        version = manifest.get("schema_version") if isinstance(manifest, dict) else None
        raise PlanError(
            f"{MANIFEST_NAME} schema_version {version!r} "
            f"is not supported (supported: {sorted(SUPPORTED_MANIFEST_VERSIONS)})."
        )
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        raise PlanError(f"{MANIFEST_NAME} lists no pages -- refusing to build an empty plan.")
    return pages


# Convert one validated manifest entry into its SharePoint page action.
def _page_action_from_manifest(
    root: Path,
    target_site_relative_path: str,
    entry: object,
    index: int,
    seen_ids: set[str],
    listed: set[Path],
) -> PublishAction:
    """Validate one manifest entry and return its corresponding page action."""
    chunk_id = _manifest_chunk_id(entry, index, seen_ids)
    rel = _safe_relative(entry.get("html_file"), f"pages[{index}].html_file")
    if rel.suffix.lower() != ".html" or rel.stem != chunk_id:
        raise PlanError(f"pages[{index}].html_file {str(rel)!r} must be '<chunk_id>.html' for chunk_id {chunk_id!r}.")
    source = (root / rel).resolve()
    if root not in source.parents:
        raise PlanError(f"pages[{index}].html_file {str(rel)!r} resolves outside the rendered output directory.")
    if not source.is_file():
        raise PlanError(f"pages[{index}].html_file {str(rel)!r} does not exist -- refusing to plan an empty page.")
    listed.add(source)
    media_refs = _manifest_media_refs(entry, index)
    title = entry.get("title") or ""
    return PublishAction(
        source_path=str(source),
        target_library="SitePages",
        target_folder=target_site_relative_path,
        target_filename=chunk_id + ".aspx",
        title=title if isinstance(title, str) else "",
        media_refs=media_refs,
    )


# Validate a manifest entry's unique identity before using its referenced files.
def _manifest_chunk_id(entry: object, index: int, seen_ids: set[str]) -> str:
    """Validate and reserve a page's unique manifest identity."""
    if not isinstance(entry, dict):
        raise PlanError(f"{MANIFEST_NAME} pages[{index}] is not an object.")
    chunk_id = entry.get("chunk_id")
    if not isinstance(chunk_id, str) or not chunk_id or "/" in chunk_id or "\\" in chunk_id or chunk_id in (".", ".."):
        raise PlanError(f"{MANIFEST_NAME} pages[{index}].chunk_id {chunk_id!r} is not a usable page identity.")
    if chunk_id in seen_ids:
        raise PlanError(f"{MANIFEST_NAME} lists chunk_id {chunk_id!r} twice -- page identities must be unique.")
    seen_ids.add(chunk_id)
    return chunk_id


# Validate page media metadata without mutating the manifest's list.
def _manifest_media_refs(entry: dict, index: int) -> list[str]:
    """Validate a page's manifest media references and return a fresh list."""
    media_refs = entry.get("media_refs") or []
    if not isinstance(media_refs, list) or not all(isinstance(media, str) for media in media_refs):
        raise PlanError(f"pages[{index}].media_refs must be a list of strings.")
    return list(media_refs)


def build_page_publish_plan_from_render(document_id: str, rendered_dir: Path,
                                        target_site_relative_path: str) -> PublishPlan:
    """Build a plan to publish the renderer's real output as SharePoint modern pages. No tenant I/O.

    Consumes `page-manifest.json` ({"schema_version": "1.0", "pages": [{chunk_id, title, html_file,
    media_refs}]}) written by `sharepoint-document-conversion`'s SharePointAspxRenderer, and the HTML
    fragments it points at. Action order is the manifest order (the renderer already applied the
    publication map); each page's identity is its chunk_id (`<chunk_id>.aspx`); `source_path` is the
    absolute path of the HTML fragment, which is exactly what spo-publish-modern-page.ps1 injects into a text web part.
    Media referenced by a fragment is recorded per action (`media_refs`) but is not uploaded or rewritten here.
    Markdown output is a different flow: see build_markdown_publish_plan. Raises PlanError on any contract breach.
    """
    rendered_dir = Path(rendered_dir)
    pages = _load_render_manifest(rendered_dir)
    root = rendered_dir.resolve()
    actions, seen_ids, listed = [], set(), set()
    for index, entry in enumerate(pages):
        actions.append(
            _page_action_from_manifest(
                root, target_site_relative_path, entry, index, seen_ids, listed
            )
        )

    unlisted = sorted(p.name for p in (root / "pages").glob("*.html") if p.resolve() not in listed) if (root / "pages").is_dir() else []
    if unlisted:
        raise PlanError(f"pages/ contains HTML fragments the manifest does not list: {unlisted} -- manifest and output disagree.")

    return PublishPlan(document_id=document_id, actions=actions, source_format="html-fragment")


@dataclass
class RollbackAction:
    target_url: str
    reason: str

    def to_dict(self) -> dict:
        """Serialize the target and explanation for one rollback action."""
        return {"target_url": self.target_url, "reason": self.reason}


@dataclass
class RollbackPlan:
    document_id: str
    actions: list = field(default_factory=list)  # list[RollbackAction]

    def to_dict(self) -> dict:
        """Serialize rollback metadata and the actions to reverse."""
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
