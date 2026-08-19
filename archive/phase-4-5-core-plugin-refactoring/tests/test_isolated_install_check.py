import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from isolated_install_check import check_isolated_install, check_no_workbench_family_dependency

_FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.slow
def test_broken_plugin_undeclared_import_fails_isolated_install():
    """Runtime negative control: imports an upstream plugin package that is never
    installed by check_isolated_install() and never declared as a dependency — the
    import-outside-pytest step must fail."""
    plugin_dir = _FIXTURES / "broken_plugin_undeclared_import"
    with pytest.raises(Exception):
        check_isolated_install(plugin_dir, "broken_plugin_undeclared_import")


def test_broken_plugin_declares_workbench_family_dependency_fails_metadata_check():
    """Static negative control (Wave 2 correction): a plugin whose pyproject.toml
    declares a pip dependency on ANY workbench-family distribution (contracts,
    runtime, or a sibling plugin) must be flagged -- every plugin must carry its
    own contract/runtime code rather than depend on a shared distribution."""
    plugin_dir = _FIXTURES / "broken_plugin_missing_dependency"
    assert check_no_workbench_family_dependency(plugin_dir) is True


def test_check_no_workbench_family_dependency_false_for_a_clean_plugin(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["pyyaml==6.0"]\n'
    )
    assert check_no_workbench_family_dependency(tmp_path) is False


def test_check_no_workbench_family_dependency_true_for_contracts_dependency(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["knowledge-workbench-contracts==0.1.0-alpha.1"]\n'
    )
    assert check_no_workbench_family_dependency(tmp_path) is True
