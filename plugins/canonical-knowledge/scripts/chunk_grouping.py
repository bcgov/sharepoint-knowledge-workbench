"""
chunk_grouping.py
==================

Convert-time topic-boundary computation for the "grouped" chunking
strategy -- a plugin-local copy of `knowledge-analysis`'s
`topic_grouping.py` (that plugin already installs a bare top-level
`topic_grouping` module; naming this module the same would collide once
both plugins are `pip install -e`'d together in `docx-to-content`'s
compatibility-shim environment -- see
docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md).

`package.py` only needs the convert-time functions
(`compute_topic_boundaries_from_roots`, with `compute_topic_boundaries` as
its pre-confirmed-roots fallback) -- the analysis-time preview these
support `knowledge-analysis` already owns and exposes via
`recommend_from_normalized`'s `proposed_topics`. This copy exists only so
`package.py` can build the grouped canonical package from a CONFIRMED
plan's `confirmed_topic_roots` without depending on `knowledge-analysis`'s
package at runtime.

`compute_topic_boundaries_from_roots` consumes an explicit, human-
confirmed root set (persisted on the plan) instead of recomputing the
heuristic -- convert must never independently re-derive a classification
the human never saw.
"""

from dataclasses import dataclass, field

import chunk_identity


class UnassignableHeadingError(Exception):
    """Raised when a heading cannot be assigned to any topic root -- a
    confirmed root's identity no longer matches the current source
    headings."""


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


def classify_headings(headings: list) -> list:
    """Classify each heading as a topic root or internal heading -- must
    match `knowledge-analysis`'s `topic_grouping.classify_headings`
    exactly, since `compute_topic_boundaries`'s fallback path depends on
    it. See that module's docstring (knowledge-analysis) for the full
    classification rationale."""
    results = []
    root_levels_seen = []
    current_root_level = None
    opening_level = None

    for heading in headings:
        level = heading["level"]

        if current_root_level is None:
            classification = "root"
            reason = "first heading in the document; establishes the initial topic-root level"
            physical_boundary = True
            requires_confirmation = False
            opening_level = level
            current_root_level = level
            root_levels_seen.append(level)
        elif level <= current_root_level:
            physical_boundary = True
            requires_confirmation = False
            if level == opening_level:
                classification = "root"
                reason = "matches the document-opening heading level"
            else:
                classification = "promoted-root"
                reason = (
                    f"heading level {level} is at or above the current topic-root "
                    f"level {current_root_level}, consistent with a mixed-level "
                    "top-level section pattern"
                )
            current_root_level = level
            if level not in root_levels_seen:
                root_levels_seen.append(level)
        elif level in root_levels_seen and level != current_root_level:
            classification = "ambiguous-root"
            physical_boundary = False
            requires_confirmation = True
            reason = (
                f"heading level {level} matches a topic-root level used earlier in "
                f"the document but appears deeper than the current root level "
                f"{current_root_level}; could be a genuinely nested child or a "
                "misclassified top-level section -- treated as an internal heading "
                "pending explicit plan confirmation"
            )
        else:
            classification = "internal-heading"
            physical_boundary = False
            requires_confirmation = False
            reason = "deeper than the current topic root; folded in as a child heading"

        results.append(
            {
                "path": list(heading["path"]),
                "occurrence": heading["occurrence"],
                "text": heading["text"],
                "source_level": level,
                "classification": classification,
                "physical_boundary": physical_boundary,
                "requires_confirmation": requires_confirmation,
                "reason": reason,
            }
        )

    return results


def _boundaries_from_flags(headings: list, physical_boundary_flags: list) -> list:
    boundaries = []
    current = None
    for heading, is_root in zip(headings, physical_boundary_flags):
        member = TopicMember(
            level=heading["level"],
            text=heading["text"],
            path=list(heading["path"]),
            occurrence=heading["occurrence"],
        )
        if is_root:
            topic_id = chunk_identity.make_topic_id([heading["text"]], occurrence=heading["occurrence"])
            current = TopicBoundary(topic_id=topic_id, title=heading["text"], members=[member])
            boundaries.append(current)
        else:
            if current is None:
                raise UnassignableHeadingError(
                    f"Heading {heading['path']!r} appears before any topic root"
                )
            current.members.append(member)
    return boundaries


def compute_topic_boundaries(headings: list) -> list:
    """Fallback for a confirmed plan with no `confirmed_topic_roots`
    persisted (older plans predating that field): recomputes the
    heuristic. Built on `classify_headings`."""
    classifications = classify_headings(headings)
    flags = [c["physical_boundary"] for c in classifications]
    return _boundaries_from_flags(headings, flags)


def compute_topic_boundaries_from_roots(headings: list, root_keys: set) -> list:
    """Convert-time topic-boundary computation from an explicit, human-
    confirmed set of topic-root identities (`root_keys`, a set of
    `(tuple(source_heading_path), occurrence)` tuples) -- never re-derives
    the classification heuristic. Raises `UnassignableHeadingError` if the
    confirmed roots no longer reconcile with the current source headings.
    """
    flags = [
        (tuple(heading["path"]), heading["occurrence"]) in root_keys for heading in headings
    ]
    return _boundaries_from_flags(headings, flags)
