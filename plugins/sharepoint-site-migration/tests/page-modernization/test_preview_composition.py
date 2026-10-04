"""
test_preview_composition.py
============================

Tests for composing a self-contained offline preview by merging site chrome
(navigation, header, logo, ancestors) with already-extracted page content
(modern-preview.html + metadata.json). Disk-only: no tenant I/O.

Every test drives the real CLI over the real filesystem -- no mocks on the
parsing or path-resolution path.
"""

import json
import subprocess
import sys


def _write_page_folder(tmp_path, *, title="Sample Page", page_name="Sample-Page.aspx",
                        content="<p>Hello world</p>", with_files=True):
    page_folder = tmp_path / "page"
    page_folder.mkdir()
    if with_files:
        (page_folder / "metadata.json").write_text(json.dumps({
            "Title": title,
            "PageName": page_name,
            "PageServerRelativeUrl": f"/sites/example/SitePages/{page_name}",
            "ExtractedAt": "2026-01-01T00:00:00Z",
        }), encoding="utf-8")
        (page_folder / "modern-preview.html").write_text(
            f'<html><body><div class="page-content">{content}</div></body></html>',
            encoding="utf-8",
        )
    return page_folder


def _write_chrome_folder(tmp_path, *, web=None, top_nav=None, ancestors=None, with_file=True):
    chrome_folder = tmp_path / "chrome"
    chrome_folder.mkdir()
    if with_file:
        chrome = {
            "Web": web if web is not None else {"Title": "Example Site", "SiteLogoUrl": "https://example.test/logo.png"},
            "TopNav": top_nav if top_nav is not None else [{"Title": "Home", "Url": "/home"}],
            "Ancestors": ancestors if ancestors is not None else [{"Title": "Root", "Url": "/"}],
        }
        (chrome_folder / "site-chrome.json").write_text(json.dumps(chrome), encoding="utf-8")
    return chrome_folder


def run_compose(scripts_dir, page_folder, chrome_folder, tmp_path, *extra):
    out = tmp_path / "full-preview.html"
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "preview_composition.py"),
         "--page-folder", str(page_folder),
         "--chrome-folder", str(chrome_folder),
         "--output", str(out), *extra],
        capture_output=True, text=True,
    )
    return result, out


def test_full_chrome_and_content_reports_observed(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path)
    chrome_folder = _write_chrome_folder(tmp_path)
    result, out = run_compose(scripts_dir, page_folder, chrome_folder, tmp_path)
    assert result.returncode == 0, result.stderr
    assert "Observed" in result.stdout
    html = out.read_text(encoding="utf-8")
    assert "Hello world" in html
    assert "Example Site" in html
    assert "Home" in html
    assert "Root" in html


def test_missing_page_folder_files_reports_unavailable_and_writes_nothing(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path, with_files=False)
    chrome_folder = _write_chrome_folder(tmp_path)
    result, out = run_compose(scripts_dir, page_folder, chrome_folder, tmp_path)
    assert result.returncode != 0
    assert "Unavailable" in result.stdout + result.stderr
    assert not out.exists()


def test_missing_chrome_folder_file_reports_unavailable_and_writes_nothing(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path)
    chrome_folder = _write_chrome_folder(tmp_path, with_file=False)
    result, out = run_compose(scripts_dir, page_folder, chrome_folder, tmp_path)
    assert result.returncode != 0
    assert "Unavailable" in result.stdout + result.stderr
    assert not out.exists()


def test_empty_page_content_reports_empty_and_writes_nothing(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path, content="")
    chrome_folder = _write_chrome_folder(tmp_path)
    result, out = run_compose(scripts_dir, page_folder, chrome_folder, tmp_path)
    assert result.returncode != 0
    assert "Empty" in result.stdout + result.stderr
    assert not out.exists()


def test_missing_logo_and_ancestors_reports_partial_but_still_writes_output(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path)
    chrome_folder = _write_chrome_folder(
        tmp_path, web={"Title": "Example Site"}, ancestors=[],
    )
    result, out = run_compose(scripts_dir, page_folder, chrome_folder, tmp_path)
    assert result.returncode == 0, result.stderr
    assert "Partial" in result.stdout
    assert "logo" in result.stdout
    assert "ancestors" in result.stdout
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "Hello world" in html


def test_partial_reason_never_fabricates_a_substitute_logo(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path)
    chrome_folder = _write_chrome_folder(tmp_path, web={"Title": "Example Site"})
    result, out = run_compose(scripts_dir, page_folder, chrome_folder, tmp_path)
    assert result.returncode == 0, result.stderr
    html = out.read_text(encoding="utf-8")
    assert "<img" not in html


def test_top_nav_beyond_five_entries_grouped_under_more(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path)
    top_nav = [{"Title": f"Item{i}", "Url": f"/item{i}"} for i in range(7)]
    chrome_folder = _write_chrome_folder(tmp_path, top_nav=top_nav)
    result, out = run_compose(scripts_dir, page_folder, chrome_folder, tmp_path)
    assert result.returncode == 0, result.stderr
    html = out.read_text(encoding="utf-8")
    assert ">More" in html
    assert "Item6" in html


def test_breadcrumb_includes_current_page_title(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path, title="My Page")
    chrome_folder = _write_chrome_folder(tmp_path)
    result, out = run_compose(scripts_dir, page_folder, chrome_folder, tmp_path)
    assert result.returncode == 0, result.stderr
    html = out.read_text(encoding="utf-8")
    assert "My Page" in html


def test_default_output_path_is_full_preview_html_in_page_folder(scripts_dir, tmp_path):
    page_folder = _write_page_folder(tmp_path)
    chrome_folder = _write_chrome_folder(tmp_path)
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "preview_composition.py"),
         "--page-folder", str(page_folder),
         "--chrome-folder", str(chrome_folder)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (page_folder / "full-preview.html").is_file()
