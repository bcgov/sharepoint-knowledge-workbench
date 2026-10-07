"""media_disposition.py
=====================

Purpose:
    General media classification/disposition mechanism (Task 18), scoped to the concrete integration point that exists today: `SlicedDocument.preamble` (front-matter content before the first structural anchor's heading line -- see `chunking.py`), which is never copied into canonical output by `package.py`'s chunk-only builders.

Key Input Dependencies:
    - hashlib
    - re
    - pathlib

General media classification/disposition mechanism (Task 18), scoped to
the concrete integration point that exists today: `SlicedDocument.preamble`
(front-matter content before the first structural anchor's heading line --
see `chunking.py`), which is never copied into canonical output by
`package.py`'s chunk-only builders. Any media referenced from the preamble
(e.g. a cover screenshot) therefore needs an explicit, recorded disposition
rather than silently disappearing.

Classification is a taxonomy of WHAT an image is; disposition is a
separate decision of WHERE it ends up. The pipeline can only propose --
never silently decide -- a classification/disposition for preamble media;
a human confirms (or overrides) the proposal via `plans.apply_media_decision`
before the plan is confirmed.

Vocabularies:
    CLASSIFICATIONS -- what the image objectively/subjectively is
    DISPOSITIONS -- where the image ends up

Function Index:
    - propose_media_decisions(preamble_text, media_dir) -> list[dict]
        Proposes one record per media reference found in the preamble,
        defaulting to classification="requires-human-review",
        disposition="requires-human-decision" -- objective signals only
        (position, file size, format), never an inferred final decision.

Key Functions Index:
    - _extract_media_refs()
    - propose_media_decisions()"""

import hashlib
import re
from pathlib import Path

CLASSIFICATIONS = frozenset(
    {
        "meaningful-body-content",
        "instructional-screenshot",
        "diagram-or-chart",
        "publication-branding",
        "publication-cover-art",
        "decorative",
        "duplicate-of-accessible-text",
        "obsolete-source-layout-artifact",
        "unclassified",
        "requires-human-review",
    }
)

DISPOSITIONS = frozenset(
    {
        "retain-in-canonical-topic",
        "retain-as-publication-media",
        "retain-as-source-evidence-only",
        "replace-with-approved-asset",
        "omit-as-reviewed-artifact",
        "requires-human-decision",
    }
)

_IMAGE_REF = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


# Extract local media references from the supplied Markdown text.
def _extract_media_refs(text: str) -> list:
    """Extract local media references from the supplied Markdown text."""
    refs = []
    for match in _IMAGE_REF.finditer(text):
        ref = match.group(2)
        if not ref.startswith(("http://", "https://")):
            refs.append(ref)
    return refs


def propose_media_decisions(preamble_text: str, media_dir: "Path | None") -> list:
    """Propose (never finalize) one media-decision record per media
    reference found in `preamble_text`, in source order.

    Each record's `classification`/`disposition` default to
    "requires-human-review"/"requires-human-decision" -- the objective
    signals gathered here (position, byte size, format) are classification
    INPUTS, not conclusions. A human confirms the real decision via
    `plans.apply_media_decision` before the plan is confirmed.
    """
    proposals = []
    for ref in _extract_media_refs(preamble_text):
        filename = ref.rsplit("/", 1)[-1]
        source_hash = None
        size_bytes = None
        if media_dir is not None and Path(media_dir).exists():
            # pandoc's --extract-media writes into <media_dir>/media/...,
            # so search recursively rather than assuming a flat layout.
            candidate = next(
                (p for p in Path(media_dir).rglob(filename) if p.is_file()), None
            )
            if candidate is not None:
                data = candidate.read_bytes()
                source_hash = hashlib.sha256(data).hexdigest()
                size_bytes = len(data)
        proposals.append(
            {
                "source_media_id": filename,
                "source_position": "preamble-before-first-heading",
                "source_hash": source_hash,
                "size_bytes": size_bytes,
                "media_type": f"image/{Path(filename).suffix.lstrip('.').lower() or 'unknown'}",
                "classification": "requires-human-review",
                "disposition": "requires-human-decision",
                "canonical_inclusion": False,
                "publication_inclusion": False,
                "derived_asset_allowed": False,
                "reason": (
                    "preamble media requires human review before a "
                    "classification/disposition can be recorded"
                ),
                "decision_authority": "pending",
                "requires_alt_text": None,
            }
        )
    return proposals
