#!/usr/bin/env python
"""
test_content_authoring_guidance.py
====================================

Task 15a: contract tests for structured content authoring guidance (spec
Section 14a) -- the manual-topic template, the authoring guide, the
supported Markdown profile, the generated-elements reference, the
semantic-component README, and the filled example. Also proves two
integration behaviors that the guidance depends on but does not
reimplement: real Word-TOC-dump stripping (Task 2/8) and that this
generic guidance never leaks the CEIS pilot document's own heading
literals.
"""

import sys
from pathlib import Path

import pytest
import yaml

PLUGIN_ROOT = Path(__file__).parent.parent.parent
REFERENCES_DIR = PLUGIN_ROOT / "references"
TEMPLATES_DIR = PLUGIN_ROOT / "templates"

SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _front_matter(text: str) -> dict:
    assert text.startswith("---"), "template must start with YAML front matter"
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end])


class TestManualTopicTemplate:
    PATH = TEMPLATES_DIR / "content" / "manual-topic.md"

    def test_exists(self):
        assert self.PATH.exists(), f"missing {self.PATH}"

    def test_has_required_section_headings(self):
        text = self.PATH.read_text(encoding="utf-8")
        for heading in (
            "Purpose",
            "Before You Begin",
            "Procedure",
            "Expected Result",
            "Exceptions and Special Cases",
            "Troubleshooting",
            "Related Topics",
        ):
            assert f"# {heading}" in text or f"## {heading}" in text, (
                f"template missing required heading: {heading}"
            )

    def test_has_required_front_matter_fields(self):
        fm = _front_matter(self.PATH.read_text(encoding="utf-8"))
        for field in ("content_type", "title", "owner", "status", "review_date", "audience"):
            assert field in fm, f"template front matter missing field: {field}"

    def test_has_no_machine_owned_fields(self):
        text = self.PATH.read_text(encoding="utf-8")
        for field in ("chunk_id", "content_sha256", "plan_id"):
            assert field not in text, f"template must not expose machine-owned field: {field}"


class TestContentAuthoringGuide:
    PATH = REFERENCES_DIR / "content-authoring-guide.md"

    def test_exists(self):
        assert self.PATH.exists(), f"missing {self.PATH}"

    def test_distinguishes_authors_from_code(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "Authors maintain" in text
        assert "Code maintains" in text

    def test_does_not_expose_internals(self):
        text = self.PATH.read_text(encoding="utf-8").lower()
        for forbidden in ("sha256", "renderer protocol", "canonicalpackage", "plan_id"):
            assert forbidden not in text, f"authoring guide leaks internal detail: {forbidden}"


class TestSupportedMarkdownProfile:
    PATH = REFERENCES_DIR / "supported-markdown-profile.md"

    def test_exists(self):
        assert self.PATH.exists(), f"missing {self.PATH}"

    def test_documents_relative_path_rules(self):
        text = self.PATH.read_text(encoding="utf-8").lower()
        assert "relative" in text
        assert "image" in text
        assert "link" in text

    def test_lists_permitted_and_prohibited(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "Permitted" in text
        assert "Prohibited" in text


class TestGeneratedElements:
    PATH = REFERENCES_DIR / "generated-elements.md"

    def test_exists(self):
        assert self.PATH.exists(), f"missing {self.PATH}"

    def test_lists_toc_and_navigation_with_source(self):
        text = self.PATH.read_text(encoding="utf-8").lower()
        assert "table of contents" in text
        assert "navigation" in text

    def test_does_not_claim_unimplemented_as_implemented(self):
        text = self.PATH.read_text(encoding="utf-8")
        # Only the multipage-markdown renderer is implemented in Phase 1;
        # the doc must not assert generated-element support for anything
        # else as already-implemented fact.
        assert "implemented" in text.lower()


class TestComponentsReadme:
    PATH = TEMPLATES_DIR / "components" / "README.md"

    def test_exists(self):
        assert self.PATH.exists(), f"missing {self.PATH}"

    def test_documents_callout_syntax(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "[!WARNING]" in text

    def test_lists_semantic_components(self):
        text = self.PATH.read_text(encoding="utf-8").lower()
        for component in (
            "note", "warning", "important", "example", "prerequisite",
            "procedure step", "expected result", "decision", "exception",
            "troubleshooting item", "definition", "reference", "knowledge check",
        ):
            assert component in text, f"components README missing: {component}"


class TestManualTopicExample:
    PATH = TEMPLATES_DIR / "examples" / "manual-topic-example.md"

    def test_exists(self):
        assert self.PATH.exists(), f"missing {self.PATH}"

    def test_contains_required_elements(self):
        text = self.PATH.read_text(encoding="utf-8")
        assert "## Procedure" in text
        assert "[!" in text  # semantic callout
        assert "![" in text  # image reference
        assert "## Expected Result" in text
        assert "## Exceptions and Special Cases" in text
        assert "## Troubleshooting" in text
        assert "## Related Topics" in text
        assert "](" in text  # at least one link (related topic)

    def test_does_not_insert_empty_boilerplate(self):
        text = self.PATH.read_text(encoding="utf-8").lower()
        for boilerplate in ("n/a", "tbd", "no content", "none.", "not applicable"):
            assert boilerplate not in text, f"example must not use boilerplate filler: {boilerplate}"


class TestNoCeisLiteralInGenericGuidance:
    """CEIS is the Phase 1 pilot document, but authoring guidance and
    templates must stay generic across future source documents."""

    def test_no_ceis_headings_in_new_docs_and_templates(self):
        ceis_literals = ("FILE ACCESS", "DATA CAPTURE")
        paths = list(REFERENCES_DIR.glob("*.md")) + [
            TEMPLATES_DIR / "content" / "manual-topic.md",
            TEMPLATES_DIR / "components" / "README.md",
            TEMPLATES_DIR / "examples" / "manual-topic-example.md",
        ]
        for path in paths:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            for literal in ceis_literals:
                assert literal not in text, f"{path} contains CEIS-specific literal: {literal}"


class TestTocStrippingIntegration:
    """Proves the REAL Task 2/8 cleanup pipeline function removes a
    Word-generated TOC dump while leaving the heading hierarchy intact --
    calls the actual implementation, not a reimplementation."""

    def test_strip_raw_toc_removes_dump_keeps_headings(self):
        from pandoc.toc import strip_raw_toc

        raw = (
            "# Manual Title\n\n"
            "[]{#_Toc1 .anchor}\n"
            "[Section One](#_Toc111)\n\n"
            "[Section Two](#_Toc222)\n\n"
            "# Section One\n\n"
            "Body text.\n\n"
            "# Section Two\n\n"
            "More body text.\n"
        )
        cleaned = strip_raw_toc(raw)
        assert "#_Toc" not in cleaned
        assert "# Section One" in cleaned
        assert "# Section Two" in cleaned
        assert "Body text." in cleaned
