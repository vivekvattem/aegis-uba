from __future__ import annotations

from pathlib import Path

import pandas as pd


def save_ablation(rows: list[dict], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
