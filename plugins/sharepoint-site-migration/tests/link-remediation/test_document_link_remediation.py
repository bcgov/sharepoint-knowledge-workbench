"""Tests for document_link_remediation.py -- rewriting broken hyperlinks
embedded INSIDE Office documents (docx/xlsx/pptx) and PDFs, distinct from
link_remediation.py which only handles page/HTML body content. Uses small
in-memory fixture documents built with the standard library (no real
tenant files, no python-docx/openpyxl/python-pptx/pymupdf dependency for
the OOXML formats, which are plain ZIP archives of XML).

Purpose: Tests for document_link_remediation.py -- rewriting broken hyperlinks embedded INSIDE Office documents (docx/xlsx/pptx) and PDFs, distinct from link_remediation.py which only handles page/HTML body content.
Key Input Dependencies: document_link_remediation, link_outcomes, link_rules.
"""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "link-remediation"))

import pytest

from document_link_remediation import (
    ConfirmationRequired,
    ExecutorRequired,
    detect_document_format,
    plan_document_link_remediation,
    apply_document_link_remediation,
)
from link_outcomes import Outcome
from link_rules import RewriteRuleset


def _ruleset() -> RewriteRuleset:
    """Test helper: ruleset."""
    return RewriteRuleset.from_dict(
        {"rules": [{"match": "/Pages/", "replacement": "/SitePages/"}]}
    )


def _make_docx(rels_xml: str) -> bytes:
    """Test helper: make docx."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", "<w:document/>")
        zf.writestr("word/_rels/document.xml.rels", rels_xml)
    return buffer.getvalue()


REL_WITH_LEGACY_LINK = (
    '<?xml version="1.0"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="hyperlink" '
    'Target="https://example.sharepoint.com/sites/Demo/Pages/Home.aspx" TargetMode="External"/>'
    "</Relationships>"
)

REL_CLEAN = (
    '<?xml version="1.0"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="hyperlink" '
    'Target="https://example.sharepoint.com/sites/Demo/SitePages/Home.aspx" TargetMode="External"/>'
    "</Relationships>"
)


class TestDetectDocumentFormat:
    def test_detects_docx_by_internal_structure(self):
        """Verify detects docx by internal structure."""
        assert detect_document_format(_make_docx(REL_CLEAN)) == "docx"

    def test_detects_pdf_by_magic_bytes(self):
        """Verify detects pdf by magic bytes."""
        assert detect_document_format(b"%PDF-1.4\n...") == "pdf"

    def test_unknown_format_is_reported_not_guessed(self):
        """Verify unknown format is reported not guessed."""
        assert detect_document_format(b"not a real document") == "unknown"


class TestPlanDocumentLinkRemediation:
    def test_docx_with_legacy_link_is_flagged_changed(self):
        """Verify docx with legacy link is flagged changed."""
        documents = {"Home.docx": _make_docx(REL_WITH_LEGACY_LINK)}
        plan = plan_document_link_remediation(documents, _ruleset())
        assert plan.outcome == Outcome.OBSERVED
        assert plan.change_count == 1
        assert plan.documents[0].is_changed is True

    def test_docx_with_no_legacy_link_is_unchanged(self):
        """Verify docx with no legacy link is unchanged."""
        documents = {"Home.docx": _make_docx(REL_CLEAN)}
        plan = plan_document_link_remediation(documents, _ruleset())
        assert plan.outcome == Outcome.EMPTY
        assert plan.change_count == 0

    def test_rewritten_docx_bytes_are_a_valid_zip_with_the_new_url(self):
        """Verify rewritten docx bytes are a valid zip with the new url."""
        documents = {"Home.docx": _make_docx(REL_WITH_LEGACY_LINK)}
        plan = plan_document_link_remediation(documents, _ruleset())
        remediated = plan.documents[0].remediated_content
        with zipfile.ZipFile(io.BytesIO(remediated)) as zf:
            rels_text = zf.read("word/_rels/document.xml.rels").decode("utf-8")
        assert "/SitePages/Home.aspx" in rels_text
        assert "/Pages/Home.aspx" not in rels_text

    def test_pdf_without_injected_handler_is_not_supported(self):
        """Verify pdf without injected handler is not supported."""
        documents = {"Report.pdf": b"%PDF-1.4\n..."}
        plan = plan_document_link_remediation(documents, _ruleset())
        assert plan.outcome == Outcome.NOT_SUPPORTED
        assert plan.documents[0].is_changed is False

    def test_pdf_with_injected_handler_is_remediated(self):
        """Verify pdf with injected handler is remediated."""
        def fake_pdf_handler(content: bytes, ruleset: RewriteRuleset):
            """Test double for fake pdf handler used by the enclosing test."""
            text = content.decode("utf-8")
            rewritten, applied = ruleset.apply(text)
            return rewritten.encode("utf-8"), applied

        documents = {"Report.pdf": b"%PDF fake /Pages/ link content"}
        plan = plan_document_link_remediation(documents, _ruleset(), pdf_handler=fake_pdf_handler)
        assert plan.outcome == Outcome.OBSERVED
        assert plan.documents[0].is_changed is True

    def test_empty_documents_is_empty_outcome(self):
        """Verify empty documents is empty outcome."""
        plan = plan_document_link_remediation({}, _ruleset())
        assert plan.outcome == Outcome.EMPTY


class TestApplyDocumentLinkRemediation:
    def test_dry_run_by_default_performs_no_writes(self):
        """Verify dry run by default performs no writes."""
        documents = {"Home.docx": _make_docx(REL_WITH_LEGACY_LINK)}
        plan = plan_document_link_remediation(documents, _ruleset())
        result = apply_document_link_remediation(plan)
        assert result.dry_run is True
        assert result.applied == ()

    def test_real_apply_without_executor_raises(self):
        """Verify real apply without executor raises."""
        documents = {"Home.docx": _make_docx(REL_WITH_LEGACY_LINK)}
        plan = plan_document_link_remediation(documents, _ruleset())
        with pytest.raises(ExecutorRequired):
            apply_document_link_remediation(
                plan, dry_run=False, executor=None, confirm=plan.confirmation_token
            )

    def test_real_apply_with_wrong_token_raises(self):
        """Verify real apply with wrong token raises."""
        documents = {"Home.docx": _make_docx(REL_WITH_LEGACY_LINK)}
        plan = plan_document_link_remediation(documents, _ruleset())
        with pytest.raises(ConfirmationRequired):
            apply_document_link_remediation(
                plan, dry_run=False, executor=lambda source, content: None, confirm="WRONG"
            )

    def test_real_apply_writes_only_changed_documents(self):
        """Verify real apply writes only changed documents."""
        documents = {
            "Home.docx": _make_docx(REL_WITH_LEGACY_LINK),
            "Clean.docx": _make_docx(REL_CLEAN),
        }
        plan = plan_document_link_remediation(documents, _ruleset())
        written = []

        def executor(source, content):
            """Test double for executor used by the enclosing test."""
            written.append(source)

        result = apply_document_link_remediation(
            plan, dry_run=False, executor=executor, confirm=plan.confirmation_token
        )
        assert result.outcome == Outcome.OBSERVED
        assert written == ["Home.docx"]
