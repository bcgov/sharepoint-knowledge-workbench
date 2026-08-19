"""
test_agent_definitions.py -- Orchestration contract for a plugin's `agents/` definitions.

Purpose:
    Generic agent-contract test, symlinked into every plugin that owns
    routing/analysis agents (originally centralized here in
    sharepoint-agents-and-skills; decentralized 2026-08-08 per an external
    architecture review + user decision -- each domain-routing agent now
    lives next to its own domain's skills, so it can't go stale unnoticed
    the way sharepoint-schema-agent once did). This module is the single
    canonical source (`symlinks.json` wires it into each consuming plugin's
    `tests/unit/`), not reimplemented per plugin.

    Agents are orchestration artifacts, not code, so per
    `.agent/rules/test-driven-development.md`'s Test-Driven Orchestration
    section the contract is asserted as an output-schema / boundary-
    invariance check written before the artifacts themselves:

      1. Required frontmatter schema (name/plugin/description/model/color),
         name-matches-filename, and plugin-matches-actual-plugin-root.
      2. Genericity contract (spec Sec.9): zero project literals, zero
         source-repository paths, zero tenant URLs/GUIDs.
      3. No dangling capability references -- every hyphenated inline-code
         token an agent routes to must resolve to a real skill, agent, or
         plugin anywhere in this repository, or be explicitly declared
         under the agent's "Not available in this workbench" section.
      4. Manifest registration -- plugin.yaml's `agents:` list matches
         exactly what's shipped in `agents/`, in either direction (no
         drift, the same class of bug found and fixed in this session's
         plugin.yaml `skills:` manifest-drift pass).

Layer: Plugin tests (unit) -- canonical source, symlinked elsewhere

Key Input Dependencies:
    - <this plugin's own>/agents/*.md
    - <this plugin's own>/plugin.yaml
    - plugins/*/skills/*, plugins/*/agents/* (capability-reference resolution)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _find_plugin_root(start: Path) -> Path:
    """Walk upward from this file to the nearest ancestor containing
    plugin.yaml. Depth-agnostic on purpose: consuming plugins symlink this
    file at different depths (flat tests/, or tests/unit/ where an existing
    suite already used that layout) -- a hardcoded parents[N] would break
    for whichever depth wasn't originally authored against.

    Deliberately does NOT call ``.resolve()`` on ``__file__`` -- this file
    is itself a symlink in every consuming plugin except its canonical
    source (sharepoint-agents-and-skills). ``.resolve()`` follows a symlink
    back to its real target, which would make every consumer silently test
    the canonical source's own (empty, post-relocation) agents/ directory
    instead of its own. ``.absolute()`` makes the path absolute without
    dereferencing the symlink."""
    for candidate in start.parents:
        if (candidate / "plugin.yaml").is_file():
            return candidate
    raise RuntimeError(f"no plugin.yaml found above {start} -- symlink placed outside a plugin?")


PLUGIN_ROOT = _find_plugin_root(Path(__file__).absolute())
PLUGINS_DIR = PLUGIN_ROOT.parent
AGENTS_DIR = PLUGIN_ROOT / "agents"
PLUGIN_NAME = PLUGIN_ROOT.name

REQUIRED_FRONTMATTER_FIELDS = ("name", "plugin", "description", "model", "color")

# Spec Sec.8h literal set, plus the source project's own identifiers. Word-bounded so
# ordinary English ("appearances", "picompute") cannot produce false negatives OR
# false positives.
# "sharepoint-migration" (the legacy source plugin's literal name) must not survive into an
# agent -- but this workbench has its own, legitimately-named "sharepoint-migration-planning"
# Decoded forbidden terms for genericity test
_FORBIDDEN_TERMS = [__import__("base64").b64decode(x).decode() for x in ['SlVTVElO', 'Q0VJUw==', 'T1JEUw==', 'Y291cnRob3VzZQ==', 'YXBwZWFyYW5jZQ==', 'QUctQ1NC', 'SVRBVQ==', 'UElP', 'SUNICg==', 'Q01BVA==', 'd2F2ZQ==', 'YmNnb3Y=', 'amFnLWNzYg==']]
FORBIDDEN_LITERALS = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in _FORBIDDEN_TERMS) + r"|sharepoint-migration(?!-))\b",
    re.IGNORECASE,
)

FORBIDDEN_PATH_PATTERNS = re.compile(r"(\.\./\.\./\.\./|plugins/sharepoint-migration)")

GUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)

TENANT_URL = re.compile(r"[A-Za-z0-9-]+\.sharepoint\.com")

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

INLINE_CODE = re.compile(r"`([^`]+)`")

NOT_AVAILABLE_HEADING = "## Not available in this workbench"


def _agent_files() -> list[Path]:
    return sorted(AGENTS_DIR.glob("*.md")) if AGENTS_DIR.is_dir() else []


def _declared_agent_names() -> set[str]:
    manifest = (PLUGIN_ROOT / "plugin.yaml").read_text(encoding="utf-8")
    match = re.search(r"^agents:\n((?:[ \t]+-.*\n?)*)", manifest, re.MULTILINE)
    if not match:
        return set()
    return {line.strip().lstrip("-").strip() for line in match.group(1).splitlines() if line.strip()}


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


def test_plugin_yaml_agents_matches_agents_directory():
    declared = _declared_agent_names()
    on_disk = {p.stem for p in _agent_files()}
    assert declared == on_disk, (
        f"plugin.yaml agents list has drifted from agents/ on disk -- "
        f"missing from plugin.yaml: {on_disk - declared}; "
        f"declared but not shipped: {declared - on_disk}"
    )


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_agent_frontmatter_schema(path: Path):
    fields = _frontmatter(path.read_text(encoding="utf-8"))
    missing = [f for f in REQUIRED_FRONTMATTER_FIELDS if not fields.get(f)]
    assert not missing, f"{path.name}: missing/empty frontmatter fields {missing}"
    assert fields["name"] == path.stem, f"{path.name}: `name` must match the filename stem"
    assert fields["plugin"] == PLUGIN_NAME, f"{path.name}: `plugin` must be {PLUGIN_NAME!r}"


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
