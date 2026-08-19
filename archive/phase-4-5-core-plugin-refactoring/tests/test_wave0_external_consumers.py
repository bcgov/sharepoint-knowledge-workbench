import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave0_external_consumers import find_external_consumer_signals


def test_find_external_consumer_signals_on_real_repo():
    repo_root = Path(__file__).resolve().parents[3]
    signals = find_external_consumer_signals(repo_root)
    assert set(signals) == {"skills_lock_files", "claude_settings", "marketplace_files", "worktrees"}
    assert isinstance(signals["worktrees"], list)


def test_find_external_consumer_signals_detects_worktrees(tmp_path):
    (tmp_path / ".worktrees" / "foo").mkdir(parents=True)
    (tmp_path / ".worktrees" / "bar").mkdir(parents=True)
    signals = find_external_consumer_signals(tmp_path)
    assert signals["worktrees"] == ["bar", "foo"]
