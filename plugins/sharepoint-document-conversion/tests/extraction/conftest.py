"""Purpose:
    Define regression tests for conftest in the extraction namespace.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - sys
    - pathlib

Key Functions Index:
    - No locally defined functions."""

import sys
from pathlib import Path

# Add plugin scripts directory to sys.path
scripts_dir = Path(__file__).resolve().parents[2] / "scripts" / "extraction"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
