import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave0_classify_edges import classify_edge, classify_all


def test_cli_edge_classified_as_orchestration():
    assert classify_edge({"from": "scripts/cli.py", "to": "scripts/convert.py"}) == "CLI_ORCHESTRATION_EDGE"


def test_intra_domain_edge_classified():
    assert (
        classify_edge({"from": "scripts/convert.py", "to": "scripts/chunking.py"})
        == "CANONICAL_KNOWLEDGE_INTERNAL"
    )


def test_sharepoint_edge_classified_as_deferred():
    assert (
        classify_edge({"from": "scripts/sharepoint_cli.py", "to": "scripts/sharepoint_package.py"})
        == "SHAREPOINT_DEFERRED_EDGE"
    )


def test_shared_contract_candidate_target():
    assert (
        classify_edge({"from": "scripts/convert.py", "to": "scripts/hashing.py"})
        == "SHARED_CONTRACT_CANDIDATE"
    )


def test_unclassified_when_owner_unknown():
    assert (
        classify_edge({"from": "scripts/unknown_a.py", "to": "scripts/unknown_b.py"})
        == "UNCLASSIFIED_REQUIRES_HUMAN_DECISION"
    )


def test_classify_all_covers_every_edge_on_real_graph():
    import json

    evidence_dir = Path(__file__).resolve().parents[3] / "docs" / "superpowers" / "plans" / "phase-4-5-evidence"
    graph = json.loads((evidence_dir / "wave-0-dependency-graph.json").read_text())
    classified = classify_all(graph)
    assert len(classified) == len(graph["edges"])
    assert all("classification" in e for e in classified)
