"""
plan_hashing.py
================

Deterministic canonical-JSON serialization and SHA-256 fingerprinting for
this plugin's `ConversionPlan` contract (see `plan_schema/analysis_plan.py`).

Named `plan_hashing` rather than `hashing` deliberately: `docx-to-content`
still carries its own `hashing.py` (needed by structured-content-assembly-domain
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

from plan_verification_core import compute_plan_id  # noqa: F401


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize `payload` to canonical JSON bytes with stable key ordering
    and stable formatting, independent of dict insertion order."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def content_hash(canonical_json: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of the given canonical JSON
    bytes (no `sha256:` prefix — callers prefix as needed)."""
    return hashlib.sha256(canonical_json).hexdigest()


# compute_plan_id itself now lives in plan_verification_core.py (the single
# canonical implementation, also consumed cross-plugin by structured-content-assembly
# via a managed symlink) -- re-exported above so existing callers
# (`plans.py`) are unaffected.
