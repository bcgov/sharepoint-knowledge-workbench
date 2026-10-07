"""hashing.py
==========

Purpose:
    Deterministic canonical-JSON serialization and SHA-256 fingerprinting for the docx-to-content contract dataclasses (see scripts/contracts.py).

Key Input Dependencies:
    - hashlib
    - json
    - typing

Deterministic canonical-JSON serialization and SHA-256 fingerprinting for the
docx-to-content contract dataclasses (see scripts/contracts.py).

Canonical JSON determinism comes from `json.dumps(..., sort_keys=True,
separators=(",", ":"))`: sort_keys guarantees identical key ordering
regardless of dict insertion order, and the compact separators remove
whitespace variance. The same logical payload always produces byte-identical
output.

`compute_plan_id` (ConversionPlan-specific) moved to document-structure-analysis's
own `hashing.py` in Phase 4.5 Wave 3, alongside the ConversionPlan type
itself -- see
docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md.

Key Functions Index:
    - canonical_json_bytes()
    - content_hash()"""

import hashlib
import json
from typing import Any


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize `payload` to canonical JSON bytes with stable key ordering
    and stable formatting, independent of dict insertion order."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def content_hash(canonical_json: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of the given canonical JSON
    bytes (no `sha256:` prefix — callers prefix as needed)."""
    return hashlib.sha256(canonical_json).hexdigest()
