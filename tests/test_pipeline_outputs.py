from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.config import load_config
from aegis_ueba.evaluation.pipeline import run_training_pipeline


def test_pipeline_writes_required_metric_files() -> None:
    config = load_config(ROOT / "configs" / "fast.yaml")
    run_training_pipeline(config, ROOT)
    required = [
        ROOT / "artifacts" / "metrics" / "metrics.json",
        ROOT / "artifacts" / "metrics" / "binary_metrics.csv",
        ROOT / "artifacts" / "metrics" / "classification_report.csv",
        ROOT / "artifacts" / "metrics" / "confusion_matrix.csv",
        ROOT / "artifacts" / "metrics" / "alert_budget_metrics.csv",
        ROOT / "artifacts" / "metrics" / "latency_metrics.json",
        ROOT / "artifacts" / "metrics" / "ablation_results.csv",
        ROOT / "artifacts" / "figures" / "ablation_comparison.png",
        ROOT / "artifacts" / "sample_alerts" / "sample_alerts.json",
    ]
    for path in required:
        assert path.exists(), str(path)
