"""
discovery_inputs.py

Purpose:
    Shared input loading and honest-outcome reporting for every `sharepoint-discovery`
    analysis module. Discovery is read-only: these helpers read already-collected export
    files from the local filesystem and never contact a SharePoint tenant.

    Implements the reporting vocabulary required by the Phase 9 specification (§13):
    a discovery step reports `Observed`, `Empty`, `Forbidden`, `Unavailable`,
    `NotSupported`, `Partial`, or `Failed` -- it never collapses a failure into an
    empty success.

Layer: plugins/sharepoint-discovery -- shared library

Key Input Dependencies:
    - JSON export files produced by a SharePoint discovery collector (any collector;
      the schema expectations are documented per analysis module).

Provenance:
    New in this repository. The CMAT source scripts this plugin was extracted from had
    no shared status vocabulary -- they printed to the console and silently substituted
    fabricated defaults when an input file was absent. See
    docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class DiscoveryStatus(str, Enum):
    """Outcome vocabulary for a single discovery/analysis step."""

    OBSERVED = "Observed"
    EMPTY = "Empty"
    FORBIDDEN = "Forbidden"
    UNAVAILABLE = "Unavailable"
    NOT_SUPPORTED = "NotSupported"
    PARTIAL = "Partial"
    FAILED = "Failed"


#: Statuses that represent a truthful, usable observation (including "nothing was there").
_OK_STATUSES = frozenset(
    {DiscoveryStatus.OBSERVED, DiscoveryStatus.EMPTY, DiscoveryStatus.PARTIAL}
)


@dataclass(frozen=True)
class DiscoveryOutcome:
    """The result of one discovery step: what was asked for, and what honestly happened."""

    status: DiscoveryStatus
    domain: str
    detail: str
    data: Any = None
    artifacts: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        """True when the step produced a truthful observation (Observed/Empty/Partial)."""
        return self.status in _OK_STATUSES

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "domain": self.domain,
            "detail": self.detail,
            "artifacts": list(self.artifacts),
        }

    # -- Constructors, one per status, so callers never build an outcome by hand. --

    @classmethod
    def observed(cls, domain: str, detail: str, data: Any = None, artifacts=()) -> "DiscoveryOutcome":
        return cls(DiscoveryStatus.OBSERVED, domain, detail, data, tuple(artifacts))

    @classmethod
    def empty(cls, domain: str, detail: str, data: Any = None, artifacts=()) -> "DiscoveryOutcome":
        return cls(DiscoveryStatus.EMPTY, domain, detail, data, tuple(artifacts))

    @classmethod
    def forbidden(cls, domain: str, detail: str) -> "DiscoveryOutcome":
        return cls(DiscoveryStatus.FORBIDDEN, domain, detail, None, ())

    @classmethod
    def unavailable(cls, domain: str, detail: str) -> "DiscoveryOutcome":
        return cls(DiscoveryStatus.UNAVAILABLE, domain, detail, None, ())

    @classmethod
    def not_supported(cls, domain: str, detail: str) -> "DiscoveryOutcome":
        return cls(DiscoveryStatus.NOT_SUPPORTED, domain, detail, None, ())

    @classmethod
    def partial(cls, domain: str, detail: str, data: Any = None, artifacts=()) -> "DiscoveryOutcome":
        return cls(DiscoveryStatus.PARTIAL, domain, detail, data, tuple(artifacts))

    @classmethod
    def failed(cls, domain: str, detail: str) -> "DiscoveryOutcome":
        return cls(DiscoveryStatus.FAILED, domain, detail, None, ())


def load_json_input(path: str | Path, *, domain: str) -> DiscoveryOutcome:
    """
    Read a JSON discovery export from the local filesystem and classify the result.

    There is no fallback to a fabricated default: an absent file is `Unavailable`,
    an unreadable file is `Forbidden`, and unparseable content is `Failed`.
    """
    p = Path(path)

    if not p.exists():
        return DiscoveryOutcome.unavailable(
            domain, f"Input not found: {p} -- run the collector for this domain first."
        )
    if p.is_dir():
        return DiscoveryOutcome.failed(domain, f"Input path is a directory, not a file: {p}")

    try:
        text = p.read_text(encoding="utf-8")
    except PermissionError as exc:
        return DiscoveryOutcome.forbidden(domain, f"Permission denied reading {p}: {exc}")
    except OSError as exc:
        return DiscoveryOutcome.failed(domain, f"Could not read {p}: {exc}")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return DiscoveryOutcome.failed(domain, f"Malformed JSON in {p}: {exc}")

    if isinstance(data, (list, dict)) and len(data) == 0:
        return DiscoveryOutcome.empty(domain, f"{p} contains no records.", data=data)

    count = len(data) if isinstance(data, (list, dict)) else 1
    return DiscoveryOutcome.observed(domain, f"{count} record(s) read from {p}.", data=data)


def require_output_dir(path: str | Path) -> Path:
    """Resolve and create an output directory. Raises on an empty/unspecified path."""
    if path is None or str(path).strip() == "":
        raise ValueError("An explicit output directory is required (no default is assumed).")
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p
