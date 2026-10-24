"""
link_integrity.py
=================

Purpose:
    Read-only verification that a link inventory is actually clean: every link
    that the rewrite ruleset says should have been rewritten still being present
    is a residual-legacy finding, malformed URLs are reported rather than
    silently passed, and -- when the caller injects a resolver -- non-external
    (relative) links that do not resolve are reported as unresolvable.

    Resolver scope: absolute http(s):// links are never passed to the injected
    resolver -- they are classified EXTERNAL and counted as healthy
    unconditionally, regardless of whether they actually resolve. Injecting a
    resolver validates relative links only; it does not make this module an
    external-link checker.

    Scope boundary: this module verifies LINKS ONLY. Reconciling a published
    package against its publication map is a different responsibility, already
    owned by the sharepoint-site-build-and-publish plugin; it is deliberately not
    duplicated here.

    Performs no writes and ships no transport: resolution is only ever done by
    a caller-injected resolver, and without one it honestly reports
    NotSupported rather than implying everything resolved.

Layer: sharepoint-site-migration / integrity

Key Input Dependencies:
    - link_extraction.LinkInventory
    - link_rules.RewriteRuleset

Usage:
    report = validate_link_integrity(inventory, ruleset)
    report = validate_link_integrity(inventory, ruleset, resolver=my_resolver)

Function Index:
    LinkFinding.to_dict, IntegrityReport.residual_count, IntegrityReport.to_dict,
    _is_malformed, _is_absolute, make_local_path_resolver.resolve,
    make_local_path_resolver, _inspect_link, validate_link_integrity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

from link_extraction import LinkInventory
from link_outcomes import Outcome, summarise
from link_rules import RewriteRuleset

Resolver = Callable[[str], bool]

_ABSOLUTE_SCHEMES = ("http://", "https://")


class LinkStatus:
    """Per-link verdicts."""

    OK = "Ok"
    RESIDUAL_LEGACY = "ResidualLegacy"
    MALFORMED = "Malformed"
    UNRESOLVABLE = "Unresolvable"
    EXTERNAL = "External"
    FORBIDDEN = "Forbidden"
    UNAVAILABLE = "Unavailable"


_HEALTHY = (LinkStatus.OK, LinkStatus.EXTERNAL)


@dataclass(frozen=True)
class LinkFinding:
    """One link's verdict, with the rewritten form it should have had when the
    ruleset still matches it."""

    source: str
    url: str
    status: str
    detail: str = ""
    expected: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize one link verdict and its expected rewritten form."""
        return {
            "source": self.source,
            "url": self.url,
            "status": self.status,
            "detail": self.detail,
            "expected": self.expected,
        }


@dataclass(frozen=True)
class IntegrityReport:
    """Evidence record for one integrity run."""

    findings: Sequence[LinkFinding] = field(default_factory=list)
    outcome: str = Outcome.EMPTY
    resolution_outcome: str = Outcome.NOT_SUPPORTED

    @property
    def residual_count(self) -> int:
        """Count links that still match a legacy rewrite rule."""
        return sum(1 for finding in self.findings if finding.status == LinkStatus.RESIDUAL_LEGACY)

    def to_dict(self) -> dict[str, Any]:
        """Serialize findings, resolution status, and residual-link count."""
        return {
            "outcome": self.outcome,
            "resolution_outcome": self.resolution_outcome,
            "link_count": len(self.findings),
            "residual_count": self.residual_count,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def _is_malformed(url: str) -> bool:
    """Reject empty, whitespace-containing, and incomplete absolute URLs."""
    candidate = url.strip()
    if not candidate or any(character.isspace() for character in candidate):
        return True
    if candidate.startswith("://"):
        return True
    for scheme in _ABSOLUTE_SCHEMES:
        if candidate.lower().startswith(scheme) and not candidate[len(scheme):].strip("/"):
            return True
    return False


def _is_absolute(url: str) -> bool:
    """Recognize HTTP and HTTPS URLs excluded from local resolution."""
    return url.lower().startswith(_ABSOLUTE_SCHEMES)


def make_local_path_resolver(root: str | Path) -> Resolver:
    """Build a resolver that checks server-relative links against a real
    directory tree on disk (e.g. an exported site). Links that would escape the
    root never resolve."""
    base = Path(root).resolve()

    def resolve(url: str) -> bool:
        """Resolve one server-relative path without allowing root traversal."""
        relative = url.split("?", 1)[0].split("#", 1)[0].lstrip("/")
        if not relative:
            return False
        try:
            candidate = (base / relative).resolve()
        except OSError:
            return False
        if base != candidate and base not in candidate.parents:
            return False
        return candidate.exists()

    return resolve


def _inspect_link(
    source: str,
    url: str,
    ruleset: RewriteRuleset,
    resolver: Resolver | None,
) -> tuple[LinkFinding, int, int, bool, bool]:
    """Return one link verdict and its resolution/error counters."""
    if _is_malformed(url):
        return LinkFinding(source, url, LinkStatus.MALFORMED, detail="url is not parseable"), 0, 0, False, False
    matching = ruleset.matches(url)
    if matching:
        return (
            LinkFinding(
                source, url, LinkStatus.RESIDUAL_LEGACY,
                detail=f"rewrite rule still matches: {matching[0].match}",
                expected=ruleset.apply(url)[0],
            ),
            0, 0, False, False,
        )
    if _is_absolute(url):
        return LinkFinding(source, url, LinkStatus.EXTERNAL), 0, 0, False, False
    if resolver is None:
        return LinkFinding(source, url, LinkStatus.OK), 0, 0, False, False
    try:
        exists = resolver(url)
    except PermissionError as exc:
        return LinkFinding(source, url, LinkStatus.FORBIDDEN, detail=str(exc)), 0, 1, True, False
    except Exception as exc:  # noqa: BLE001 -- caller-supplied resolver
        return LinkFinding(source, url, LinkStatus.UNAVAILABLE, detail=str(exc)), 0, 1, False, True
    if exists:
        return LinkFinding(source, url, LinkStatus.OK), 1, 0, False, False
    return LinkFinding(source, url, LinkStatus.UNRESOLVABLE, detail="target not found"), 0, 1, False, False


def validate_link_integrity(
    inventory: LinkInventory,
    ruleset: RewriteRuleset,
    *,
    resolver: Resolver | None = None,
) -> IntegrityReport:
    """Verify every link in ``inventory`` against ``ruleset`` (and, optionally,
    against an injected resolver)."""
    findings: list[LinkFinding] = []
    resolved_ok = 0
    resolved_bad = 0
    forbidden = False
    unavailable = False

    for link in inventory.links:
        finding, ok_count, bad_count, was_forbidden, was_unavailable = _inspect_link(
            link.source, link.url, ruleset, resolver
        )
        findings.append(finding)
        resolved_ok += ok_count
        resolved_bad += bad_count
        forbidden = forbidden or was_forbidden
        unavailable = unavailable or was_unavailable

    if resolver is None:
        resolution_outcome = Outcome.NOT_SUPPORTED
    elif resolved_ok == 0 and forbidden:
        resolution_outcome = Outcome.FORBIDDEN
    elif resolved_ok == 0 and unavailable:
        resolution_outcome = Outcome.UNAVAILABLE
    else:
        resolution_outcome = summarise(resolved_ok, resolved_bad)

    healthy = sum(1 for finding in findings if finding.status in _HEALTHY)
    unhealthy = len(findings) - healthy

    return IntegrityReport(
        findings=list(findings),
        outcome=summarise(healthy, unhealthy),
        resolution_outcome=resolution_outcome,
    )
