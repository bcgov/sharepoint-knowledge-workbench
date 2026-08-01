"""
Wave 1 Step 6 (plan text): "Using the approved original_skill_dispositions,
fill wave-0-test-ledger.json's proposed_owner_domain for every test."

File-level domain assignment for every test file in plugins/docx-to-content/tests/,
grounded in wave-1-decisions.json's approved script/skill dispositions and the plan's
Known File Inventory table. Two files (test_analyze_structure.py, whose production
counterpart was explicitly split by human decision) get function-level overrides
instead of one file-wide domain, because their tests genuinely belong to two
different target plugins post-split. test_convert.py's production counterpart also
split, but none of its 6 actual tests individually exercise the
source-document-extraction-bound run_pandoc_extraction function, so file-level
CANONICAL_KNOWLEDGE is accurate for all of them (recorded explicitly below, not
assumed).
"""
from __future__ import annotations

DOMAINS = {
    "SOURCE_DOCUMENT_EXTRACTION",
    "KNOWLEDGE_ANALYSIS",
    "CANONICAL_KNOWLEDGE",
    "KNOWLEDGE_PUBLICATION",
    "NEUTRAL_CONTRACT_DISTRIBUTION",
    "NEUTRAL_RUNTIME_DISTRIBUTION",
    "REPOSITORY_ORCHESTRATION",
    "OUT_OF_PHASE_4_5_SCOPE",
    "CROSS_CUTTING_MULTIPLE_DOMAINS",
}

# File-level default. Files whose production code was split (analyze_structure.py)
# get per-test overrides below instead of relying on this default.
FILE_OWNER_DOMAIN: dict[str, "str | None"] = {
    # tests/unit/
    "tests/unit/test_analyze_structure.py": None,  # per-test override, see ANALYZE_STRUCTURE_TEST_OVERRIDES
    "tests/unit/test_atomic_output.py": "NEUTRAL_RUNTIME_DISTRIBUTION",
    "tests/unit/test_attrs.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_canonical_package_mutations.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_chunking.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_cli.py": "REPOSITORY_ORCHESTRATION",
    "tests/unit/test_convert.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_dependencies.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_dispositions.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_emf_convert.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_footnotes.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_heading_emphasis.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_identity.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_images.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_import_boundaries.py": "KNOWLEDGE_PUBLICATION",
    "tests/unit/test_independent_fixture.py": "KNOWLEDGE_PUBLICATION",
    "tests/unit/test_media_disposition.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_multipage_markdown.py": "KNOWLEDGE_PUBLICATION",
    "tests/unit/test_package.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_package_load.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_pandoc_validate.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_plans.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_publication_map.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_regression_pipeline.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_renderer_protocol.py": "KNOWLEDGE_PUBLICATION",
    "tests/unit/test_runtime_independence.py": "KNOWLEDGE_PUBLICATION",
    "tests/unit/test_sharepoint_cli.py": "OUT_OF_PHASE_4_5_SCOPE",
    "tests/unit/test_sharepoint_dry_run.py": "OUT_OF_PHASE_4_5_SCOPE",
    "tests/unit/test_sharepoint_package.py": "OUT_OF_PHASE_4_5_SCOPE",
    "tests/unit/test_sharepoint_reconcile.py": "OUT_OF_PHASE_4_5_SCOPE",
    "tests/unit/test_tables.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_toc.py": "SOURCE_DOCUMENT_EXTRACTION",
    "tests/unit/test_topic_grouping.py": "KNOWLEDGE_ANALYSIS",
    "tests/unit/test_validate_canonical.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_validate_canonical_mutations.py": "CANONICAL_KNOWLEDGE",
    "tests/unit/test_validate_rendered.py": "KNOWLEDGE_PUBLICATION",
    "tests/unit/test_validate_rendered_mutations.py": "KNOWLEDGE_PUBLICATION",
    # tests/contract/
    "tests/contract/test_content_authoring_guidance.py": "CANONICAL_KNOWLEDGE",
    "tests/contract/test_contracts.py": "NEUTRAL_CONTRACT_DISTRIBUTION",
    "tests/contract/test_future_output_profiles.py": "CROSS_CUTTING_MULTIPLE_DOMAINS",
    "tests/contract/test_skill_contracts.py": "REPOSITORY_ORCHESTRATION",
    # tests/integration/
    "tests/integration/test_atomic_promotion.py": "CROSS_CUTTING_MULTIPLE_DOMAINS",
    "tests/integration/test_generalization_e2e.py": "CROSS_CUTTING_MULTIPLE_DOMAINS",
    "tests/integration/test_golden_master.py": "CROSS_CUTTING_MULTIPLE_DOMAINS",
    "tests/integration/test_plugin_structure.py": "REPOSITORY_ORCHESTRATION",
}

