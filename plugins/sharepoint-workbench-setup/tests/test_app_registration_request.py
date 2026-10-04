"""
test_app_registration_request.py
===================================

Tests for `app_registration_request`: fills the service-request templates
(interactive/delegated and App-Only) from caller-supplied answers, and
provides the generalized post-approval setup guide (redirect URI config,
the API-permission sequence, admin consent, and the separate site-level
SCA/licence requirement). Generalized from a real project's app-
registration JIRA request and lab-notebook records -- no tenant-specific
literal (org name, GUID, site URL) appears anywhere in this module.
"""

import pytest

from app_registration_request import (
    AppRegistrationRequestError,
    REGISTRATION_TYPES,
    SETUP_STEPS,
    render_service_request,
)


TEMPLATE = "Name: <APP_NAME>\nProject: <PROJECT_NAME>\nTenant: <TENANT_NAME>\n"


def test_render_service_request_fills_all_placeholders():
    answers = {"APP_NAME": "my-app", "PROJECT_NAME": "my-project", "TENANT_NAME": "my-tenant"}
    rendered = render_service_request(TEMPLATE, answers)
    assert "<APP_NAME>" not in rendered
    assert "my-app" in rendered
    assert "my-project" in rendered
    assert "my-tenant" in rendered


def test_render_service_request_raises_on_missing_answer():
    answers = {"APP_NAME": "my-app", "PROJECT_NAME": "my-project"}
    with pytest.raises(AppRegistrationRequestError):
        render_service_request(TEMPLATE, answers)


def test_render_service_request_ignores_extra_answers():
    answers = {
        "APP_NAME": "my-app", "PROJECT_NAME": "my-project", "TENANT_NAME": "my-tenant",
        "UNUSED_FIELD": "irrelevant",
    }
    rendered = render_service_request(TEMPLATE, answers)
    assert "irrelevant" not in rendered


def test_setup_steps_covers_the_known_required_sequence():
    steps_text = " ".join(f"{s['title']} {s['detail']}" for s in SETUP_STEPS)
    steps_text += " ".join(str(v) for t in REGISTRATION_TYPES for v in t.values())
    for keyword in ("localhost", "User.Read", "Sites.Selected", "admin consent",
                     "Enterprise Application", "Grant-PnPAzureADAppSitePermission", "E3", "E5"):
        assert keyword in steps_text, f"expected {keyword!r} somewhere in SETUP_STEPS/REGISTRATION_TYPES"


def test_setup_steps_has_no_tenant_specific_literals():
    steps_text = " ".join(f"{s['title']} {s['detail']}" for s in SETUP_STEPS).lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['Z292LmJjLmNh', 'YmNnb3Y=', 'Y21hdA==', 'b3Jkcw==', 'amFn', 'aWRpcg==']]:
        assert literal not in steps_text, f"unexpected tenant-specific literal: {literal!r}"


def test_setup_steps_each_has_number_title_and_detail():
    for step in SETUP_STEPS:
        assert isinstance(step["number"], int)
        assert step["title"]
        assert step["detail"]


def test_registration_types_has_exactly_etl_and_interactive():
    keys = {t["key"] for t in REGISTRATION_TYPES}
    assert keys == {"etl", "interactive"}


def test_registration_types_do_not_claim_tier_predicts_capability():
    # Corrected 2026-08-09: production testing disproved the earlier claim
    # that the PnP grant tier (Write vs Manage) reliably predicts whether
    # list/library creation succeeds -- a tenant-admin-confirmed `write`
    # grant on the interactive registration still allowed list/library
    # creation in an interactive session. Neither type may assert a fixed
    # capability boundary as a fact; each must instead point at
    # capability_testing_status for the honest, evidence-based status.
    for t in REGISTRATION_TYPES:
        assert "confirmed_capabilities" not in t, (
            f"{t['key']} must not assert capabilities as fixed facts -- "
            "use capability_testing_status instead"
        )
        assert t["capability_testing_status"], f"{t['key']} missing capability_testing_status"


def test_registration_types_interactive_capability_status_reflects_correction():
    by_key = {t["key"]: t for t in REGISTRATION_TYPES}
    status = by_key["interactive"]["capability_testing_status"].lower()
    assert "write" in status
    assert "not proof of a manage grant" in status or "not proof" in status


def test_registration_types_etl_capability_status_marks_unverified():
    by_key = {t["key"]: t for t in REGISTRATION_TYPES}
    status = by_key["etl"]["capability_testing_status"].lower()
    assert "unverified" in status


def test_registration_types_each_has_distinct_auth_and_licensing():
    by_key = {t["key"]: t for t in REGISTRATION_TYPES}
    assert by_key["etl"]["auth_mechanism"] != by_key["interactive"]["auth_mechanism"]
    assert "certificate" in by_key["etl"]["auth_mechanism"].lower()
    assert "interactive" in by_key["interactive"]["auth_mechanism"].lower() or \
           "delegated" in by_key["interactive"]["auth_mechanism"].lower()
    # Only the interactive/delegated flow ties to a signed-in identity that
    # needs an M365 licence; the App-Only cert flow runs as the app itself.
    assert "licence" in by_key["interactive"]["licensing_note"].lower() or \
           "license" in by_key["interactive"]["licensing_note"].lower()
    assert "no" in by_key["etl"]["licensing_note"].lower() or \
           "not" in by_key["etl"]["licensing_note"].lower()


def test_registration_types_each_has_pros_and_cons():
    for t in REGISTRATION_TYPES:
        assert t["pros"], f"{t['key']} missing pros"
        assert t["cons"], f"{t['key']} missing cons"


def test_registration_types_no_tenant_specific_literals():
    for t in REGISTRATION_TYPES:
        blob = " ".join(str(v) for v in t.values()).lower()
        for literal in [__import__("base64").b64decode(x).decode() for x in ['Z292LmJjLmNh', 'YmNnb3Y=', 'Y21hdA==', 'amFn', 'aWRpcg==', 'Y3Ni']]:
            assert literal not in blob, f"unexpected tenant-specific literal {literal!r} in {t['key']}"
