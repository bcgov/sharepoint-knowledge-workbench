"""Purpose:
    Exercise local agent updates while preserving unrelated configuration.

Key Input Dependencies:
    - scripts/create-sharepoint-agent.ps1 and scripts/update-sharepoint-agent.ps1
    - temporary agent JSON files
    - PowerShell (pwsh) when available

Executable tests for update-sharepoint-agent.ps1 (zero tenant I/O).

Function Index:
    - existing_agent
    - run_update
    - test_updates_description_without_recreating
    - test_updates_knowledge_sources_replacing_existing
    - test_fails_on_missing_agent_path
    - test_no_update_parameters_is_rejected
    - test_empty_knowledge_sources_requires_explicit_allow
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

CREATE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "create-sharepoint-agent.ps1"
UPDATE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "update-sharepoint-agent.ps1"

pwsh = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(pwsh is None, reason="pwsh not installed")


# Create a valid local agent artifact that update tests can modify.
@pytest.fixture()
def existing_agent(tmp_path):
    """Create a valid local agent artifact that update tests can modify."""
    out = tmp_path / "agent.agent"
    subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", str(CREATE_SCRIPT),
         "-AgentName", "Original", "-AgentDescription", "Original description.",
         "-AgentInstructions", "Original instructions.",
         "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/test",
         "-OutputPath", str(out)],
        capture_output=True, text=True, check=True,
    )
    return out


# Run the agent-update PowerShell script and return its captured process result.
def run_update(args: list[str]) -> subprocess.CompletedProcess:
    """Run the agent-update PowerShell script and return its captured process result."""
    return subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", str(UPDATE_SCRIPT), *args],
        capture_output=True, text=True,
    )


# Verify that updates description without recreating.
def test_updates_description_without_recreating(existing_agent):
    """Verify that updates description without recreating."""
    result = run_update(["-AgentPath", str(existing_agent), "-AgentDescription", "New description."])
    assert result.returncode == 0, result.stderr
    data = json.loads(existing_agent.read_text())
    gpt = data["customCopilotConfig"]["gptDefinition"]
    assert gpt["description"] == "New description."
    assert gpt["instructions"] == "Original instructions."  # unchanged


# Verify that updates knowledge sources replacing existing.
def test_updates_knowledge_sources_replacing_existing(existing_agent):
    """Verify that updates knowledge sources replacing existing."""
    result = run_update([
        "-AgentPath", str(existing_agent),
        "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/new",
    ])
    assert result.returncode == 0, result.stderr
    data = json.loads(existing_agent.read_text())
    urls = [i["url"] for i in data["customCopilotConfig"]["gptDefinition"]["capabilities"][0]["items_by_url"]]
    assert urls == ["https://example.sharepoint.com/sites/new"]


# Verify that fails on missing agent path.
def test_fails_on_missing_agent_path(tmp_path):
    """Verify that fails on missing agent path."""
    result = run_update(["-AgentPath", str(tmp_path / "nope.agent"), "-AgentDescription", "x"])
    assert result.returncode != 0


# Verify that no update parameters is rejected.
def test_no_update_parameters_is_rejected(existing_agent):
    """Verify that no update parameters is rejected."""
    result = run_update(["-AgentPath", str(existing_agent)])
    assert result.returncode != 0


# Verify that empty knowledge sources requires explicit allow.
def test_empty_knowledge_sources_requires_explicit_allow(existing_agent):
    """Verify that empty knowledge sources requires explicit allow."""
    result = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command",
         f"& '{UPDATE_SCRIPT}' -AgentPath '{existing_agent}' -KnowledgeSourcePaths @()"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
