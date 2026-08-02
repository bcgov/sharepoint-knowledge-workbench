"""
identity.py
===========

Thin local re-export of `identity_core.py` (the single canonical
implementation of chunk/topic identity, shared with `canonical-knowledge`
via a managed cross-plugin symlink). Kept as a separate bare-name module
so existing internal imports (`from identity import make_chunk_id`, etc.)
continue to work unchanged. See
docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md.
"""

from identity_core import (  # noqa: F401
    _slugify_component,
    normalize_heading_path,
    make_chunk_id,
    make_topic_id,
)
