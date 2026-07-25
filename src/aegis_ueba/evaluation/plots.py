from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_score_histogram(frame: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4))
    frame["risk_score"].hist(bins=30)
    plt.title("Risk Score Distribution")
    plt.xlabel("Risk score")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
