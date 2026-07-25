from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd

from aegis_ueba.data_generation.generator import generate_synthetic_dataset, save_datasets
from aegis_ueba.detection.detector import HybridDetector
from aegis_ueba.evaluation.ablation import save_ablation
from aegis_ueba.evaluation.metrics import (
    alert_budget_metrics,
    binary_metrics,
    classification_metrics,
    multiclass_metrics,
    save_json,
    save_metrics,
)
from aegis_ueba.evaluation.plots import save_ablation_figure, save_score_histogram
from aegis_ueba.evaluation.validation import behavioural_signature_checks, dataset_summary, save_validation_artifacts


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
    summary = dataset_summary(events)
    signatures = behavioural_signature_checks(events)
    save_validation_artifacts(summary, signatures, root)
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
    y_true = scored_test["is_anomaly"].to_numpy()
    y_score = scored_test["risk_score"].to_numpy() / 100.0
    binary = binary_metrics(y_true, y_score, detector.threshold / 100.0)
    alert_budget = alert_budget_metrics(y_true, y_score, config.risk["alert_budget_top_pct"])
    anomalies = scored_test[scored_test["is_anomaly"] == 1].copy()
    if anomalies.empty:
        multi = {"macro_f1": 0.0, "weighted_f1": 0.0}
        cls_report = pd.DataFrame(columns=["label", "precision", "recall", "f1-score", "support"])
        cls_cm = pd.DataFrame()
        cls_summary = {"unknown_anomaly_rate": 0.0}
    else:
        multi = multiclass_metrics(anomalies["label"].to_numpy(), anomalies["predicted_attack_type"].to_numpy())
        cls_summary, cls_report, cls_cm = classification_metrics(anomalies["label"].to_numpy(), anomalies["predicted_attack_type"].to_numpy())
    scored_test.to_csv(sample_dir / "scored_test_events.csv", index=False)
    scored_test.nlargest(100, "risk_score").to_csv(sample_dir / "top_alerts.csv", index=False)
    sample_alerts = {}
    for attack_type in ["brute_force", "impossible_travel", "credential_stuffing", "lateral_movement", "device_spoofing", "low_and_slow_exfiltration"]:
        view = scored_test[scored_test["label"] == attack_type].sort_values("risk_score", ascending=False)
        if not view.empty:
            sample_alerts[attack_type] = view.iloc[0].to_dict()
    save_json({**binary, **multi, **cls_summary, **fit_info, **alert_budget, **summary}, metrics_dir / "metrics.json")
    save_metrics(binary, metrics_dir / "binary_metrics.csv")
    save_metrics(alert_budget, metrics_dir / "alert_budget_metrics.csv")
    save_metrics({**fit_info, **multi, **cls_summary}, metrics_dir / "evaluation_metrics.csv")
    cls_report.to_csv(metrics_dir / "classification_report.csv", index=False)
    if not cls_cm.empty:
        cls_cm.to_csv(metrics_dir / "confusion_matrix.csv")
    else:
        pd.DataFrame().to_csv(metrics_dir / "confusion_matrix.csv")
    (sample_dir / "sample_alerts.json").write_text(json.dumps(sample_alerts, indent=2, default=str), encoding="utf-8")
    save_score_histogram(scored_test, figures_dir / "risk_score_histogram.png")
    replay_metrics = detector.replay(scored_test)
    save_json(replay_metrics, metrics_dir / "latency_metrics.json")

    def _variant_scores(scored: pd.DataFrame, variant: str) -> np.ndarray:
        if variant == "statistical_baseline":
            return scored["statistical_score"].to_numpy()
        if variant == "isolation_baseline":
            return scored["isolation_score"].to_numpy()
        if variant == "gru_score_alone":
            return scored["sequence_score"].to_numpy()
        if variant == "hybrid_without_peer":
            values = (
                scored["entity_deviation"] * config.risk["weights"]["entity_deviation"]
                + np.maximum.reduce([scored["sequence_score"], scored["isolation_score"], scored["statistical_score"]]) * config.risk["weights"]["sequence_anomaly"]
                + scored["contextual_score"] * config.risk["weights"]["contextual_evidence"]
                + scored["classifier_confidence"] * config.risk["weights"]["classifier_confidence"]
            )
            return values.to_numpy()
        if variant == "hybrid_without_contextual":
            values = (
                scored["entity_deviation"] * config.risk["weights"]["entity_deviation"]
                + scored["peer_deviation"] * config.risk["weights"]["peer_deviation"]
                + np.maximum.reduce([scored["sequence_score"], scored["isolation_score"], scored["statistical_score"]]) * config.risk["weights"]["sequence_anomaly"]
                + scored["classifier_confidence"] * config.risk["weights"]["classifier_confidence"]
            )
            return values.to_numpy()
        return scored["risk_score"].to_numpy() / 100.0

    ablation_rows = []
    for variant in [
        "statistical_baseline",
        "isolation_baseline",
        "gru_score_alone",
        "hybrid_without_peer",
        "hybrid_without_contextual",
        "full_hybrid",
    ]:
        scores = _variant_scores(scored_test, variant)
        threshold = float(np.quantile(scores, 1.0 - config.risk["alert_budget_top_pct"])) if len(scores) else 1.0
        result = binary_metrics(y_true, scores, threshold)
        budget_variant = alert_budget_metrics(y_true, scores, config.risk["alert_budget_top_pct"])
        ablation_rows.append(
            {
                "variant": variant,
                "pr_auc": result["pr_auc"],
                "precision": result["precision"],
                "recall": result["recall"],
                "f1": result["f1"],
                "false_positive_rate": result["false_positive_rate"],
                "recall_at_top_1pct": budget_variant["recall_at_budget"],
            }
        )
    ablation_df = pd.DataFrame(ablation_rows)
    save_ablation(ablation_rows, metrics_dir / "ablation_results.csv")
    save_ablation_figure(ablation_df, figures_dir / "ablation_comparison.png")
    split_info = pd.DataFrame(
        [
            {"split": "train", "rows": len(train_df), "start": train_df["timestamp"].min(), "end": train_df["timestamp"].max()},
            {"split": "validation", "rows": len(val_df), "start": val_df["timestamp"].min(), "end": val_df["timestamp"].max()},
            {"split": "test", "rows": len(test_df), "start": test_df["timestamp"].min(), "end": test_df["timestamp"].max()},
        ]
    )
    split_info.to_csv(metrics_dir / "split_summary.csv", index=False)
    cold_start_eval = {
        "cold_start_events": int(scored_test["cold_start"].sum()),
        "cold_start_mean_risk": float(scored_test.loc[scored_test["cold_start"] == 1, "risk_score"].mean()) if int(scored_test["cold_start"].sum()) else 0.0,
    }
    drift_eval = {
        "profile_updates_applied": int((scored_test["drift_badge"] == "stable").sum()),
        "high_risk_quarantine_threshold": float(config.risk["safe_profile_update_threshold"]),
    }
    save_json(cold_start_eval, metrics_dir / "cold_start_metrics.json")
    save_json(drift_eval, metrics_dir / "drift_metrics.json")
    return {**binary, **multi, **cls_summary, **fit_info, **replay_metrics, **alert_budget, **cold_start_eval, **drift_eval}
