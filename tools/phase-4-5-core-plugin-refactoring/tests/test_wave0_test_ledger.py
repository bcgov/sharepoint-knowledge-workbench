import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave0_test_ledger import build_test_ledger


def test_build_test_ledger_lists_real_test_functions():
    plugin_root = Path(__file__).resolve().parents[3] / "plugins" / "docx-to-content"
    ledger = build_test_ledger(plugin_root)
    # Baseline was 529 at Wave 0. Waves 2/3/4 relocated tests to
    # source-document-extraction/knowledge-analysis/canonical-knowledge as
    # their domains were extracted (tests moved, not lost -- see each
    # wave's test-migration ledger); docx-to-content's own count
    # legitimately shrinks each wave. 150 is a loose floor proving the
    # ledger still finds a substantial, real test suite, not a specific
    # wave's exact count.
    assert len(ledger["entries"]) > 150
    sample = ledger["entries"][0]
    assert set(sample) == {"file", "test_name", "proposed_owner_domain"}
    assert sample["proposed_owner_domain"] is None


def test_build_test_ledger_does_not_double_count_class_methods(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_cls.py").write_text(
        "class TestFoo:\n"
        "    def test_one(self):\n"
        "        assert True\n"
        "    def test_two(self):\n"
        "        assert True\n"
    )
    ledger = build_test_ledger(tmp_path)
    assert len(ledger["entries"]) == 2
    names = {e["test_name"] for e in ledger["entries"]}
    assert names == {"TestFoo::test_one", "TestFoo::test_two"}


def test_build_test_ledger_matches_pytest_collected_count_on_real_repo():
    plugin_root = Path(__file__).resolve().parents[3] / "plugins" / "docx-to-content"
    ledger = build_test_ledger(plugin_root)
    # AST-counted distinct test functions/methods should be close to pytest's collected count
    # (530 at the recorded baseline); parametrized tests inflate pytest's count but not the AST
    # count, so ledger entries should be <= pytest's collected total, never wildly over it.
    assert len(ledger["entries"]) <= 530


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
