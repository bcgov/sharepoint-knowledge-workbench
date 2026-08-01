"""
Unit tests for Phase 4 metadata visibility probe generator and report template.
"""

import importlib.util
import re
import socket
from pathlib import Path
import pytest

# Load hyphenated module dynamically
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = (
    REPO_ROOT
    / "tools"
    / "phase-4-native-sharepoint-skills"
    / "deployment"
    / "scripts"
    / "probe-metadata-visibility.py"
)

spec = importlib.util.spec_from_file_location("probe_metadata_visibility", SCRIPT_PATH)
probe_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe_module)

TEST_FIELDS = probe_module.TEST_FIELDS
generate_probe_queries = probe_module.generate_probe_queries


def test_metadata_visibility_report_covers_all_7_fields():
    report_file = (
        REPO_ROOT
        / "docs"
        / "reports"
        / "phase-4-native-sharepoint-skills"
        / "metadata-visibility-report.md"
    )

    assert report_file.exists(), f"Report file must exist at {report_file}"
    content = report_file.read_text(encoding="utf-8")

    required_fields = [
        "TopicID",
        "PublicationOrder",
        "TopicContentSHA256",
        "Status",
        "ReviewDate",
        "TransitionAction",
        "TransitionTarget",
    ]
    for field in required_fields:
        assert field in content, f"Field '{field}' missing from report content"

    assert "Status: NOT_EXECUTED" in content

    classification_states = [
        "AVAILABLE_AS_STRUCTURED_METADATA",
        "AVAILABLE_THROUGH_RENDERED_OR_FILE_CONTENT",
        "VISIBLE_ONLY_IN_SHAREPOINT_UI",
        "INFERRED_NOT_VERIFIED",
        "NOT_OBSERVED",
        "INACCESSIBLE_TO_TEST_IDENTITY",
    ]
    for state in classification_states:
        assert state in content, f"Classification vocabulary '{state}' missing from report"


def test_probe_metadata_visibility_generator():
    topic_fn = "ceis-support-faq--218dfe1f.html"
    queries = generate_probe_queries(topic_fn)

    assert len(queries) == 7
    assert len(TEST_FIELDS) == 7

    fields_seen = [q["field"] for q in queries]
    assert fields_seen == TEST_FIELDS

    for q in queries:
        assert q["target_topic"] == topic_fn
        assert "field" in q
        assert "prompt" in q
        assert "rule" in q
        # Ensure no real 64-hex SHA-256 hash string is inside the prompt
        assert not re.search(r"\b[a-fA-F0-9]{64}\b", q["prompt"])

    sha_query = next(q for q in queries if q["field"] == "TopicContentSHA256")
    assert "TopicContentSHA256" in sha_query["prompt"]
    assert "Never include the real SHA-256 hash in the prompt" in sha_query["rule"]


def test_zero_network_calls(monkeypatch):
    def mock_socket_create_connection(*args, **kwargs):
        raise RuntimeError("Network calls strictly forbidden in test")

    monkeypatch.setattr(socket, "create_connection", mock_socket_create_connection)

    queries = generate_probe_queries("sample.html")
    assert len(queries) == 7
