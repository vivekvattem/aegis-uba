from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd


class PeerProfileStore:
    def __init__(self, columns: list[str]) -> None:
        self.columns = columns
        self.counts: dict[tuple[str, ...], dict[str, Counter]] = {}

    def _key(self, row: pd.Series) -> tuple[str, ...]:
        return tuple(str(row[col]) for col in self.columns)

    def fit(self, frame: pd.DataFrame) -> "PeerProfileStore":
        for _, row in frame.iterrows():
            self.update(row)
        return self

    def update(self, row: pd.Series) -> None:
        key = self._key(row)
        record = self.counts.setdefault(key, {"resource": Counter(), "country": Counter(), "protocol": Counter()})
        record["resource"][str(row["resource_accessed"])] += 1
        record["country"][str(row["source_country"])] += 1
        record["protocol"][str(row["protocol"])] += 1

    def score(self, row: pd.Series) -> float:
        key = self._key(row)
        record = self.counts.get(key)
        if not record:
            return 0.25
        scores = []
        for field, value in [("resource", row["resource_accessed"]), ("country", row["source_country"]), ("protocol", row["protocol"])]:
            counter = record[field]
            scores.append(counter[str(value)] / max(1, sum(counter.values())))
        return float(np.clip(1 - np.mean(scores), 0.0, 1.0))
