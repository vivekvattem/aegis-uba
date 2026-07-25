from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from aegis_ueba.profiles.entity_profile import EntityProfileStore


@dataclass
class DriftDecision:
    should_update: bool
    reason: str


class DriftManager:
    def __init__(self, safe_threshold: float, alpha: float, min_trusted_observations: int) -> None:
        self.safe_threshold = safe_threshold
        self.alpha = alpha
        self.min_trusted_observations = min_trusted_observations

    def evaluate_update(self, row: pd.Series, risk_score: float, store: EntityProfileStore) -> DriftDecision:
        state = store.get(str(row["entity_id"]))
        if risk_score > self.safe_threshold:
            return DriftDecision(False, "quarantined_high_risk")
        if state is None or state.trusted_events < self.min_trusted_observations:
            return DriftDecision(True, "cold_start_bootstrap")
        return DriftDecision(True, "trusted_low_risk")
