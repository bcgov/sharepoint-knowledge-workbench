"""Executable tests for create-sharepoint-agent.ps1, run via pwsh (zero tenant I/O)."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "create-sharepoint-agent.ps1"

pwsh = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(pwsh is None, reason="pwsh not installed")


def run_script(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_writes_valid_agent_json(tmp_path):
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


def test_requires_at_least_one_knowledge_source(tmp_path):
    out = tmp_path / "x.agent"
    result = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command",
         f"& '{SCRIPT}' -AgentName 'X' -AgentDescription 'x' -AgentInstructions 'x' "
         f"-KnowledgeSourcePaths @() -OutputPath '{out}'"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert not out.exists()


def test_refuses_to_overwrite_without_flag(tmp_path):
    out = tmp_path / "x.agent"
    out.write_text("existing")
    result = run_script([
        "-AgentName", "X", "-AgentDescription", "x", "-AgentInstructions", "x",
        "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/test",
        "-OutputPath", str(out),
    ])
    assert result.returncode != 0
    assert out.read_text() == "existing"


def test_both_instruction_sources_rejected(tmp_path):
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


def test_custom_list_and_folder_capability_types(tmp_path):
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

