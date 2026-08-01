"""
conftest.py
===========

Adds the plugin's scripts/ directory to sys.path so tests can import
`pandoc.*` and other script modules directly (e.g.
`from pandoc.attrs import strip_pandoc_attrs`), matching the
scripts/pandoc/ layout on disk without requiring package installation.
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
