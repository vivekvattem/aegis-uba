from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

from aegis_ueba.config import load_config
from aegis_ueba.data_generation.generator import generate_synthetic_dataset, save_datasets
from aegis_ueba.utils.logging import get_logger
from aegis_ueba.utils.reproducibility import set_global_seed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = load_config(ROOT / args.config)
    set_global_seed(config.project["seed"])
    logger = get_logger("generate_data")
    events = generate_synthetic_dataset(config.data, config.project["seed"])
    paths = save_datasets(events, ROOT)
    logger.info("generated %s events", len(events))
    logger.info("saved labeled dataset to %s", paths["labeled"])
    logger.info("saved inference dataset to %s", paths["inference"])


if __name__ == "__main__":
    main()
