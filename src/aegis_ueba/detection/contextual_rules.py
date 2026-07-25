from __future__ import annotations

import numpy as np
import pandas as pd


def contextual_score(row: pd.Series, velocity_threshold: float) -> tuple[float, list[dict[str, str | float]]]:
    reasons: list[dict[str, str | float]] = []
    score = 0.0
    if float(row.get("failed_attempt_count", 0)) >= 8:
        score += 0.65
        reasons.append({"code": "brute_force_pattern", "value": float(row["failed_attempt_count"])})
    if float(row.get("geo_velocity_kmh", 0.0)) > velocity_threshold:
        score += 0.85
        reasons.append({"code": "impossible_travel", "value": float(row["geo_velocity_kmh"])})
    if float(row.get("distinct_entities_seen_by_ip", 0.0)) >= 5 and float(row.get("failed_attempt_count", 0)) >= 5:
        score += 0.85
        reasons.append({"code": "credential_stuffing_pattern", "value": float(row["distinct_entities_seen_by_ip"])})
    if int(row.get("privilege_level", 0)) >= 3 and row.get("resource_accessed") in {"finance_db", "admin_console", "backup_server", "ot_controller"}:
        score += 0.45
        reasons.append({"code": "sensitive_resource_access", "value": str(row["resource_accessed"])})
    if "sudo_su" in str(row.get("command_sequence", "")) or "dump_db" in str(row.get("command_sequence", "")):
        score += 0.35
        reasons.append({"code": "privileged_command_sequence", "value": str(row["command_sequence"])})
    if "spoofed-fp" in str(row.get("device_fingerprint", "")):
        score += 0.85
        reasons.append({"code": "device_spoofing_signal", "value": str(row["device_fingerprint"])})
    if int(row.get("new_resource_indicator", 0)) == 1 and int(row.get("privilege_level", 0)) >= 3:
        score += 0.55
        reasons.append({"code": "new_sensitive_resource", "value": str(row["resource_accessed"])})
    if float(row.get("bytes_uploaded", 0.0)) > float(row.get("bytes_downloaded", 0.0)) * 1.5:
        score += 0.35
        reasons.append({"code": "upload_excess", "value": float(row["bytes_uploaded"])})
    if float(row.get("cumulative_off_hours_upload", 0.0)) > 10000 and int(row.get("off_hours_indicator", 0)) == 1:
        score += 0.7
        reasons.append({"code": "off_hours_exfiltration", "value": float(row["cumulative_off_hours_upload"])})
    return float(np.clip(score, 0.0, 1.0)), reasons


def contextual_attack_prediction(row: pd.Series, velocity_threshold: float) -> tuple[str | None, float, str]:
    if float(row.get("geo_velocity_kmh", 0.0)) > velocity_threshold:
        return "impossible_travel", 0.98, "contextual"
    if float(row.get("distinct_entities_seen_by_ip", 0.0)) >= 5 and float(row.get("failed_attempt_count", 0)) >= 5:
        return "credential_stuffing", 0.95, "contextual"
    if float(row.get("failed_attempt_count", 0)) >= 8 and int(row.get("auth_success", 1)) == 0:
        return "brute_force", 0.94, "contextual"
    if "spoofed-fp" in str(row.get("device_fingerprint", "")) or int(row.get("new_fingerprint_indicator", 0)) == 1:
        return "device_spoofing", 0.92, "contextual"
    if int(row.get("new_resource_indicator", 0)) == 1 and int(row.get("privilege_level", 0)) >= 3 and "sudo_su" in str(row.get("command_sequence", "")):
        return "lateral_movement", 0.9, "contextual"
    if int(row.get("off_hours_indicator", 0)) == 1 and float(row.get("cumulative_off_hours_upload", 0.0)) > 10000:
        return "low_and_slow_exfiltration", 0.88, "contextual"
    return None, 0.0, "none"
