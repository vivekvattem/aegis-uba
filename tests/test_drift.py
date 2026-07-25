from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.profiles.drift_manager import DriftManager
from aegis_ueba.profiles.entity_profile import EntityProfileStore


def test_high_risk_events_are_quarantined() -> None:
    manager = DriftManager(safe_threshold=35, alpha=0.1, min_trusted_observations=3)
    store = EntityProfileStore()
    row = pd.Series({"entity_id": "u1"})
    decision = manager.evaluate_update(row, 90, store)
    assert not decision.should_update
