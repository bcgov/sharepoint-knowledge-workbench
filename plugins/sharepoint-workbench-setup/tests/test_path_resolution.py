"""
test_path_resolution.py
=========================

Tests for `path_resolution.py` -- the `resolve-document-paths` skill's
logic. Per `.agent/rules/test-driven-development.md`'s "Critical
Runtime Paths -- No Mocking Allowed", path resolution and file-existence
checks are exercised against a REAL filesystem (pytest's `tmp_path`),
never mocked.
"""

from pathlib import Path

import pytest

from path_resolution import (
    DOWNSTREAM_INVOCATIONS,
    ResolvedInvocation,
    format_invocations,
    resolve_workbench_paths,
)


CONNECTION = {
    "SiteUrl": "https://example.invalid/sites/example",
    "TenantId": "00000000-0000-0000-0000-000000000000",
    "ClientId": "11111111-1111-1111-1111-111111111111",
    "AuthenticationMode": "DeviceCode",
}

WORKFLOW_PROFILE = {
    "SchemaVersion": "1.0",
    "Document": {
        "DocumentId": "example-doc",
        "SourcePath": "intake/example.docx",
        "SourceFormat": "docx",
        "IsRevision": False,
    },
    "RequestedStages": [],
    "RequestedRendererProfiles": [],
    "UnsupportedRequests": [],
    "HumanConfirmationGates": {},
    "PublicationProfilePath": "publication-profiles/example-doc.publication.psd1",
    "AgentActionsRequested": [],
    "OutstandingDecisions": [],
}

PUBLICATION_PROFILE = {
    "SchemaVersion": "1.0",
    "Document": {
        "DocumentId": "example-doc",
        "Title": "Example",
        "ContentType": "Manual",
        "ContentOwner": "Owner",
        "SourcePackagePath": "runs/example-doc/canonical",
        "PackageIdentity": "example-doc-v1",
    },
    "HumanPublication": {"Enabled": False},
    "PagePublication": {"Enabled": False},
    "AgentGrounding": {"Enabled": False},
    "Agents": [],
    "NativeSkills": [],
    "Evidence": {"OutputPath": ""},
}


def _make_export_tree(root, document_id, subdirs_and_files):
    """Create `<root>/sharepoint-exports/<document_id>/<subdir>/<file>`
    for each `(subdir, filename)` pair, real files on the real
    filesystem."""
    export_root = root / "sharepoint-exports" / document_id
    for subdir, filename in subdirs_and_files:
        d = export_root / subdir
        d.mkdir(parents=True, exist_ok=True)
        (d / filename).write_text("{}")
    return export_root


class TestRegistryIsPureData:
    def test_registry_names_the_two_downstream_plugins(self):
        plugins = {entry.plugin for entry in DOWNSTREAM_INVOCATIONS}
        assert plugins == {"sharepoint-site-assessment", "sharepoint-site-migration"}

    def test_every_route_names_a_real_current_skill_in_its_owning_plugin(self):
        # Identity check against the repository checkout. Skipped when this plugin is
        # tested outside the monorepo (it must stay installable on its own).
        plugins_dir = Path(__file__).resolve().parents[2]
        if not (plugins_dir / "sharepoint-site-assessment").is_dir():
            pytest.skip("sibling plugins are not present in this checkout")
        missing = [
            f"{entry.plugin}/{entry.skill}"
            for entry in DOWNSTREAM_INVOCATIONS
            if not (plugins_dir / entry.plugin / "skills" / entry.skill / "SKILL.md").is_file()
        ]
        assert not missing, f"routes naming skills that do not exist: {missing}"

    def test_registry_entries_are_plain_data_no_callables(self):
        for entry in DOWNSTREAM_INVOCATIONS:
            for path_entry in entry.required_paths:
                assert isinstance(path_entry, dict)
                assert not callable(path_entry.get("filename"))


