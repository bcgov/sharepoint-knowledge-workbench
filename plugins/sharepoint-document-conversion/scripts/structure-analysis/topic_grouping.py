"""topic_grouping.py
==================

Purpose:
    Thin local re-export of `topic_boundary_core.py` (the single canonical implementation of topic-boundary computation, shared with `structured-content-assembly` via a managed cross-plugin symlink).

Key Input Dependencies:
    - topic_boundary_core

Thin local re-export of `topic_boundary_core.py` (the single canonical
implementation of topic-boundary computation, shared with
`structured-content-assembly` via a managed cross-plugin symlink). Kept as a
separate bare-name module so existing internal imports (`from
topic_grouping import compute_topic_boundaries`, etc.) continue to work
unchanged. See
docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md.

Key Functions Index:
    - No locally defined functions."""

from topic_boundary_core import (  # noqa: F401
    UnassignableHeadingError,
    TopicMember,
    TopicBoundary,
    classify_headings,
    compute_topic_boundaries,
    compute_topic_boundaries_from_roots,
)
