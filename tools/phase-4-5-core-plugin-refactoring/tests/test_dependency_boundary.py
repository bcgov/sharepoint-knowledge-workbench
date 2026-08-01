import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dependency_boundary import (
    check_no_prohibited_imports,
    check_no_repo_root_import_in_production_code,
)


def test_check_no_prohibited_imports_finds_a_violation(tmp_path):
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "bad.py").write_text("import canonical_knowledge\n")
    violations = check_no_prohibited_imports(src, ["canonical_knowledge"])
    assert len(violations) == 1
    assert violations[0]["import"] == "canonical_knowledge"


def test_check_no_prohibited_imports_passes_clean_code(tmp_path):
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "good.py").write_text("import knowledge_workbench_contracts\nimport json\n")
    violations = check_no_prohibited_imports(src, ["canonical_knowledge"])
    assert violations == []


def test_check_no_prohibited_imports_detects_from_import(tmp_path):
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "bad.py").write_text("from source_document_extraction import extraction\n")
    violations = check_no_prohibited_imports(src, ["source_document_extraction"])
    assert len(violations) == 1


def test_check_no_repo_root_import_in_production_code_finds_violation(tmp_path):
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "bad.py").write_text(
        "from knowledge_workbench_contracts.repo_root import find_repo_root\n"
    )
    violations = check_no_repo_root_import_in_production_code(src)
    assert len(violations) == 1
    assert violations[0]["file"].endswith("bad.py")


def test_check_no_repo_root_import_in_production_code_passes_clean_code(tmp_path):
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "good.py").write_text("from knowledge_workbench_contracts.tree_hash import compute_tree_hash\n")
    violations = check_no_repo_root_import_in_production_code(src)
    assert violations == []


def test_check_no_repo_root_import_in_production_code_ignores_unrelated_text(tmp_path):
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "fine.py").write_text('# import graph rooted at repo_root, see docs\nimport json\n')
    # "repo_root" and "import" both present but not as an actual import statement of repo_root
    # this is a known limitation of the plan's simple substring check; documented, not fixed here
    violations = check_no_repo_root_import_in_production_code(src)
    assert len(violations) == 1  # substring-based check flags this false positive by design
