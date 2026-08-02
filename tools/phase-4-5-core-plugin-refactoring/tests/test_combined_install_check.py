import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from combined_install_check import PLUGINS, check_combined_install


def test_plugins_tuple_matches_the_four_domain_plugins():
    assert set(PLUGINS) == {
        "source-document-extraction",
        "knowledge-analysis",
        "canonical-knowledge",
        "knowledge-publication",
    }


@pytest.mark.slow
def test_check_combined_install_all_four_pass_with_zero_collisions():
    repo_root = Path(
        __import__("subprocess")
        .check_output(["git", "rev-parse", "--show-toplevel"])
        .decode()
        .strip()
    )
    results = check_combined_install(repo_root)
    assert set(results) == set(PLUGINS)
    assert all(rc == 0 for rc in results.values()), results
