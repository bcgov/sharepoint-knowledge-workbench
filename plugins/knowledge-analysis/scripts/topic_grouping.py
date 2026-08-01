"""
topic_grouping.py
==================

Deterministic topic-boundary computation for the "grouped" chunking
strategy (Task 17-topic-grouping, refined for Task 18's mixed-level
logical-root detection).

The original rule ("every level-1 heading starts a topic") assumed every
source document consistently authors its top-level sections at heading
level 1. The real CEIS pilot document disproved that: its first 14
top-level sections are styled Heading 2, the remaining 11 Heading 1 --
never mixed within a section (children are always exactly one level
deeper than their section's root, and no Heading 2 is ever used as a
genuine child beneath a Heading 1 in that document). See
docs/reports/ for the diagnostic evidence.

`classify_headings` detects this pattern deterministically: it tracks the
current topic-root level and treats any heading at or above that level
(i.e. equally or less deep) as a new topic root, updating the current
root level to match. This reproduces the historical level==1-only
behavior unchanged for documents that never vary their root level. A
heading that appears deeper than the current root but matches a level
already used as a root earlier in the document (a "bidirectional"
inconsistency -- root level rising back up after having gone deeper) is
never silently promoted or silently folded in: it is classified
"ambiguous-root", left as an internal heading by default, and flagged for
explicit human review.

`compute_topic_boundaries` is the analysis-time preview built on top of
`classify_headings` -- advisory only. `compute_topic_boundaries_from_roots`
is the convert-time function that consumes an explicit, human-confirmed
root set (persisted on the plan) instead of recomputing the heuristic --
convert must never independently re-derive a classification the human
never saw.
"""

from dataclasses import dataclass, field

import identity


class UnassignableHeadingError(Exception):
    """Raised when a heading cannot be assigned to any topic root -- either
    it appears before any heading has established a root (should not
    happen; the first heading always becomes a root), or, for the
    confirmed-roots path, a confirmed root's identity no longer matches
    the current source headings."""


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
    """Classify each heading as a topic root or internal heading.

    Returns one dict per input heading, in source order:
        path, occurrence, text, source_level, classification
        ("root" | "promoted-root" | "ambiguous-root" | "internal-heading"),
        physical_boundary (bool), requires_confirmation (bool), reason.

    "root": a heading whose level matches the level the document opened
    with. "promoted-root": a heading treated as a topic root even though
    its level differs from the document's opening root level, because it
    is at or above (i.e. equally or less deep than) the current root
    level -- a mixed-level top-level section pattern. "ambiguous-root": a
    heading deeper than the current root level but matching a level
    already used as a root earlier -- a possible root-level reversal that
    is never silently resolved; it defaults to an internal heading
    (physical_boundary=False) pending explicit confirmation.
    """
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
            topic_id = identity.make_topic_id([heading["text"]], occurrence=heading["occurrence"])
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
    """Analysis-time (advisory) topic-boundary preview, built on
    `classify_headings`. Unchanged in behavior for documents whose
    top-level sections are consistently authored at a single heading
    level; additionally identifies mixed-level top-level sections
    (`classify_headings`'s "promoted-root") as topic roots too.
    """
    classifications = classify_headings(headings)
    flags = [c["physical_boundary"] for c in classifications]
    return _boundaries_from_flags(headings, flags)


def compute_topic_boundaries_from_roots(headings: list, root_keys: set) -> list:
    """Convert-time topic-boundary computation from an explicit,
    human-confirmed set of topic-root identities (`root_keys`, a set of
    `(tuple(source_heading_path), occurrence)` tuples) -- never
    re-derives the classification heuristic. Raises
    `UnassignableHeadingError` if the confirmed roots no longer reconcile
    with the current source headings (e.g. the first heading isn't a
    confirmed root), signalling a stale/mismatched confirmed plan rather
    than silently falling back to a heuristic.
    """
    flags = [
        (tuple(heading["path"]), heading["occurrence"]) in root_keys for heading in headings
    ]
    return _boundaries_from_flags(headings, flags)
