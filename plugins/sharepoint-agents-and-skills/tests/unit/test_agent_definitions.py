"""
test_agent_definitions.py -- Orchestration contract for this plugin's `agents/` definitions.

Purpose:
    Phase 9 Wave 2 extracts four generic SharePoint routing agents from the CMAT
    `sharepoint-migration` plugin into this plugin's `agents/` directory. Agents are
    orchestration artifacts, not code, so per `.agent/rules/test-driven-development.md`'s
    Test-Driven Orchestration section the contract is asserted as an output-schema /
    boundary-invariance check written before the artifacts themselves:

      1. Required frontmatter schema (name/plugin/description/model/color) and
         name-matches-filename.
      2. Genericity contract (spec Sec.9): zero project literals, zero source-repository
         paths, zero tenant URLs/GUIDs.
      3. No dangling capability references -- every hyphenated inline-code token an agent
         routes to must resolve to a real skill or plugin in THIS repository, or be
         explicitly declared under the agent's "Not available in this workbench" section.
      4. Manifest registration -- plugin.yaml lists every agent file.

Layer: Plugin tests (unit)

Key Input Dependencies:
    - plugins/sharepoint-agents-and-skills/agents/*.md
    - plugins/sharepoint-agents-and-skills/plugin.yaml
    - plugins/*/skills/* (capability-reference resolution)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = PLUGIN_ROOT.parent
AGENTS_DIR = PLUGIN_ROOT / "agents"

EXPECTED_AGENTS = {
    "sharepoint-link-agent",
    "sharepoint-modernization-agent",
    "sharepoint-schema-agent",
    "sharepoint-validation-agent",
    "sharepoint-deployment-planning-agent",
    "sharepoint-deployment-sequencing-agent",
    "sharepoint-content-migration-sequencing-agent",
}

REQUIRED_FRONTMATTER_FIELDS = ("name", "plugin", "description", "model", "color")

# Spec Sec.8h literal set, plus the source project's own identifiers. Word-bounded so
# ordinary English ("appearances", "picompute") cannot produce false negatives OR
# false positives.
FORBIDDEN_LITERALS = re.compile(
    r"\b(JUSTIN|CEIS|ORDS|courthouse|appearance|AG-CSB|ITAU|PIO|ICM|CMAT|wave|bcgov|"
    r"jag-csb|sharepoint-migration)\b",
    re.IGNORECASE,
)

# Source-repository coupling: CMAT's relative-traversal script paths must not survive.
FORBIDDEN_PATH_PATTERNS = re.compile(r"(\.\./\.\./\.\./|plugins/sharepoint-migration)")

GUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)

TENANT_URL = re.compile(r"[A-Za-z0-9-]+\.sharepoint\.com")

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

INLINE_CODE = re.compile(r"`([^`]+)`")

NOT_AVAILABLE_HEADING = "## Not available in this workbench"


def _agent_files() -> list[Path]:
    return sorted(AGENTS_DIR.glob("*.md")) if AGENTS_DIR.is_dir() else []


def _frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML frontmatter reader -- flat scalars and `>`-folded blocks only."""
    match = FRONTMATTER.match(text)
    assert match, "agent file must open with a `---` frontmatter block"
    fields: dict[str, str] = {}
    key = None
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t")) and key:
            fields[key] = (fields[key] + " " + line.strip()).strip()
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        fields[key] = value.strip().lstrip(">").strip()
    return fields


def _body(text: str) -> str:
    match = FRONTMATTER.match(text)
    return text[match.end():] if match else text


def _known_capability_names() -> set[str]:
    names: set[str] = set()
    for plugin_dir in PLUGINS_DIR.iterdir():
        if not plugin_dir.is_dir():
            continue
        names.add(plugin_dir.name)
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            names.update(d.name for d in skills_dir.iterdir() if d.is_dir())
        agents_dir = plugin_dir / "agents"
        if agents_dir.is_dir():
            names.update(f.stem for f in agents_dir.glob("*.md"))
    return names


def _declared_unavailable(body: str) -> set[str]:
    """Capability names an agent explicitly declares as not-yet-built here."""
    if NOT_AVAILABLE_HEADING not in body:
        return set()
    section = body.split(NOT_AVAILABLE_HEADING, 1)[1]
    section = re.split(r"\n## ", section, maxsplit=1)[0]
    return {token for token in INLINE_CODE.findall(section) if "-" in token}


def test_expected_agents_exist():
    assert AGENTS_DIR.is_dir(), f"missing agents directory: {AGENTS_DIR}"
    assert {p.stem for p in _agent_files()} == EXPECTED_AGENTS


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_agent_frontmatter_schema(path: Path):
    fields = _frontmatter(path.read_text(encoding="utf-8"))
    missing = [f for f in REQUIRED_FRONTMATTER_FIELDS if not fields.get(f)]
    assert not missing, f"{path.name}: missing/empty frontmatter fields {missing}"
    assert fields["name"] == path.stem, f"{path.name}: `name` must match the filename stem"
    assert fields["plugin"] == "sharepoint-agents-and-skills"


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_agent_has_no_project_literals(path: Path):
    hits = sorted(set(FORBIDDEN_LITERALS.findall(path.read_text(encoding="utf-8"))))
    assert not hits, f"{path.name}: forbidden project literals {hits}"


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_agent_has_no_source_repository_coupling(path: Path):
    text = path.read_text(encoding="utf-8")
    assert not FORBIDDEN_PATH_PATTERNS.search(text), f"{path.name}: source-repository path"
    assert not GUID.search(text), f"{path.name}: literal GUID"
    assert not TENANT_URL.search(text), f"{path.name}: tenant URL"


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_agent_has_no_dangling_capability_references(path: Path):
    body = _body(path.read_text(encoding="utf-8"))
    known = _known_capability_names() | _declared_unavailable(body)
    referenced = {
        token
        for token in INLINE_CODE.findall(body)
        if re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+", token)
    }
    dangling = sorted(referenced - known)
    assert not dangling, (
        f"{path.name}: references capabilities that do not exist here and are not declared "
        f"under '{NOT_AVAILABLE_HEADING}': {dangling}"
    )


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_agent_declares_honest_unavailability_section(path: Path):
    """Boundary invariance: an agent may never imply automated coverage it lacks."""
    body = _body(path.read_text(encoding="utf-8"))
    assert NOT_AVAILABLE_HEADING in body, (
        f"{path.name}: must carry a '{NOT_AVAILABLE_HEADING}' section, even if it lists "
        "nothing, so no routing target is silently assumed to be implemented"
    )


def test_plugin_manifest_registers_every_agent():
    manifest = (PLUGIN_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    section = manifest.split("agents:", 1)
    assert len(section) == 2, "plugin.yaml must declare an `agents:` list"
    listed = set(re.findall(r"^\s+-\s+([a-z0-9-]+)\s*$", section[1], re.MULTILINE))
    assert EXPECTED_AGENTS <= listed, f"plugin.yaml missing agents: {EXPECTED_AGENTS - listed}"
