"""
conftest.py
===========

Makes the plugin's flat `scripts/` directory importable for the plugin-local
test suite without requiring an install, and exposes the shared paths every
test module needs (scripts dir for subprocess CLI runs, packaged assets dir,
neutral fixtures dir).

No test in this suite mocks file parsing, path resolution, or script
execution -- `.agent/rules/test-driven-development.md`'s "Critical Runtime
Paths -- No Mocking Allowed" section applies directly to this plugin, whose
entire job is parsing files off disk.
"""

import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
ASSETS_DIR = SCRIPTS_DIR / "assets"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def scripts_dir() -> Path:
    """Absolute path to the plugin's flat scripts directory."""
    return SCRIPTS_DIR


@pytest.fixture
def assets_dir() -> Path:
    """Absolute path to the packaged assets directory."""
    return ASSETS_DIR


@pytest.fixture
def fixtures_dir() -> Path:
    """Absolute path to the neutral test fixtures directory."""
    return FIXTURES_DIR
