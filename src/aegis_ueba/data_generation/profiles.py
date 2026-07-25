from __future__ import annotations

from dataclasses import dataclass

import numpy as np


COUNTRIES = [
    ("US", "New York", 40.7128, -74.0060),
    ("US", "Austin", 30.2672, -97.7431),
    ("GB", "London", 51.5072, -0.1276),
    ("DE", "Berlin", 52.5200, 13.4050),
    ("IN", "Bengaluru", 12.9716, 77.5946),
    ("SG", "Singapore", 1.3521, 103.8198),
    ("AU", "Sydney", -33.8688, 151.2093),
]

ROLES = {
    "user": ["analyst", "engineer", "finance", "operator", "support"],
    "service_account": ["batch_job", "integration", "backup", "deployer"],
    "edge_device": ["plc", "sensor", "gateway", "camera"],
}

PROTOCOLS = ["ssh", "https", "mqtt", "rdp", "smb", "modbus", "opcua"]
AUTH_METHODS = ["password", "token", "certificate", "biometric"]
RESOURCES = [
    "crm_api",
    "finance_db",
    "engineering_repo",
    "vpn_gateway",
    "hr_portal",
    "ot_controller",
    "iot_broker",
    "shared_drive",
    "admin_console",
    "backup_server",
    "source_code",
    "warehouse_system",
]
SENSITIVE_RESOURCES = {"finance_db", "admin_console", "backup_server", "ot_controller"}
COMMAND_POOLS = {
    "low": ["ls", "cat", "pwd", "curl", "ping", "read_tag"],
    "medium": ["scp", "git_pull", "service_status", "netstat", "write_tag"],
    "high": ["sudo_su", "useradd", "iptables", "dump_db", "restart_plc", "vault_read"],
}


@dataclass
class EntityProfile:
    entity_id: str
    entity_type: str
    role: str
    home_country: str
    home_city: str
    latitude: float
    longitude: float
    source_ip_prefix: str
    preferred_auth: str
    known_fingerprints: list[str]
    common_resources: list[str]
    common_protocols: list[str]
    common_ports: list[int]
    typical_hours: list[int]
    weekend_activity_rate: float
    median_duration: float
    median_upload: float
    median_download: float
    privilege_level: int
    command_pool: list[str]


def _ip_prefix(entity_type: str, rng: np.random.Generator) -> str:
    ranges = {
        "user": "10.10",
        "service_account": "10.20",
        "edge_device": "10.30",
    }
    return f"{ranges[entity_type]}.{int(rng.integers(1, 255))}"


def build_entity_profiles(config: dict, rng: np.random.Generator) -> list[EntityProfile]:
    entities = config["entities"]
    mix = config["entity_type_mix"]
    types = list(mix.keys())
    probs = np.array(list(mix.values()), dtype=float)
    probs = probs / probs.sum()
    profiles: list[EntityProfile] = []
    for idx in range(entities):
        entity_type = str(rng.choice(types, p=probs))
        role = str(rng.choice(ROLES[entity_type]))
        country, city, lat, lon = COUNTRIES[int(rng.integers(0, len(COUNTRIES)))]
        resource_count = int(rng.integers(2, 5)) if entity_type == "edge_device" else int(rng.integers(3, 6))
        resources = list(rng.choice(RESOURCES, size=resource_count, replace=False))
        protocols = list(rng.choice(PROTOCOLS, size=int(rng.integers(1, 3)), replace=False))
        ports = [443 if "https" in protocols else 22]
        ports.extend(8883 if p == "mqtt" else 3389 if p == "rdp" else 502 if p == "modbus" else 4840 if p == "opcua" else 445 if p == "smb" else 22 for p in protocols)
        hour_anchor = int(rng.integers(6, 11)) if entity_type == "user" else int(rng.integers(0, 24))
        typical_hours = sorted({(hour_anchor + offset) % 24 for offset in rng.choice(range(10), size=4, replace=False)})
        privilege_level = 3 if role in {"deployer", "gateway", "operator"} else 2 if entity_type != "user" else 1
        command_level = "high" if privilege_level == 3 else "medium" if privilege_level == 2 else "low"
        profiles.append(
            EntityProfile(
                entity_id=f"{entity_type[:2]}_{idx:04d}",
                entity_type=entity_type,
                role=role,
                home_country=country,
                home_city=city,
                latitude=float(lat),
                longitude=float(lon),
                source_ip_prefix=_ip_prefix(entity_type, rng),
                preferred_auth=str(rng.choice(AUTH_METHODS)),
                known_fingerprints=[f"{entity_type}-{role}-fp-{int(rng.integers(100, 999))}" for _ in range(2)],
                common_resources=resources,
                common_protocols=protocols,
                common_ports=sorted(set(int(p) for p in ports)),
                typical_hours=typical_hours,
                weekend_activity_rate=float(rng.uniform(0.1, 0.6)),
                median_duration=float(rng.uniform(5, 120)),
                median_upload=float(rng.uniform(10, 4000)),
                median_download=float(rng.uniform(20, 8000)),
                privilege_level=privilege_level,
                command_pool=COMMAND_POOLS[command_level],
            )
        )
    return profiles
