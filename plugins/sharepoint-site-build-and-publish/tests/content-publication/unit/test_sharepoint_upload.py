import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "content-publication"))

from sharepoint_publish_plan import PublishAction, PublishPlan  # noqa: E402
from sharepoint_upload import UploadError, UploadResult, upload_pages  # noqa: E402


def _plan(n=2):
    actions = [
        PublishAction(
            source_path=f"/local/rendered/page-{i}.html",
            target_library="SitePages",
            target_folder="SitePages/Demo",
            target_filename=f"page-{i}.aspx",
        )
        for i in range(n)
    ]
    return PublishPlan(document_id="demo-doc", actions=actions)


def test_upload_pages_requires_injected_uploader_no_live_default():
    plan = _plan()
    with pytest.raises(NotImplementedError):
        upload_pages(plan)


def test_upload_pages_succeeds_with_injected_uploader():
    plan = _plan()
    calls = []

    def fake_uploader(action):
        calls.append(action)
        return UploadResult(action=action, success=True, detail="created")

    results = upload_pages(plan, uploader=fake_uploader)

    assert len(results) == 2
    assert all(r.success for r in results)
    assert len(calls) == 2
    assert results[0].to_dict()["target_filename"] == "page-0.aspx"


def test_upload_pages_stops_on_first_failure():
    plan = _plan(n=3)
    calls = []

    def fake_uploader(action):
        calls.append(action)
        if len(calls) == 2:
            return UploadResult(action=action, success=False, detail="access denied")
        return UploadResult(action=action, success=True, detail="created")

    with pytest.raises(UploadError):
        upload_pages(plan, uploader=fake_uploader)

    # stopped after the failing second call -- did not attempt the third
    assert len(calls) == 2


def test_upload_pages_rejects_empty_plan():
    empty_plan = PublishPlan(document_id="empty-doc", actions=[])

    def fake_uploader(action):
        return UploadResult(action=action, success=True)

    with pytest.raises(UploadError):
        upload_pages(empty_plan, uploader=fake_uploader)


def test_upload_result_to_dict_has_no_project_literals():
    action = PublishAction(
        source_path="/local/rendered/index.html",
        target_library="SitePages",
        target_folder="SitePages/Demo",
        target_filename="index.aspx",
    )
    result = UploadResult(action=action, success=True, detail="created")
    payload = result.to_dict()

    blob = str(payload).lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['YmNnb3Y=', 'amFnLWNzYg==', 'Y21hdA==', 'anVzdGlu', 'Y2Vpcw==', 'b3Jkcw==']]:
        assert literal not in blob
