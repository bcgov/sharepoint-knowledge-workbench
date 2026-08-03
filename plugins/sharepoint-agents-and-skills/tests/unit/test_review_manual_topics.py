"""Unit tests for review_manual_topics.py's deterministic topic resolution."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from review_manual_topics import (  # noqa: E402
    resolve_topic,
    TopicNotFoundError,
    TooManyRelatedTopicsError,
)


@pytest.fixture()
def content_root(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "data-capture-standards--d1d8e601.md").write_text(
        "## DATA CAPTURE STANDARDS\n\nSome content here.\n"
    )
    (pages / "file-access--e19256ff.md").write_text(
        "## FILE ACCESS\n\nSee [Data Capture Standards](data-capture-standards--d1d8e601.md) for rules.\n"
    )
    (pages / "orders--25c57174.md").write_text("## ORDERS\n\nOrders content.\n")
    (pages / "warrants--f373f7fc.md").write_text("## WARRANTS\n\nWarrants content.\n")
    (pages / "three-links--aaaaaaaa.md").write_text(
        "See [A](orders--25c57174.md), [B](warrants--f373f7fc.md), "
        "and [C](file-access--e19256ff.md).\n"
    )
    return pages


def test_resolves_primary_topic_by_exact_filename(content_root):
    result = resolve_topic(content_root, "data-capture-standards--d1d8e601")
    assert result.primary.slug == "data-capture-standards--d1d8e601"
    assert "DATA CAPTURE STANDARDS" in result.primary.content
    assert result.related == []


def test_resolves_related_topics_from_markdown_links(content_root):
    result = resolve_topic(content_root, "file-access--e19256ff")
    assert result.primary.slug == "file-access--e19256ff"
    assert len(result.related) == 1
    assert result.related[0].slug == "data-capture-standards--d1d8e601"


def test_not_found_raises_without_inventing_content(content_root):
    with pytest.raises(TopicNotFoundError):
        resolve_topic(content_root, "non-existent-topic--99999999")


def test_more_than_two_related_topics_is_rejected(content_root):
    with pytest.raises(TooManyRelatedTopicsError):
        resolve_topic(content_root, "three-links--aaaaaaaa")


def test_resolves_by_slug_prefix_when_hash_omitted(content_root):
    result = resolve_topic(content_root, "orders")
    assert result.primary.slug == "orders--25c57174"


def test_ambiguous_prefix_raises(content_root):
    (content_root / "orders--bbbbbbbb.md").write_text("## ORDERS DUPLICATE\n")
    with pytest.raises(TopicNotFoundError):
        resolve_topic(content_root, "orders")
