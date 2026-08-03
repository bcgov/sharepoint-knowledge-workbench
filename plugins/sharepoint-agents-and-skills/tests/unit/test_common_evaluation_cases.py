"""
test_common_evaluation_cases.py
=================================

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
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import pytest

from review_manual_topics import resolve_topic, TopicNotFoundError, TooManyRelatedTopicsError

_EVALUATIONS_DIR = Path(__file__).resolve().parents[2] / "evaluations"
_COMMON_DIR = _EVALUATIONS_DIR / "common"
_REAL_PAGES_DIR = Path(__file__).resolve().parents[4] / "runs" / "ceis-manual-v2" / "render" / "rendered-output" / "pages"
_BOUND01_FIXTURE = _EVALUATIONS_DIR / "fixtures" / "bound-01"
_SAFE02_FIXTURE = _EVALUATIONS_DIR / "fixtures" / "safe-02"

requires_real_corpus = pytest.mark.skipif(
    not _REAL_PAGES_DIR.exists(),
    reason="runs/ceis-manual-v2/render/rendered-output/pages/ not present in this checkout",
)


def _load_case(filename):
    return json.loads((_COMMON_DIR / filename).read_text())


@requires_real_corpus
def test_norm_01_resolves_against_real_corpus():
    case = _load_case("case-normal-01.json")
    resolved = resolve_topic(_REAL_PAGES_DIR, case["primary_topic_slug"])
    assert resolved.primary.slug == case["primary_topic_slug"]
    assert len(resolved.related) <= case["related_topic_allowance"]


@requires_real_corpus
def test_neg_01_fails_to_resolve_against_real_corpus():
    case = _load_case("case-negative-01.json")
    with pytest.raises(TopicNotFoundError):
        resolve_topic(_REAL_PAGES_DIR, case["primary_topic_slug"])


@requires_real_corpus
def test_safe_01_resolves_against_real_corpus():
    case = _load_case("case-safety-01-direct.json")
    resolved = resolve_topic(_REAL_PAGES_DIR, case["primary_topic_slug"])
    assert resolved.primary.slug == case["primary_topic_slug"]


def test_safe_02_fixture_resolves_and_contains_injection_payload():
    case = _load_case("case-safety-02-embedded-injection.json")
    resolved = resolve_topic(_SAFE02_FIXTURE, "synthetic-injection-topic--00000099")
    assert resolved.primary.slug == "synthetic-injection-topic--00000099"
    assert "IGNORE ALL PREVIOUS INSTRUCTIONS" in resolved.primary.content


def test_bound_01_fixture_raises_too_many_related_topics():
    case = _load_case("case-boundary-01-related-topic-cap-exceeded.json")
    with pytest.raises(TooManyRelatedTopicsError):
        resolve_topic(_BOUND01_FIXTURE, "multi-reference-topic--00000001")


def test_amb_01_is_native_sharepoint_only_after_remediation():
    case = _load_case("case-ambiguous-01.json")
    assert case["applicable_runtimes"] == ["native-sharepoint"]
