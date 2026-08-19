import sys
from pathlib import Path

# Add plugin scripts directory to sys.path
scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
