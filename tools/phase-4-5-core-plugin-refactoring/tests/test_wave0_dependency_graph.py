import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave0_dependency_graph import build_dependency_graph


def test_build_dependency_graph_finds_real_internal_edge():
    plugin_root = Path(__file__).resolve().parents[3] / "plugins" / "docx-to-content"
    graph = build_dependency_graph(plugin_root)
    edges = {(e["from"], e["to"]) for e in graph["edges"]}
    # cli.py is known to import convert.py's conversion pipeline (scripts/cli.py -> scripts/convert.py)
    assert any(frm.endswith("cli.py") and to.endswith("convert.py") for frm, to in edges)


def test_build_dependency_graph_ignores_stdlib_and_third_party(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "a.py").write_text("import os\nimport json\nfrom . import b\n")
    (scripts / "b.py").write_text("x = 1\n")
    graph = build_dependency_graph(tmp_path)
    edges = {(e["from"], e["to"]) for e in graph["edges"]}
    assert ("scripts/a.py", "scripts/b.py") in edges
    assert not any(to in ("os", "json") for _, to in edges)
