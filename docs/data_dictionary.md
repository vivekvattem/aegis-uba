# Data Dictionary

Official fields are implemented in `src/aegis_ueba/schemas.py`.

- `entity_id`, `entity_type`, `timestamp`, `source_ip`, `geo_location`, `resource_accessed`, `auth_method`, `session_duration`, `command_sequence`, `device_fingerprint`, and `label` satisfy the core schema.
- Added fields include `role`, `event_id`, `session_id`, `auth_success`, `failed_attempt_count`, `source_country`, `latitude`, `longitude`, `bytes_uploaded`, `bytes_downloaded`, `protocol`, `port`, `privilege_level`, `response_status`, `destination_system`, `event_type`, `synthetic_attack_id`, `is_anomaly`, and `anomaly_type`.
- Ground-truth fields are excluded from inference datasets and model features.
