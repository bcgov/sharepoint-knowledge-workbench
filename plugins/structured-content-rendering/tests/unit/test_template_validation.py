"""
test_template_validation.py
============================

Tests for `template_validation` (Phase 6 Task 0.16): the
`validate-rendering-template` skill. Validates a `RenderingTemplate`
(from `templates.py`) against schema/placeholder/required-section/
format-profile-compatibility rules, with a negative control for every
detection class -- each check has at least one test proving it actually
rejects the defect it claims to catch, not just that valid templates
pass.
"""

import pytest

import templates
import template_validation as tv


def _template(content, fmt="markdown", profile="generic"):
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
    ("ceis", "markdown"),
    ("generic", "aspx"),
    ("ceis", "aspx"),
])
def test_canonical_starter_templates_pass(tmp_path, profile, fmt):
    dest = tmp_path / f"{profile}-{fmt}.tpl"
    template = templates.create_rendering_template(profile, fmt, dest)
    report = tv.validate_rendering_template(template)
    assert report.status == "PASS", report.issues


# ---------------------------------------------------------------------------
# Negative controls -- one per detection class
# ---------------------------------------------------------------------------

def test_missing_title_placeholder_fails():
    tpl = _template("{{body}}\n", fmt="markdown")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "missing_placeholder" for i in report.issues)


def test_missing_body_placeholder_fails():
    tpl = _template("## {{title}}\n", fmt="markdown")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "missing_placeholder" for i in report.issues)


def test_unknown_placeholder_fails():
    tpl = _template("## {{title}}\n\n{{body}}\n\n{{unsupported_token}}\n", fmt="markdown")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "unknown_placeholder" for i in report.issues)


def test_markdown_title_not_in_heading_line_fails():
    tpl = _template("{{title}}\n\n{{body}}\n", fmt="markdown")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "title_not_in_heading" for i in report.issues)


def test_aspx_title_not_in_heading_tag_fails():
    tpl = _template("{{title}}\n{{body}}\n", fmt="aspx")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "title_not_in_heading" for i in report.issues)


def test_aspx_full_page_wrapper_fails():
    tpl = _template("<html><body><h1>{{title}}</h1>{{body}}</body></html>", fmt="aspx")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "forbidden_page_wrapper" for i in report.issues)


def test_unknown_format_fails():
    tpl = _template("{{title}}\n{{body}}\n", fmt="docx")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "unknown_format" for i in report.issues)


def test_unknown_profile_fails():
    tpl = _template("## {{title}}\n\n{{body}}\n", fmt="markdown", profile="nonexistent")
    report = tv.validate_rendering_template(tpl)
    assert report.status == "FAIL"
    assert any(i.code == "unknown_profile" for i in report.issues)
