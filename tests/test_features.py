from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.config import load_config
from aegis_ueba.data_generation.generator import generate_synthetic_dataset
from aegis_ueba.features.geographic import haversine_km
from aegis_ueba.features.preprocessing import engineer_features


def test_feature_engineering_creates_expected_columns() -> None:
    config = load_config(ROOT / "configs" / "fast.yaml")
    frame = generate_synthetic_dataset(config.data, config.project["seed"]).head(200)
    feat = engineer_features(frame)
    assert "hour_sin" in feat.columns
    assert "distance_from_prev_km" in feat.columns
    assert haversine_km(0, 0, 0, 0) == 0
