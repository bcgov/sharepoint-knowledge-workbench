# NOTE: repo_root.py is exported for repository-tooling use only (Wave 6's
# integration test evidence generation) — this test proves it works, but
# Wave 2-5's dependency-boundary check independently proves no plugin
# production code imports it (see Wave 2 Step 9).
import pytest

from knowledge_workbench_contracts.repo_root import find_repo_root


def test_finds_repo_root_marker(tmp_path):
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert find_repo_root(nested, markers=(".git",)) == tmp_path


def test_raises_when_no_marker_found(tmp_path):
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        find_repo_root(nested, markers=(".git",))
