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
    return df
