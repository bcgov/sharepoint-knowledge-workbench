"""
topic_grouping.py
==================

Deterministic topic-boundary computation for the "grouped" chunking
strategy (Task 17-topic-grouping). Groups a flat, source-ordered heading
list (the same shape `analyze_structure.parse_headings` produces) into
topics: every level-1 heading starts a new topic; every heading at level 2+
belongs to the most recently seen level-1 topic. Child headings stay in
source document order within their topic.
"""

from dataclasses import dataclass, field

import identity


class UnassignableHeadingError(Exception):
    """Raised when a heading appears before any level-1 topic root."""


@dataclass(frozen=True)
class TopicMember:
    level: int
    text: str
    path: list
    occurrence: int


@dataclass
class TopicBoundary:
    topic_id: str
    title: str
    members: list = field(default_factory=list)


def compute_topic_boundaries(headings: list) -> list:
    """Group a source-ordered heading list into topics.

    Every level-1 heading starts a new topic (its own topic id is derived
    from its own path via `identity.make_topic_id`); every heading at
    level 2+ is folded into the most recently seen level-1 topic, in
    source order.
    """
    boundaries = []
    current = None
    for heading in headings:
        member = TopicMember(
            level=heading["level"],
            text=heading["text"],
            path=list(heading["path"]),
            occurrence=heading["occurrence"],
        )
        if heading["level"] == 1:
            topic_id = identity.make_topic_id([heading["text"]], occurrence=heading["occurrence"])
            current = TopicBoundary(topic_id=topic_id, title=heading["text"], members=[member])
            boundaries.append(current)
        else:
            if current is None:
                raise UnassignableHeadingError(
                    f"Heading {heading['path']!r} appears before any level-1 topic root"
                )
            current.members.append(member)
    return boundaries
