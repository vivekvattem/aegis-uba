from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class EntityProfileState:
    entity_id: str
    trusted_events: int = 0
    hours: Counter = field(default_factory=Counter)
    countries: Counter = field(default_factory=Counter)
    resources: Counter = field(default_factory=Counter)
    fingerprints: Counter = field(default_factory=Counter)
    upload_mean: float = 0.0
    duration_mean: float = 0.0
    version: int = 0


class EntityProfileStore:
    def __init__(self) -> None:
        self.store: dict[str, EntityProfileState] = {}

    def fit(self, frame: pd.DataFrame) -> "EntityProfileStore":
        for _, row in frame.iterrows():
            self.update(row, alpha=1.0)
        return self

    def get(self, entity_id: str) -> EntityProfileState | None:
        return self.store.get(entity_id)

    def update(self, row: pd.Series, alpha: float = 0.15) -> None:
        entity_id = str(row["entity_id"])
        state = self.store.setdefault(entity_id, EntityProfileState(entity_id=entity_id))
        state.trusted_events += 1
        state.hours[int(row["hour"])] += 1
        state.countries[str(row["source_country"])] += 1
        state.resources[str(row["resource_accessed"])] += 1
        state.fingerprints[str(row["device_fingerprint"])] += 1
        if state.trusted_events == 1:
            state.upload_mean = float(row["bytes_uploaded"])
            state.duration_mean = float(row["session_duration"])
        else:
            state.upload_mean = (1 - alpha) * state.upload_mean + alpha * float(row["bytes_uploaded"])
            state.duration_mean = (1 - alpha) * state.duration_mean + alpha * float(row["session_duration"])
        state.version += 1

    def score(self, row: pd.Series) -> dict[str, float]:
        state = self.get(str(row["entity_id"]))
        if state is None or state.trusted_events == 0:
            return {"entity_deviation": 0.35, "cold_start": 1.0}
        hour_freq = state.hours[int(row["hour"])] / max(1, sum(state.hours.values()))
        country_freq = state.countries[str(row["source_country"])] / max(1, sum(state.countries.values()))
        resource_freq = state.resources[str(row["resource_accessed"])] / max(1, sum(state.resources.values()))
        fp_freq = state.fingerprints[str(row["device_fingerprint"])] / max(1, sum(state.fingerprints.values()))
        upload_dev = abs(float(row["bytes_uploaded"]) - state.upload_mean) / max(1.0, state.upload_mean)
        duration_dev = abs(float(row["session_duration"]) - state.duration_mean) / max(1.0, state.duration_mean)
        deviation = 1 - np.mean([hour_freq, country_freq, resource_freq, fp_freq])
        deviation = float(np.clip(0.6 * deviation + 0.2 * min(1.0, upload_dev) + 0.2 * min(1.0, duration_dev), 0.0, 1.0))
        return {"entity_deviation": deviation, "cold_start": 0.0}