# Per-test overrides for tests/unit/test_analyze_structure.py — its production
# counterpart (analyze_structure.py) was split by explicit human decision
# (wave-1-analyze-structure-split-decision.md); tests exercising strategy
# recommendation / analysis-plan construction go to KNOWLEDGE_ANALYSIS, every other
# test (raw extraction, heading parsing, statistics, defect detection) goes to
# SOURCE_DOCUMENT_EXTRACTION, matching the approved split exactly.
_KNOWLEDGE_ANALYSIS_TEST_NAMES = {
    "test_analyze_report_includes_proposed_topics_preview",
    "test_analyze_report_proposed_topics_absent_for_no_headings_is_empty_list",
    "test_small_single_recommends_single_strategy",
    "test_repeated_headings_recommends_chunked_strategy",
    "test_recommendation_constants_are_named_and_configurable",
    "test_draft_plan_has_source_fingerprint_and_draft_status",
    "test_draft_plan_chunk_anchors_are_structural_not_line_offsets",
    "test_draft_plan_anchor_occurrence_disambiguates_repeated_paths",
    "test_analyze_writes_analysis_package_layout",
}
_CROSS_CUTTING_TEST_NAMES = {
    "test_no_ceis_literal_in_analyze_structure_source",  # source-hygiene test spanning the whole (post-split) file
}

# Per-test override for tests/unit/test_atomic_output.py — its production counterpart also splits
# (create_staging_dir/promote -> knowledge_workbench_runtime; build_generator_info/
# write_generator_info -> explicitly NOT part of that distribution, duplicated per consuming
# domain instead, per wave-1-shared-contract-decision.md and spec §13c). These two tests exercise
# only the excluded generator-info functions, so they do not belong under
# NEUTRAL_RUNTIME_DISTRIBUTION with the rest of the file (found during independent Wave 1 review —
# the file-level default had missed this split, unlike its sibling test_analyze_structure.py).
_ATOMIC_OUTPUT_CROSS_CUTTING_TEST_NAMES = {
    "test_build_generator_info_reuses_dependencies_probes",
    "test_write_generator_info_is_deterministic_json_utf8",
}


def owner_domain_for(test_file: str, test_name: str) -> str:
    if test_file == "tests/unit/test_analyze_structure.py":
        if test_name in _KNOWLEDGE_ANALYSIS_TEST_NAMES:
            return "KNOWLEDGE_ANALYSIS"
        if test_name in _CROSS_CUTTING_TEST_NAMES:
            return "CROSS_CUTTING_MULTIPLE_DOMAINS"
        return "SOURCE_DOCUMENT_EXTRACTION"

    if test_file == "tests/unit/test_atomic_output.py" and test_name in _ATOMIC_OUTPUT_CROSS_CUTTING_TEST_NAMES:
        return "CROSS_CUTTING_MULTIPLE_DOMAINS"

    domain = FILE_OWNER_DOMAIN.get(test_file)
    if domain is None:
        raise KeyError(f"no owner-domain mapping for test file: {test_file!r}")
    return domain


def fill_ledger(ledger: dict) -> dict:
    """Returns a new ledger dict with proposed_owner_domain filled for every entry."""
    filled_entries = []
    for entry in ledger["entries"]:
        test_name = entry["test_name"].split("::")[-1]  # strip ClassName:: prefix if present
        domain = owner_domain_for(entry["file"], test_name)
        filled_entries.append({**entry, "proposed_owner_domain": domain})
    return {**ledger, "entries": filled_entries}
