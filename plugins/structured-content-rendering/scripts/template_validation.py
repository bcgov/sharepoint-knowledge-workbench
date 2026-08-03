"""
template_validation.py
========================

Phase 6 Task 0.16 -- the `validate-rendering-template` skill. Validates
a `RenderingTemplate` (`templates.py`) against schema/placeholder/
required-section/format-profile-compatibility rules, independent of any
canonical package or render output (`validate-rendered-output`, a
separate skill in `renderers/validate_rendered.py`, is what validates
actual rendered *output*; this module validates the *template
definition itself*, before it is ever used to render anything).

Every issue this module raises is `severity="error"` -- like
`renderers.validate_rendered`'s own render-layer validator, there is
nothing about a malformed template that a human should "accept as-is"
the way a reviewable canonical-content discrepancy might be, so status
is always PASS or FAIL, never WARN.
"""

import re
from dataclasses import dataclass, field

import templates as templates_module

_PLACEHOLDER = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")

KNOWN_PLACEHOLDERS = frozenset({"title", "body", "media_dir"})
REQUIRED_PLACEHOLDERS = frozenset({"title", "body"})

_MARKDOWN_TITLE_HEADING = re.compile(r"(?m)^#{1,6}[ \t]+.*\{\{title\}\}")
_ASPX_TITLE_HEADING = re.compile(r"<h[1-6][^>]*>\s*\{\{title\}\}\s*</h[1-6]>")
_ASPX_PAGE_WRAPPER = re.compile(r"(?i)</?(html|head|body)\b")


@dataclass
class TemplateValidationIssue:
    severity: str
    code: str
    message: str


@dataclass
class TemplateValidationReport:
    status: str
    issues: list = field(default_factory=list)


def _error(code: str, message: str) -> "TemplateValidationIssue":
    return TemplateValidationIssue(severity="error", code=code, message=message)


def _check_known_profile_and_format(template) -> list:
    issues = []
    if template.profile not in templates_module.KNOWN_PROFILES:
        issues.append(_error(
            "unknown_profile",
            f"template profile {template.profile!r} is not one of this "
            f"plugin's known profiles ({sorted(templates_module.KNOWN_PROFILES)})",
        ))
    if template.format not in templates_module.KNOWN_FORMATS:
        issues.append(_error(
            "unknown_format",
            f"template format {template.format!r} is not one of this "
            f"plugin's known formats ({sorted(templates_module.KNOWN_FORMATS)})",
        ))
    return issues


def _check_placeholders(template) -> list:
    issues = []
    present = set(_PLACEHOLDER.findall(template.content))

    missing = REQUIRED_PLACEHOLDERS - present
    for name in sorted(missing):
        issues.append(_error(
            "missing_placeholder",
            f"required placeholder {{{{{name}}}}} is missing from the template",
        ))

    unknown = present - KNOWN_PLACEHOLDERS
    for name in sorted(unknown):
        issues.append(_error(
            "unknown_placeholder",
            f"placeholder {{{{{name}}}}} is not one of this plugin's known "
            f"placeholders ({sorted(KNOWN_PLACEHOLDERS)})",
        ))
    return issues


def _check_title_in_heading(template) -> list:
    """The `{{title}}` placeholder must appear inside a heading construct
    appropriate to the template's format -- a markdown `#`-prefixed
    heading line, or an ASPX `<h1>`-`<h6>` tag. A template that places
    `{{title}}` as bare body text would render a page with no actual
    heading element."""
    if "{{title}}" not in template.content:
        return []  # already reported by _check_placeholders
    if template.format == "markdown":
        if not _MARKDOWN_TITLE_HEADING.search(template.content):
            return [_error(
                "title_not_in_heading",
                "{{title}} does not appear on a markdown heading line "
                "(e.g. '## {{title}}')",
            )]
    elif template.format == "aspx":
        if not _ASPX_TITLE_HEADING.search(template.content):
            return [_error(
                "title_not_in_heading",
                "{{title}} does not appear inside an <h1>-<h6> heading tag",
            )]
    return []


def _check_aspx_fragment_only(template) -> list:
    """An ASPX rendering template must be a bare fragment (suitable for a
    single `Add-PnPPageTextPart`), never a full page with `<html>`/
    `<head>`/`<body>` wrapper tags -- Phase 3.0 Sec.15 confirmed raw
    wrapped `.aspx` upload to Site Pages is `Access denied`, a platform
    boundary; a template that produces that shape would be building
    toward a route that cannot work."""
    if template.format != "aspx":
        return []
    if _ASPX_PAGE_WRAPPER.search(template.content):
        return [_error(
            "forbidden_page_wrapper",
            "ASPX rendering template contains an <html>/<head>/<body> "
            "wrapper tag -- templates must be bare fragments for "
            "Add-PnPPageTextPart, never a full wrapped page (raw .aspx "
            "upload is a confirmed Access denied platform boundary)",
        )]
    return []


def validate_rendering_template(template: "templates_module.RenderingTemplate") -> "TemplateValidationReport":
    """Validate `template` (a `RenderingTemplate`, typically freshly
    created by `templates.create_rendering_template` or loaded via
    `templates.load_rendering_template`) against this plugin's
    schema/placeholder/required-section/format-profile-compatibility
    rules. Returns a `TemplateValidationReport`, always PASS or FAIL."""
    issues = []
    issues.extend(_check_known_profile_and_format(template))
    issues.extend(_check_placeholders(template))
    issues.extend(_check_title_in_heading(template))
    issues.extend(_check_aspx_fragment_only(template))

    status = "FAIL" if issues else "PASS"
    return TemplateValidationReport(status=status, issues=issues)
