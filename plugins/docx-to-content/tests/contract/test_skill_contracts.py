#!/usr/bin/env python
"""
test_skill_contracts.py
========================

Task 15: contract tests for the three SKILL.md files
(analyze-document, convert-document, render-content). These are pure
text-content assertions -- they do not execute the CLI -- proving each
SKILL.md documents the required elements: trigger/purpose, exact CLI
invocation, inputs/outputs, preconditions, PASS/WARN/FAIL + exit-code
behavior, prohibited shortcuts, and handoff to the next skill.
"""

from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = PLUGIN_ROOT / "skills"


def _read(skill_name: str) -> str:
    path = SKILLS_DIR / skill_name / "SKILL.md"
    assert path.exists(), f"missing {path}"
    return path.read_text(encoding="utf-8")


class TestAnalyzeDocumentSkillContract:
    def setup_method(self):
        self.text = _read("analyze-document")

    def test_has_exact_cli_invocation(self):
        assert "python -m scripts.cli analyze --source" in self.text
        assert "--output" in self.text

    def test_emphasizes_transitory_raw_output(self):
        assert "transitory" in self.text.lower()

    def test_emphasizes_draft_plan(self):
        assert "draft plan" in self.text.lower()

    def test_documents_exit_codes(self):
        for code in ("0", "2", "3", "4"):
            assert code in self.text

    def test_documents_pass_warn_fail(self):
        assert "PASS" in self.text
        assert "FAIL" in self.text

    def test_documents_prohibited_shortcuts(self):
        assert "prohibited" in self.text.lower() or "must not" in self.text.lower()

    def test_documents_handoff(self):
        assert "confirm" in self.text.lower()


class TestConvertDocumentSkillContract:
    def setup_method(self):
        self.text = _read("convert-document")

    def test_has_exact_cli_invocations(self):
        assert "python -m scripts.cli confirm --draft-plan" in self.text
        assert "python -m scripts.cli convert --source" in self.text

    def test_emphasizes_confirmed_plan(self):
        assert "confirmed plan" in self.text.lower()

    def test_emphasizes_source_hash(self):
        assert "source_sha256" in self.text or "source hash" in self.text.lower()

    def test_emphasizes_staging(self):
        assert "staging" in self.text.lower()

    def test_emphasizes_canonical_validation(self):
        assert "canonical" in self.text.lower()
        assert "validat" in self.text.lower()

    def test_documents_exit_codes(self):
        for code in ("0", "2", "3", "4"):
            assert code in self.text

    def test_documents_pass_warn_fail(self):
        for word in ("PASS", "WARN", "FAIL"):
            assert word in self.text

    def test_documents_prohibited_shortcuts(self):
        assert "prohibited" in self.text.lower() or "must not" in self.text.lower()

    def test_documents_handoff(self):
        assert "render" in self.text.lower()


class TestRenderContentSkillContract:
    def setup_method(self):
        self.text = _read("render-content")

    def test_has_exact_cli_invocation(self):
        assert "python -m scripts.cli render --canonical" in self.text
        assert "--renderer" in self.text
        assert "multipage-markdown" in self.text

    def test_emphasizes_canonical_only_input(self):
        assert "canonical" in self.text.lower()

    def test_emphasizes_renderer_validation(self):
        assert "validat" in self.text.lower()

    def test_documents_exit_codes(self):
        for code in ("0", "2", "3", "4"):
            assert code in self.text

    def test_documents_pass_warn_fail(self):
        for word in ("PASS", "FAIL"):
            assert word in self.text

    def test_documents_prohibited_shortcuts(self):
        assert "prohibited" in self.text.lower() or "must not" in self.text.lower()

    def test_documents_cmd_render_as_fully_wired(self):
        # Task 14b wired cmd_render up to the real render pipeline -- the
        # skill contract must reflect that (no more "not yet implemented"
        # gap language) and say so explicitly.
        assert "wired" in self.text.lower()
        assert "not yet" not in self.text.lower()
        assert "notimplementederror" not in self.text.lower()
