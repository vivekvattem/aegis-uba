from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from aegis_ueba.data_generation.attacks import inject_attacks
from aegis_ueba.data_generation.profiles import SENSITIVE_RESOURCES, build_entity_profiles
from aegis_ueba.schemas import REQUIRED_FIELDS


def _sample_timestamp(start: datetime, days: int, hours: list[int], weekend_rate: float, rng: np.random.Generator) -> datetime:
    day_offset = int(rng.integers(0, days))
    base = start + timedelta(days=day_offset)
    if base.weekday() >= 5 and rng.random() > weekend_rate:
        base = base + timedelta(days=(7 - base.weekday()))
    hour = int(rng.choice(hours))
    minute = int(rng.integers(0, 60))
    second = int(rng.integers(0, 60))
    return base.replace(hour=hour, minute=minute, second=second)


def _sample_commands(command_pool: list[str], rng: np.random.Generator) -> str:
    length = int(rng.integers(2, min(5, len(command_pool)) + 1))
    return "|".join(rng.choice(command_pool, size=length, replace=False).tolist())


def generate_synthetic_dataset(config: dict, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = datetime(2026, 1, 1, 0, 0, 0)
    profiles = build_entity_profiles(config, rng)
    rows: list[dict] = []
    for profile in profiles:
        count = int(rng.integers(config["events_per_entity_min"], config["events_per_entity_max"] + 1))
        for event_idx in range(count):
            timestamp = _sample_timestamp(start, config["days"], profile.typical_hours, profile.weekend_activity_rate, rng)
            protocol = str(rng.choice(profile.common_protocols))
            port = int(rng.choice(profile.common_ports))
            resource = str(rng.choice(profile.common_resources))
            rows.append(
                {
                    "event_id": f"evt_{profile.entity_id}_{event_idx:04d}",
                    "session_id": f"ses_{profile.entity_id}_{event_idx // 3:04d}",
                    "entity_id": profile.entity_id,
                    "entity_type": profile.entity_type,
                    "role": profile.role,
                    "timestamp": timestamp,
                    "source_ip": f"{profile.source_ip_prefix}.{int(rng.integers(1, 255))}",
                    "source_country": profile.home_country,
                    "geo_location": profile.home_city,
                    "latitude": profile.latitude + float(rng.normal(0, 0.2)),
                    "longitude": profile.longitude + float(rng.normal(0, 0.2)),
                    "resource_accessed": resource,
                    "destination_system": f"{resource}-node-{int(rng.integers(1, 10))}",
                    "auth_method": profile.preferred_auth,
                    "auth_success": 1,
                    "failed_attempt_count": 0,
                    "session_duration": max(1.0, profile.median_duration + float(rng.normal(0, profile.median_duration * 0.3))),
                    "command_sequence": _sample_commands(profile.command_pool, rng),
                    "device_fingerprint": str(rng.choice(profile.known_fingerprints)),
                    "protocol": protocol,
                    "port": port,
                    "privilege_level": profile.privilege_level,
                    "response_status": 200,
                    "event_type": "data_transfer" if resource in SENSITIVE_RESOURCES and rng.random() < 0.3 else "login",
                    "bytes_uploaded": max(0.0, profile.median_upload * float(rng.uniform(0.6, 1.5))),
                    "bytes_downloaded": max(0.0, profile.median_download * float(rng.uniform(0.6, 1.5))),
                    "label": "normal",
                    "is_anomaly": 0,
                    "anomaly_type": "normal",
                    "synthetic_attack_id": None,
                }
            )
    events = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
    events = inject_attacks(events, config, rng)
    return events[REQUIRED_FIELDS]


def save_datasets(events: pd.DataFrame, root: str | Path) -> dict[str, Path]:
    root = Path(root)
    raw_dir = root / "data" / "raw"
    processed_dir = root / "data" / "processed"
    inference_dir = root / "data" / "inference"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    inference_dir.mkdir(parents=True, exist_ok=True)
    labeled_path = raw_dir / "synthetic_events.csv"
    inference_path = inference_dir / "synthetic_events_inference.csv"
    events.to_csv(labeled_path, index=False)
    inference_cols = [c for c in events.columns if c not in {"label", "is_anomaly", "anomaly_type", "synthetic_attack_id"}]
    events[inference_cols].to_csv(inference_path, index=False)
    return {"labeled": labeled_path, "inference": inference_path}
