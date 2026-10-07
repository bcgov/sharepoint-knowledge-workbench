"""Purpose: Verify explicit destination mapping and link rewrite planning.

Key Input Dependencies:
- scripts/link-remediation/map_file_destinations.py
- scripts/link-remediation/generate_link_rewrite_plan.py
- Temporary CSV, workbook, and document fixtures created by pytest

Functions:
- _write_pipeline_file_inventory
- _write_pipeline_link_inventory
- test_destination_mapping_and_rewrite_pipeline
- write_mapping_workbook (including nested inline_row)
- test_explicit_container_parameters_map_full_library_and_guard_counts
- test_destination_mapper_refuses_to_overwrite_inventory
- test_mapping_workbook_is_optional_read_only_and_must_match_cli_parameters
- test_link_plan_preserves_fragments_and_distinguishes_out_of_map_targets
- test_link_plan_preserves_raw_query_and_fragment_when_resolution_omits_them
- test_link_planner_refuses_to_overwrite_either_input
- test_mapping_script_cli_runs_with_explicit_scope
"""
import csv
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from map_file_destinations import map_destinations
from generate_link_rewrite_plan import plan_rewrites


MAPPING_SCRIPT = Path(__file__).resolve().parents[2] / "scripts/link-remediation/map_file_destinations.py"


def _write_pipeline_file_inventory(files_csv: Path) -> None:
    """Write a minimal file inventory for the end-to-end mapping test."""
    fieldnames = [
        "SourceSiteUrl", "WebUrl", "LibraryTitle", "RelativePath", "LibraryRelativePath",
        "ServerRelativeUrl", "FileUrl", "FileName", "FileExtension",
    ]
    rows = [
        {
            "SourceSiteUrl": "https://source.onprem.test",
            "WebUrl": "https://source.onprem.test/CourtAdmin",
            "LibraryTitle": "Pages",
            "RelativePath": "CourtAdmin/Pages/guide.pdf",
            "LibraryRelativePath": "guide.pdf",
            "ServerRelativeUrl": "/CourtAdmin/Pages/guide.pdf",
            "FileUrl": "https://source.onprem.test/CourtAdmin/Pages/guide.pdf",
            "FileName": "guide.pdf",
            "FileExtension": "pdf",
        },
        {
            "SourceSiteUrl": "https://source.onprem.test",
            "WebUrl": "https://source.onprem.test/CourtAdmin",
            "LibraryTitle": "Pages",
            "RelativePath": "CourtAdmin/Pages/default.aspx",
            "LibraryRelativePath": "default.aspx",
            "ServerRelativeUrl": "/CourtAdmin/Pages/default.aspx",
            "FileUrl": "https://source.onprem.test/CourtAdmin/Pages/default.aspx",
            "FileName": "default.aspx",
            "FileExtension": "aspx",
        },
    ]
    with files_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_pipeline_link_inventory(links_csv: Path) -> None:
    """Write internal and external link rows for the end-to-end rewrite test."""
    fieldnames = [
        "SourceUrl", "WebUrl", "LibraryTitle", "RelativePath", "ServerRelativeUrl",
        "LocalPath", "SourcePart", "RawUrl", "ResolvedUrl", "LinkKind", "OccurrenceCount",
    ]
    page_url = "https://source.onprem.test/CourtAdmin/Pages/default.aspx"
    source_path = "/CourtAdmin/Pages/default.aspx"
    rows = [
        {
            "SourceUrl": page_url,
            "ServerRelativeUrl": source_path,
            "SourcePart": "markup",
            "RawUrl": "/Administration Documents/Policies/guide.pdf",
            "ResolvedUrl": "https://source.onprem.test/CourtAdmin/Pages/guide.pdf",
            "LinkKind": "hyperlink",
            "OccurrenceCount": "1",
        },
        {
            "SourceUrl": page_url,
            "ServerRelativeUrl": source_path,
            "SourcePart": "markup",
            "RawUrl": "https://www.google.com",
            "ResolvedUrl": "https://www.google.com",
            "LinkKind": "hyperlink",
            "OccurrenceCount": "1",
        },
    ]
    with links_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_destination_mapping_and_rewrite_pipeline(tmp_path: Path) -> None:
    """Map a full source library, then plan link rewrites using that map."""
    files_csv = tmp_path / "files.csv"
    map_csv = tmp_path / "file-migration-map.csv"
    links_csv = tmp_path / "links.csv"
    plan_csv = tmp_path / "link-rewrite-plan.csv"
    _write_pipeline_file_inventory(files_csv)

    summary_map = map_destinations(
        files_csv=files_csv,
        output_csv=map_csv,
        source_web_url="https://source.onprem.test/CourtAdmin",
        source_library_title="Pages",
        source_server_relative_prefix="/CourtAdmin/Pages/",
        target_site_url="https://tenant.sharepoint.com/sites/Target",
        target_library_title="Site Pages",
        target_library_root_url="/sites/Target/Site Pages",
        target_folder_prefix="CourtAdmin",
        aspx_to_html=True,
    )
    assert summary_map["Status"] == "COMPLETED"
    assert summary_map["MappedFiles"] == 2
    assert summary_map["AspxRenamed"] == 1

    with map_csv.open(encoding="utf-8-sig") as handle:
        map_rows = list(csv.DictReader(handle))
    page_map = next(row for row in map_rows if row["SourceFileUrl"].endswith("default.aspx"))
    assert page_map["TargetFileName"] == "default.html"
    assert page_map["TargetServerRelativeUrl"] == (
        "/sites/Target/Site%20Pages/CourtAdmin/default.html"
    )

    _write_pipeline_link_inventory(links_csv)
    summary_plan = plan_rewrites(
        links_csv=links_csv,
        migration_map_csv=map_csv,
        output_csv=plan_csv,
    )
    assert summary_plan["Status"] == "COMPLETED"
    assert summary_plan["ResolvedInternal"] == 1
    assert summary_plan["External"] == 1

    with plan_csv.open(encoding="utf-8-sig") as handle:
        plan_rows = list(csv.DictReader(handle))
    internal_plan = next(row for row in plan_rows if row["TargetStatus"] == "RESOLVED_INTERNAL")
    assert internal_plan["TargetSPOServerRelativeUrl"] == (
        "/sites/Target/Site%20Pages/CourtAdmin/guide.pdf"
    )


