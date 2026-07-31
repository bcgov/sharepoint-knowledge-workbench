"""Contract test suite for review-manual-topics SKILL.md native SharePoint skill.

Enforces specification requirements for Phase 4 native SharePoint skill authoring:
- Valid YAML frontmatter (name, description)
- Input resolution order & single-topic focus with max 2 related topics
- Prohibited scopes (read-only, no write/hash/package/link validation, no auto-approval, no prompt injection)
- Honest metadata unavailable phrasing & cross-reference terminology
- Human recommendation boundaries
- No live tenant URLs, GUIDs, app IDs, or command execution instructions
"""

import re
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_PATH = (
    REPO_ROOT
    / "tools"
    / "phase-4-native-sharepoint-skills"
    / "skills"
    / "review-manual-topics"
    / "SKILL.md"
)


def get_skill_content() -> str:
    assert SKILL_PATH.exists(), f"SKILL.md must exist at path: {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


def parse_frontmatter(content: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    assert match is not None, "SKILL.md must contain valid YAML frontmatter between '---' markers"
    yaml_text = match.group(1)
    data = yaml.safe_load(yaml_text)
    assert isinstance(data, dict), "YAML frontmatter must parse to a dictionary"
    return data


def test_frontmatter_contract():
    content = get_skill_content()
    fm = parse_frontmatter(content)
    assert fm.get("name") == "review-manual-topics", "Frontmatter 'name' must be 'review-manual-topics'"
    description = fm.get("description")
    assert description and isinstance(description, str) and len(description.strip()) > 10, (
        "Frontmatter 'description' must be a non-empty string"
    )


def test_input_resolution_hierarchy():
    content = get_skill_content()
    # Hierarchy order: (1) selected SharePoint file/context, (2) explicit filename or URL, (3) Topic ID
    content_lower = content.lower()
    assert "selected sharepoint file" in content_lower or "selected topic" in content_lower
    assert "filename or url" in content_lower or "explicit topic file url" in content_lower or "explicit filename" in content_lower
    assert "topic id" in content_lower
    assert "unique resolution" in content_lower or "resolve the topic id reliably" in content_lower or "proves unique resolution" in content_lower


def test_cardinality_and_evidence_limits():
    content = get_skill_content()
    content_lower = content.lower()

    # Single-topic primary subject rule
    assert "exactly one" in content_lower or "single topic" in content_lower or "one explicitly selected" in content_lower

    # Max 2 related topics evidence limit
    assert "up to 2" in content_lower or "max 2" in content_lower or "maximum 2" in content_lower or "up to two" in content_lower


def test_prohibited_scopes():
    content = get_skill_content()
    content_lower = content.lower()

    # Prohibited write / edit actions
    assert "no write" in content_lower or "do not perform" in content_lower or "read-only" in content_lower or "prohibited" in content_lower

    # No scanning all 25 topics
    assert "25 topics" in content_lower or "all topics" in content_lower

    # No hash recalculation / cryptographic proofs
    assert "hash" in content_lower

    # No canonical package identity proofs
    assert "canonical package" in content_lower

    # No deterministic technical link validation
    assert "technical link" in content_lower or "deterministic" in content_lower

    # No automatic approval or publication
    assert "auto" in content_lower or "approve" in content_lower or "publish" in content_lower

    # No prompt injection
    assert "prompt injection" in content_lower or "embedded prompt" in content_lower


def test_honest_metadata_language():
    content = get_skill_content()

    # Must contain honest metadata unavailable phrasing
    phrase_1 = "This metadata field was not available through the tested agent context, so metadata integrity was not evaluated."
    phrase_2 = "Metadata integrity not evaluated because the required field was not available through the tested agent context."

    assert (phrase_1 in content) or (phrase_2 in content), (
        "SKILL.md must include honest metadata unavailable phrasing"
    )


test_cross_reference_terminology_cases = [
    "REFERENCE_RETRIEVED",
    "REFERENCE_NOT_RETRIEVED",
    "REFERENCE_INACCESSIBLE",
    "REFERENCE_AMBIGUOUS",
    "REFERENCE_SEMANTICALLY_INCONSISTENT",
]


@pytest.mark.parametrize("term", test_cross_reference_terminology_cases)
def test_cross_reference_terms(term: str):
    content = get_skill_content()
    assert term in content, f"SKILL.md must contain cross-reference term '{term}'"


def test_logical_output_structure_sections():
    content = get_skill_content()

    required_sections = [
        "Topic reviewed",
        "Related evidence consulted",
        "Summary assessment",
        "Completeness findings",
        "Cross-reference findings",
        "Ambiguities or conflicts",
        "Unable to evaluate items",
        "Recommended human follow-up",
        "Source citations",
    ]

    for sec in required_sections:
        assert sec in content, f"Logical output structure must include '{sec}' section header/item"


def test_human_recommendation_boundary():
    content = get_skill_content()
    content_lower = content.lower()

    assert "recommend" in content_lower
    assert "human" in content_lower


def test_no_sensitive_or_execution_artifacts():
    content = get_skill_content()

    # No live https:// URLs
    assert "https://" not in content, "SKILL.md must not contain live https:// URLs"

    # No GUIDs
    guid_pattern = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
    assert not guid_pattern.search(content), "SKILL.md must not contain GUIDs"

    # No command execution instructions (PnP PowerShell, CLI commands, etc.)
    forbidden_cmds = [
        "Connect-PnPOnline",
        "Add-PnPFile",
        "Get-PnPListItem",
        "m365 ",
        "curl ",
        "Invoke-RestMethod",
        "pip install",
        "npm install",
    ]
    for cmd in forbidden_cmds:
        assert cmd not in content, f"SKILL.md must not contain command execution instruction '{cmd}'"
