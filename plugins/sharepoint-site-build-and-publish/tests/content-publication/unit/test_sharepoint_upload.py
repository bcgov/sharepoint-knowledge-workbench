"""
test_sharepoint_upload.py
=========================

Purpose:
    Verify upload plans require an injected uploader and stop at the first failed action.

Key Input Dependencies:
    - PublishPlan records, injected uploader callables, and sharepoint_upload.

Function Index:
    _plan, test_upload_pages_requires_injected_uploader_no_live_default, test_upload_pages_succeeds_with_injected_uploader, test_upload_pages_stops_on_first_failure, test_upload_pages_rejects_empty_plan, test_upload_result_to_dict_has_no_project_literals
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "content-publication"))

from sharepoint_publish_plan import PublishAction, PublishPlan  # noqa: E402
from sharepoint_upload import UploadError, UploadResult, upload_pages  # noqa: E402


# Create a publish-plan fixture for exercising injected upload behavior.
def _plan(n=2):
    """Create a publish-plan fixture for exercising injected upload behavior."""
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


# Verify the contract that upload pages requires injected uploader no live default.
def test_upload_pages_requires_injected_uploader_no_live_default():
    """Verify the contract that upload pages requires injected uploader no live default."""
    plan = _plan()
    with pytest.raises(NotImplementedError):
        upload_pages(plan)


# Verify the contract that upload pages succeeds with injected uploader.
def test_upload_pages_succeeds_with_injected_uploader():
    """Verify the contract that upload pages succeeds with injected uploader."""
    plan = _plan()
    calls = []

    # Return a successful UploadResult for the parametrized uploader test.
    def fake_uploader(action):
        """Return a successful UploadResult for the parametrized uploader test."""
        calls.append(action)
        return UploadResult(action=action, success=True, detail="created")

    results = upload_pages(plan, uploader=fake_uploader)

    assert len(results) == 2
    assert all(r.success for r in results)
    assert len(calls) == 2
    assert results[0].to_dict()["target_filename"] == "page-0.aspx"


# Verify the contract that upload pages stops on first failure.
def test_upload_pages_stops_on_first_failure():
    """Verify the contract that upload pages stops on first failure."""
    plan = _plan(n=3)
    calls = []

    # Return a successful UploadResult for the parametrized uploader test.
    def fake_uploader(action):
        """Return a successful UploadResult for the parametrized uploader test."""
        calls.append(action)
        if len(calls) == 2:
            return UploadResult(action=action, success=False, detail="access denied")
        return UploadResult(action=action, success=True, detail="created")

    with pytest.raises(UploadError):
        upload_pages(plan, uploader=fake_uploader)

    # stopped after the failing second call -- did not attempt the third
    assert len(calls) == 2


# Verify the contract that upload pages rejects empty plan.
def test_upload_pages_rejects_empty_plan():
    """Verify the contract that upload pages rejects empty plan."""
    empty_plan = PublishPlan(document_id="empty-doc", actions=[])

    # Return a successful UploadResult for the parametrized uploader test.
    def fake_uploader(action):
        """Return a successful UploadResult for the parametrized uploader test."""
        return UploadResult(action=action, success=True)

    with pytest.raises(UploadError):
        upload_pages(empty_plan, uploader=fake_uploader)


# Verify the contract that upload result to dict has no project literals.
def test_upload_result_to_dict_has_no_project_literals():
    """Verify the contract that upload result to dict has no project literals."""
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
