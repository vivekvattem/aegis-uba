from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

from aegis_ueba.config import load_config
from aegis_ueba.evaluation.pipeline import run_training_pipeline
from aegis_ueba.utils.logging import get_logger
from aegis_ueba.utils.reproducibility import set_global_seed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = load_config(ROOT / args.config)
    set_global_seed(config.project["seed"])
    logger = get_logger("train")
    metrics = run_training_pipeline(config, ROOT)
    logger.info("completed training pipeline: %s", metrics)


if __name__ == "__main__":
    main()
