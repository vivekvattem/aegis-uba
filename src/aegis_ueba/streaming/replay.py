from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd


@dataclass
class ReplayMetrics:
    total_duration_seconds: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    events_per_second: float


def replay_events(frame: pd.DataFrame, scorer: Callable[[pd.DataFrame], object] | None = None, batch_size: int = 1) -> ReplayMetrics:
    latencies = []
    effective_batch_size = max(1, batch_size)
    start = time.perf_counter()
    for idx in range(0, len(frame), effective_batch_size):
        t0 = time.perf_counter()
        batch = frame.iloc[idx : idx + effective_batch_size]
        if scorer is not None:
            scorer(batch)
        else:
            _ = batch.shape[0]
        latencies.append((time.perf_counter() - t0) / max(1, len(batch)))
    elapsed = max(1e-9, time.perf_counter() - start)
    avg_latency_ms = elapsed * 1000.0 / max(1, len(frame))
    return ReplayMetrics(
        total_duration_seconds=float(elapsed),
        avg_latency_ms=float(avg_latency_ms),
        p50_latency_ms=float(np.percentile(latencies, 50) * 1000.0) if latencies else 0.0,
        p95_latency_ms=float(np.percentile(latencies, 95) * 1000.0) if latencies else 0.0,
        events_per_second=float(len(frame) / elapsed),
    )
