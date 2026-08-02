"""
topic_grouping.py
==================

Thin local re-export of `topic_boundary_core.py` (the single canonical
implementation of topic-boundary computation, shared with
`canonical-knowledge` via a managed cross-plugin symlink). Kept as a
separate bare-name module so existing internal imports (`from
topic_grouping import compute_topic_boundaries`, etc.) continue to work
unchanged. See
docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md.
"""

from topic_boundary_core import (  # noqa: F401
    UnassignableHeadingError,
    TopicMember,
    TopicBoundary,
    classify_headings,
    compute_topic_boundaries,
    compute_topic_boundaries_from_roots,
)
