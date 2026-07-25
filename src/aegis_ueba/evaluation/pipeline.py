from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from aegis_ueba.data_generation.generator import generate_synthetic_dataset, save_datasets
from aegis_ueba.detection.detector import HybridDetector
from aegis_ueba.evaluation.ablation import save_ablation
from aegis_ueba.evaluation.metrics import binary_metrics, multiclass_metrics, save_metrics
from aegis_ueba.evaluation.plots import save_score_histogram


def chronological_split(frame: pd.DataFrame, split_cfg) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = frame.sort_values("timestamp").reset_index(drop=True)
    n = len(df)
    train_end = int(n * split_cfg.train)
    val_end = train_end + int(n * split_cfg.validation)
    return df.iloc[:train_end].copy(), df.iloc[train_end:val_end].copy(), df.iloc[val_end:].copy()


def run_training_pipeline(config, root: str | Path) -> dict[str, float]:
    root = Path(root)
    events = generate_synthetic_dataset(config.data, config.project["seed"])
    save_datasets(events, root)
    train_df, val_df, test_df = chronological_split(events, config.split)
    detector = HybridDetector(config.model_dump(), config.project["seed"])
    fit_info = detector.fit(train_df, val_df)
    scored_test = detector.score(test_df, update_profiles=True)
    detector.save(root)
    metrics_dir = root / "artifacts" / "metrics"
    figures_dir = root / "artifacts" / "figures"
    sample_dir = root / "artifacts" / "sample_alerts"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    sample_dir.mkdir(parents=True, exist_ok=True)
    binary = binary_metrics(scored_test["is_anomaly"].to_numpy(), scored_test["risk_score"].to_numpy() / 100.0, detector.threshold / 100.0)
    anomalies = scored_test[scored_test["is_anomaly"] == 1].copy()
    if anomalies.empty:
        multi = {"macro_f1": 0.0, "weighted_f1": 0.0}
    else:
        multi = multiclass_metrics(anomalies["label"].to_numpy(), anomalies["predicted_attack_type"].to_numpy())
    scored_test.to_csv(sample_dir / "scored_test_events.csv", index=False)
    scored_test.nlargest(100, "risk_score").to_csv(sample_dir / "top_alerts.csv", index=False)
    save_metrics({**binary, **multi, **fit_info}, metrics_dir / "evaluation_metrics.csv")
    save_score_histogram(scored_test, figures_dir / "risk_score_histogram.png")
    replay_metrics = detector.replay(scored_test)
    save_metrics(replay_metrics, metrics_dir / "replay_metrics.csv")
    save_ablation(
        [
            {"variant": "statistical_baseline", "mean_score": float(scored_test["statistical_score"].mean())},
            {"variant": "isolation_baseline", "mean_score": float(scored_test["isolation_score"].mean())},
            {"variant": "gru_sequence_score", "mean_score": float(scored_test["sequence_score"].mean())},
            {"variant": "full_hybrid", "mean_score": float(scored_test["risk_score"].mean())},
        ],
        metrics_dir / "ablations.csv",
    )
    split_info = pd.DataFrame(
        [
            {"split": "train", "rows": len(train_df), "start": train_df["timestamp"].min(), "end": train_df["timestamp"].max()},
            {"split": "validation", "rows": len(val_df), "start": val_df["timestamp"].min(), "end": val_df["timestamp"].max()},
            {"split": "test", "rows": len(test_df), "start": test_df["timestamp"].min(), "end": test_df["timestamp"].max()},
        ]
    )
    split_info.to_csv(metrics_dir / "split_summary.csv", index=False)
    return {**binary, **multi, **fit_info, **replay_metrics}
