"""Executable tests for create-sharepoint-agent-template.ps1 and apply-sharepoint-agent-template.ps1."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
CREATE_TEMPLATE = SCRIPTS / "create-sharepoint-agent-template.ps1"
APPLY_TEMPLATE = SCRIPTS / "apply-sharepoint-agent-template.ps1"

pwsh = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(pwsh is None, reason="pwsh not installed")


def run(script: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", str(script), *args],
        capture_output=True, text=True,
    )


def test_creates_valid_template(tmp_path):
    out = tmp_path / "template.json"
    result = run(CREATE_TEMPLATE, [
        "-TemplateName", "example-template",
        "-Purpose", "Answer questions about a knowledge base.",
        "-InstructionsTemplate", "## Purpose\n\nAnswer based on grounded content only.",
        "-AnswerBoundary", "Only answer from grounded sources.",
        "-RefusalBehavior", "Decline politely if out of scope.",
        "-CitationExpectations", "Always cite the source page.",
        "-KnowledgeSourcePlaceholderCount", "1",
        "-TemplateVersion", "1.0.0",
        "-OutputPath", str(out),
    ])
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text())
    assert data["templateName"] == "example-template"
    assert data["knowledgeSourcePlaceholderCount"] == 1


def test_apply_produces_valid_agent_with_correct_source_count(tmp_path):
    template_path = tmp_path / "template.json"
    run(CREATE_TEMPLATE, [
        "-TemplateName", "example-template",
        "-Purpose", "x",
        "-InstructionsTemplate", "Base instructions.",
        "-KnowledgeSourcePlaceholderCount", "2",
        "-TemplateVersion", "1.0.0",
        "-OutputPath", str(template_path),
    ])

    # NOTE: -File mode's positional binding for a multi-value array parameter followed by more
    # named parameters is unreliable (confirmed via direct reproduction outside pytest too) --
    # -Command with an explicit @(...) array literal is the correct, reliable invocation style
    # for multi-value array parameters. This is a PowerShell CLI-parsing characteristic, not a
    # script defect (single-value array parameters work fine under -File, see
    # test_create_sharepoint_agent.py).
    agent_out = tmp_path / "concrete-agent.agent"
    result = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command",
         f"& '{APPLY_TEMPLATE}' -TemplatePath '{template_path}' -AgentName 'Concrete Agent' "
         f"-AgentDescription 'Applied from template.' "
         f"-KnowledgeSourcePaths @('https://example.sharepoint.com/sites/a','https://example.sharepoint.com/sites/b') "
         f"-OutputPath '{agent_out}'"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(agent_out.read_text())
    gpt = data["customCopilotConfig"]["gptDefinition"]
    assert gpt["name"] == "Concrete Agent"
    urls = [i["url"] for i in gpt["capabilities"][0]["items_by_url"]]
    assert len(urls) == 2
    assert "Base instructions." in gpt["instructions"]


def test_apply_rejects_wrong_knowledge_source_count(tmp_path):
    template_path = tmp_path / "template.json"
    run(CREATE_TEMPLATE, [
        "-TemplateName", "example-template",
        "-Purpose", "x",
        "-InstructionsTemplate", "Base.",
        "-KnowledgeSourcePlaceholderCount", "2",
        "-TemplateVersion", "1.0.0",
        "-OutputPath", str(template_path),
    ])
    agent_out = tmp_path / "agent.agent"
    result = run(APPLY_TEMPLATE, [
        "-TemplatePath", str(template_path),
        "-AgentName", "X", "-AgentDescription", "x",
        "-KnowledgeSourcePaths", "https://example.sharepoint.com/sites/a",
        "-OutputPath", str(agent_out),
    ])
    assert result.returncode != 0
    assert not agent_out.exists()


def test_create_template_requires_positive_placeholder_count(tmp_path):
    out = tmp_path / "template.json"
    result = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command",
         f"& '{CREATE_TEMPLATE}' -TemplateName t -Purpose p -InstructionsTemplate i "
         f"-KnowledgeSourcePlaceholderCount 0 -TemplateVersion 1.0.0 -OutputPath '{out}'"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert not out.exists()
