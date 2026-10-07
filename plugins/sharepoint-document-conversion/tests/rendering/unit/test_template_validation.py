"""test_template_validation.py
============================

Purpose:
    Tests for `template_validation` (Phase 6 Task 0.16): the `validate-rendering-template` skill.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pytest
    - templates
    - template_validation

Tests for `template_validation` (Phase 6 Task 0.16): the
`validate-rendering-template` skill. Validates a `RenderingTemplate`
(from `templates.py`) against schema/placeholder/required-section/
format-profile-compatibility rules, with a negative control for every
detection class -- each check has at least one test proving it actually
rejects the defect it claims to catch, not just that valid templates
pass.

Key Functions Index:
    - _template()
    - test_canonical_starter_templates_pass()
    - test_missing_title_placeholder_fails()
    - test_missing_body_placeholder_fails()
    - test_unknown_placeholder_fails()
    - test_markdown_title_not_in_heading_line_fails()
    - test_aspx_title_not_in_heading_tag_fails()
    - test_aspx_full_page_wrapper_fails()
    - test_unknown_format_fails()
    - test_unknown_profile_fails()"""

import pytest

import templates
import template_validation as tv


# Create the rendering-template mapping consumed by the validation test.
def _template(content, fmt="markdown", profile="generic"):
    """Create the rendering-template mapping consumed by the validation test."""
    return templates.RenderingTemplate(
        schema_version=templates.TEMPLATE_SCHEMA_VERSION,
        profile=profile,
        format=fmt,
        content=content,
        path=None,
    )


# ---------------------------------------------------------------------------
# Positive controls -- the plugin's own canonical starters must all pass
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("profile,fmt", [
    ("generic", "markdown"),
    ("standard-manual", "markdown"),
    ("generic", "aspx"),
    ("standard-manual", "aspx"),
])
def test_canonical_starter_templates_pass(tmp_path, profile, fmt):
    """Verify canonical starter templates pass."""
    dest = tmp_path / f"{profile}-{fmt}.tpl"
    template = templates.create_rendering_template(profile, fmt, dest)
    report = tv.validate_rendering_template(template)
    assert report.status == "PASS", report.issues


# ---------------------------------------------------------------------------
# Negative controls -- one per detection class
# ---------------------------------------------------------------------------

def test_missing_title_placeholder_fails():
    """Verify missing title placeholder fails."""
    tpl = _template("{{body}}\n", fmt="markdown")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "missing_placeholder" for i in report.issues)


# Verify missing body placeholder fails.
def test_missing_body_placeholder_fails():
    """Verify missing body placeholder fails."""
    tpl = _template("## {{title}}\n", fmt="markdown")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "missing_placeholder" for i in report.issues)


# Verify unknown placeholder fails.
def test_unknown_placeholder_fails():
    """Verify unknown placeholder fails."""
    tpl = _template("## {{title}}\n\n{{body}}\n\n{{unsupported_token}}\n", fmt="markdown")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "unknown_placeholder" for i in report.issues)


# Verify Markdown title not in heading line fails.
def test_markdown_title_not_in_heading_line_fails():
    """Verify Markdown title not in heading line fails."""
    tpl = _template("{{title}}\n\n{{body}}\n", fmt="markdown")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "title_not_in_heading" for i in report.issues)


# Verify ASPX title not in heading tag fails.
def test_aspx_title_not_in_heading_tag_fails():
    """Verify ASPX title not in heading tag fails."""
    tpl = _template("{{title}}\n{{body}}\n", fmt="aspx")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "title_not_in_heading" for i in report.issues)


# Verify ASPX full page wrapper fails.
def test_aspx_full_page_wrapper_fails():
    """Verify ASPX full page wrapper fails."""
    tpl = _template("<html><body><h1>{{title}}</h1>{{body}}</body></html>", fmt="aspx")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "forbidden_page_wrapper" for i in report.issues)


# Verify unknown format fails.
def test_unknown_format_fails():
    """Verify unknown format fails."""
    tpl = _template("{{title}}\n{{body}}\n", fmt="docx")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "unknown_format" for i in report.issues)


# Verify unknown profile fails.
def test_unknown_profile_fails():
    """Verify unknown profile fails."""
    tpl = _template("## {{title}}\n\n{{body}}\n", fmt="markdown", profile="nonexistent")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "unknown_profile" for i in report.issues)
