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
    artifact_root = ROOT / config.project["output_dir"]
    required = [
        artifact_root / "metrics" / "metrics.json",
        artifact_root / "metrics" / "binary_metrics.csv",
        artifact_root / "metrics" / "classification_report.csv",
        artifact_root / "metrics" / "confusion_matrix.csv",
        artifact_root / "metrics" / "alert_budget_metrics.csv",
        artifact_root / "metrics" / "latency_metrics.json",
        artifact_root / "metrics" / "ablation_results.csv",
        artifact_root / "figures" / "ablation_comparison.png",
        artifact_root / "sample_alerts" / "sample_alerts.json",
    ]
    for path in required:
        assert path.exists(), str(path)
