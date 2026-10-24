"""
completeness_checks.py
========================

Purpose:
    Generic completeness checks for a dependency matrix, run BEFORE
    ``dependency_graph.build_dependency_matrix`` / ``wave_planning.
    plan_waves`` compute a deployment order. ``plan_waves`` already reports
    unresolved dependencies and cycles as blocking findings within the graph
    it is given -- these checks catch a different class of problem: the
    matrix itself silently not matching the source it claims to describe
    (an object present at the source but missing from the matrix, or a
    matrix entry with no corresponding source object because the source was
    renamed or removed and the matrix went stale).

    Generalized from a real 18-check completeness QA gate, keeping only the
    checks that are shape-agnostic (source coverage, orphan matrix entries,
    unresolved lookup targets, destination-name collisions). Deliberately
    NOT ported: project-specific business-rule checks tied to one source
    schema's own domain concepts (e.g. calendar structural consistency,
    legacy content-type substitution rules) -- those depend on knowledge
    this module has no business having.

Layer: sharepoint-site-migration / dependency-graph analysis (stage 3a)

Key Input Dependencies:
    - wave_planning.DeploymentObject (local to this plugin)
    - provisioning_outcomes.Outcome (symlinked from sharepoint-site-build-and-publish)

Function Index:
    CoverageCheckResult.orphans, CompletenessSummary.to_dict,
    check_source_coverage, check_orphan_matrix_entries,
    check_lookup_targets_exist, check_destination_name_collisions,
    run_all_checks
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from provisioning_outcomes import Outcome
from wave_planning import DeploymentObject


@dataclass(frozen=True)
class CoverageCheckResult:
    """Result of a set-membership completeness check (source coverage or
    orphan-entry detection). ``missing``/``orphans`` are the exact names,
    never a bare count -- callers must be able to act on the result
    directly."""

    outcome: str
    missing: tuple[str, ...] = ()

    @property
    def orphans(self) -> tuple[str, ...]:
        """Expose unmatched matrix names using the domain-specific term."""
        return self.missing


@dataclass(frozen=True)
class LookupTargetCheckResult:
    """``unresolved`` is a tuple of ``(object_name, missing_target_name)``
    pairs -- naming both sides so the caller knows exactly which
    dependency declaration to fix."""

    outcome: str
    unresolved: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CollisionCheckResult:
    outcome: str
    collisions: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompletenessSummary:
    outcome: str
    all_passed: bool
    failed_check_names: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        """Serialize the aggregate gate result and failed check identifiers."""
        return {
            "outcome": self.outcome,
            "all_passed": self.all_passed,
            "failed_check_names": list(self.failed_check_names),
        }


def check_source_coverage(*, matrix_names: set[str], source_names: set[str]) -> CoverageCheckResult:
    """Every object observed at the source must have a corresponding matrix
    entry -- an object missing from the matrix will silently never be
    deployed."""
    if not source_names and not matrix_names:
        return CoverageCheckResult(outcome=Outcome.EMPTY)
    missing = tuple(sorted(source_names - matrix_names))
    outcome = Outcome.FAILED if missing else Outcome.OBSERVED
    return CoverageCheckResult(outcome=outcome, missing=missing)


def check_orphan_matrix_entries(*, matrix_names: set[str], source_names: set[str]) -> CoverageCheckResult:
    """Every matrix entry must correspond to a real source object -- an
    entry with no source match usually means the source was renamed or
    removed and the matrix went stale. Report it; never silently ignore it
    (and never silently drop it from deployment either)."""
    if not source_names and not matrix_names:
        return CoverageCheckResult(outcome=Outcome.EMPTY)
    orphans = tuple(sorted(matrix_names - source_names))
    outcome = Outcome.FAILED if orphans else Outcome.OBSERVED
    return CoverageCheckResult(outcome=outcome, missing=orphans)


def check_lookup_targets_exist(objects: Sequence[DeploymentObject]) -> LookupTargetCheckResult:
    """Every ``dependsOn`` reference must resolve to another object in the
    same matrix. This overlaps with what ``wave_planning.plan_waves`` itself
    reports as an ``UNRESOLVED DEPENDENCY`` blocking finding -- this check
    exists to surface the same problem earlier, before a caller invests in
    building a full ``DeploymentObject`` graph and running the planner, and
    to report it in a structured (name, target) form rather than a prose
    string."""
    if not objects:
        return LookupTargetCheckResult(outcome=Outcome.EMPTY)

    names = {obj.name for obj in objects}
    unresolved: list[tuple[str, str]] = []
    for obj in objects:
        for dep in obj.depends_on:
            if dep not in names:
                unresolved.append((obj.name, dep))

    outcome = Outcome.FAILED if unresolved else Outcome.OBSERVED
    return LookupTargetCheckResult(outcome=outcome, unresolved=tuple(unresolved))


def check_destination_name_collisions(objects: Sequence[DeploymentObject]) -> CollisionCheckResult:
    """Two objects cannot declare the same name -- whichever a caller's
    deployment executor resolves second would silently overwrite or
    misidentify the first. Detected the same way ``list_provisioning``'s
    ``detect_duplicate_lists`` treats a duplicate title: a blocking finding,
    not a warning."""
    if not objects:
        return CollisionCheckResult(outcome=Outcome.EMPTY)

    seen: set[str] = set()
    collisions: list[str] = []
    for obj in objects:
        if obj.name in seen and obj.name not in collisions:
            collisions.append(obj.name)
        seen.add(obj.name)

    outcome = Outcome.FAILED if collisions else Outcome.OBSERVED
    return CollisionCheckResult(outcome=outcome, collisions=tuple(sorted(collisions)))


_CHECKS = ("source_coverage", "orphan_matrix_entries", "lookup_targets_exist", "destination_name_collisions")


def run_all_checks(objects: Sequence[DeploymentObject], *, source_names: set[str]) -> CompletenessSummary:
    """Run every completeness check and reduce to one honest summary --
    ``all_passed`` is true only when every individual check reported
    ``OBSERVED`` or ``EMPTY``; otherwise ``failed_check_names`` names exactly
    which check(s) failed, never just a single aggregate boolean."""
    matrix_names = {obj.name for obj in objects}

    results = {
        "source_coverage": check_source_coverage(matrix_names=matrix_names, source_names=source_names),
        "orphan_matrix_entries": check_orphan_matrix_entries(
            matrix_names=matrix_names, source_names=source_names
        ),
        "lookup_targets_exist": check_lookup_targets_exist(objects),
        "destination_name_collisions": check_destination_name_collisions(objects),
    }

    failed = tuple(name for name in _CHECKS if results[name].outcome == Outcome.FAILED)

    if all(results[name].outcome == Outcome.EMPTY for name in _CHECKS):
        outcome = Outcome.EMPTY
    elif failed:
        # A completeness gate is pass/fail as a whole -- any single failed
        # check blocks the matrix, it is never "partially complete".
        outcome = Outcome.FAILED
    else:
        outcome = Outcome.OBSERVED

    return CompletenessSummary(outcome=outcome, all_passed=not failed, failed_check_names=failed)
