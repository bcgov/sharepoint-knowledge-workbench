import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave0_classify_edges import (
    classify_edge,
    classify_all,
    validate_classified_edges,
    DEPENDENCY_CLASSIFICATIONS,
    PROPOSED_DOMAINS,
    DISPOSITIONS,
)


def test_cli_edge_classified_as_orchestration():
    e = classify_edge({"from": "scripts/cli.py", "to": "scripts/convert.py"})
    assert e["dependency_classification"] == "CLI_ORCHESTRATION"
    assert e["disposition"] == "PROVISIONALLY_ACCEPTED"


def test_intra_domain_edge_classified_as_valid_forward_dependency():
    e = classify_edge({"from": "scripts/chunking.py", "to": "scripts/canonical_package.py"})
    assert e["dependency_classification"] == "VALID_FORWARD_DEPENDENCY"
    assert e["proposed_source_domain"] == "CANONICAL_KNOWLEDGE"
    assert e["proposed_target_domain"] == "CANONICAL_KNOWLEDGE"
    assert e["disposition"] == "PROVISIONALLY_ACCEPTED"


def test_sharepoint_edge_classified_as_out_of_scope():
    e = classify_edge({"from": "scripts/sharepoint_cli.py", "to": "scripts/sharepoint_package.py"})
    assert e["proposed_source_domain"] == "OUT_OF_PHASE_4_5_SCOPE"
    assert e["disposition"] == "OUT_OF_SCOPE_RETAIN_IN_PLACE"


def test_shared_contract_target_classified():
    e = classify_edge({"from": "scripts/package.py", "to": "scripts/contracts.py"})
    assert e["dependency_classification"] == "SHARED_CONTRACT"
    assert e["proposed_target_domain"] == "NEUTRAL_CONTRACT_DISTRIBUTION"
    assert e["disposition"] == "PROVISIONALLY_ACCEPTED"


def test_split_pending_file_edge_requires_human_decision():
    e = classify_edge({"from": "scripts/chunking.py", "to": "scripts/analyze_structure.py"})
    assert e["proposed_target_domain"] == "UNRESOLVED"
    assert e["disposition"] == "REQUIRES_HUMAN_DECISION"


def test_presentation_coupling_requires_human_decision():
    e = classify_edge({"from": "scripts/renderers/protocol.py", "to": "scripts/canonical_package.py"})
    assert e["dependency_classification"] == "PRESENTATION_COUPLING"
    assert e["proposed_source_domain"] == "KNOWLEDGE_PUBLICATION"
    assert e["proposed_target_domain"] == "CANONICAL_KNOWLEDGE"
    assert e["disposition"] == "REQUIRES_HUMAN_DECISION"


def test_unresolved_owner_classified_as_historical_or_dead_requires_confirmation():
    e = classify_edge({"from": "scripts/unknown_a.py", "to": "scripts/unknown_b.py"})
    assert e["dependency_classification"] == "HISTORICAL_OR_DEAD"
    assert e["disposition"] == "HISTORICAL_OR_DEAD_REQUIRES_CONFIRMATION"


def test_every_edge_has_a_rationale():
    e = classify_edge({"from": "scripts/cli.py", "to": "scripts/convert.py"})
    assert isinstance(e["rationale"], str) and e["rationale"]


def test_classify_all_covers_every_edge_on_real_graph_with_no_validation_errors():
    import json

    evidence_dir = Path(__file__).resolve().parents[3] / "docs" / "superpowers" / "plans" / "phase-4-5-evidence"
    graph = json.loads((evidence_dir / "wave-0-dependency-graph.json").read_text())
    classified = classify_all(graph)
    assert len(classified) == len(graph["edges"]) == 58

    errors = validate_classified_edges(classified)
    assert errors == [], f"validation errors: {errors}"

    # No edge is left in a genuinely unclassified state — every dependency_classification and
    # proposed domain must be a real member of the approved vocabularies (checked above by
    # validate_classified_edges). UNRESOLVED itself is an allowed domain value (it marks edges
    # touching a file the plan's own Known File Inventory flags as split/duplicated, e.g.
    # analyze_structure.py) — it is not the same as "unclassified."

    # Cross-domain/pending-decision edges must remain visibly unresolved for Wave 1, not silently
    # decided during Wave 0.
    requires_decision = [e for e in classified if e["disposition"] == "REQUIRES_HUMAN_DECISION"]
    assert len(requires_decision) > 0
    for e in requires_decision:
        assert e["rationale"]


def test_validate_classified_edges_flags_bad_vocabulary():
    bad = [
        {
            "from": "a",
            "to": "b",
            "dependency_classification": "NOT_A_REAL_VALUE",
            "proposed_source_domain": "CANONICAL_KNOWLEDGE",
            "proposed_target_domain": "CANONICAL_KNOWLEDGE",
            "disposition": "PROVISIONALLY_ACCEPTED",
            "rationale": "x",
        }
    ]
    errors = validate_classified_edges(bad)
    assert len(errors) == 1
    assert "dependency_classification" in errors[0]


def test_vocabularies_have_expected_sizes():
    assert len(DEPENDENCY_CLASSIFICATIONS) == 9
    assert len(PROPOSED_DOMAINS) == 8
    assert len(DISPOSITIONS) == 4
