from __future__ import annotations

REASON_LIBRARY = {
    "brute_force_pattern": "Repeated authentication failures were observed in a short window.",
    "impossible_travel": "The inferred travel speed between consecutive locations is unrealistic.",
    "sensitive_resource_access": "The event touched a sensitive or privileged resource.",
    "privileged_command_sequence": "The command sequence contains privileged administrative actions.",
    "device_spoofing_signal": "The device fingerprint does not match known trusted devices.",
    "upload_excess": "Outbound data volume exceeds the expected download-adjusted pattern.",
}
