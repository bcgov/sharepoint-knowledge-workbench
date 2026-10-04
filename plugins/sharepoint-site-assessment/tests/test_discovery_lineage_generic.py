"""
test_discovery_lineage_generic.py

Purpose:
    The discovery-lineage report generators must be site-agnostic. Each test feeds a small, unrelated "second site" fixture and
    checks that both the numbers and the narrative come from that fixture: nothing is inherited from the site the scripts were
    originally written for, and a metric that cannot be observed is reported as unavailable instead of being invented.

Layer: plugins/sharepoint-site-assessment -- tests
"""

import base64
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from test_genericity_and_independence import PROJECT_LITERALS, _literal_pattern  # noqa: E402

LINEAGE = Path(__file__).resolve().parents[1] / "scripts" / "discovery-lineage"
EXTRA_LITERALS = tuple(base64.b64decode(x).decode() for x in ["YmNzcw==", "QnJhbmNoIEluZm8="])
ORIGINAL_SITE_NUMBERS = ("654", "4792", "193", "181")


def run_script(name, *args):
    return subprocess.run([sys.executable, str(LINEAGE / name), *args], capture_output=True, text=True, timeout=120)


@pytest.fixture()
def second_site(tmp_path):
    """An unrelated site's discovery outputs, deliberately tiny and different from any real site."""
    root = tmp_path / "export"
    (root / "all_aspx_pages").mkdir(parents=True)
    (root / "all_aspx_pages" / "aspx-manifest.json").write_text(json.dumps([{"file": "a.aspx"}, {"file": "b.aspx"}, {"file": "c.aspx"}]))
    (root / "all_aspx_pages" / "a.aspx").write_text('<a href="http://old.example.org/Pages/home.aspx">home</a>')
    nav = root / "analysis" / "navigation"
    nav.mkdir(parents=True)
    (nav / "top-nav.json").write_text(json.dumps([{"Title": "Home", "Url": "/", "Children": []}, {"Title": "Docs", "Url": "/docs"}]))
    (nav / "quick-launch-nav.json").write_text(json.dumps([{"Title": "Lists", "Url": "/lists"}]))
    config = tmp_path / "config.psd1"
    config.write_text(f'@{{ ExportBase = "{root.as_posix()}" }}')
    return root, config


def assert_inherits_nothing(text):
    for number in ORIGINAL_SITE_NUMBERS:
        assert not re.search(rf"(?<![\d.]){number}(?![\d])", text), f"inherited figure {number}"
    for literal in PROJECT_LITERALS + EXTRA_LITERALS:
        assert not _literal_pattern(literal).search(text), f"inherited literal {literal!r}"


def test_meta_review_reports_only_observed_metrics(second_site, tmp_path):
    root, config = second_site
    out = tmp_path / "out"
    result = run_script("generate-master-discovery-meta-review.py", "--config", str(config), "--output-dir", str(out), "--site-name", "Other Site")
    assert result.returncode == 0, result.stderr
    report = (out / "MASTER-DISCOVERY-META-REVIEW-CATALOG.md").read_text(encoding="utf-8")
    assert "3" in report                       # the three pages in this site's manifest
    assert "unavailable" in report             # web parts, links, groups ... were not observed
    assert "Unknown" in report                 # no basis for a complexity rating
    assert_inherits_nothing(report)
    assert not re.search(r"(?i)oob_pages.*\d|spfx_candidates.*\d", report.split("## Data quality")[0].replace("unavailable", ""))


