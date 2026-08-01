import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave0_inventory import build_inventory


def test_build_inventory_finds_top_level_scripts_and_tests():
    plugin_root = Path(__file__).resolve().parents[3] / "plugins" / "docx-to-content"
    inv = build_inventory(plugin_root)
    script_names = {Path(s).name for s in inv["scripts"]}
    assert "cli.py" in script_names
    assert "analyze_structure.py" in script_names
    assert len(inv["tests"]) > 0
    assert len(inv["skills"]) == 4


def test_build_inventory_returns_relative_paths(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("x = 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("def test_x(): pass\n")
    (tmp_path / "skills").mkdir()
    inv = build_inventory(tmp_path)
    assert inv["scripts"] == ["scripts/foo.py"]
    assert inv["tests"] == ["tests/test_foo.py"]
    assert inv["skills"] == []