def write_mapping_workbook(path: Path, target_folder: str = "administrative documents") -> None:
    """Create a minimal XLSX fixture with the documented mapping sheet."""
    headers = [
        "SourceWebUrl",
        "SourceLibraryTitle",
        "SourceServerRelativePrefix",
        "TargetSiteUrl",
        "TargetLibraryTitle",
        "TargetLibraryRootUrl",
        "TargetFolderPrefix",
        "RenameAspxToHtml",
    ]
    values = [
        "https://source.example/DivisionA",
        "Administration Documents",
        "/DivisionA/Administration Documents/",
        "https://tenant.sharepoint.com/sites/Target-DEV",
        "divisiona",
        "/sites/Target-DEV/divisiona",
        target_folder,
        "true",
    ]

    def inline_row(number: int, cells: list[str]) -> str:
        """Render one worksheet row using inline string cells."""
        rendered = []
        for index, value in enumerate(cells, 1):
            column = chr(ord("A") + index - 1)
            rendered.append(
                f'<c r="{column}{number}" t="inlineStr"><is><t>{value}</t></is></c>'
            )
        return f'<row r="{number}">{"".join(rendered)}</row>'

    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{inline_row(1, headers)}{inline_row(2, values)}</sheetData>'
        '</worksheet>'
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Destination Mapping" sheetId="1" r:id="rId1"/></sheets>'
        '</workbook>'
    )
    relationships = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", relationships)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)


