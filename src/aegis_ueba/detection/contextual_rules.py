from __future__ import annotations

import numpy as np
import pandas as pd


def contextual_score(row: pd.Series, velocity_threshold: float) -> tuple[float, list[dict[str, str | float]]]:
    reasons: list[dict[str, str | float]] = []
    score = 0.0
    if float(row.get("failed_attempt_count", 0)) >= 8:
        score += 0.35
        reasons.append({"code": "brute_force_pattern", "value": float(row["failed_attempt_count"])})
    if float(row.get("geo_velocity_kmh", 0.0)) > velocity_threshold:
        score += 0.35
        reasons.append({"code": "impossible_travel", "value": float(row["geo_velocity_kmh"])})
    if int(row.get("privilege_level", 0)) >= 3 and row.get("resource_accessed") in {"finance_db", "admin_console", "backup_server", "ot_controller"}:
        score += 0.2
        reasons.append({"code": "sensitive_resource_access", "value": str(row["resource_accessed"])})
    if "sudo_su" in str(row.get("command_sequence", "")) or "dump_db" in str(row.get("command_sequence", "")):
        score += 0.2
        reasons.append({"code": "privileged_command_sequence", "value": str(row["command_sequence"])})
    if "spoofed-fp" in str(row.get("device_fingerprint", "")):
        score += 0.3
        reasons.append({"code": "device_spoofing_signal", "value": str(row["device_fingerprint"])})
    if float(row.get("bytes_uploaded", 0.0)) > float(row.get("bytes_downloaded", 0.0)) * 1.5:
        score += 0.18
        reasons.append({"code": "upload_excess", "value": float(row["bytes_uploaded"])})
    return float(np.clip(score, 0.0, 1.0)), reasons
