from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.config import load_config
from aegis_ueba.data_generation.generator import generate_synthetic_dataset
from aegis_ueba.evaluation.pipeline import chronological_split


def test_chronological_split_and_campaign_separation() -> None:
    config = load_config(ROOT / "configs" / "fast.yaml")
    events = generate_synthetic_dataset(config.data, config.project["seed"], split_config=config.split.model_dump())
    train_df, val_df, test_df = chronological_split(events, config.split)
    assert train_df["timestamp"].max() <= val_df["timestamp"].min()
    assert val_df["timestamp"].max() <= test_df["timestamp"].min()
    train_campaigns = set(train_df["synthetic_attack_id"].dropna())
    val_campaigns = set(val_df["synthetic_attack_id"].dropna())
    test_campaigns = set(test_df["synthetic_attack_id"].dropna())
    assert train_campaigns.isdisjoint(val_campaigns)
    assert train_campaigns.isdisjoint(test_campaigns)
    assert val_campaigns.isdisjoint(test_campaigns)
