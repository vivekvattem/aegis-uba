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
    assert metrics.events_per_second > 0
    assert metrics.total_duration_seconds > 0
