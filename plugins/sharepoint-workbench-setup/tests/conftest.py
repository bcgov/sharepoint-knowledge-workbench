"""
Purpose:
    Make the plugin scripts available to pytest modules during test collection.

Key Input Dependencies:
    - The plugin scripts/ directory containing imported test modules.

Function Index:
    None (no functions are defined in this module).
"""

import sys
from pathlib import Path

# Add scripts/ to sys.path
scripts_dir = Path(__file__).resolve().parent.parent / 'scripts'
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
