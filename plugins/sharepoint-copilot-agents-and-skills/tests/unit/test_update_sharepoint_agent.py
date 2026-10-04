"""Executable tests for update-sharepoint-agent.ps1 (zero tenant I/O)."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

CREATE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "create-sharepoint-agent.ps1"
UPDATE_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "update-sharepoint-agent.ps1"

pwsh = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(pwsh is None, reason="pwsh not installed")


@pytest.fixture()
def existing_agent(tmp_path):
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


def run_update(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", str(UPDATE_SCRIPT), *args],
        capture_output=True, text=True,
    )


def test_updates_description_without_recreating(existing_agent):
    result = run_update(["-AgentPath", str(existing_agent), "-AgentDescription", "New description."])
    assert result.returncode == 0, result.stderr
    data = json.loads(existing_agent.read_text())
    gpt = data["customCopilotConfig"]["gptDefinition"]
    assert gpt["description"] == "New description."
    assert gpt["instructions"] == "Original instructions."  # unchanged


def test_updates_knowledge_sources_replacing_existing(existing_agent):
    result = run_update([
        "-AgentPath", str(existing_agent),
        "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/new",
    ])
    assert result.returncode == 0, result.stderr
    data = json.loads(existing_agent.read_text())
    urls = [i["url"] for i in data["customCopilotConfig"]["gptDefinition"]["capabilities"][0]["items_by_url"]]
    assert urls == ["https://example.sharepoint.com/sites/new"]


def test_fails_on_missing_agent_path(tmp_path):
    result = run_update(["-AgentPath", str(tmp_path / "nope.agent"), "-AgentDescription", "x"])
    assert result.returncode != 0


def test_no_update_parameters_is_rejected(existing_agent):
    result = run_update(["-AgentPath", str(existing_agent)])
    assert result.returncode != 0


def test_empty_knowledge_sources_requires_explicit_allow(existing_agent):
    result = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command",
         f"& '{UPDATE_SCRIPT}' -AgentPath '{existing_agent}' -KnowledgeSourcePaths @()"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