def test_explicit_container_parameters_map_full_library_and_guard_counts(tmp_path: Path) -> None:
    """Map only the selected library and enforce the requested inventory counts."""
    files_csv = tmp_path / "files.csv"
    with files_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "SourceSiteUrl", "WebUrl", "LibraryTitle", "RelativePath", "LibraryRelativePath",
            "ServerRelativeUrl", "FileUrl", "FileName", "FileExtension",
        ])
        writer.writeheader()
        writer.writerows([
            {
                "SourceSiteUrl": "https://source.example",
                "WebUrl": "https://source.example/DivisionA",
                "LibraryTitle": "Administration Documents",
                "RelativePath": "DivisionA/Administration Documents/messages/notice.aspx",
                "LibraryRelativePath": "messages/notice.aspx",
                "ServerRelativeUrl": "/DivisionA/Administration Documents/messages/notice.aspx",
                "FileUrl": "https://source.example/DivisionA/Administration%20Documents/messages/notice.aspx",
                "FileName": "notice.aspx",
                "FileExtension": ".aspx",
            },
            {
                "SourceSiteUrl": "https://source.example",
                "WebUrl": "https://source.example/DivisionA",
                "LibraryTitle": "Administration Documents",
                "RelativePath": "DivisionA/Administration Documents/guide.pdf",
                "LibraryRelativePath": "guide.pdf",
                "ServerRelativeUrl": "/DivisionA/Administration Documents/guide.pdf",
                "FileUrl": "https://source.example/DivisionA/Administration%20Documents/guide.pdf",
                "FileName": "guide.pdf",
                "FileExtension": ".pdf",
            },
            {
                "SourceSiteUrl": "https://source.example",
                "WebUrl": "https://source.example/DivisionA",
                "LibraryTitle": "Documents",
                "RelativePath": "DivisionA/Documents/other.pdf",
                "LibraryRelativePath": "other.pdf",
                "ServerRelativeUrl": "/DivisionA/Documents/other.pdf",
                "FileUrl": "https://source.example/DivisionA/Documents/other.pdf",
                "FileName": "other.pdf",
                "FileExtension": ".pdf",
            },
        ])

    output_csv = tmp_path / "map.csv"
    summary = map_destinations(
        files_csv=files_csv,
        output_csv=output_csv,
        source_web_url="https://source.example/DivisionA",
        source_library_title="Administration Documents",
        source_server_relative_prefix="/DivisionA/Administration Documents/",
        target_site_url="https://tenant.sharepoint.com/sites/Target-DEV",
        target_library_title="divisiona",
        target_library_root_url="/sites/Target-DEV/divisiona",
        target_folder_prefix="administrative documents",
        aspx_to_html=True,
        expected_source_files=2,
        expected_aspx_count=1,
    )

    assert summary["Status"] == "COMPLETED"
    assert summary["MappedFiles"] == 2
    assert summary["AspxRenamed"] == 1
    with output_csv.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    page = next(row for row in rows if row["SourceFileUrl"].endswith("notice.aspx"))
    assert page["TargetFileName"] == "notice.html"
    assert page["TargetServerRelativeUrl"] == (
        "/sites/Target-DEV/divisiona/administrative%20documents/messages/notice.html"
    )


def test_destination_mapper_refuses_to_overwrite_inventory(tmp_path: Path) -> None:
    """Preserve the source inventory when the output path aliases it."""
    files_csv = tmp_path / "files.csv"
    with files_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["WebUrl", "LibraryTitle", "ServerRelativeUrl"])
        writer.writeheader()
        writer.writerow({
            "WebUrl": "https://source.example/DepartmentA",
            "LibraryTitle": "Policies",
            "ServerRelativeUrl": "/DepartmentA/Policies/guide.pdf",
        })
    original = files_csv.read_bytes()

    with pytest.raises(ValueError, match="output path must differ from every input"):
        map_destinations(
            files_csv=files_csv,
            output_csv=files_csv,
            source_web_url="https://source.example/DepartmentA",
            source_library_title="Policies",
            target_site_url="https://tenant.example/sites/Target",
            target_library_title="Records",
            target_library_root_url="/sites/Target/Records",
        )

    assert files_csv.read_bytes() == original


