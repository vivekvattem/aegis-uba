from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ReplayMetrics:
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    events_per_second: float


def replay_events(frame: pd.DataFrame) -> ReplayMetrics:
    latencies = []
    start = time.perf_counter()
    for _ in frame.itertuples(index=False):
        t0 = time.perf_counter()
        latencies.append((time.perf_counter() - t0) * 1000)
    elapsed = max(1e-9, time.perf_counter() - start)
    return ReplayMetrics(
        avg_latency_ms=float(np.mean(latencies)) if latencies else 0.0,
        p50_latency_ms=float(np.percentile(latencies, 50)) if latencies else 0.0,
        p95_latency_ms=float(np.percentile(latencies, 95)) if latencies else 0.0,
        events_per_second=float(len(frame) / elapsed),
    )
