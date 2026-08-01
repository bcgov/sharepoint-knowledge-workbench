"""
plan_hashing.py
================

Deterministic canonical-JSON serialization and SHA-256 fingerprinting for
this plugin's `ConversionPlan` contract (see `plan_schema/analysis_plan.py`).

Named `plan_hashing` rather than `hashing` deliberately: `docx-to-content`
still carries its own `hashing.py` (needed by canonical-knowledge-domain
files not yet extracted), and both are `pip install -e`'d together in the
compatibility-shim environment -- a bare `hashing` name here would collide
and silently resolve to whichever module wins the sys.path race. See
docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md.

Canonical JSON determinism comes from `json.dumps(..., sort_keys=True,
separators=(",", ":"))`: sort_keys guarantees identical key ordering
regardless of dict insertion order, and the compact separators remove
whitespace variance. The same logical payload always produces byte-identical
output.
"""

import hashlib
import json
from typing import Any

from plan_schema.analysis_plan import ConversionPlan


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize `payload` to canonical JSON bytes with stable key ordering
    and stable formatting, independent of dict insertion order."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def content_hash(canonical_json: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of the given canonical JSON
    bytes (no `sha256:` prefix — callers prefix as needed)."""
    return hashlib.sha256(canonical_json).hexdigest()


def compute_plan_id(plan: ConversionPlan) -> str:
    """Compute a `sha256:`-prefixed content hash for a ConversionPlan.

    Excludes:
    - the `plan_id` field itself (it cannot depend on its own value), and
    - `confirmation.confirmed_at` (a timestamp; per spec, timestamps must
      not alter content hashes).

    All other fields, including `confirmation.status` and
    `confirmation.confirmed_by`, participate in the hash.
    """
    data = plan.to_dict()
    data.pop("plan_id", None)
    confirmation = data.get("confirmation")
    if isinstance(confirmation, dict):
        confirmation = dict(confirmation)
        confirmation.pop("confirmed_at", None)
        data["confirmation"] = confirmation
    digest = content_hash(canonical_json_bytes(data))
    return f"sha256:{digest}"
