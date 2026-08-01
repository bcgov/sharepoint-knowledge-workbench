import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from isolated_install_check import check_isolated_install, check_declares_dependency

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_CONTRACTS_DIR = Path(__file__).resolve().parents[3] / "contracts" / "python"
_REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.slow
def test_broken_plugin_undeclared_import_fails_isolated_install():
    """Runtime negative control: imports an upstream plugin package that is never
    installed by check_isolated_install() and never declared as a dependency — the
    import-outside-pytest step must fail."""
    plugin_dir = _FIXTURES / "broken_plugin_undeclared_import"
    with pytest.raises(Exception):
        check_isolated_install(
            plugin_dir, _CONTRACTS_DIR, _REPO_ROOT, "broken_plugin_undeclared_import"
        )


def test_broken_plugin_missing_dependency_fails_metadata_check():
    """Static negative control: check_isolated_install() always installs the contracts
    distribution alongside every plugin, so it cannot catch an undeclared dependency on
    contracts specifically — check_declares_dependency() (static metadata inspection) is
    the actual check that must correctly flag this fixture."""
    plugin_dir = _FIXTURES / "broken_plugin_missing_dependency"
    assert check_declares_dependency(plugin_dir, "knowledge-workbench-contracts") is False


def test_check_declares_dependency_true_for_a_correctly_declared_plugin(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["knowledge-workbench-contracts==0.1.0-alpha.1"]\n'
    )
    assert check_declares_dependency(tmp_path, "knowledge-workbench-contracts") is True
