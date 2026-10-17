"""Two-λ variant of the pinned, unmodified public AI Futures Model.

The calibration keeps the preset's λ; a separate forward λ applies to coding labor from today on.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream"
sys.path.insert(0, str(UPSTREAM))
