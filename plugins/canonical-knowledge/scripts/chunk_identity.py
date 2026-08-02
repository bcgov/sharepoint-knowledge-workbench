"""
chunk_identity.py
==================

Stable structural chunk identity -- a plugin-local copy of
`knowledge-analysis`'s `identity.make_chunk_id` (that plugin already
installs a bare top-level `identity` module; naming this module the same
would collide once both plugins are `pip install -e`'d together in
`docx-to-content`'s compatibility-shim environment -- see
docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md's
`hashing`/`plan_hashing` precedent, and
docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md
for why this module exists as a duplicate rather than a cross-plugin
import).

`chunking.py`'s reconciliation must recompute the *exact same* stable_key
`knowledge-analysis` computed during analysis, so the slug/hash algorithm
here must stay byte-for-byte identical to the producer's copy -- kept in
sync by hand, not generated.

A chunk ID must not depend on ordinal position alone. It is derived from:
- the normalized full heading path,
- the heading occurrence needed to distinguish repeated paths,
- a short hash of the normalized structural key.

Shape: `<slugified-full-heading-path-joined-by-hyphens>--<short-hash>`,
e.g. `file-access-how-to-seal-a-file--7d91c4a2`.
"""

import hashlib
import re
import unicodedata

_HASH_LENGTH = 8

# Matches runs of characters that are not lowercase ascii letters or digits,
# so they can be collapsed to a single hyphen.
_NON_SLUG_CHARS = re.compile(r"[^a-z0-9]+")


def _content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slugify_component(text: str) -> str:
    """Normalize a single heading-path component into a lowercase,
    hyphen-separated slug fragment. See identity.py's docstring
    (knowledge-analysis) for the full Unicode-handling rationale -- this
    copy must stay byte-for-byte identical to it."""
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    slug = _NON_SLUG_CHARS.sub("-", ascii_only.lower()).strip("-")
    if slug:
        return slug
    return "x" + _content_hash(text.encode("utf-8"))[:_HASH_LENGTH]


def normalize_heading_path(heading_path: list) -> str:
    """Normalize a full heading path into a single structural key string."""
    components = [_slugify_component(part) for part in heading_path]
    return "-".join(c for c in components if c)


def make_chunk_id(heading_path: list, occurrence: int = 1) -> str:
    """Produce the stable chunk ID for a heading path -- must match
    `knowledge-analysis`'s `identity.make_chunk_id` exactly for
    reconciliation to succeed."""
    slug = normalize_heading_path(heading_path)
    structural_key = f"{slug}\x00{occurrence}"
    digest = _content_hash(structural_key.encode("utf-8"))[:_HASH_LENGTH]
    return f"{slug}--{digest}"


def make_topic_id(top_level_heading_path: list, occurrence: int = 1) -> str:
    """Produce the stable topic ID for a top-level (grouping) heading path
    -- must match `knowledge-analysis`'s `identity.make_topic_id` exactly."""
    slug = normalize_heading_path(top_level_heading_path)
    structural_key = f"topic\x00{slug}\x00{occurrence}"
    digest = _content_hash(structural_key.encode("utf-8"))[:_HASH_LENGTH]
    return f"{slug}--{digest}"
