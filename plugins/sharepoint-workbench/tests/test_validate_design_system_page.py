"""Tests for validate_design_system_page.py (real file I/O and real subprocess exit codes).

Key Input Dependencies: publishing-sharepoint-pages/scripts/validate_design_system_page.py.
"""
import json
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS_DIR = PLUGIN / ".apm" / "skills" if (PLUGIN / ".apm" / "skills").exists() else PLUGIN / "skills"
SKILL = SKILLS_DIR / "publishing-sharepoint-pages"
SCRIPT = SKILL / "scripts" / "validate_design_system_page.py"
sys.path.insert(0, str(SCRIPT.parent))
import validate_design_system_page as v  # noqa: E402

ACK = "The B.C. Public Service acknowledges the territories of First Nations around B.C."
GOOD = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>T</title>
<link rel="stylesheet" href="/sites/X/SiteAssets/bc-gov-design-system/colors_and_type.css">
<style>a:focus-visible{{outline:2px solid #2E5DD7}}</style></head><body>
<header class="site-header"><img src="/sites/X/SiteAssets/bc-gov-design-system/icons/bc-logo.png" alt="BC">
<div class="subheader">Sheriff</div></header>
<main><nav aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li></ol></nav>
<h1>Title</h1><h2>Sub</h2><table><tr><th scope="row">A</th><td><a href="#x">b</a></td></tr></table>
<ul><li>one</li></ul></main><footer>{ACK}</footer></body></html>"""
SOURCE = "<html><body><h1>T</h1><table><tr><th>A</th><td><a href='#x'>b</a></td></tr></table><ul><li>one</li></ul></body></html>"


def failed(report):
    return set(report["failed"])


def test_good_page_passes_with_parity():
    assert v.validate(GOOD, SOURCE)["status"] == "PASS"


def test_missing_chrome_fails():
    bad = GOOD.replace('<header class="site-header">', "<header>")
    assert "site-header" in failed(v.validate(bad))


def test_breadcrumb_items_do_not_break_parity():
    assert "parity-li" not in failed(v.validate(GOOD, SOURCE))


def test_lost_table_row_fails_parity():
    src = SOURCE.replace("<table>", "<table><tr><td>x</td></tr>")
    assert "parity-tr" in failed(v.validate(GOOD, src))


def test_external_import_and_script_fail():
    bad = GOOD.replace("</style>", "@import url('https://fonts.googleapis.com/x');</style><script>1</script>")
    assert {"no-external-assets", "no-active-markup"} <= failed(v.validate(bad))


def test_unknown_hex_color_fails_when_tokens_given():
    bad = GOOD.replace("#2E5DD7", "#123456")
    assert "no-unknown-hex-colors" in failed(v.validate(bad, tokens_css="--x: #2E5DD7;"))


def test_cli_exit_codes(tmp_path):
    page = tmp_path / "p.html"
    page.write_text(GOOD, encoding="utf-8")
    ok = subprocess.run([sys.executable, str(SCRIPT), str(page)], capture_output=True, text=True)
    assert ok.returncode == 0 and json.loads(ok.stdout)["status"] == "PASS"
    page.write_text("<html></html>", encoding="utf-8")
    bad = subprocess.run([sys.executable, str(SCRIPT), str(page)], capture_output=True, text=True)
    assert bad.returncode == 1
    missing = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path / "none.html")], capture_output=True, text=True)
    assert missing.returncode == 2


def test_inlined_design_tokens_satisfy_the_css_check_without_a_link():
    inlined = GOOD.replace(
        '<link rel="stylesheet" href="/sites/X/SiteAssets/bc-gov-design-system/colors_and_type.css">\n',
        "").replace("<style>", "<style>:root{--color-brand-primary:#013366;--color-brand-link:#255A90;}")
    assert "design-system-css-link" not in failed(v.validate(inlined, SOURCE))
    missing = GOOD.replace(
        '<link rel="stylesheet" href="/sites/X/SiteAssets/bc-gov-design-system/colors_and_type.css">\n', "")
    assert "design-system-css-link" in failed(v.validate(missing, SOURCE))


def test_footer_links_do_not_count_as_source_links():
    with_footer = GOOD.replace(f"<footer>{ACK}</footer>",
                               f'<footer>{ACK}<a href="https://www2.gov.bc.ca/privacy">Privacy</a>'
                               f'<a href="https://www2.gov.bc.ca/disclaimer">Disclaimer</a></footer>')
    assert v.validate(with_footer, SOURCE)["status"] == "PASS"
