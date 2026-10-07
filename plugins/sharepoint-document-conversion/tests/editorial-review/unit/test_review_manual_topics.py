"""Purpose:
    Unit tests for review_manual_topics.py's deterministic topic resolution.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - sys
    - pathlib
    - pytest
    - review_manual_topics

Unit tests for review_manual_topics.py's deterministic topic resolution.

Key Functions Index:
    - content_root()
    - test_resolves_primary_topic_by_exact_filename()
    - test_resolves_related_topics_from_markdown_links()
    - test_not_found_raises_without_inventing_content()
    - test_more_than_two_related_topics_is_rejected()
    - test_resolves_by_slug_prefix_when_hash_omitted()
    - test_ambiguous_prefix_raises()"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "editorial-review"))

from review_manual_topics import (  # noqa: E402
    resolve_topic,
    TopicNotFoundError,
    TooManyRelatedTopicsError,
)


# Return the root directory used by the editorial content fixtures.
@pytest.fixture()
def content_root(tmp_path):
    """Return the root directory used by the editorial content fixtures."""
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "example-standards-topic--d1d8e601.md").write_text(
        "## EXAMPLE STANDARDS\n\nSome content here.\n"
    )
    (pages / "file-access--e19256ff.md").write_text(
        "## FILE ACCESS\n\nSee [Example Standards](example-standards-topic--d1d8e601.md) for rules.\n"
    )
    (pages / "topic-a--25c57174.md").write_text("## TOPIC A\n\nTopic A content.\n")
    (pages / "topic-b--f373f7fc.md").write_text("## TOPIC B\n\nTopic B content.\n")
    (pages / "three-links--aaaaaaaa.md").write_text(
        "See [A](topic-a--25c57174.md), [B](topic-b--f373f7fc.md), "
        "and [C](file-access--e19256ff.md).\n"
    )
    return pages


# Verify resolves primary topic by exact filename.
def test_resolves_primary_topic_by_exact_filename(content_root):
    """Verify resolves primary topic by exact filename."""
    result = resolve_topic(content_root, "example-standards-topic--d1d8e601")
    assert result.primary.slug == "example-standards-topic--d1d8e601"
    assert "EXAMPLE STANDARDS" in result.primary.content
    assert result.related == []


# Verify resolves related topics from Markdown links.
def test_resolves_related_topics_from_markdown_links(content_root):
    """Verify resolves related topics from Markdown links."""
    result = resolve_topic(content_root, "file-access--e19256ff")
    assert result.primary.slug == "file-access--e19256ff"
    assert len(result.related) == 1
    assert result.related[0].slug == "example-standards-topic--d1d8e601"


# Verify not found raises without inventing content.
def test_not_found_raises_without_inventing_content(content_root):
    """Verify not found raises without inventing content."""
    with pytest.raises(TopicNotFoundError):
        resolve_topic(content_root, "non-existent-topic--99999999")


# Verify rejection of more than two related topics is.
def test_more_than_two_related_topics_is_rejected(content_root):
    """Verify rejection of more than two related topics is."""
    with pytest.raises(TooManyRelatedTopicsError):
        resolve_topic(content_root, "three-links--aaaaaaaa")


# Verify resolves by slug prefix when hash omitted.
def test_resolves_by_slug_prefix_when_hash_omitted(content_root):
    """Verify resolves by slug prefix when hash omitted."""
    result = resolve_topic(content_root, "topic-a")
    assert result.primary.slug == "topic-a--25c57174"


# Verify ambiguous prefix raises.
def test_ambiguous_prefix_raises(content_root):
    """Verify ambiguous prefix raises."""
    (content_root / "topic-a--bbbbbbbb.md").write_text("## TOPIC A DUPLICATE\n")
    with pytest.raises(TopicNotFoundError):
        resolve_topic(content_root, "topic-a")
