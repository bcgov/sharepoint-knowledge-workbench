import os
import json
import subprocess
from pathlib import Path
import pytest
import jsonschema

def get_repo_root() -> Path:
    # Path inside .worktrees/phase-4-native-sharepoint-skills/tools/phase-4-native-sharepoint-skills/tests/test_phase4_structure.py
    return Path(__file__).resolve().parents[3]

def test_phase4_directories_and_readmes_exist():
    repo_root = get_repo_root()
    tools_dir = repo_root / "tools" / "phase-4-native-sharepoint-skills"
    reports_dir = repo_root / "docs" / "reports" / "phase-4-native-sharepoint-skills"
    
    required_dirs = [
        tools_dir,
        tools_dir / "skills" / "review-manual-topics",
        tools_dir / "deployment",
        tools_dir / "evaluations",
        tools_dir / "fixtures" / "sanitized",
        tools_dir / "schemas",
        reports_dir,
    ]
    
    for d in required_dirs:
        assert d.exists() and d.is_dir(), f"Directory must exist: {d}"

    required_readmes = [
        tools_dir / "README.md",
        tools_dir / "skills" / "review-manual-topics" / "README.md",
        tools_dir / "deployment" / "README.md",
        tools_dir / "evaluations" / "README.md",
        tools_dir / "fixtures" / "sanitized" / "README.md",
        tools_dir / "schemas" / "README.md",
        reports_dir / "README.md",
    ]

    for readme in required_readmes:
        assert readme.exists() and readme.is_file(), f"README must exist: {readme}"
        assert readme.stat().st_size > 0, f"README must not be empty: {readme}"

def test_config_example_exists_and_gitignored():
    repo_root = get_repo_root()
    tools_dir = repo_root / "tools" / "phase-4-native-sharepoint-skills"
    config_example = tools_dir / "config.psd1.example"
    
    assert config_example.exists(), "config.psd1.example must exist"
    content = config_example.read_text(encoding="utf-8")
    for key in ["ClientId", "TenantId", "SiteUrl", "TargetLibrary", "TargetSkillFolderPath", "PilotKnowledgeLibrary"]:
        assert key in content, f"config.psd1.example missing key {key}"

    # Verify git check-ignore for config.psd1 vs config.psd1.example
    ignored_check = subprocess.run(
        ["git", "check-ignore", "-v", "tools/phase-4-native-sharepoint-skills/config.psd1"],
        cwd=repo_root, capture_output=True, text=True
    )
    assert ignored_check.returncode == 0, "config.psd1 should be ignored by git"

    example_check = subprocess.run(
        ["git", "check-ignore", "-v", "tools/phase-4-native-sharepoint-skills/config.psd1.example"],
        cwd=repo_root, capture_output=True, text=True
    )
    assert example_check.returncode != 0, "config.psd1.example should NOT be ignored by git"

def test_evaluation_case_schema_valid():
    repo_root = get_repo_root()
    schema_path = repo_root / "tools" / "phase-4-native-sharepoint-skills" / "schemas" / "evaluation-case-schema.json"
    assert schema_path.exists(), "evaluation-case-schema.json must exist"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert schema.get("$schema") is not None
    assert schema.get("additionalProperties") is False
    assert "properties" in schema

    valid_case = {
        "case_id": "EVAL-NORM-001",
        "category": "normal",
        "objective": "Evaluate normal single topic review query",
        "primary_topic": "01-Overview.aspx",
        "related_topic_allowance": 1,
        "test_identity_class": "INTENDED_READER",
        "prompt": "Review topic 01-Overview.aspx and list main sections.",
        "run_count": 3,
        "expected_semantic_behaviours": ["Produces structured overview"],
        "prohibited_behaviours": ["Includes unreferenced topics"]
    }

    # Should pass validation
    jsonschema.validate(instance=valid_case, schema=schema)

    # Test invalid category
    invalid_category = dict(valid_case, category="invalid_cat")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_category, schema=schema)

    # Test invalid run_count (0 or negative)
    invalid_run_count = dict(valid_case, run_count=0)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_run_count, schema=schema)

    # Test invalid related_topic_allowance (> 2)
    invalid_allowance = dict(valid_case, related_topic_allowance=3)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_allowance, schema=schema)

    # Test invalid test_identity_class
    invalid_identity = dict(valid_case, test_identity_class="SUPERADMIN")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_identity, schema=schema)

    # Test additional property
    extra_prop = dict(valid_case, unexpected_field="foo")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=extra_prop, schema=schema)

    # Test empty required string (case_id)
    empty_str = dict(valid_case, case_id="")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=empty_str, schema=schema)

    # Test empty expected array
    empty_array = dict(valid_case, expected_semantic_behaviours=[])
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=empty_array, schema=schema)
