"""
conftest.py
===========

Adds the plugin's scripts/ directory to sys.path so tests can import
sharepoint_*.py modules directly, matching docx-to-content's original
pre-Phase-4.5 convention (this plugin was carried out of docx-to-content
wholesale in Wave 8, unmigrated -- sharepoint-content-publication is out of
Phase 4.5's scope, per CLAUDE.md).
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
