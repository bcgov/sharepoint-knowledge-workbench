import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave0_test_ledger import build_test_ledger


def test_build_test_ledger_lists_real_test_functions():
    plugin_root = Path(__file__).resolve().parents[3] / "plugins" / "docx-to-content"
    ledger = build_test_ledger(plugin_root)
    assert len(ledger["entries"]) > 400  # 529 passed, 1 skipped per start-here.md baseline
    sample = ledger["entries"][0]
    assert set(sample) == {"file", "test_name", "proposed_owner_domain"}
    assert sample["proposed_owner_domain"] is None


def test_build_test_ledger_on_minimal_fixture(tmp_path):
    tests_dir = tmp_path / "tests" / "unit"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_x.py").write_text(
        "def test_one():\n    assert True\n\n"
        "def test_two():\n    assert True\n\n"
        "def helper():\n    pass\n"
    )
    ledger = build_test_ledger(tmp_path)
    names = {e["test_name"] for e in ledger["entries"]}
    assert names == {"test_one", "test_two"}
