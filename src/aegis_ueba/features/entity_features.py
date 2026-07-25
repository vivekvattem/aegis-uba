from __future__ import annotations

import pandas as pd

from aegis_ueba.features.geographic import haversine_km, velocity_kmh


def add_entity_history_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy().sort_values(["entity_id", "timestamp"]).reset_index(drop=True)
    ts = pd.to_datetime(df["timestamp"])
    df["prev_timestamp"] = df.groupby("entity_id")["timestamp"].shift(1)
    df["prev_latitude"] = df.groupby("entity_id")["latitude"].shift(1)
    df["prev_longitude"] = df.groupby("entity_id")["longitude"].shift(1)
    df["prev_country"] = df.groupby("entity_id")["source_country"].shift(1)
    prev_ts = pd.to_datetime(df["prev_timestamp"])
    df["time_since_prev_hours"] = ((ts - prev_ts).dt.total_seconds() / 3600).fillna(9999.0)
    distances = []
    velocities = []
    for _, row in df.iterrows():
        if pd.isna(row["prev_latitude"]):
            distances.append(0.0)
            velocities.append(0.0)
        else:
            dist = haversine_km(float(row["prev_latitude"]), float(row["prev_longitude"]), float(row["latitude"]), float(row["longitude"]))
            distances.append(dist)
            velocities.append(velocity_kmh(dist, float(row["time_since_prev_hours"])))
    df["distance_from_prev_km"] = distances
    df["geo_velocity_kmh"] = velocities
    df["new_country_indicator"] = (df["source_country"] != df["prev_country"]).fillna(False).astype(int)

    new_resource = []
    new_fingerprint = []
    prior_resource_count = []
    prior_fingerprint_count = []
    for _, group in df.groupby("entity_id", sort=False):
        seen_resources: set[str] = set()
        seen_fingerprints: set[str] = set()
        for _, row in group.iterrows():
            resource = str(row["resource_accessed"])
            fingerprint = str(row["device_fingerprint"])
            new_resource.append(int(resource not in seen_resources))
            new_fingerprint.append(int(fingerprint not in seen_fingerprints))
            prior_resource_count.append(len(seen_resources))
            prior_fingerprint_count.append(len(seen_fingerprints))
            seen_resources.add(resource)
            seen_fingerprints.add(fingerprint)
    df["new_resource_indicator"] = new_resource
    df["new_fingerprint_indicator"] = new_fingerprint
    df["prior_resource_count"] = prior_resource_count
    df["prior_fingerprint_count"] = prior_fingerprint_count
    return df
