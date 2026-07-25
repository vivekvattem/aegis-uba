from __future__ import annotations

import numpy as np


def percentile_threshold(scores: np.ndarray, percentile: float) -> float:
    if len(scores) == 0:
        return 1.0
    return float(np.quantile(scores, percentile))
