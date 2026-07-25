from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.config import load_config
from aegis_ueba.data_generation.generator import generate_synthetic_dataset
from aegis_ueba.evaluation.validation import behavioural_signature_checks, dataset_summary


def test_dataset_summary_contains_required_entity_and_attack_types() -> None:
    config = load_config(ROOT / "configs" / "fast.yaml")
    events = generate_synthetic_dataset(config.data, config.project["seed"])
    summary = dataset_summary(events)
    assert {"user", "service_account", "edge_device"} <= set(summary["count_by_entity_type"].keys())
    assert "normal" in summary["count_by_anomaly_type"]


def test_behavioural_signatures_have_expected_markers() -> None:
    config = load_config(ROOT / "configs" / "fast.yaml")
    events = generate_synthetic_dataset(config.data, config.project["seed"])
    signatures = behavioural_signature_checks(events)
    assert signatures["brute_force"]["min_failed_attempt_count"] >= 8
    assert signatures["device_spoofing"]["spoofed_fingerprint_share"] > 0
    assert signatures["credential_stuffing"]["count"] > 0
