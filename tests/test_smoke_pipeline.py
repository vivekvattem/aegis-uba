from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.config import load_config
from aegis_ueba.evaluation.pipeline import run_training_pipeline


def test_fast_pipeline_smoke() -> None:
    config = load_config(ROOT / "configs" / "fast.yaml")
    metrics = run_training_pipeline(config, ROOT)
    assert "pr_auc" in metrics
