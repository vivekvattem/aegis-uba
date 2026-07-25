from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.detection.contextual_rules import contextual_attack_prediction, contextual_score


def test_contextual_impossible_travel_activation() -> None:
    row = pd.Series({"geo_velocity_kmh": 5000.0, "failed_attempt_count": 0, "auth_success": 1})
    label, confidence, source = contextual_attack_prediction(row, velocity_threshold=900.0)
    score, _ = contextual_score(row, velocity_threshold=900.0)
    assert label == "impossible_travel"
    assert confidence > 0.9
    assert source == "contextual"
    assert score > 0.8
