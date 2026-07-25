from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from aegis_ueba.features.preprocessing import engineer_features
from aegis_ueba.schemas import REQUIRED_FIELDS


def dataset_summary(events: pd.DataFrame) -> dict:
    counts_by_type = events["entity_type"].value_counts().sort_index().to_dict()
    counts_by_label = events["label"].value_counts().sort_index().to_dict()
    null_counts = {field: int(events[field].isna().sum()) for field in REQUIRED_FIELDS}
    summary = {
        "total_event_count": int(len(events)),
        "normal_count": int((events["is_anomaly"] == 0).sum()),
        "anomaly_count": int((events["is_anomaly"] == 1).sum()),
        "anomaly_percentage": float(events["is_anomaly"].mean() * 100.0),
        "count_by_anomaly_type": counts_by_label,
        "count_by_entity_type": counts_by_type,
        "min_timestamp": str(pd.to_datetime(events["timestamp"]).min()),
        "max_timestamp": str(pd.to_datetime(events["timestamp"]).max()),
        "unique_entity_count": int(events["entity_id"].nunique()),
        "null_counts_required_fields": null_counts,
        "duplicate_event_id_count": int(events["event_id"].duplicated().sum()),
    }
    return summary


def behavioural_signature_checks(events: pd.DataFrame) -> dict[str, dict]:
    feat = engineer_features(events)
    brute_force = feat[feat["label"] == "brute_force"]
    impossible = feat[feat["label"] == "impossible_travel"]
    stuffing = feat[feat["label"] == "credential_stuffing"]
    lateral = feat[feat["label"] == "lateral_movement"]
    spoof = feat[feat["label"] == "device_spoofing"]
    exfil = feat[feat["label"] == "low_and_slow_exfiltration"].copy()
    insider = feat[feat["label"] == "insider_drift"].copy()
    exfil["off_hours"] = (~exfil["hour"].between(7, 19)).astype(int)

    stuffing_ip_targets = (
        stuffing.groupby("source_ip")["entity_id"].nunique().sort_values(ascending=False).head(3).to_dict()
        if not stuffing.empty
        else {}
    )
    return {
        "brute_force": {
            "count": int(len(brute_force)),
            "min_failed_attempt_count": int(brute_force["failed_attempt_count"].min()) if not brute_force.empty else 0,
            "max_events_last_15m": float(brute_force["events_last_15m"].max()) if not brute_force.empty else 0.0,
        },
        "impossible_travel": {
            "count": int(len(impossible)),
            "max_geo_velocity_kmh": float(impossible["geo_velocity_kmh"].max()) if not impossible.empty else 0.0,
            "median_geo_velocity_kmh": float(impossible["geo_velocity_kmh"].median()) if not impossible.empty else 0.0,
        },
        "credential_stuffing": {
            "count": int(len(stuffing)),
            "top_source_ip_entity_targets": stuffing_ip_targets,
        },
        "lateral_movement": {
            "count": int(len(lateral)),
            "sensitive_resource_share": float(lateral["resource_accessed"].isin({"finance_db", "admin_console", "backup_server", "ot_controller"}).mean()) if not lateral.empty else 0.0,
        },
        "device_spoofing": {
            "count": int(len(spoof)),
            "spoofed_fingerprint_share": float(spoof["device_fingerprint"].astype(str).str.contains("spoofed-fp").mean()) if not spoof.empty else 0.0,
        },
        "low_and_slow_exfiltration": {
            "count": int(len(exfil)),
            "mean_uploaded_bytes": float(exfil["bytes_uploaded"].mean()) if not exfil.empty else 0.0,
            "off_hours_share": float(exfil["off_hours"].mean()) if not exfil.empty else 0.0,
        },
        "insider_drift": {
            "count": int(len(insider)),
            "mean_privilege_level": float(insider["privilege_level"].mean()) if not insider.empty else 0.0,
        },
    }


def save_validation_artifacts(summary: dict, signatures: dict, root: str | Path) -> None:
    root = Path(root)
    metrics_dir = root / "artifacts" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    (metrics_dir / "dataset_summary.json").write_text(__import__("json").dumps(summary, indent=2), encoding="utf-8")
    (metrics_dir / "behavioural_signatures.json").write_text(__import__("json").dumps(signatures, indent=2), encoding="utf-8")
