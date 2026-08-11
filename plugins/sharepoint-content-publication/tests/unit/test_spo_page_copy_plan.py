import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from spo_page_copy_plan import CopyPagePlanError, build_copy_page_plan  # noqa: E402


def test_build_copy_page_plan_for_single_site_page():
    plan = build_copy_page_plan(
        source_site_url="https://tenant.sharepoint.com/sites/Test",
        target_site_url="https://tenant.sharepoint.com/sites/Prod",
        page_name="Briefing.aspx",
    )

    assert plan["operation"] == "copy-spo-page"
    assert plan["source"]["site_url"] == "https://tenant.sharepoint.com/sites/Test"
    assert plan["target"]["site_url"] == "https://tenant.sharepoint.com/sites/Prod"
    assert plan["page"]["name"] == "Briefing.aspx"
    assert plan["page"]["library"] == "Site Pages"
    assert plan["safety"]["tenant_io"] == "none"
    assert "Add-PnPPage" in plan["recommended_execution"]


def test_build_copy_page_plan_rejects_non_aspx_page_name():
    with pytest.raises(CopyPagePlanError, match="must end with .aspx"):
        build_copy_page_plan(
            source_site_url="https://tenant.sharepoint.com/sites/Test",
            target_site_url="https://tenant.sharepoint.com/sites/Prod",
            page_name="Briefing.html",
        )


def test_copy_page_plan_json_serializable():
    plan = build_copy_page_plan(
        source_site_url="https://tenant.sharepoint.com/sites/Test",
        target_site_url="https://tenant.sharepoint.com/sites/Prod",
        page_name="Briefing.aspx",
        overwrite=True,
    )

    encoded = json.dumps(plan)

    assert '"overwrite": true' in encoded
