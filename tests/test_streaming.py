from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.streaming.replay import replay_events


def test_replay_metrics_are_mathematically_consistent() -> None:
    frame = pd.DataFrame({"x": list(range(100))})
    metrics = replay_events(frame, scorer=lambda batch: batch.shape[0], batch_size=10)
    reconstructed_avg = metrics.total_duration_seconds * 1000.0 / len(frame)
    assert abs(metrics.avg_latency_ms - reconstructed_avg) < 1e-6
    assert metrics.events_processed == len(frame)
    assert metrics.events_per_second > 0
    assert metrics.total_duration_seconds > 0


def test_replay_percentiles_use_individual_event_latencies() -> None:
    frame = pd.DataFrame({"x": list(range(5))})
    observed_batch_sizes: list[int] = []

    def scorer(batch: pd.DataFrame) -> int:
        observed_batch_sizes.append(len(batch))
        return len(batch)

    metrics = replay_events(frame, scorer=scorer, batch_size=2)
    assert observed_batch_sizes == [2, 2, 1]
    assert metrics.p50_latency_ms >= 0
    assert metrics.p95_latency_ms >= metrics.p50_latency_ms


def test_replay_handles_empty_frames() -> None:
    frame = pd.DataFrame({"x": []})
    metrics = replay_events(frame, scorer=lambda batch: batch.shape[0], batch_size=8)
    assert metrics.events_processed == 0
    assert metrics.avg_latency_ms == 0.0
    assert metrics.p50_latency_ms == 0.0
    assert metrics.p95_latency_ms == 0.0
    assert metrics.events_per_second == 0.0


def test_replay_reports_batch_size_and_stage_description() -> None:
    frame = pd.DataFrame({"x": list(range(4))})
    metrics = replay_events(frame, scorer=lambda batch: batch.shape[0], batch_size=3)
    assert metrics.batch_size == 3
    assert "excludes model training" in metrics.included_processing_stages.lower()
