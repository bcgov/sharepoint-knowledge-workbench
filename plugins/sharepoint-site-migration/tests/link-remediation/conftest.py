"""
conftest.py
===========

Purpose:
    Makes the plugin's flat ``scripts/link-remediation/`` directory importable by bare module
    name during test runs without requiring an editable install first, matching
    the convention used by the other workbench plugins' test suites.

Layer: sharepoint-site-migration / tests

Key Input Dependencies: pytest and the plugin directory tree.
"""

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "link-remediation"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

FIXTURES = Path(__file__).resolve().parent / "fixtures"