class TestResolveWorkbenchPaths:
    def test_all_present_yields_available_for_every_entry_and_pass_overall(self, tmp_path):
        for entry in DOWNSTREAM_INVOCATIONS:
            _make_export_tree(
                tmp_path,
                "example-doc",
                [(entry.export_subdir, p["filename"]) for p in entry.required_paths],
            )

        result = resolve_workbench_paths(
            document_id="example-doc",
            connection=CONNECTION,
            workflow_profile=WORKFLOW_PROFILE,
            publication_profile=PUBLICATION_PROFILE,
            workbench_root=tmp_path,
        )

        assert result.overall_status == "PASS"
        assert len(result.invocations) == len(DOWNSTREAM_INVOCATIONS)
        for invocation in result.invocations:
            assert invocation.status == "AVAILABLE"
            assert invocation.missing == []

    def test_no_exports_on_disk_yields_empty_overall(self, tmp_path):
        result = resolve_workbench_paths(
            document_id="example-doc",
            connection=CONNECTION,
            workflow_profile=WORKFLOW_PROFILE,
            publication_profile=PUBLICATION_PROFILE,
            workbench_root=tmp_path,
        )

        assert result.overall_status == "EMPTY"
        for invocation in result.invocations:
            assert invocation.status == "UNAVAILABLE"
            assert invocation.missing

    def test_some_present_some_missing_yields_partial_overall(self, tmp_path):
        first_entry = DOWNSTREAM_INVOCATIONS[0]
        _make_export_tree(
            tmp_path,
            "example-doc",
            [(first_entry.export_subdir, p["filename"]) for p in first_entry.required_paths],
        )

        result = resolve_workbench_paths(
            document_id="example-doc",
            connection=CONNECTION,
            workflow_profile=WORKFLOW_PROFILE,
            publication_profile=PUBLICATION_PROFILE,
            workbench_root=tmp_path,
        )

        assert result.overall_status == "PARTIAL"
        statuses = {inv.skill: inv.status for inv in result.invocations}
        assert statuses[first_entry.skill] == "AVAILABLE"
        assert any(status == "UNAVAILABLE" for status in statuses.values())

    def test_partial_within_one_invocation_names_the_missing_file(self, tmp_path):
        first_entry = DOWNSTREAM_INVOCATIONS[0]
        if len(first_entry.required_paths) < 2:
            pytest.skip("first registry entry has fewer than 2 required paths")
        present = first_entry.required_paths[:-1]
        missing = first_entry.required_paths[-1]
        _make_export_tree(
            tmp_path,
            "example-doc",
            [(first_entry.export_subdir, p["filename"]) for p in present],
        )

        result = resolve_workbench_paths(
            document_id="example-doc",
            connection=CONNECTION,
            workflow_profile=WORKFLOW_PROFILE,
            publication_profile=PUBLICATION_PROFILE,
            workbench_root=tmp_path,
        )

        first_invocation = next(inv for inv in result.invocations if inv.skill == first_entry.skill)
        assert first_invocation.status == "PARTIAL"
        assert missing["filename"] in first_invocation.missing

    def test_never_fabricates_a_path_for_a_missing_file(self, tmp_path):
        result = resolve_workbench_paths(
            document_id="example-doc",
            connection=CONNECTION,
            workflow_profile=WORKFLOW_PROFILE,
            publication_profile=PUBLICATION_PROFILE,
            workbench_root=tmp_path,
        )
        for invocation in result.invocations:
            for arg_name in invocation.missing_args():
                assert arg_name not in invocation.args

    def test_document_id_mismatch_between_workflow_profile_and_call_raises(self, tmp_path):
        with pytest.raises(ValueError):
            resolve_workbench_paths(
                document_id="other-doc",
                connection=CONNECTION,
                workflow_profile=WORKFLOW_PROFILE,
                publication_profile=PUBLICATION_PROFILE,
                workbench_root=tmp_path,
            )


class TestFormatInvocations:
    def test_format_never_contains_a_path_it_reported_unavailable(self, tmp_path):
        result = resolve_workbench_paths(
            document_id="example-doc",
            connection=CONNECTION,
            workflow_profile=WORKFLOW_PROFILE,
            publication_profile=PUBLICATION_PROFILE,
            workbench_root=tmp_path,
        )
        text = format_invocations(result)
        assert "UNAVAILABLE" in text
        for invocation in result.invocations:
            for missing_filename in invocation.missing:
                for resolved_val in invocation.args.values():
                    assert missing_filename not in str(resolved_val)

    def test_format_lists_plugin_and_skill_for_every_invocation(self, tmp_path):
        result = resolve_workbench_paths(
            document_id="example-doc",
            connection=CONNECTION,
            workflow_profile=WORKFLOW_PROFILE,
            publication_profile=PUBLICATION_PROFILE,
            workbench_root=tmp_path,
        )
        text = format_invocations(result)
        for invocation in result.invocations:
            assert invocation.plugin in text
            assert invocation.skill in text

    def test_format_does_not_execute_anything(self, tmp_path):
        # Purely a documentation-level assertion: format_invocations must
        # return a string, never run a subprocess or import a downstream
        # plugin module.
        result = resolve_workbench_paths(
            document_id="example-doc",
            connection=CONNECTION,
            workflow_profile=WORKFLOW_PROFILE,
            publication_profile=PUBLICATION_PROFILE,
            workbench_root=tmp_path,
        )
        assert isinstance(format_invocations(result), str)


class TestModuleNeverImportsDownstreamPlugins:
    def test_module_source_has_no_downstream_plugin_imports(self):
        import path_resolution

        source = open(path_resolution.__file__).read()
        for plugin_name in (
            "sharepoint_discovery",
            "sharepoint_schema",
            "sharepoint_link_remediation",
            "sharepoint_page_modernization",
        ):
            assert f"import {plugin_name}" not in source
            assert f"from {plugin_name}" not in source
        assert "import subprocess" not in source
