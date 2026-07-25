from __future__ import annotations

import numpy as np
import pandas as pd

from aegis_ueba.profiles.entity_profile import EntityProfileStore
from aegis_ueba.profiles.peer_profile import PeerProfileStore


class StatisticalBaseline:
    def __init__(self, peer_columns: list[str]) -> None:
        self.entity_profiles = EntityProfileStore()
        self.peer_profiles = PeerProfileStore(peer_columns)

    def fit(self, frame: pd.DataFrame) -> "StatisticalBaseline":
        self.entity_profiles.fit(frame)
        self.peer_profiles.fit(frame)
        return self

    def score_frame(self, frame: pd.DataFrame) -> np.ndarray:
        scores = []
        for _, row in frame.iterrows():
            entity_score = self.entity_profiles.score(row)["entity_deviation"]
            peer_score = self.peer_profiles.score(row)
            auth_score = min(1.0, float(row["failed_attempt_count"]) / 10.0)
            scores.append(np.clip(0.55 * entity_score + 0.25 * peer_score + 0.20 * auth_score, 0.0, 1.0))
        return np.array(scores)
