"""Producer -> planner -> executor contract for page publication.

Producer: `sharepoint-document-conversion`'s SharePointAspxRenderer writes `page-manifest.json` plus one HTML fragment per
page (a golden copy of its real output is in fixtures/rendered-output/). Planner: `build_page_publish_plan_from_render`.
Executor: `spo-upload-plan.ps1`, which injects each action's source_path file, unchanged, into a text web part.
The Markdown flow (`build_markdown_publish_plan`, `spo-publish-markdown-plan.ps1`) is a separate route and is unchanged.

Purpose:
    Verify the renderer manifest, publish planner, and upload executor preserve the page-publication contract.

Key Input Dependencies:
    - Rendered-output fixture, page-manifest.json contract, planner module, and pwsh for gated executor tests.

Function Index:
    rendered, _manifest, _write_manifest, test_plan_follows_manifest_order_not_filename_order, test_actions_point_at_the_real_html_fragments_with_page_identities, test_media_references_are_recorded_not_dropped, test_plan_declares_html_fragment_source_format_and_round_trips_json, test_contract_breaches_are_refused, test_markdown_only_output_is_rejected_with_a_pointer_to_the_markdown_flow, test_markdown_flow_is_unchanged_and_unmarked, test_legacy_markdown_to_page_plan_is_marked_markdown, _run_executor, _run_markdown_executor, test_markdown_executor_dry_run_plans_library_check_and_missing_folder_creation, test_executor_dry_run_accepts_the_planned_html_fragments_and_reports_media, test_executor_refuses_a_markdown_source_plan, test_executor_still_accepts_a_legacy_plan_without_source_format
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PACKAGE / "scripts" / "content-publication"))

from sharepoint_publish_plan import (  # noqa: E402
    PlanError,
    build_aspx_publish_plan,
    build_markdown_publish_plan,
    build_page_publish_plan_from_render,
)

GOLDEN = Path(__file__).resolve().parents[1] / "fixtures" / "rendered-output"
EXECUTOR = PACKAGE / "scripts" / "content-publication" / "spo-upload-plan.ps1"
MARKDOWN_EXECUTOR = PACKAGE / "scripts" / "content-publication" / "spo-publish-markdown-plan.ps1"
requires_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not installed")


# Copy the golden renderer output into an isolated writable test directory.
@pytest.fixture()
def rendered(tmp_path):
    """Copy the golden renderer output into an isolated writable test directory."""
    target = tmp_path / "rendered-output"
    shutil.copytree(GOLDEN, target)
    return target


# Read the rendered fixture manifest as a mutable dictionary for contract tests.
def _manifest(rendered):
    """Read the rendered fixture manifest as a mutable dictionary for contract tests."""
    return json.loads((rendered / "page-manifest.json").read_text(encoding="utf-8"))


# Persist a modified renderer manifest into the current test fixture.
def _write_manifest(rendered, data):
    """Persist a modified renderer manifest into the current test fixture."""
    (rendered / "page-manifest.json").write_text(json.dumps(data), encoding="utf-8")


# ---- planner: consumes the real renderer output ----------------------------------------------------------------

# Verify the contract that plan follows manifest order not filename order.
def test_plan_follows_manifest_order_not_filename_order(rendered):
    # The golden output was rendered from a grouped package whose publication map puts alpha before beta even though the
    # chunks were listed beta-first; the manifest order is authoritative and must be preserved.
    """Verify the contract that plan follows manifest order not filename order."""
    plan = build_page_publish_plan_from_render("doc-1", rendered, "SitePages/MyDoc")
    assert [a.target_filename for a in plan.actions] == ["alpha--22222222.aspx", "beta--11111111.aspx"]
    assert [a.title for a in plan.actions] == ["Alpha", "Beta"]


# Verify the contract that actions point at the real html fragments with page identities.
def test_actions_point_at_the_real_html_fragments_with_page_identities(rendered):
    """Verify the contract that actions point at the real html fragments with page identities."""
    plan = build_page_publish_plan_from_render("doc-1", rendered, "SitePages/MyDoc")
    for action in plan.actions:
        source = Path(action.source_path)
        assert source.is_absolute() and source.suffix == ".html" and source.is_file()
        assert source.read_text(encoding="utf-8").lstrip().startswith("<h1")  # a fragment, not Markdown
        assert action.target_library == "SitePages" and action.target_folder == "SitePages/MyDoc"
        assert action.target_filename == source.stem + ".aspx"


# Verify the contract that media references are recorded not dropped.
def test_media_references_are_recorded_not_dropped(rendered):
    """Verify the contract that media references are recorded not dropped."""
    plan = build_page_publish_plan_from_render("doc-1", rendered, "SitePages/MyDoc")
    by_page = {a.target_filename: a for a in plan.actions}
    assert by_page["beta--11111111.aspx"].media_refs == ["../media/diagram.png"]
    assert by_page["alpha--22222222.aspx"].media_refs == []
    assert "media_refs" not in by_page["alpha--22222222.aspx"].to_dict()


# Verify the contract that plan declares html fragment source format and round trips json.
def test_plan_declares_html_fragment_source_format_and_round_trips_json(rendered):
    """Verify the contract that plan declares html fragment source format and round trips json."""
    data = json.loads(json.dumps(build_page_publish_plan_from_render("doc-1", rendered, "SitePages/MyDoc").to_dict()))
    assert data["source_format"] == "html-fragment" and data["action_count"] == 2


# Verify the contract that contract breaches are refused.
@pytest.mark.parametrize("mutate, message", [
    (lambda r, m: (r / "page-manifest.json").unlink(), "not sharepoint-aspx renderer output"),
    (lambda r, m: m.update(schema_version="9.9"), "schema_version"),
    (lambda r, m: m.update(pages=[]), "lists no pages"),
    (lambda r, m: m["pages"][1].update(chunk_id=m["pages"][0]["chunk_id"],
                                       html_file=m["pages"][0]["html_file"]), "twice"),
    (lambda r, m: m["pages"][0].update(html_file="../outside.html"), "relative path inside"),
    (lambda r, m: m["pages"][0].update(html_file="/etc/hosts"), "relative path inside"),
    (lambda r, m: m["pages"][0].update(html_file="pages/other-name.html"), "must be '<chunk_id>.html'"),
    (lambda r, m: (r / m["pages"][0]["html_file"]).unlink(), "does not exist"),
    (lambda r, m: (r / "pages" / "stray--333.html").write_text("<p>x</p>"), "does not list"),
])
def test_contract_breaches_are_refused(rendered, mutate, message):
    """Verify the contract that contract breaches are refused."""
    manifest = _manifest(rendered)
    mutate(rendered, manifest)
    if (rendered / "page-manifest.json").exists():
        _write_manifest(rendered, manifest)
    with pytest.raises(PlanError, match=message):
        build_page_publish_plan_from_render("doc-1", rendered, "SitePages/MyDoc")


# Verify the contract that markdown only output is rejected with a pointer to the markdown flow.
def test_markdown_only_output_is_rejected_with_a_pointer_to_the_markdown_flow(tmp_path):
    """Verify the contract that markdown only output is rejected with a pointer to the markdown flow."""
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "topic--1.md").write_text("# Topic")
    with pytest.raises(PlanError, match="build_markdown_publish_plan"):
        build_page_publish_plan_from_render("doc-1", tmp_path, "SitePages/MyDoc")


# ---- the Markdown flow stays separate and is marked so the HTML executor can refuse it ---------------------------

# Verify the contract that markdown flow is unchanged and unmarked.
def test_markdown_flow_is_unchanged_and_unmarked(tmp_path):
    """Verify the contract that markdown flow is unchanged and unmarked."""
    (tmp_path / "a.md").write_text("# A")
    data = build_markdown_publish_plan("doc-1", tmp_path, "Lib", "Folder").to_dict()
    assert "source_format" not in data and set(data["actions"][0]) == {"source_path", "target_library", "target_folder", "target_filename"}


# Verify the contract that legacy markdown to page plan is marked markdown.
def test_legacy_markdown_to_page_plan_is_marked_markdown(tmp_path):
    """Verify the contract that legacy markdown to page plan is marked markdown."""
    (tmp_path / "a.md").write_text("# A")
    assert build_aspx_publish_plan("doc-1", tmp_path, "SitePages").to_dict()["source_format"] == "markdown"


# ---- executor: dry run only, no tenant I/O -------------------------------------------------------------------------

# Run the upload-plan PowerShell executor in its default dry-run mode.
def _run_executor(plan_path, tmp_path):
    """Run the upload-plan PowerShell executor in its default dry-run mode."""
    config = tmp_path / "config.psd1"
    config.write_text(
        "@{ Connection = @{ SiteUrl = 'https://example.invalid/sites/t'; ClientId = 'c'; TenantId = 't' }; "
        "Authentication = @{ TenantAdminUrl = 'https://example-admin.invalid' } }", encoding="utf-8")
    return subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(EXECUTOR), "-PlanPath", str(plan_path), "-ConfigPath", str(config)],
        capture_output=True, text=True, timeout=120,
    )


# Run the Markdown executor in its default dry-run mode.
def _run_markdown_executor(plan_path, tmp_path):
    """Run the Markdown executor in its default dry-run mode."""
    config = tmp_path / "config.psd1"
    config.write_text(
        "@{ Connection = @{ SiteUrl = 'https://example.invalid/sites/t'; ClientId = 'c'; TenantId = 't' }; "
        "Authentication = @{ TenantAdminUrl = 'https://example-admin.invalid' } }", encoding="utf-8")
    return subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(MARKDOWN_EXECUTOR), "-PlanPath", str(plan_path), "-ConfigPath", str(config)],
        capture_output=True, text=True, timeout=120,
    )


# Verify the Markdown dry run plans library verification and nested folder creation.
@requires_pwsh
def test_markdown_executor_dry_run_plans_library_check_and_missing_folder_creation(tmp_path):
    """Verify the Markdown dry run plans library verification and nested folder creation."""
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({
        "document_id": "assets",
        "actions": [{
            "source_path": str(tmp_path / "font.woff2"),
            "target_library": "SiteAssets",
            "target_folder": "shared/fonts/bc",
            "target_filename": "font.woff2",
        }],
    }), encoding="utf-8")

    result = _run_markdown_executor(plan_path, tmp_path)

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    actions = summary["actions"]
    action = actions[0] if isinstance(actions, list) else actions
    assert summary["safety"]["tenant_io"] == "none"
    assert action["verify_library"] == 'Get-PnPList -Identity "SiteAssets"'
    assert action["resolve_target_folder"] == (
        'Resolve-PnPFolder -SiteRelativePath "SiteAssets/shared/fonts/bc"'
    )
    assert action["verify_target_folder"] == 'Get-PnPFolder -Url "SiteAssets/shared/fonts/bc"'


# Verify the contract that executor dry run accepts the planned html fragments and reports media.
@requires_pwsh
def test_executor_dry_run_accepts_the_planned_html_fragments_and_reports_media(rendered, tmp_path):
    """Verify the contract that executor dry run accepts the planned html fragments and reports media."""
    plan = build_page_publish_plan_from_render("doc-1", rendered, "SitePages/MyDoc")
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan.to_dict()), encoding="utf-8")
    result = _run_executor(plan_path, tmp_path)
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["safety"]["tenant_io"] == "none" and summary["action_count"] == 2
    assert [a["page_name"] for a in summary["actions"]] == ["alpha--22222222", "beta--11111111"]
    assert summary["actions"][1]["media_refs"] == ["../media/diagram.png"]


# Verify the contract that executor refuses a markdown source plan.
@requires_pwsh
def test_executor_refuses_a_markdown_source_plan(tmp_path):
    """Verify the contract that executor refuses a markdown source plan."""
    (tmp_path / "a.md").write_text("# A")
    plan = build_aspx_publish_plan("doc-1", tmp_path, "SitePages")
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan.to_dict()), encoding="utf-8")
    result = _run_executor(plan_path, tmp_path)
    assert result.returncode != 0
    assert "source_format 'markdown'" in (result.stderr + result.stdout)


# Verify the contract that executor still accepts a legacy plan without source format.
@requires_pwsh
def test_executor_still_accepts_a_legacy_plan_without_source_format(tmp_path):
    """Verify the contract that executor still accepts a legacy plan without source format."""
    html = tmp_path / "page1.html"
    html.write_text("<p>x</p>")
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"document_id": "d", "actions": [
        {"source_path": str(html), "target_library": "SitePages", "target_folder": "", "target_filename": "page1.aspx"}]}))
    assert _run_executor(plan_path, tmp_path).returncode == 0
