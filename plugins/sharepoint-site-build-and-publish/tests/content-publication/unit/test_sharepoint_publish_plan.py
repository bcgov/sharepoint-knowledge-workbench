"""
test_sharepoint_publish_plan.py
===============================

Purpose:
    Verify Markdown, ASPX, and rollback plans contain only safe local publication actions.

Key Input Dependencies:
    - sharepoint_publish_plan and pytest temporary-path fixtures.

Function Index:
    source_dir, test_markdown_publish_plan_covers_all_files, test_markdown_publish_plan_rejects_missing_source, test_markdown_publish_plan_rejects_empty_source, test_aspx_publish_plan_converts_md_to_aspx_filenames, test_rollback_plan_reverses_publish_plan_actions, test_rollback_plan_rejects_cross_document_mismatch
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "content-publication"))

from sharepoint_publish_plan import (  # noqa: E402
    build_markdown_publish_plan,
    build_aspx_publish_plan,
    build_rollback_plan,
    PublishPlan,
    PublishAction,
    PlanError,
)


# Create a rendered Markdown directory containing index and topic pages.
@pytest.fixture()
def source_dir(tmp_path):
    """Create a rendered Markdown directory containing index and topic pages."""
    d = tmp_path / "rendered"
    d.mkdir()
    (d / "index.md").write_text("# Index")
    pages = d / "pages"
    pages.mkdir()
    (pages / "topic-a--111.md").write_text("content a")
    (pages / "topic-b--222.md").write_text("content b")
    return d


# Verify the contract that markdown publish plan covers all files.
def test_markdown_publish_plan_covers_all_files(source_dir):
    """Verify the contract that markdown publish plan covers all files."""
    plan = build_markdown_publish_plan("doc-1", source_dir, "MyLibrary", "MyFolder")
    assert plan.document_id == "doc-1"
    assert len(plan.actions) == 3
    filenames = {a.target_filename for a in plan.actions}
    assert filenames == {"index.md", "topic-a--111.md", "topic-b--222.md"}


# Verify the contract that markdown publish plan rejects missing source.
def test_markdown_publish_plan_rejects_missing_source(tmp_path):
    """Verify the contract that markdown publish plan rejects missing source."""
    with pytest.raises(PlanError):
        build_markdown_publish_plan("doc-1", tmp_path / "does-not-exist", "Lib", "Folder")


# Verify the contract that markdown publish plan rejects empty source.
def test_markdown_publish_plan_rejects_empty_source(tmp_path):
    """Verify the contract that markdown publish plan rejects empty source."""
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(PlanError):
        build_markdown_publish_plan("doc-1", empty, "Lib", "Folder")


# Verify the contract that aspx publish plan converts md to aspx filenames.
def test_aspx_publish_plan_converts_md_to_aspx_filenames(source_dir):
    """Verify the contract that aspx publish plan converts md to aspx filenames."""
    plan = build_aspx_publish_plan("doc-1", source_dir / "pages", "SitePages/MyDoc")
    filenames = {a.target_filename for a in plan.actions}
    assert filenames == {"topic-a--111.aspx", "topic-b--222.aspx"}
    assert all(a.target_library == "SitePages" for a in plan.actions)


# Verify the contract that rollback plan reverses publish plan actions.
def test_rollback_plan_reverses_publish_plan_actions():
    """Verify the contract that rollback plan reverses publish plan actions."""
    publish_plan = PublishPlan(document_id="doc-1", actions=[
        PublishAction("local/a.md", "MyLibrary", "MyFolder", "a.md"),
        PublishAction("local/b.md", "MyLibrary", "MyFolder", "b.md"),
    ])
    rollback = build_rollback_plan("doc-1", publish_plan)
    assert rollback.document_id == "doc-1"
    assert len(rollback.actions) == 2
    assert all("doc-1" in a.reason for a in rollback.actions)


# Verify the contract that rollback plan rejects cross document mismatch.
def test_rollback_plan_rejects_cross_document_mismatch():
    """Verify the contract that rollback plan rejects cross document mismatch."""
    publish_plan = PublishPlan(document_id="doc-1", actions=[
        PublishAction("local/a.md", "MyLibrary", "MyFolder", "a.md"),
    ])
    with pytest.raises(PlanError):
        build_rollback_plan("doc-2", publish_plan)  # wrong document_id -- must not silently rollback doc-1's actions
