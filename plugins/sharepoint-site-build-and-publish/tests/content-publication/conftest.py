"""
conftest.py
===========

Adds the plugin's scripts/content-publication/ directory to sys.path so tests can import
sharepoint_*.py modules directly, matching docx-to-content's original
pre-Phase-4.5 convention (this plugin was carried out of docx-to-content
wholesale in Wave 8, unmigrated -- sharepoint-site-build-and-publish is out of
Phase 4.5's scope, per CLAUDE.md).

Purpose:
    Configure the content-publication test namespace to import its flat script modules.

Key Input Dependencies:
    - The plugin scripts/content-publication directory and Python sys.path.

Function Index:
    none
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts" / "content-publication"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
