"""Modern page fields are exported with remote identity using mocked PnP reads."""
import json
import shutil
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/link-remediation/collect-sharepoint-page-content.ps1"


def test_exports_canvas_and_webpart_fields(tmp_path):
    assert SCRIPT.exists(), "page-field collector is missing"
    harness = Path(__file__).parent / "fixtures/page-content-mocks.ps1"
    result = subprocess.run([shutil.which("pwsh"), "-NoProfile", "-File", str(harness),
                             "-Collector", str(SCRIPT), "-OutputDir", str(tmp_path)],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    exports = list(tmp_path.glob("*.page.json"))
    assert len(exports) == 1
    payload = json.loads(exports[0].read_text(encoding="utf-8-sig"))
    assert payload["SourceUrl"] == "https://tenant.sharepoint.com/sites/root/SitePages/news.aspx"
    assert "CanvasContent1" in payload["Fields"]
    assert "LayoutWebpartsContent" in payload["Fields"]
    assert "DOWNLOADED" in (tmp_path / "page-content.csv").read_text(encoding="utf-8-sig")
