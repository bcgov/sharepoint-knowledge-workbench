"""Tests for sp_text_webpart_html.py (real HTML files, real vocabulary JSON, real CLI subprocess).

Purpose: Verify the Text web part linter flags non-editor markup and harvests tenant captures safely.

Key Input Dependencies: scripts/sp_text_webpart_html.py, assets/rte-vocabulary.json.
Usage: python -m pytest plugins/sp-migration/tests/test_sp_text_webpart_html.py

Function index: problems, run_cli, test_* cases for check_html, harvest and the CLI exit codes.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS_DIR = PLUGIN / ".apm" / "skills" if (PLUGIN / ".apm" / "skills").exists() else PLUGIN / "skills"
SKILL = SKILLS_DIR / "publishing-sharepoint-pages"
SCRIPT = SKILL / "scripts" / "sp_text_webpart_html.py"
VOCAB = SKILL / "assets" / "rte-vocabulary.json"
sys.path.insert(0, str(SCRIPT.parent))
import sp_text_webpart_html as lint  # noqa: E402

TABLE = (
    '<div class="canvasRteResponsiveTable"><div class="tableLeftAlign tableWrapper">'
    '<table class="filledHeaderTableStyleTheme" title="Table"><tbody><tr>'
    '<td style="width: 800px"><strong>H</strong></td></tr></tbody></table></div></div>'
)


def problems(html: str) -> list:
    """Return the lint problems for an HTML string using the shipped vocabulary."""
    vocab, allow = lint.load_vocab(VOCAB)
    return lint.check_html(html, vocab, allow)


def test_editor_native_markup_has_no_problems():
    """Editor-native markup yields no problems."""
    html = '<h2>T</h2><p style="text-align:center">a <strong>b</strong> <a href="/x">l</a></p>' + TABLE
    assert problems(html) == []


def test_flags_unwrapped_div_with_inline_styles():
    """A styled, unwrapped div is flagged with its tokens attribute."""
    found = problems('<div data-sp-bc-tokens="1" style="background-color:#fef1d8"><p>x</p></div>')
    text = " ".join(m for _, m in found)
    assert "<div> only allowed" in text
    assert "background-color" in text
    assert "data-sp-bc-tokens" in text


def test_flags_font_family_raw_img_nested_table_and_colspan():
    """Unsupported fonts, images and table structure are flagged."""
    html = (
        '<p style="font-family:Arial">x</p><img src="/a.png">'
        '<table><tr><td colspan="2"><table><tr><td>n</td></tr></table></td></tr></table>'
    )
    text = " ".join(m for _, m in problems(html))
    assert "font-family" in text
    assert "raw <img>" in text
    assert "nested table" in text
    assert "colspan" in text


def test_unknown_class_is_flagged():
    """A class outside the vocabulary is flagged."""
    assert any("myBox" in m for _, m in problems('<p class="myBox">x</p>'))


def test_content_outside_rte_marker_is_ignored():
    """Only content inside data-sp-rte is linted."""
    html = '<div data-sp-canvascontrol="" style="x:y"><div data-sp-rte=""><p>ok</p></div></div><font>z</font>'
    assert problems(html) == []


def test_harvest_adds_per_tag_style_without_widening_other_tags(tmp_path):
    """Harvest allows a style only on the tag where it was captured."""
    vocab_copy = tmp_path / "vocab.json"
    shutil.copy(VOCAB, vocab_copy)
    capture = tmp_path / "capture.html"
    capture.write_text('<p>a <span style="font-size:28px" class="fontSizeNew">b</span></p>', encoding="utf-8")
    added = lint.harvest([capture], vocab_copy, write=True)
    saved = json.loads(vocab_copy.read_text(encoding="utf-8"))["tenant"]
    assert "span:font-size" in saved["styles"]
    assert "fontSizeNew" in saved["classes"]
    assert added["added_to_tenant"]["styles"] == ["span:font-size"]
    vocab, allow = lint.load_vocab(vocab_copy)
    assert lint.check_html('<span style="font-size:28px">x</span>', vocab, allow) == []
    assert lint.check_html('<p style="font-size:28px">x</p>', vocab, allow) != []


def test_harvest_reports_structural_problems_instead_of_allowing_them(tmp_path):
    """Harvest reports structural problems rather than allowing them."""
    vocab_copy = tmp_path / "vocab.json"
    shutil.copy(VOCAB, vocab_copy)
    capture = tmp_path / "capture.html"
    capture.write_text('<div style="color:red"><p>a</p></div>', encoding="utf-8")
    added = lint.harvest([capture], vocab_copy, write=True)
    assert added["structural_notes"]
    saved = json.loads(vocab_copy.read_text(encoding="utf-8"))["tenant"]
    assert "div" not in saved["tags"]


def run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run the linter CLI in a real subprocess from the given working directory."""
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd)


def test_cli_exit_codes_and_default_vocabulary(tmp_path):
    """The CLI exits 0 for clean and 1 for flagged markup."""
    good = tmp_path / "good.html"
    good.write_text("<p>ok</p>", encoding="utf-8")
    bad = tmp_path / "bad.html"
    bad.write_text('<p style="font-family:Arial">x</p>', encoding="utf-8")
    ok = run_cli("check", str(good), cwd=tmp_path)
    assert ok.returncode == 0, ok.stderr
    fail = run_cli("check", str(bad), cwd=tmp_path)
    assert fail.returncode == 1
    assert "font-family" in fail.stdout


def test_cli_rejects_missing_file(tmp_path):
    """The CLI exits 2 for a missing file."""
    result = run_cli("check", str(tmp_path / "missing.html"), cwd=tmp_path)
    assert result.returncode == 2
    assert "not found" in result.stderr
