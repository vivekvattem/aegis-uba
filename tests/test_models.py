from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from aegis_ueba.models.attack_classifier import AttackClassifier
from aegis_ueba.models.gru_autoencoder import GruSequenceAutoencoder


def test_gru_scores_are_nonconstant() -> None:
    rng = np.random.default_rng(42)
    train = rng.normal(size=(32, 5, 6)).astype(np.float32)
    val = rng.normal(size=(16, 5, 6)).astype(np.float32)
    model = GruSequenceAutoencoder(6, 4, 1, 0.0, 0.001, 2, 8, 1)
    model.fit(train, val)
    scores = model.score(val)
    assert scores.max() > scores.min()


def test_attack_classifier_unknown_threshold() -> None:
    x = np.array([[0.0, 0.0], [0.1, 0.2], [10.0, 10.0], [10.1, 9.9]])
    y = np.array(["brute_force", "brute_force", "device_spoofing", "device_spoofing"])
    clf = AttackClassifier(20, 3, 42, 0.95).fit(x, y)
    labels, confidence = clf.predict(np.array([[5.0, 5.0]]))
    assert labels[0] == "unknown_anomaly"
    assert 0 <= confidence[0] <= 1
