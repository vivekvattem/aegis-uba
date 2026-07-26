from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd


@dataclass
class ReplayMetrics:
    events_processed: int
    total_duration_seconds: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    events_per_second: float
    batch_size: int
    included_processing_stages: str


def replay_events(frame: pd.DataFrame, scorer: Callable[[pd.DataFrame], object] | None = None, batch_size: int = 1) -> ReplayMetrics:
    latencies: list[float] = []
    effective_batch_size = max(1, batch_size)
    start = time.perf_counter()
    for idx in range(0, len(frame), effective_batch_size):
        t0 = time.perf_counter()
        batch = frame.iloc[idx : idx + effective_batch_size]
        if scorer is not None:
            scorer(batch)
        else:
            _ = batch.shape[0]
        per_event_latency_seconds = (time.perf_counter() - t0) / max(1, len(batch))
        latencies.extend([per_event_latency_seconds] * len(batch))
    elapsed = max(1e-9, time.perf_counter() - start)
    processed_events = int(len(frame))
    avg_latency_ms = elapsed * 1000.0 / processed_events if processed_events else 0.0
    return ReplayMetrics(
        events_processed=processed_events,
        total_duration_seconds=float(elapsed),
        avg_latency_ms=float(avg_latency_ms),
        p50_latency_ms=float(np.percentile(latencies, 50) * 1000.0) if latencies else 0.0,
        p95_latency_ms=float(np.percentile(latencies, 95) * 1000.0) if latencies else 0.0,
        events_per_second=float(processed_events / elapsed) if processed_events else 0.0,
        batch_size=int(effective_batch_size),
        included_processing_stages=(
            "Batch iteration and scorer invocation only; excludes model training and excludes warm-up unless called by the benchmark harness."
        ),
    )
