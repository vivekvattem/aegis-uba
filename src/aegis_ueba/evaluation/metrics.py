from __future__ import annotations

from pathlib import Path

import json
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
)


def binary_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float]:
    pred = (scores >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, pred, average="binary", zero_division=0)
    cm = confusion_matrix(y_true, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    try:
        roc = roc_auc_score(y_true, scores)
    except ValueError:
        roc = 0.0
    return {
        "pr_auc": float(average_precision_score(y_true, scores)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc),
        "threshold": float(threshold),
        "false_positive_rate": float(fp / max(1, fp + tn)),
        "false_negative_rate": float(fn / max(1, fn + tp)),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }


def multiclass_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    return {"macro_f1": float(macro), "weighted_f1": float(weighted)}


def save_metrics(metrics: dict[str, float], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(path, index=False)


def save_json(payload: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[dict[str, float], pd.DataFrame, pd.DataFrame]:
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report).transpose().reset_index().rename(columns={"index": "label"})
    labels = sorted(set(y_true.tolist()) | set(y_pred.tolist()))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    cm_df.index.name = "actual"
    unknown_rate = float(np.mean(np.array(y_pred, dtype=object) == "unknown_anomaly"))
    summary = {
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "weighted_f1": float(report["weighted avg"]["f1-score"]),
        "unknown_anomaly_rate": unknown_rate,
    }
    return summary, report_df, cm_df


def alert_budget_metrics(y_true: np.ndarray, scores: np.ndarray, top_fraction: float) -> dict[str, float]:
    n = len(scores)
    budget = max(1, int(np.ceil(n * top_fraction)))
    ranked_idx = np.argsort(scores)[::-1][:budget]
    alerts = y_true[ranked_idx]
    tp = int(alerts.sum())
    precision = float(tp / max(1, budget))
    recall = float(tp / max(1, int(y_true.sum())))
    return {
        "top_fraction": float(top_fraction),
        "budget_events": int(budget),
        "precision_at_budget": precision,
        "recall_at_budget": recall,
        "true_attacks_in_budget": tp,
        "alerts_per_10000_events": float(budget / max(1, n) * 10000.0),
    }
