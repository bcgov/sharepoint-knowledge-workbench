"""Purpose:
    Mirrors the native SharePoint review-manual-topics skill's Input Resolution Hierarchy and one-primary-plus-max-two-related boundary, operating over this local rendered manual output (runs/sample-manual/render/rendered-output/pages/) instead of a live tenant.

Key Input Dependencies:
    - re
    - dataclasses
    - pathlib

review_manual_topics.py — repository/Claude runtime, deterministic topic resolution.

Mirrors the native SharePoint review-manual-topics skill's Input Resolution
Hierarchy and one-primary-plus-max-two-related boundary, operating over this
local rendered manual output (runs/sample-manual/render/rendered-output/pages/)
instead of a live tenant. Never invents content for a missing topic. Performs
no tenant writes — there is nothing to write, the source is the repo's own
render output.

The editorial synthesis itself (completeness, structure, cross-reference
consistency, terminology clarity) is performed by the model per the skill's
own instructions (SKILL.md) — this module only resolves which raw content the
model is allowed to see, enforcing the boundary in code.

Key Functions Index:
    - _load_topic()
    - _find_by_slug_or_prefix()
    - resolve_topic()"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)#]+\.md)[^)]*\)")


class TopicNotFoundError(Exception):
    """Raised when the primary topic cannot be uniquely resolved. Never invent content."""


class TooManyRelatedTopicsError(Exception):
    """Raised when a primary topic links to more than 2 other topic pages."""


@dataclass(frozen=True)
class Topic:
    slug: str
    path: Path
    content: str


@dataclass(frozen=True)
class ResolvedTopic:
    primary: Topic
    related: list[Topic] = field(default_factory=list)


# Load the explicitly selected Markdown topic page and its publication metadata for editorial review.
def _load_topic(pages_dir: Path, filename: str) -> Topic:
    """Load the explicitly selected Markdown topic page and its publication metadata for editorial review."""
    path = pages_dir / filename
    slug = path.stem
    return Topic(slug=slug, path=path, content=path.read_text(encoding="utf-8"))


# Find by slug or prefix among the supplied records.
def _find_by_slug_or_prefix(pages_dir: Path, slug_or_prefix: str) -> Path:
    """Find by slug or prefix among the supplied records."""
    exact = pages_dir / f"{slug_or_prefix}.md"
    if exact.exists():
        return exact

    matches = sorted(pages_dir.glob(f"{slug_or_prefix}--*.md"))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise TopicNotFoundError(
            f"'{slug_or_prefix}' is ambiguous: matches {[m.name for m in matches]}. "
            "Request explicit filename clarification."
        )
    raise TopicNotFoundError(
        f"Primary topic '{slug_or_prefix}' was not found or is inaccessible."
    )


def resolve_topic(pages_dir: Path, primary_slug_or_filename: str) -> ResolvedTopic:
    """
    Resolve exactly one primary topic and at most 2 explicitly cross-referenced
    related topic pages, mirroring the native skill's Input Resolution Hierarchy.

    Raises TopicNotFoundError if the primary topic doesn't resolve uniquely.
    Raises TooManyRelatedTopicsError if the primary topic links to more than 2
    other topic pages (the native skill's boundary — do not silently truncate).
    """
    stem = primary_slug_or_filename.removesuffix(".md")
    primary_path = _find_by_slug_or_prefix(pages_dir, stem)
    primary = _load_topic(pages_dir, primary_path.name)

    related_filenames = []
    for match in _LINK_PATTERN.finditer(primary.content):
        target = Path(match.group(1)).name
        if target != primary_path.name and target not in related_filenames:
            related_filenames.append(target)

    if len(related_filenames) > 2:
        raise TooManyRelatedTopicsError(
            f"Primary topic '{primary.slug}' links to {len(related_filenames)} other "
            "topic pages; the boundary is at most 2 related topics per invocation."
        )

    related = [
        _load_topic(pages_dir, filename)
        for filename in related_filenames
        if (pages_dir / filename).exists()
    ]

    return ResolvedTopic(primary=primary, related=related)
