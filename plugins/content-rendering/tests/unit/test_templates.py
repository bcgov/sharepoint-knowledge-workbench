"""
test_templates.py
==================

Tests for `templates` (Phase 6 Task 0.16): the shared module backing the
`create-markdown-rendering-template` and `create-aspx-rendering-template`
skills. Both skills instantiate a new *rendering* template file (page
structure -- headings/body/media placement) from one of the plugin's
canonical starter templates under `assets/templates/{generic,solutions/
ceis}/{markdown,aspx}/` (see that directory's own comment headers for the
real evidence each starter is derived from -- Sample manual rendered
output for markdown, Phase 3.0 Sec.15's tenant experiment for ASPX).

Distinct from the *agent/native-skill* template system Task 0.7/0.8 owns
(agent instructions, answer formatting) -- these are page/document-layout
templates only.
"""

from pathlib import Path

import pytest

import templates


def test_create_markdown_template_generic_profile(tmp_path):
    dest = tmp_path / "my-template.md"
    tpl = templates.create_rendering_template(
        profile="generic", fmt="markdown", output_path=dest,
    )

    assert dest.exists()
    assert tpl.profile == "generic"
    assert tpl.format == "markdown"
    assert "{{title}}" in tpl.content
    assert "{{body}}" in tpl.content
    assert dest.read_text(encoding="utf-8") == tpl.content

    sidecar = dest.with_suffix(dest.suffix + ".meta.json")
    assert sidecar.exists()


def test_create_markdown_template_standard_manual_profile(tmp_path):
    dest = tmp_path / "standard-manual-template.md"
    tpl = templates.create_rendering_template(
        profile="standard-manual", fmt="markdown", output_path=dest,
    )
    assert tpl.profile == "standard-manual"
    assert "{{title}}" in tpl.content
    assert "{{body}}" in tpl.content


def test_create_aspx_template_generic_profile(tmp_path):
    dest = tmp_path / "my-template.html"
    tpl = templates.create_rendering_template(
        profile="generic", fmt="aspx", output_path=dest,
    )
    assert dest.exists()
    assert tpl.format == "aspx"
    assert "{{title}}" in tpl.content
    assert "{{body}}" in tpl.content
    assert "<html" not in tpl.content  # fragment only, no page wrapper


def test_create_aspx_template_standard_manual_profile(tmp_path):
    dest = tmp_path / "standard-manual-template.html"
    tpl = templates.create_rendering_template(
        profile="standard-manual", fmt="aspx", output_path=dest,
    )
    assert tpl.profile == "standard-manual"
    assert tpl.format == "aspx"


def test_unknown_profile_raises():
    with pytest.raises(templates.UnknownTemplateProfileError):
        templates.create_rendering_template(
            profile="nonexistent", fmt="markdown", output_path=Path("/tmp/x.md"),
        )


def test_unknown_format_raises():
    with pytest.raises(templates.UnknownTemplateFormatError):
        templates.create_rendering_template(
            profile="generic", fmt="pdf", output_path=Path("/tmp/x.pdf"),
        )


def test_load_rendering_template_round_trips(tmp_path):
    dest = tmp_path / "my-template.md"
    created = templates.create_rendering_template(
        profile="generic", fmt="markdown", output_path=dest,
    )
    loaded = templates.load_rendering_template(dest)

    assert loaded.profile == created.profile
    assert loaded.format == created.format
    assert loaded.content == created.content


def test_load_missing_sidecar_raises(tmp_path):
    dest = tmp_path / "orphan.md"
    dest.write_text("## {{title}}\n\n{{body}}\n")
    with pytest.raises(templates.MissingTemplateMetadataError):
        templates.load_rendering_template(dest)

