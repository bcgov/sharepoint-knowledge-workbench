"""identity_core.py
=================

Purpose:
    Stable structural chunk identity (spec Section 6.6, "Stable chunk identity").

Key Input Dependencies:
    - hashlib
    - re
    - unicodedata

Stable structural chunk identity (spec Section 6.6, "Stable chunk
identity"). A chunk ID must not depend on ordinal position alone. It is
derived from:

- the normalized full heading path,
- the heading occurrence needed to distinguish repeated paths,
- a short hash of the normalized structural key.

Spec example shape (copied verbatim): `file-access-how-to-seal-a-file--7d91c4a2`
i.e. `<slugified-full-heading-path-joined-by-hyphens>--<short-hash>`.

`source_order` (display ordering, tracked by the caller — e.g. as position
in `ConversionPlan.chunk_anchors` or a caller-supplied index) is explicitly
NOT part of identity and is not accepted as a parameter anywhere in this
module: there is no ordinal/index parameter on `make_chunk_id`, so document
position cannot leak into the ID by construction.

This is the single canonical implementation of chunk/topic identity,
shared by `document-structure-analysis` (via `identity.py`, a thin local re-export)
and `structured-content-assembly` (via a managed cross-plugin symlink at this
exact module name, `identity_core.py` -- both plugins need byte-identical
identity computation for chunking.py's reconciliation to succeed against
the analysis-time anchors `document-structure-analysis` already computed). See
docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md.

Self-contained (stdlib-only hashing) rather than importing
`document-structure-analysis`'s own `plan_hashing.py`, so this module can be
symlinked into another plugin without pulling in a second cross-plugin
dependency.

Key Functions Index:
    - _content_hash()
    - _slugify_component()
    - normalize_heading_path()
    - make_chunk_id()
    - make_topic_id()"""

import hashlib
import re
import unicodedata

_HASH_LENGTH = 8


# Compute the SHA-256 digest of the supplied source content.
def _content_hash(data: bytes) -> str:
    """Compute the SHA-256 digest of the supplied source content."""
    return hashlib.sha256(data).hexdigest()


# Matches runs of characters that are not lowercase ascii letters or digits,
# so they can be collapsed to a single hyphen.
_NON_SLUG_CHARS = re.compile(r"[^a-z0-9]+")


def _slugify_component(text: str) -> str:
    """Normalize a single heading-path component into a lowercase,
    hyphen-separated slug fragment.

    Unicode handling: text is NFKD-normalized and combining marks are
    stripped, which transliterates accented Latin characters sensibly
    (e.g. "Configuración" -> "configuracion"). Characters with no ASCII
    decomposition (e.g. CJK, Cyrillic) are dropped by the ASCII encode step;
    if that would leave the component with no slug-able characters at all,
    a stable fallback of the component's UTF-8 bytes hashed to a short hex
    tag is used instead, so a non-Latin heading never silently collapses to
    an empty string.
    """
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    slug = _NON_SLUG_CHARS.sub("-", ascii_only.lower()).strip("-")
    if slug:
        return slug
    # Non-Latin script fallback: derive a stable short tag from the
    # original text's UTF-8 bytes rather than dropping it silently.
    return "x" + _content_hash(text.encode("utf-8"))[:_HASH_LENGTH]


def normalize_heading_path(heading_path: list) -> str:
    """Normalize a full heading path into a single structural key string.

    Joins the per-component slugs with hyphens, lowercase, with all
    whitespace/punctuation collapsed to single hyphens and no leading/
    trailing hyphens.

    Example: ["FILE ACCESS", "How to Seal a File"] ->
    "file-access-how-to-seal-a-file"
    """
    components = [_slugify_component(part) for part in heading_path]
    return "-".join(c for c in components if c)


def make_chunk_id(heading_path: list, occurrence: int = 1) -> str:
    """Produce the stable chunk ID for a heading path, in the spec's
    `<slug>--<short-hash>` shape (e.g. `file-access-how-to-seal-a-file--7d91c4a2`).

    `occurrence` disambiguates two entirely separate headings that share an
    identical full path (e.g. two top-level sections both titled
    "Overview"). It is not appended to the ID as a visible suffix (e.g.
    `-2`) — the spec's example doesn't show that pattern. Instead it
    participates in the hashed structural key: the hash input is the
    normalized path plus occurrence, so occurrence 1 and occurrence 2 of
    the same path produce the same slug but different hash segments.

    `heading_path` and `occurrence` are the only inputs — there is no
    ordinal/index/source_order parameter, so document position cannot leak
    into the ID by construction (position independence).
    """
    slug = normalize_heading_path(heading_path)
    structural_key = f"{slug}\x00{occurrence}"
    digest = _content_hash(structural_key.encode("utf-8"))[:_HASH_LENGTH]
    return f"{slug}--{digest}"


def make_topic_id(top_level_heading_path: list, occurrence: int = 1) -> str:
    """Produce the stable topic ID for a top-level (grouping) heading path.

    Distinct from `make_chunk_id`: a topic groups one or more structural
    anchors under a single top-level heading, so its identity must be
    derived only from that top-level heading's own path (never a
    descendant's path), keeping topic identity independent of which/how
    many structural anchors happen to be folded into it.
    """
    slug = normalize_heading_path(top_level_heading_path)
    structural_key = f"topic\x00{slug}\x00{occurrence}"
    digest = _content_hash(structural_key.encode("utf-8"))[:_HASH_LENGTH]
    return f"{slug}--{digest}"
