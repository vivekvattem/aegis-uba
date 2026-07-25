from __future__ import annotations

import numpy as np


def severity_band(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def combine_scores(components: dict[str, float], weights: dict[str, float]) -> float:
    total = 0.0
    for key, weight in weights.items():
        total += float(weight) * float(components.get(key, 0.0))
    return float(np.clip(total * 100.0, 0.0, 100.0))