def test_meta_review_with_no_outputs_fails_instead_of_inventing_a_report(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    config = tmp_path / "config.psd1"
    config.write_text(f'@{{ ExportBase = "{empty.as_posix()}" }}')
    result = run_script("generate-master-discovery-meta-review.py", "--config", str(config), "--output-dir", str(tmp_path / "out"))
    assert result.returncode == 2 and "nothing to review" in result.stderr
    assert not (tmp_path / "out" / "MASTER-DISCOVERY-META-REVIEW-CATALOG.md").exists()


def test_meta_review_flags_invalid_input_and_never_falls_back_to_defaults(second_site, tmp_path):
    root, config = second_site
    (root / "all_aspx_pages" / "aspx-manifest.json").write_text("{not json")
    (root / "analysis" / "webpart-code-groups.json").write_text(json.dumps({"groups": [{}, {}]}))
    out = tmp_path / "out"
    result = run_script("generate-master-discovery-meta-review.py", "--config", str(config), "--output-dir", str(out))
    assert result.returncode == 0 and "aspx-manifest.json" in result.stderr
    report = (out / "MASTER-DISCOVERY-META-REVIEW-CATALOG.md").read_text(encoding="utf-8")
    assert "Input problem" in report
    assert_inherits_nothing(report)


def test_navigation_web_count_is_only_what_the_caller_supplies(second_site, tmp_path):
    root, config = second_site
    out = tmp_path / "out"
    result = run_script("generate-deep-nav-analysis.py", "--config", str(config), "--output-dir", str(out), "--site-name", "Other Site")
    assert result.returncode == 0, result.stderr
    text = (out / "SITE-NAVIGATION-CHROME-SUMMARY.md").read_text(encoding="utf-8")
    assert re.search(r"Subwebs Scanned\*\*: unavailable", text)
    out2 = tmp_path / "out2"
    run_script("generate-deep-nav-analysis.py", "--config", str(config), "--output-dir", str(out2), "--web-count", "2")
    assert re.search(r"Subwebs Scanned\*\*: 2\b", (out2 / "SITE-NAVIGATION-CHROME-SUMMARY.md").read_text(encoding="utf-8"))


def test_webpart_catalog_has_no_site_specific_conclusions(tmp_path):
    analysis = tmp_path / "analysis"
    analysis.mkdir()
    group = {"category": "TextOnly", "instanceCount": 1, "pagePartPairs": [["page.aspx", "wp1"]], "signature": "",
             "sampleContent": '<p>Contact <a href="mailto:help@example.org">support</a> for help. See <a href="/docs/guide.pdf">guide</a>.</p>'}
    (analysis / "webpart-code-groups.json").write_text(json.dumps({"groups": [group]}))
    result = run_script("generate-deep-webpart-analysis.py", str(analysis), "Other Site")
    assert result.returncode == 0, result.stdout + result.stderr
    text = (analysis / "ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md").read_text(encoding="utf-8")
    assert f"**Generated:** {date.today().isoformat()}" in text      # not a frozen date
    assert "Heuristic classification" in text                        # inferred conclusions are labelled as such
    for word in ("Y291cnQ=", "c3VydmV5", "c3VwZXJ2aXNvcg==", "YnJhbmNo"):
        assert not re.search(base64.b64decode(word).decode(), text, re.IGNORECASE)
    assert_inherits_nothing(text)


def test_link_analysis_derives_source_host_and_target_from_arguments(second_site, tmp_path):
    root, config = second_site
    out = tmp_path / "out"
    result = run_script("generate-deep-link-analysis.py", "--config", str(config), "--output-dir", str(out), "--site-name", "Other Site",
                        "--site-url", "http://old.example.org/site", "--target-site-url", "https://new.example.com/sites/Fresh")
    assert result.returncode == 0, result.stderr
    report = (out / "LEGACY-LINK-INVENTORY-REPORT.md").read_text(encoding="utf-8")
    assert "https://new.example.com/sites/Fresh/Pages/home.aspx" in report
    assert json.loads((out / "link-summary.json").read_text())["flagged_links"] == 1
    assert_inherits_nothing(report)


def test_no_discovery_lineage_script_carries_site_literals_or_urls():
    offenders = []
    for path in sorted(LINEAGE.iterdir()):
        if path.suffix not in {".py", ".ps1"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for literal in PROJECT_LITERALS + EXTRA_LITERALS:
            if _literal_pattern(literal).search(text):
                offenders.append((path.name, literal))
        for match in re.finditer(r"https?://[A-Za-z0-9.-]+\.[a-z]{2,}", text):
            if "example" not in match.group(0):
                offenders.append((path.name, match.group(0)))
    assert not offenders, offenders


def test_meta_review_counts_nested_pages_only_when_the_manifest_is_absent_and_says_so(tmp_path):
    root = tmp_path / "export"
    (root / "all_aspx_pages" / "sub" / "deeper").mkdir(parents=True)
    for rel in ("a.aspx", "sub/b.aspx", "sub/deeper/c.aspx"):
        (root / "all_aspx_pages" / rel).write_text("<html/>")
    config = tmp_path / "config.psd1"
    config.write_text(f'@{{ ExportBase = "{root.as_posix()}" }}')
    out = tmp_path / "out"
    result = run_script("generate-master-discovery-meta-review.py", "--config", str(config), "--output-dir", str(out))
    assert result.returncode == 0, result.stderr
    report = (out / "MASTER-DISCOVERY-META-REVIEW-CATALOG.md").read_text(encoding="utf-8")
    assert "counted from the downloaded .aspx files" in report


def test_meta_review_never_substitutes_a_count_for_an_unreadable_manifest(tmp_path):
    root = tmp_path / "export"
    (root / "all_aspx_pages").mkdir(parents=True)
    (root / "all_aspx_pages" / "a.aspx").write_text("<html/>")
    (root / "all_aspx_pages" / "aspx-manifest.json").write_text("{broken")
    (root / "analysis").mkdir()
    (root / "analysis" / "webpart-code-groups.json").write_text(json.dumps({"groups": [{}]}))
    config = tmp_path / "config.psd1"
    config.write_text(f'@{{ ExportBase = "{root.as_posix()}" }}')
    out = tmp_path / "out"
    result = run_script("generate-master-discovery-meta-review.py", "--config", str(config), "--output-dir", str(out))
    assert result.returncode == 0 and "aspx-manifest.json" in result.stderr
    report = (out / "MASTER-DISCOVERY-META-REVIEW-CATALOG.md").read_text(encoding="utf-8")
    assert "counted from the downloaded" not in report and "`total_pages`" in report   # listed as unavailable
