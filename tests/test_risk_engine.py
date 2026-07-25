from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.detection.risk_engine import combine_scores, severity_band


def test_risk_score_bounds() -> None:
    score = combine_scores({"entity_deviation": 1.0}, {"entity_deviation": 1.0})
    assert 0 <= score <= 100
    assert severity_band(85) == "critical"
