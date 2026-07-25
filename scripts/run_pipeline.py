from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

from aegis_ueba.config import load_config
from aegis_ueba.evaluation.pipeline import run_training_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = load_config(ROOT / args.config)
    metrics = run_training_pipeline(config, ROOT)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
