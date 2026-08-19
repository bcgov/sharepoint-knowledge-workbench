import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave0_dependency_graph import build_dependency_graph


@pytest.mark.skip(
    reason=(
        "plugins/docx-to-content was removed in Phase 4.5 Wave 8 (see "
        "docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md). Kept as a "
        "historical record, not re-targeted -- build_dependency_graph's own logic is still "
        "exercised by the tmp_path-based test below."
    )
)
def test_build_dependency_graph_finds_real_internal_edge():
    plugin_root = Path(__file__).resolve().parents[3] / "plugins" / "docx-to-content"
    graph = build_dependency_graph(plugin_root)
    edges = {(e["from"], e["to"]) for e in graph["edges"]}
    # cli.py is known to import analyze_structure.py, the docx-to-content
    # orchestrator that stays local even after Phase 4.5 Wave 4 moved
    # convert.py out to the installed canonical-knowledge package
    # (scripts/cli.py -> scripts/analyze_structure.py).
    assert any(frm.endswith("cli.py") and to.endswith("analyze_structure.py") for frm, to in edges)


def test_build_dependency_graph_ignores_stdlib_and_third_party(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "a.py").write_text("import os\nimport json\nfrom . import b\n")
    (scripts / "b.py").write_text("x = 1\n")
    graph = build_dependency_graph(tmp_path)
    edges = {(e["from"], e["to"]) for e in graph["edges"]}
    assert ("scripts/a.py", "scripts/b.py") in edges
    assert not any(to in ("os", "json") for _, to in edges)