def test_mapping_workbook_is_optional_read_only_and_must_match_cli_parameters(
    tmp_path: Path,
) -> None:
    """Accept an optional matching workbook and reject a mismatched mapping."""
    files_csv = tmp_path / "files.csv"
    with files_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "WebUrl", "LibraryTitle", "LibraryRelativePath", "ServerRelativeUrl",
            "FileUrl", "FileName",
        ])
        writer.writeheader()
        writer.writerow({
            "WebUrl": "https://source.example/DivisionA",
            "LibraryTitle": "Administration Documents",
            "LibraryRelativePath": "notice.aspx",
            "ServerRelativeUrl": "/DivisionA/Administration Documents/notice.aspx",
            "FileUrl": "https://source.example/DivisionA/Administration%20Documents/notice.aspx",
            "FileName": "notice.aspx",
        })

    workbook = tmp_path / "mapping.xlsx"
    write_mapping_workbook(workbook)
    output_csv = tmp_path / "map.csv"
    summary = map_destinations(
        files_csv=files_csv,
        output_csv=output_csv,
        source_web_url="https://source.example/DivisionA",
        source_library_title="Administration Documents",
        source_server_relative_prefix="/DivisionA/Administration Documents/",
        target_site_url="https://tenant.sharepoint.com/sites/Target-DEV",
        target_library_title="divisiona",
        target_library_root_url="/sites/Target-DEV/divisiona",
        target_folder_prefix="administrative documents",
        aspx_to_html=True,
        mapping_workbook=workbook,
    )
    assert summary["WorkbookValidation"] == "MATCHED"

    write_mapping_workbook(workbook, target_folder="wrong folder")
    try:
        map_destinations(
            files_csv=files_csv,
            output_csv=tmp_path / "mismatch.csv",
            source_web_url="https://source.example/DivisionA",
            source_library_title="Administration Documents",
            source_server_relative_prefix="/DivisionA/Administration Documents/",
            target_site_url="https://tenant.sharepoint.com/sites/Target-DEV",
            target_library_title="divisiona",
            target_library_root_url="/sites/Target-DEV/divisiona",
            target_folder_prefix="administrative documents",
            aspx_to_html=True,
            mapping_workbook=workbook,
        )
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("a mismatched workbook mapping must fail closed")
    assert not (tmp_path / "mismatch.csv").exists()


def test_link_plan_preserves_fragments_and_distinguishes_out_of_map_targets(
    tmp_path: Path,
) -> None:
    """Retain URL fragments and classify internal targets missing from the map."""
    migration_map = tmp_path / "map.csv"
    with migration_map.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "SourceServerRelativeUrl", "SourceFileUrl", "TargetServerRelativeUrl", "TargetFileUrl",
        ])
        writer.writeheader()
        writer.writerow({
            "SourceServerRelativeUrl": "/DivisionA/Administration Documents/guide.pdf",
            "SourceFileUrl": "https://source.example/DivisionA/Administration%20Documents/guide.pdf",
            "TargetServerRelativeUrl": "/sites/Target-DEV/divisiona/administrative%20documents/guide.pdf",
            "TargetFileUrl": "https://tenant.sharepoint.com/sites/Target-DEV/divisiona/administrative%20documents/guide.pdf",
        })

    links_csv = tmp_path / "links.csv"
    with links_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "SourceUrl", "ServerRelativeUrl", "SourcePart", "RawUrl", "ResolvedUrl", "LinkKind",
        ])
        writer.writeheader()
        writer.writerows([
            {
                "SourceUrl": "https://source.example/DivisionA/Administration%20Documents/page.aspx",
                "ServerRelativeUrl": "/DivisionA/Administration Documents/page.aspx",
                "SourcePart": "markup",
                "RawUrl": "https://source.example/DivisionA/Administration%20Documents/guide.pdf?download=1#page=2",
                "ResolvedUrl": "https://source.example/DivisionA/Administration%20Documents/guide.pdf?download=1#page=2",
                "LinkKind": "hyperlink",
            },
            {
                "SourceUrl": "https://source.example/DivisionA/Administration%20Documents/page.aspx",
                "ServerRelativeUrl": "/DivisionA/Administration Documents/page.aspx",
                "SourcePart": "markup",
                "RawUrl": "/DivisionA/Documents/unmapped.pdf",
                "ResolvedUrl": "https://source.example/DivisionA/Documents/unmapped.pdf",
                "LinkKind": "hyperlink",
            },
            {
                "SourceUrl": "https://source.example/DivisionA/Administration%20Documents/page.aspx",
                "ServerRelativeUrl": "/DivisionA/Administration Documents/page.aspx",
                "SourcePart": "markup",
                "RawUrl": "https://example.org/external",
                "ResolvedUrl": "https://example.org/external",
                "LinkKind": "hyperlink",
            },
        ])

    output_csv = tmp_path / "plan.csv"
    summary = plan_rewrites(links_csv, migration_map, output_csv)
    with output_csv.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert summary["ResolvedInternal"] == 1
    assert summary["External"] == 1
    assert summary["UnmappedNotInMap"] == 1
    assert rows[0]["TargetSPOUrl"].endswith("guide.pdf?download=1#page=2")
    assert rows[1]["TargetStatus"] == "UNMAPPED_NOT_IN_MAP"


