"""Makes the jhe package importable when a check is run as `python checks/<name>.py` from any directory."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
