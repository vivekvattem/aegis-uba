from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

import numpy as np
import pandas as pd

from aegis_ueba.data_generation.profiles import COUNTRIES, SENSITIVE_RESOURCES


def _sample_far_location(rng: np.random.Generator, current_country: str) -> tuple[str, str, float, float]:
    options = [row for row in COUNTRIES if row[0] != current_country]
    country, city, lat, lon = options[int(rng.integers(0, len(options)))]
    return country, city, float(lat), float(lon)


def inject_attacks(
    events: pd.DataFrame,
    config: dict,
    rng: np.random.Generator,
    split_config: dict | None = None,
) -> pd.DataFrame:
    target_anomalies = max(1, int(len(events) * config["anomaly_rate"]))
    weights = config["attack_type_weights"]
    attack_types = list(weights.keys())
    probs = np.array(list(weights.values()), dtype=float)
    probs = probs / probs.sum()
    split_cfg = split_config or {"train": 0.6, "validation": 0.2, "test": 0.2}
    ts = pd.to_datetime(events["timestamp"])
    min_ts = ts.min()
    max_ts = ts.max()
    total_span = max_ts - min_ts
    train_end = min_ts + total_span * split_cfg["train"]
    val_end = train_end + total_span * split_cfg["validation"]
    windows = [
        ("train", min_ts, train_end),
        ("validation", train_end, val_end),
        ("test", val_end, max_ts + timedelta(seconds=1)),
    ]
    campaigns_per_attack = int(config.get("campaigns_per_attack", 3))
    attack_budgets = {attack: max(6, int(target_anomalies * weights[attack])) for attack in attack_types}
    attack_counter = 0
    entity_events = defaultdict(list)
    for idx, row in events.iterrows():
        entity_events[row["entity_id"]].append(idx)

    def _apply(indices: list[int], attack_type: str, attack_id: str, split_start, split_end) -> None:
        if not indices:
            return
        split_seconds = max(3600.0, (split_end - split_start).total_seconds())
        campaign_anchor = split_start + timedelta(seconds=split_seconds * float(rng.uniform(0.2, 0.75)))
        for pos, idx in enumerate(indices):
            row = events.loc[idx]
            events.at[idx, "is_anomaly"] = 1
            events.at[idx, "synthetic_attack_id"] = attack_id
            events.at[idx, "label"] = attack_type
            events.at[idx, "anomaly_type"] = attack_type
            if attack_type == "brute_force":
                events.at[idx, "auth_success"] = 0
                events.at[idx, "failed_attempt_count"] = int(rng.integers(11, 20))
                events.at[idx, "event_type"] = "login"
                events.at[idx, "session_duration"] = float(rng.uniform(1, 5))
                events.at[idx, "timestamp"] = campaign_anchor + timedelta(seconds=pos * 45)
            elif attack_type == "impossible_travel":
                country, city, lat, lon = _sample_far_location(rng, row["source_country"])
                events.at[idx, "source_country"] = country
                events.at[idx, "geo_location"] = city
                events.at[idx, "latitude"] = lat
                events.at[idx, "longitude"] = lon
                events.at[idx, "timestamp"] = campaign_anchor + timedelta(minutes=10 * pos)
            elif attack_type == "credential_stuffing":
                events.at[idx, "auth_success"] = 0
                events.at[idx, "failed_attempt_count"] = int(rng.integers(6, 16))
                events.at[idx, "source_ip"] = "185.199.110.153"
                events.at[idx, "event_type"] = "login"
                events.at[idx, "timestamp"] = campaign_anchor + timedelta(seconds=pos * 20)
            elif attack_type == "lateral_movement":
                events.at[idx, "resource_accessed"] = str(rng.choice(list(SENSITIVE_RESOURCES)))
                events.at[idx, "privilege_level"] = 3
                events.at[idx, "command_sequence"] = "netstat|ssh|sudo_su|vault_read"
                events.at[idx, "destination_system"] = f"internal-{int(rng.integers(100, 999))}"
                events.at[idx, "timestamp"] = campaign_anchor + timedelta(minutes=15 * pos)
            elif attack_type == "device_spoofing":
                events.at[idx, "device_fingerprint"] = f"spoofed-fp-{int(rng.integers(1000, 9999))}"
                events.at[idx, "protocol"] = str(rng.choice(["rdp", "ssh", "smb"]))
                events.at[idx, "timestamp"] = campaign_anchor + timedelta(minutes=30 * pos)
            elif attack_type == "low_and_slow_exfiltration":
                events.at[idx, "bytes_uploaded"] = float(row["bytes_uploaded"]) * rng.uniform(5.0, 9.0)
                events.at[idx, "event_type"] = "data_transfer"
                events.at[idx, "session_duration"] = float(row["session_duration"]) * rng.uniform(1.3, 2.2)
                events.at[idx, "timestamp"] = (campaign_anchor + timedelta(hours=pos * 4)).replace(hour=int(rng.choice([0, 1, 2, 3, 4, 23])))
            elif attack_type == "insider_drift":
                events.at[idx, "resource_accessed"] = str(rng.choice(list(SENSITIVE_RESOURCES)))
                events.at[idx, "privilege_level"] = min(3, int(row["privilege_level"]) + 1)
                events.at[idx, "timestamp"] = campaign_anchor + timedelta(hours=pos * 8)

    for attack_type in attack_types:
        target = attack_budgets[attack_type]
        campaigns_total = max(3, campaigns_per_attack)
        events_per_campaign = max(2, target // campaigns_total)
        for campaign_idx in range(campaigns_total):
            split_name, split_start, split_end = windows[campaign_idx % len(windows)]
            attack_counter += 1
            attack_id = f"atk_{attack_type}_{split_name}_{attack_counter:05d}"
            window_mask = (ts >= split_start) & (ts < split_end)
            candidate = events.loc[window_mask].copy()
            if candidate.empty:
                continue
            if attack_type == "credential_stuffing":
                chosen = candidate.sample(n=min(events_per_campaign, len(candidate)), random_state=int(rng.integers(0, 1_000_000))).index.tolist()
            else:
                entity_id = str(rng.choice(candidate["entity_id"].unique()))
                entity_rows = candidate[candidate["entity_id"] == entity_id]
                if entity_rows.empty:
                    continue
                chosen = entity_rows.sample(n=min(events_per_campaign, len(entity_rows)), random_state=int(rng.integers(0, 1_000_000))).index.tolist()
            _apply(chosen, attack_type, attack_id, split_start, split_end)
    events = events.sort_values("timestamp").reset_index(drop=True)
    return events
