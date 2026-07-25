from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_recall_fscore_support, roc_auc_score


def binary_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float]:
    pred = (scores >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, pred, average="binary", zero_division=0)
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
    }


def multiclass_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    return {"macro_f1": float(macro), "weighted_f1": float(weighted)}


def save_metrics(metrics: dict[str, float], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(path, index=False)
