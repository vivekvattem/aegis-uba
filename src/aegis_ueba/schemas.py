from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EntityType = Literal["user", "service_account", "edge_device"]
AuthMethod = Literal["password", "token", "certificate", "biometric"]


class EventRecord(BaseModel):
    event_id: str
    session_id: str
    entity_id: str
    entity_type: EntityType
    role: str
    timestamp: datetime
    source_ip: str
    source_country: str
    geo_location: str
    latitude: float
    longitude: float
    resource_accessed: str
    destination_system: str
    auth_method: AuthMethod
    auth_success: int
    failed_attempt_count: int = Field(ge=0)
    session_duration: float = Field(ge=0.0)
    command_sequence: str
    device_fingerprint: str
    protocol: str
    port: int
    privilege_level: int
    response_status: int
    event_type: str
    bytes_uploaded: float = Field(ge=0.0)
    bytes_downloaded: float = Field(ge=0.0)
    label: str
    is_anomaly: int
    anomaly_type: str
    synthetic_attack_id: str | None = None


REQUIRED_FIELDS = list(EventRecord.model_fields.keys())
