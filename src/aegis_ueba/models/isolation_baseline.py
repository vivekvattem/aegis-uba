from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationBaseline:
    def __init__(self, contamination: float, random_state: int) -> None:
        self.model = IsolationForest(contamination=contamination, random_state=random_state, n_estimators=200)

    def fit(self, matrix: np.ndarray) -> "IsolationBaseline":
        self.model.fit(matrix)
        return self

    def score(self, matrix: np.ndarray) -> np.ndarray:
        raw = -self.model.score_samples(matrix)
        raw = (raw - raw.min()) / max(1e-9, raw.max() - raw.min())
        return raw
