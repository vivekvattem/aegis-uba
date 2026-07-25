from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.config import load_config
from aegis_ueba.data_generation.generator import generate_synthetic_dataset
from aegis_ueba.schemas import REQUIRED_FIELDS


def test_generator_is_deterministic() -> None:
    config = load_config(ROOT / "configs" / "fast.yaml")
    first = generate_synthetic_dataset(config.data, config.project["seed"])
    second = generate_synthetic_dataset(config.data, config.project["seed"])
    assert first.equals(second)
    assert list(first.columns) == REQUIRED_FIELDS
    assert first["is_anomaly"].mean() > 0
