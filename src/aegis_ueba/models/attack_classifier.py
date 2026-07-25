from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier


class AttackClassifier:
    def __init__(self, n_estimators: int, max_depth: int, random_state: int, unknown_threshold: float) -> None:
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight="balanced_subsample",
            random_state=random_state,
        )
        self.unknown_threshold = unknown_threshold
        self.classes_: list[str] = []

    def fit(self, matrix: np.ndarray, labels: np.ndarray) -> "AttackClassifier":
        self.model.fit(matrix, labels)
        self.classes_ = list(self.model.classes_)
        return self

    def predict(self, matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        probabilities = self.model.predict_proba(matrix)
        best_idx = probabilities.argmax(axis=1)
        labels = np.array([self.classes_[idx] for idx in best_idx], dtype=object)
        confidence = probabilities.max(axis=1)
        labels = np.where(confidence < self.unknown_threshold, "unknown_anomaly", labels)
        return labels, confidence
