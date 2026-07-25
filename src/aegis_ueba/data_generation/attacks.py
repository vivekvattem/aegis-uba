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
) -> pd.DataFrame:
    target_anomalies = max(1, int(len(events) * config["anomaly_rate"]))
    weights = config["attack_type_weights"]
    attack_types = list(weights.keys())
    probs = np.array(list(weights.values()), dtype=float)
    probs = probs / probs.sum()
    attack_counter = 0
    entity_events = defaultdict(list)
    for idx, row in events.iterrows():
        entity_events[row["entity_id"]].append(idx)

    anomaly_indices: set[int] = set()
    while len(anomaly_indices) < target_anomalies:
        attack_type = str(rng.choice(attack_types, p=probs))
        attack_counter += 1
        attack_id = f"atk_{attack_counter:05d}"
        if attack_type == "credential_stuffing":
            candidate_indices = list(rng.choice(events.index, size=min(8, len(events)), replace=False))
        else:
            entity_id = str(rng.choice(events["entity_id"].unique()))
            entity_idx = entity_events[entity_id]
            candidate_indices = [int(rng.choice(entity_idx))]
        for idx in candidate_indices:
            row = events.loc[idx]
            if idx in anomaly_indices:
                continue
            anomaly_indices.add(idx)
            events.at[idx, "is_anomaly"] = 1
            events.at[idx, "synthetic_attack_id"] = attack_id
            events.at[idx, "label"] = attack_type
            events.at[idx, "anomaly_type"] = attack_type
            if attack_type == "brute_force":
                events.at[idx, "auth_success"] = 0
                events.at[idx, "failed_attempt_count"] = int(rng.integers(8, 20))
                events.at[idx, "event_type"] = "login"
                events.at[idx, "session_duration"] = float(rng.uniform(1, 5))
            elif attack_type == "impossible_travel":
                country, city, lat, lon = _sample_far_location(rng, row["source_country"])
                events.at[idx, "source_country"] = country
                events.at[idx, "geo_location"] = city
                events.at[idx, "latitude"] = lat
                events.at[idx, "longitude"] = lon
            elif attack_type == "credential_stuffing":
                events.at[idx, "auth_success"] = 0
                events.at[idx, "failed_attempt_count"] = int(rng.integers(5, 15))
                events.at[idx, "source_ip"] = "185.199.110.153"
                events.at[idx, "event_type"] = "login"
            elif attack_type == "lateral_movement":
                events.at[idx, "resource_accessed"] = str(rng.choice(list(SENSITIVE_RESOURCES)))
                events.at[idx, "privilege_level"] = 3
                events.at[idx, "command_sequence"] = "netstat|ssh|sudo_su|vault_read"
                events.at[idx, "destination_system"] = f"internal-{int(rng.integers(100, 999))}"
            elif attack_type == "device_spoofing":
                events.at[idx, "device_fingerprint"] = f"spoofed-fp-{int(rng.integers(1000, 9999))}"
                events.at[idx, "protocol"] = str(rng.choice(["rdp", "ssh", "smb"]))
            elif attack_type == "low_and_slow_exfiltration":
                events.at[idx, "bytes_uploaded"] = float(row["bytes_uploaded"]) * rng.uniform(3.0, 6.0)
                events.at[idx, "event_type"] = "data_transfer"
                events.at[idx, "session_duration"] = float(row["session_duration"]) * rng.uniform(1.2, 2.2)
            elif attack_type == "insider_drift":
                events.at[idx, "resource_accessed"] = str(rng.choice(list(SENSITIVE_RESOURCES)))
                events.at[idx, "privilege_level"] = min(3, int(row["privilege_level"]) + 1)
    events = events.sort_values("timestamp").reset_index(drop=True)
    return events