def test_link_plan_preserves_raw_query_and_fragment_when_resolution_omits_them(
    tmp_path: Path,
) -> None:
    """Carry query and fragment data from the raw link to the target URL."""
    migration_map = tmp_path / "map.csv"
    with migration_map.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "SourceServerRelativeUrl", "SourceFileUrl", "TargetServerRelativeUrl", "TargetFileUrl",
        ])
        writer.writeheader()
        writer.writerow({
            "SourceServerRelativeUrl": "/DepartmentA/Policies/guide.pdf",
            "SourceFileUrl": "https://source.example/DepartmentA/Policies/guide.pdf",
            "TargetServerRelativeUrl": "/sites/Target/Records/guide.pdf",
            "TargetFileUrl": "https://tenant.example/sites/Target/Records/guide.pdf",
        })

    links_csv = tmp_path / "links.csv"
    with links_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["RawUrl", "ResolvedUrl"])
        writer.writeheader()
        writer.writerow({
            "RawUrl": "/DepartmentA/Policies/guide.pdf?download=1#page=2",
            "ResolvedUrl": "https://source.example/DepartmentA/Policies/guide.pdf",
        })

    output_csv = tmp_path / "plan.csv"
    plan_rewrites(links_csv, migration_map, output_csv)
    with output_csv.open(encoding="utf-8-sig", newline="") as handle:
        row = next(csv.DictReader(handle))

    assert row["TargetSPOUrl"] == (
        "https://tenant.example/sites/Target/Records/guide.pdf?download=1#page=2"
    )


@pytest.mark.parametrize("output_input", ["links", "map"])
def test_link_planner_refuses_to_overwrite_either_input(
    tmp_path: Path,
    output_input: str,
) -> None:
    """Preserve either planner input when it is selected as the output path."""
    links_csv = tmp_path / "links.csv"
    links_csv.write_text(
        "RawUrl,ResolvedUrl\n/guide.pdf,https://source.example/guide.pdf\n",
        encoding="utf-8",
    )
    migration_map = tmp_path / "map.csv"
    migration_map.write_text(
        "SourceServerRelativeUrl,SourceFileUrl,TargetServerRelativeUrl,TargetFileUrl\n"
        "/guide.pdf,https://source.example/guide.pdf,/sites/Target/Records/guide.pdf,"
        "https://tenant.example/sites/Target/Records/guide.pdf\n",
        encoding="utf-8",
    )
    protected_path = links_csv if output_input == "links" else migration_map
    original = protected_path.read_bytes()

    with pytest.raises(ValueError, match="output path must differ from every input"):
        plan_rewrites(links_csv, migration_map, protected_path)

    assert protected_path.read_bytes() == original


def test_mapping_script_cli_runs_with_explicit_scope(tmp_path: Path) -> None:
    """Run the mapper as a subprocess with explicit source and target scope."""
    files_csv = tmp_path / "files.csv"
    with files_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "SourceSiteUrl", "WebUrl", "LibraryTitle", "ServerRelativeUrl",
            "FileUrl", "FileName", "FileExtension",
        ])
        writer.writeheader()
        writer.writerow({
            "SourceSiteUrl": "https://source.example",
            "WebUrl": "https://source.example/DivisionA",
            "LibraryTitle": "Administration Documents",
            "ServerRelativeUrl": "/DivisionA/Administration Documents/page.aspx",
            "FileUrl": "https://source.example/DivisionA/Administration%20Documents/page.aspx",
            "FileName": "page.aspx",
            "FileExtension": ".aspx",
        })
    output_csv = tmp_path / "map.csv"
    result = subprocess.run(
        [
            sys.executable,
            str(MAPPING_SCRIPT),
            "--files-csv", str(files_csv),
            "--source-web-url", "https://source.example/DivisionA",
            "--source-library-title", "Administration Documents",
            "--source-server-relative-prefix", "/DivisionA/Administration Documents/",
            "--target-site-url", "https://tenant.sharepoint.com/sites/Target-DEV",
            "--target-library-title", "divisiona",
            "--target-library-root-url", "/sites/Target-DEV/divisiona",
            "--target-folder-prefix", "administrative documents",
            "--aspx-to-html",
            "--expected-source-files", "1",
            "--expected-aspx-count", "1",
            "--output-csv", str(output_csv),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert '"MappedFiles": 1' in result.stdout
    with output_csv.open(encoding="utf-8-sig", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["TargetFileName"] == "page.html"
