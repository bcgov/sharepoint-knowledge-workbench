"""Negative-control fixture (Wave 1 Step 5): imports knowledge_workbench_contracts
without declaring it in this fixture's own pyproject.toml [project].dependencies.
A correct metadata-inspection check must flag this fixture's dependency
declaration as incomplete, even though the import would happen to succeed at
runtime if the contracts distribution is coincidentally already installed in
the environment (which is exactly the undeclared-dependency risk this check
guards against — see check_declares_dependency() in isolated_install_check.py)."""
from knowledge_workbench_contracts.tree_hash import compute_tree_hash  # noqa: F401
