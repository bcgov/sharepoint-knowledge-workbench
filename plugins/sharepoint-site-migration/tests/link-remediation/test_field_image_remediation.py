"""Tests for field_image_remediation.py -- inventory-verified remediation of
embedded <img> references in a rich-text list field, distinct from both
update-page-links (blind rule-based page-body rewrite) and
update-links-in-documents (Office/PDF file content): this module
cross-references each item's embedded image reference against a real
document-library inventory before proposing any fix, so a rewrite is only
ever proposed for a confirmed-matching file, never a blind regex guess."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "link-remediation"))

import pytest

from field_image_remediation import (
    ConfirmationRequired,
    ExecutorRequired,
    classify_field_images,
    generate_gap_report,
    plan_field_image_remediation,
    apply_field_image_remediation,
)
from link_outcomes import Outcome
from link_rules import RewriteRuleset


def _ruleset() -> RewriteRuleset:
    return RewriteRuleset.from_dict(
        {"rules": [{"match": "/PublishingImages/", "replacement": "/Images1/"}]}
    )


class TestClassifyFieldImages:
    def test_no_img_tag_at_all(self):
        result = classify_field_images({"1": "Just a text description"}, inventory={})
        assert result["1"].status == "no_img_tag"

    def test_img_tag_with_no_src_attribute(self):
        result = classify_field_images({"1": '<img alt="" style="margin:5px;" />'}, inventory={})
        assert result["1"].status == "img_no_src"

    def test_matched_when_filename_exists_in_inventory(self):
        html = '<img src="/sites/Demo/PublishingImages/Lists/Authors/EditForm/photo.jpg" />'
        result = classify_field_images({"1": html}, inventory={"photo.jpg": "/sites/Demo/Images1/photo.jpg"})
        assert result["1"].status == "matched"
        assert result["1"].extracted_filename == "photo.jpg"
        assert result["1"].matched_relative_url == "/sites/Demo/Images1/photo.jpg"

    def test_missing_when_filename_not_in_inventory(self):
        html = '<img src="/sites/Demo/PublishingImages/photo.jpg" />'
        result = classify_field_images({"1": html}, inventory={})
        assert result["1"].status == "missing"

    def test_filename_matching_is_case_insensitive(self):
        html = '<img src="/sites/Demo/PublishingImages/Photo.JPG" />'
        result = classify_field_images({"1": html}, inventory={"photo.jpg": "/x/photo.jpg"})
        assert result["1"].status == "matched"

    def test_url_encoded_filename_is_decoded_before_lookup(self):
        html = '<img src="/sites/Demo/PublishingImages/My%20Photo.jpg" />'
        result = classify_field_images({"1": html}, inventory={"my photo.jpg": "/x/my photo.jpg"})
        assert result["1"].status == "matched"


class TestPlanFieldImageRemediation:
    def test_empty_items_is_empty_outcome(self):
        plan = plan_field_image_remediation({}, inventory={}, ruleset=_ruleset())
        assert plan.outcome == Outcome.EMPTY

    def test_only_matched_items_get_a_proposed_fix(self):
        items = {
            "1": '<img src="/sites/Demo/PublishingImages/photo.jpg" />',  # matched
            "2": '<img src="/sites/Demo/PublishingImages/gone.jpg" />',  # missing
            "3": "plain text",  # no_img_tag
        }
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/sites/Demo/Images1/photo.jpg"}, ruleset=_ruleset()
        )
        assert plan.change_count == 1
        fixed = plan.changed_items[0]
        assert fixed.source_id == "1"
        assert "/Images1/" in fixed.new_field_value
        assert "/PublishingImages/" not in fixed.new_field_value

    def test_rewrite_preserves_the_rest_of_the_html(self):
        items = {"1": '<p>Hi</p><img src="/sites/Demo/PublishingImages/photo.jpg" alt="me"/>'}
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/sites/Demo/Images1/photo.jpg"}, ruleset=_ruleset()
        )
        assert "<p>Hi</p>" in plan.changed_items[0].new_field_value
        assert 'alt="me"' in plan.changed_items[0].new_field_value

    def test_missing_and_broken_placeholder_items_are_reported_not_silently_dropped(self):
        items = {
            "1": '<img src="/sites/Demo/PublishingImages/gone.jpg" />',
            "2": '<img alt="" />',
        }
        plan = plan_field_image_remediation(items, inventory={}, ruleset=_ruleset())
        assert plan.change_count == 0
        assert plan.classifications["1"].status == "missing"
        assert plan.classifications["2"].status == "img_no_src"

    def test_outcome_observed_when_at_least_one_fix_is_proposed(self):
        items = {"1": '<img src="/sites/Demo/PublishingImages/photo.jpg" />'}
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/x/photo.jpg"}, ruleset=_ruleset()
        )
        assert plan.outcome == Outcome.OBSERVED

    def test_outcome_empty_when_no_fix_is_proposed(self):
        items = {"1": "plain text"}
        plan = plan_field_image_remediation(items, inventory={}, ruleset=_ruleset())
        assert plan.outcome == Outcome.EMPTY


class TestApplyFieldImageRemediation:
    def test_dry_run_by_default_performs_no_writes(self):
        items = {"1": '<img src="/sites/Demo/PublishingImages/photo.jpg" />'}
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/x/photo.jpg"}, ruleset=_ruleset()
        )
        result = apply_field_image_remediation(plan)
        assert result.dry_run is True
        assert result.applied == ()

    def test_real_apply_without_executor_raises(self):
        items = {"1": '<img src="/sites/Demo/PublishingImages/photo.jpg" />'}
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/x/photo.jpg"}, ruleset=_ruleset()
        )
        with pytest.raises(ExecutorRequired):
            apply_field_image_remediation(plan, dry_run=False, executor=None, confirm=plan.confirmation_token)

    def test_real_apply_with_wrong_token_raises(self):
        items = {"1": '<img src="/sites/Demo/PublishingImages/photo.jpg" />'}
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/x/photo.jpg"}, ruleset=_ruleset()
        )
        with pytest.raises(ConfirmationRequired):
            apply_field_image_remediation(
                plan, dry_run=False, executor=lambda source_id, value: None, confirm="WRONG"
            )

    def test_real_apply_writes_only_matched_items(self):
        items = {
            "1": '<img src="/sites/Demo/PublishingImages/photo.jpg" />',
            "2": '<img src="/sites/Demo/PublishingImages/gone.jpg" />',
        }
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/x/photo.jpg"}, ruleset=_ruleset()
        )
        written = []

        def executor(source_id, value):
            written.append(source_id)

        result = apply_field_image_remediation(
            plan, dry_run=False, executor=executor, confirm=plan.confirmation_token
        )
        assert result.outcome == Outcome.OBSERVED
        assert written == ["1"]


class TestGenerateGapReport:
    def test_report_states_counts_for_every_status(self):
        items = {
            "1": '<img src="/sites/Demo/PublishingImages/photo.jpg" />',  # matched
            "2": '<img src="/sites/Demo/PublishingImages/gone.jpg" />',  # missing
            "3": '<img alt="" />',  # img_no_src
            "4": "plain text",  # no_img_tag
        }
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/x/photo.jpg"}, ruleset=_ruleset()
        )
        report = generate_gap_report(plan)
        assert "Total items" in report
        assert "4" in report  # total count
        assert "matched" in report.lower()
        assert "missing" in report.lower()

    def test_report_names_every_missing_item_individually(self):
        """A gap report that only shows a count of missing items is not
        actionable -- the reviewer needs to know exactly which items still
        need attention, matching the source pattern's per-row CSV output."""
        items = {"42": '<img src="/sites/Demo/PublishingImages/gone.jpg" />'}
        plan = plan_field_image_remediation(items, inventory={}, ruleset=_ruleset())
        report = generate_gap_report(plan)
        assert "42" in report
        assert "gone.jpg" in report

    def test_report_names_every_proposed_fix_individually(self):
        items = {"7": '<img src="/sites/Demo/PublishingImages/photo.jpg" />'}
        plan = plan_field_image_remediation(
            items, inventory={"photo.jpg": "/x/photo.jpg"}, ruleset=_ruleset()
        )
        report = generate_gap_report(plan)
        assert "7" in report

    def test_report_on_empty_plan_states_nothing_to_do(self):
        plan = plan_field_image_remediation({}, inventory={}, ruleset=_ruleset())
        report = generate_gap_report(plan)
        assert "Total items" in report
        assert "0" in report
