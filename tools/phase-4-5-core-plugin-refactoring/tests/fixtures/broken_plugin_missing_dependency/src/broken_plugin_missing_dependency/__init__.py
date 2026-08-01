"""Negative-control fixture (Wave 2 correction): this pyproject.toml declares
a workbench-family distribution (knowledge-workbench-contracts) as a pip
dependency. Under the corrected model (see
docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md)
no plugin may depend on any shared workbench distribution -- every plugin
must carry its own contract/runtime code. check_no_workbench_family_dependency()
must flag this fixture's pyproject.toml as a violation."""
