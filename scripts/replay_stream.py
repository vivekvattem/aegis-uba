from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

from aegis_ueba.config import load_config
from aegis_ueba.streaming.replay import replay_events


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    _ = load_config(ROOT / args.config)
    path = ROOT / "artifacts" / "sample_alerts" / "scored_test_events.csv"
    frame = pd.read_csv(path)
    metrics = replay_events(frame)
    print(metrics)


if __name__ == "__main__":
    main()
