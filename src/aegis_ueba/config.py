from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class SplitConfig(BaseModel):
    train: float
    validation: float
    test: float

    @field_validator("test")
    @classmethod
    def validate_sum(cls, value: float, info: Any) -> float:
        data = info.data
        train = data.get("train", 0.0)
        validation = data.get("validation", 0.0)
        total = train + validation + value
        if abs(total - 1.0) > 1e-6:
            raise ValueError("split ratios must sum to 1.0")
        return value


class AppConfig(BaseModel):
    project: dict[str, Any]
    data: dict[str, Any]
    features: dict[str, Any]
    split: SplitConfig
    models: dict[str, Any]
    risk: dict[str, Any]
    drift: dict[str, Any]
    replay: dict[str, Any]


def load_config(path: str | Path) -> AppConfig:
    with Path(path).open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return AppConfig.model_validate(raw)
