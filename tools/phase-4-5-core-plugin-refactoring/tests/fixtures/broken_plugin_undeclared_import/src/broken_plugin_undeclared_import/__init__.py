"""Negative-control fixture (Wave 1 Step 5): imports an upstream plugin's
implementation package that is never installed by isolated_install_check.py
and never declared in this fixture's own pyproject.toml dependencies. A
correct isolated-install check must fail on this fixture."""
import canonical_knowledge  # noqa: F401  (deliberately undeclared, never installed)
