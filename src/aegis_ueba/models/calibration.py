from __future__ import annotations

import numpy as np
from sklearn.metrics import precision_recall_fscore_support


def percentile_threshold(scores: np.ndarray, percentile: float) -> float:
    if len(scores) == 0:
        return 1.0
    return float(np.quantile(scores, percentile))


def optimal_f1_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    if len(scores) == 0:
        return 1.0
    candidates = np.unique(np.quantile(scores, np.linspace(0.5, 0.995, 60)))
    best_threshold = float(candidates[0])
    best = (-1.0, -1.0, 1.0)
    for threshold in candidates:
        pred = (scores >= threshold).astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, pred, average="binary", zero_division=0)
        key = (float(f1), float(recall), -float(threshold))
        if key > best:
            best = key
            best_threshold = float(threshold)
    return best_threshold
