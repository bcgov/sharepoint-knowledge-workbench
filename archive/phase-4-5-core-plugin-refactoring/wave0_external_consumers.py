"""Wave 0 Step 7: external-consumer signal discovery (per approved plan, verbatim)."""
from __future__ import annotations

from pathlib import Path


def find_external_consumer_signals(repo_root: Path) -> dict:
    signals = {"skills_lock_files": [], "claude_settings": [], "marketplace_files": [], "worktrees": []}
    for p in repo_root.rglob("skills-lock.json"):
        signals["skills_lock_files"].append(str(p.relative_to(repo_root)))
    settings = repo_root / ".claude" / "settings.json"
    if settings.exists():
        signals["claude_settings"].append(str(settings.relative_to(repo_root)))
    for p in repo_root.rglob("marketplace.json"):
        signals["marketplace_files"].append(str(p.relative_to(repo_root)))
    worktrees_dir = repo_root / ".worktrees"
    if worktrees_dir.exists():
        signals["worktrees"] = sorted(p.name for p in worktrees_dir.iterdir() if p.is_dir())
    return signals
