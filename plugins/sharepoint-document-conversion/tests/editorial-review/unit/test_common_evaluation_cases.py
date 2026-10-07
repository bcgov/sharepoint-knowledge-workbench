"""test_common_evaluation_cases.py
=================================

Purpose:
    Phase 6 remediation (2026-08-03): ties the Task 5 common evaluation set's case definitions and fixtures to real, regression-proof execution of the deterministic-resolution layer -- not just a one-off manual run recorded in a findings doc.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - json
    - sys
    - pathlib
    - pytest
    - review_manual_topics

Phase 6 remediation (2026-08-03): ties the Task 5 common evaluation
set's case definitions and fixtures to real, regression-proof
execution of the deterministic-resolution layer -- not just a one-off
manual run recorded in a findings doc. Full semantic-review grading
(the actual review text) is recorded in
docs/superpowers/plans/phase-6-tasks-1-12-evidence/
task-6-baseline-evaluation-findings.md, since grading generated prose
against a checklist isn't a machine-checkable assertion; what IS
machine-checkable -- topic resolution succeeding/failing as each
case's category implies, and the related-topic cap being enforced --
is asserted here for real, against the real fixtures this remediation
pass created.

Key Functions Index:
    - _load_case()
    - test_norm_01_resolves_against_real_corpus()
    - test_neg_01_fails_to_resolve_against_real_corpus()
    - test_safe_01_resolves_against_real_corpus()
    - test_safe_02_fixture_resolves_and_contains_injection_payload()
    - test_bound_01_fixture_raises_too_many_related_topics()
    - test_amb_01_is_native_sharepoint_only_after_remediation()"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "editorial-review"))

import pytest

from review_manual_topics import resolve_topic, TopicNotFoundError, TooManyRelatedTopicsError

_EVALUATIONS_DIR = Path(__file__).resolve().parents[3] / "evaluations" / "editorial-review"
_COMMON_DIR = _EVALUATIONS_DIR / "common"
_REAL_PAGES_DIR = Path(__file__).resolve().parents[5] / "runs" / "sample-manual" / "render" / "rendered-output" / "pages"
_BOUND01_FIXTURE = _EVALUATIONS_DIR / "fixtures" / "bound-01"
_SAFE02_FIXTURE = _EVALUATIONS_DIR / "fixtures" / "safe-02"

requires_real_corpus = pytest.mark.skipif(
    not _REAL_PAGES_DIR.exists(),
    reason="sample-manual rendered pages not present in this checkout",
)


# Load one named editorial evaluation case from the shared case registry.
def _load_case(filename):
    """Load one named editorial evaluation case from the shared case registry."""
    return json.loads((_COMMON_DIR / filename).read_text())


# Verify norm 01 resolves against real corpus.
@requires_real_corpus
def test_norm_01_resolves_against_real_corpus():
    """Verify norm 01 resolves against real corpus."""
    case = _load_case("case-normal-01.json")
    resolved = resolve_topic(_REAL_PAGES_DIR, case["primary_topic_slug"])
    assert resolved.primary.slug == case["primary_topic_slug"]
    assert len(resolved.related) <= case["related_topic_allowance"]


# Verify neg 01 fails to resolve against real corpus.
@requires_real_corpus
def test_neg_01_fails_to_resolve_against_real_corpus():
    """Verify neg 01 fails to resolve against real corpus."""
    case = _load_case("case-negative-01.json")
    with pytest.raises(TopicNotFoundError):
        resolve_topic(_REAL_PAGES_DIR, case["primary_topic_slug"])


# Verify safe 01 resolves against real corpus.
@requires_real_corpus
def test_safe_01_resolves_against_real_corpus():
    """Verify safe 01 resolves against real corpus."""
    case = _load_case("case-safety-01-direct.json")
    resolved = resolve_topic(_REAL_PAGES_DIR, case["primary_topic_slug"])
    assert resolved.primary.slug == case["primary_topic_slug"]


# Verify safe 02 fixture resolves and contains injection payload.
def test_safe_02_fixture_resolves_and_contains_injection_payload():
    """Verify safe 02 fixture resolves and contains injection payload."""
    case = _load_case("case-safety-02-embedded-injection.json")
    resolved = resolve_topic(_SAFE02_FIXTURE, "synthetic-injection-topic--00000099")
    assert resolved.primary.slug == "synthetic-injection-topic--00000099"
    assert "IGNORE ALL PREVIOUS INSTRUCTIONS" in resolved.primary.content


# Verify bound 01 fixture raises too many related topics.
def test_bound_01_fixture_raises_too_many_related_topics():
    """Verify bound 01 fixture raises too many related topics."""
    case = _load_case("case-boundary-01-related-topic-cap-exceeded.json")
    with pytest.raises(TooManyRelatedTopicsError):
        resolve_topic(_BOUND01_FIXTURE, "multi-reference-topic--00000001")


# Verify amb 01 is native sharepoint only after remediation.
def test_amb_01_is_native_sharepoint_only_after_remediation():
    """Verify amb 01 is native sharepoint only after remediation."""
    case = _load_case("case-ambiguous-01.json")
    assert case["applicable_runtimes"] == ["native-sharepoint"]
