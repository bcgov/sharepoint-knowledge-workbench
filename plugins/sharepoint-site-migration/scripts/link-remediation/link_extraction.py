"""
link_extraction.py
==================

Purpose:
    Read-only inventory of every hyperlink, asset reference, form action and
    embedded URL found in page markup (classic .aspx, modern page canvas HTML,
    web-part payloads, or any HTML-shaped text). Produces the inventory that
    remediation and integrity validation both consume. Performs no writes and
    no network or tenant I/O of any kind.

Layer: sharepoint-site-migration / extraction

Key Input Dependencies:
    - page markup, supplied either as text or as real files on disk

Usage:
    from link_extraction import extract_links_from_paths
    inventory = extract_links_from_paths(["exported/page.aspx"])
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from link_outcomes import Outcome

#: Attributes whose values are treated as link surfaces.
_LINK_ATTRIBUTE = re.compile(r"""(?:href|src|action|url)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)

#: In-page anchors and script pseudo-URLs are never migration surfaces.
_NON_NAVIGATIONAL_PREFIXES = ("#", "javascript:", "mailto:", "tel:")

#: Platform-shipped artifacts present on every SharePoint page. These are
#: product filenames, not any particular organisation's content, and are
#: ignored by default so they do not swamp a migration inventory.
_PLATFORM_ARTIFACTS = ("blank.gif", "init.js", "sp.js", "corev15.css")

_ASSET_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js", ".ico")


@dataclass(frozen=True)
class ExtractedLink:
    """One link occurrence, attributed to the content it was found in."""

    source: str
    url: str
    kind: str

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "url": self.url, "kind": self.kind}


@dataclass(frozen=True)
class LinkInventory:
    """The result of an extraction run, including anything that went wrong."""

    links: Sequence[ExtractedLink] = field(default_factory=list)
    problems: Sequence[str] = field(default_factory=list)
    outcome: str = Outcome.EMPTY

    @classmethod
    def from_links(
        cls,
        links: Iterable[ExtractedLink],
        problems: Iterable[str] = (),
        *,
        sources_attempted: int | None = None,
    ) -> "LinkInventory":
        links = list(links)
        problems = list(problems)
        if sources_attempted is not None and problems and len(problems) == sources_attempted:
            outcome = Outcome.FAILED
        elif problems:
            outcome = Outcome.PARTIAL
        elif links:
            outcome = Outcome.OBSERVED
        else:
            outcome = Outcome.EMPTY
        return cls(links=links, problems=problems, outcome=outcome)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "link_count": len(self.links),
            "links": [link.to_dict() for link in self.links],
            "problems": list(self.problems),
        }


def classify(url: str) -> str:
    """Classify a link into one of the migration-relevant link surfaces."""
    lowered = url.lower()
    if "_catalogs/masterpage" in lowered or "/style library/" in lowered:
        return "masterpage-asset"
    if lowered.endswith(_ASSET_SUFFIXES):
        return "asset-reference"
    if "form.aspx" in lowered:
        return "form-action"
    if lowered.endswith(".aspx") or "/pages/" in lowered or "/sitepages/" in lowered:
        return "page-link"
    return "hyperlink"


def extract_links_from_text(
    content: str,
    source: str,
    *,
    ignore_platform_artifacts: bool = True,
) -> list[ExtractedLink]:
    """Extract every link surface from one piece of markup. Never raises on
    malformed markup -- unparseable fragments simply yield no link."""
    if not content:
        return []

    found: list[ExtractedLink] = []
    seen: set[str] = set()
    for raw in _LINK_ATTRIBUTE.findall(content):
        url = raw.strip()
        if not url or url in seen:
            continue
        if url.lower().startswith(_NON_NAVIGATIONAL_PREFIXES):
            continue
        if ignore_platform_artifacts and any(artifact in url.lower() for artifact in _PLATFORM_ARTIFACTS):
            continue
        seen.add(url)
        found.append(ExtractedLink(source=source, url=url, kind=classify(url)))
    return found


def extract_links_from_paths(
    paths: Iterable[str | Path],
    *,
    ignore_platform_artifacts: bool = True,
) -> LinkInventory:
    """Extract links from real files on disk.

    Unreadable or missing inputs are reported as problems and downgrade the
    outcome to Partial (or Failed if nothing could be read) -- they never
    silently disappear into an apparently-successful empty result.
    """
    links: list[ExtractedLink] = []
    problems: list[str] = []
    attempted = 0

    for candidate in paths:
        attempted += 1
        path = Path(candidate)
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except FileNotFoundError:
            problems.append(f"not found: {path}")
            continue
        except PermissionError as exc:
            problems.append(f"permission denied: {path} ({exc})")
            continue
        except OSError as exc:
            problems.append(f"unreadable: {path} ({exc})")
            continue
        links.extend(
            extract_links_from_text(
                content, source=path.name, ignore_platform_artifacts=ignore_platform_artifacts
            )
        )

    return LinkInventory.from_links(links, problems, sources_attempted=attempted)
