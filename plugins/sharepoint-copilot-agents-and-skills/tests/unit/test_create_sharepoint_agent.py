"""Purpose:
    Exercise local SharePoint agent JSON creation and its validation safeguards.

Key Input Dependencies:
    - scripts/create-sharepoint-agent.ps1
    - PowerShell (pwsh) when available

Executable tests for create-sharepoint-agent.ps1, run via pwsh (zero tenant I/O).

Function Index:
    - run_script
    - test_writes_valid_agent_json
    - test_requires_at_least_one_knowledge_source
    - test_refuses_to_overwrite_without_flag
    - test_both_instruction_sources_rejected
    - test_custom_list_and_folder_capability_types
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "create-sharepoint-agent.ps1"

pwsh = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(pwsh is None, reason="pwsh not installed")


# Run the agent-creation PowerShell script with the supplied arguments.
def run_script(args: list[str]) -> subprocess.CompletedProcess:
    """Run the agent-creation PowerShell script with the supplied arguments."""
    return subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


# The command writes valid agent JSON with the requested name and knowledge-source URL.
def test_writes_valid_agent_json(tmp_path):
    """The command writes valid agent JSON with the requested name and knowledge-source URL."""
    out = tmp_path / "example-agent.agent"
    result = run_script([
        "-AgentName", "Example Agent",
        "-AgentDescription", "Helps with example content.",
        "-AgentInstructions", "Provide accurate information in a formal tone.",
        "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/test/Shared Documents",
        "-OutputPath", str(out),
    ])
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text())
    assert data["schemaVersion"] == "0.2.0"
    gpt = data["customCopilotConfig"]["gptDefinition"]
    assert gpt["name"] == "Example Agent"
    assert gpt["behavior_overrides"]["special_instructions"]["discourage_model_knowledge"] is True
    urls = [item["url"] for item in gpt["capabilities"][0]["items_by_url"]]
    assert urls == ["https://example.sharepoint.com/sites/test/Shared Documents"]


# Agent creation rejects an empty knowledge-source list before writing output.
def test_requires_at_least_one_knowledge_source(tmp_path):
    """Agent creation rejects an empty knowledge-source list before writing output."""
    out = tmp_path / "x.agent"
    result = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command",
         f"& '{SCRIPT}' -AgentName 'X' -AgentDescription 'x' -AgentInstructions 'x' "
         f"-KnowledgeSourcePaths @() -OutputPath '{out}'"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert not out.exists()


# An existing agent file is preserved unless overwrite is explicitly authorized.
def test_refuses_to_overwrite_without_flag(tmp_path):
    """An existing agent file is preserved unless overwrite is explicitly authorized."""
    out = tmp_path / "x.agent"
    out.write_text("existing")
    result = run_script([
        "-AgentName", "X", "-AgentDescription", "x", "-AgentInstructions", "x",
        "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/test",
        "-OutputPath", str(out),
    ])
    assert result.returncode != 0
    assert out.read_text() == "existing"


# Agent creation rejects simultaneous inline and file-based instruction sources.
def test_both_instruction_sources_rejected(tmp_path):
    """Agent creation rejects simultaneous inline and file-based instruction sources."""
    instr = tmp_path / "instr.md"
    instr.write_text("file instructions")
    out = tmp_path / "x.agent"
    result = run_script([
        "-AgentName", "X", "-AgentDescription", "x",
        "-AgentInstructions", "inline", "-AgentInstructionsPath", str(instr),
        "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/test",
        "-OutputPath", str(out),
    ])
    assert result.returncode != 0
    assert not out.exists()


# A custom list URL is emitted as a List capability with its list name.
def test_custom_list_and_folder_capability_types(tmp_path):
    """A custom list URL is emitted as a List capability with its list name."""
    out = tmp_path / "list-test.agent"
    result = run_script([
        "-AgentName", "List Agent",
        "-AgentDescription", "Helps with list content.",
        "-AgentInstructions", "Answer questions from list.",
        "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/test/Lists/CustomList",
        "-OutputPath", str(out),
    ])
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text())
    item = data["customCopilotConfig"]["gptDefinition"]["capabilities"][0]["items_by_url"][0]
    assert item["type"] == "List"
    assert item["unique_id"] == "00000000-0000-0000-0000-000000000000"
    assert item["list_id"] == "00000000-0000-0000-0000-000000000000"
    assert item["name"] == "CustomList"

