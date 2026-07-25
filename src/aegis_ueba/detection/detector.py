from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from aegis_ueba.detection.contextual_rules import contextual_score
from aegis_ueba.detection.risk_engine import combine_scores, severity_band
from aegis_ueba.explainability.explanations import build_explanations
from aegis_ueba.features.preprocessing import build_transformer, engineer_features, transform_features
from aegis_ueba.features.sequence_builder import build_sequences
from aegis_ueba.models.attack_classifier import AttackClassifier
from aegis_ueba.models.calibration import percentile_threshold
from aegis_ueba.models.gru_autoencoder import GruSequenceAutoencoder
from aegis_ueba.models.isolation_baseline import IsolationBaseline
from aegis_ueba.models.statistical_baseline import StatisticalBaseline
from aegis_ueba.profiles.drift_manager import DriftManager
from aegis_ueba.profiles.entity_profile import EntityProfileStore
from aegis_ueba.profiles.peer_profile import PeerProfileStore
from aegis_ueba.streaming.replay import replay_events


@dataclass
class DetectionArtifacts:
    threshold: float
    sequence_threshold: float
    transformer_path: Path
    bundle_path: Path


class HybridDetector:
    def __init__(self, config: dict, seed: int) -> None:
        self.config = config
        self.seed = seed
        self.statistical = StatisticalBaseline(config["features"]["peer_group_columns"])
        self.entity_store = EntityProfileStore()
        self.peer_store = PeerProfileStore(config["features"]["peer_group_columns"])
        self.isolation = None
        self.gru = None
        self.classifier = None
        self.transformer = None
        self.threshold = 0.5
        self.sequence_threshold = 0.5
        self.drift = DriftManager(
            safe_threshold=config["risk"]["safe_profile_update_threshold"],
            alpha=config["drift"]["ewma_alpha"],
            min_trusted_observations=config["drift"]["min_trusted_observations"],
        )

    def fit(self, train_df: pd.DataFrame, val_df: pd.DataFrame) -> dict[str, float]:
        train_feat = engineer_features(train_df)
        val_feat = engineer_features(val_df)
        normal_train = train_feat[train_feat["is_anomaly"] == 0].copy()
        self.transformer = build_transformer(normal_train)
        x_train = transform_features(normal_train, self.transformer)
        x_val = transform_features(val_feat, self.transformer)
        self.entity_store.fit(normal_train)
        self.peer_store.fit(normal_train)
        self.statistical.fit(normal_train)
        self.isolation = IsolationBaseline(self.config["models"]["isolation_contamination"], self.seed).fit(x_train)
        seq_len = self.config["features"]["sequence_length"]
        train_seq, _ = build_sequences(x_train, normal_train["entity_id"].tolist(), seq_len)
        val_seq, _ = build_sequences(x_val, val_feat["entity_id"].tolist(), seq_len)
        if len(train_seq) == 0 or len(val_seq) == 0:
            train_seq = np.zeros((1, seq_len, x_train.shape[1]))
            val_seq = np.zeros((1, seq_len, x_train.shape[1]))
        self.gru = GruSequenceAutoencoder(
            input_dim=x_train.shape[1],
            hidden_dim=self.config["models"]["gru_hidden_dim"],
            num_layers=self.config["models"]["gru_num_layers"],
            dropout=self.config["models"]["gru_dropout"],
            lr=self.config["models"]["gru_lr"],
            epochs=self.config["models"]["gru_epochs"],
            batch_size=self.config["models"]["gru_batch_size"],
            patience=self.config["models"]["early_stopping_patience"],
        )
        gru_result = self.gru.fit(train_seq, val_seq)
        seq_scores = self.gru.score(val_seq)
        self.sequence_threshold = percentile_threshold(seq_scores, self.config["risk"]["threshold_percentile"])
        suspicious = train_feat[train_feat["label"] != "normal"].copy()
        if suspicious.empty:
            suspicious = train_feat[train_feat["is_anomaly"] == 1].copy()
        if suspicious.empty:
            suspicious = val_feat[val_feat["is_anomaly"] == 1].copy()
        if suspicious.empty:
            suspicious = val_feat.copy()
        x_cls = transform_features(suspicious, self.transformer)
        y_cls = suspicious["label"].to_numpy()
        self.classifier = AttackClassifier(
            n_estimators=self.config["models"]["classifier_estimators"],
            max_depth=self.config["models"]["classifier_max_depth"],
            random_state=self.seed,
            unknown_threshold=self.config["models"]["classifier_unknown_threshold"],
        ).fit(x_cls, y_cls)
        val_scored = self.score(val_df, update_profiles=False)
        self.threshold = float(np.quantile(val_scored["risk_score"], self.config["risk"]["threshold_percentile"]))
        return {"gru_train_loss": gru_result.train_loss, "gru_val_loss": gru_result.val_loss, "risk_threshold": self.threshold}

    def score(self, frame: pd.DataFrame, update_profiles: bool = False) -> pd.DataFrame:
        feat = engineer_features(frame)
        matrix = transform_features(feat, self.transformer)
        statistical_scores = self.statistical.score_frame(feat)
        isolation_scores = self.isolation.score(matrix)
        seq_len = self.config["features"]["sequence_length"]
        sequences, seq_indices = build_sequences(matrix, feat["entity_id"].tolist(), seq_len)
        seq_scores = np.zeros(len(feat))
        if len(sequences) > 0:
            seq_scores_at_idx = self.gru.score(sequences)
            for idx, score in zip(seq_indices, seq_scores_at_idx):
                seq_scores[idx] = score
        labels, confidence = self.classifier.predict(matrix)
        outputs = []
        for i, row in feat.iterrows():
            entity_meta = self.entity_store.score(row)
            peer_dev = self.peer_store.score(row)
            contextual, reasons = contextual_score(row, self.config["features"]["velocity_kmh_threshold"])
            auth_severity = min(1.0, float(row["failed_attempt_count"]) / 10.0)
            resource_criticality = 1.0 if row["resource_accessed"] in {"finance_db", "admin_console", "backup_server", "ot_controller"} else 0.2
            components = {
                "entity_deviation": entity_meta["entity_deviation"],
                "peer_deviation": peer_dev,
                "sequence_anomaly": max(float(seq_scores[i]), float(isolation_scores[i]), float(statistical_scores[i])),
                "contextual_evidence": contextual,
                "auth_severity": auth_severity,
                "resource_criticality": resource_criticality,
                "classifier_confidence": float(confidence[i]),
            }
            risk = combine_scores(components, self.config["risk"]["weights"])
            explanation_text = build_explanations(reasons)
            outputs.append(
                {
                    **row.to_dict(),
                    "statistical_score": float(statistical_scores[i]),
                    "isolation_score": float(isolation_scores[i]),
                    "sequence_score": float(seq_scores[i]),
                    "peer_deviation": float(peer_dev),
                    "entity_deviation": float(entity_meta["entity_deviation"]),
                    "contextual_score": float(contextual),
                    "risk_score": float(risk),
                    "severity": severity_band(risk),
                    "predicted_attack_type": str(labels[i]),
                    "classifier_confidence": float(confidence[i]),
                    "cold_start": int(entity_meta["cold_start"]),
                    "drift_badge": "warming" if entity_meta["cold_start"] else "stable",
                    "reasons": " | ".join(explanation_text),
                }
            )
            if update_profiles:
                decision = self.drift.evaluate_update(row, risk, self.entity_store)
                if decision.should_update:
                    self.entity_store.update(row, alpha=self.config["drift"]["ewma_alpha"])
                    self.peer_store.update(row)
        return pd.DataFrame(outputs)

    def save(self, root: str | Path) -> DetectionArtifacts:
        root = Path(root)
        model_dir = root / "artifacts" / "models"
        pre_dir = root / "artifacts" / "preprocessors"
        model_dir.mkdir(parents=True, exist_ok=True)
        pre_dir.mkdir(parents=True, exist_ok=True)
        bundle = {
            "config": self.config,
            "seed": self.seed,
            "statistical": self.statistical,
            "entity_store": self.entity_store,
            "peer_store": self.peer_store,
            "isolation": self.isolation,
            "gru": self.gru,
            "classifier": self.classifier,
            "threshold": self.threshold,
            "sequence_threshold": self.sequence_threshold,
        }
        transformer_path = pre_dir / "transformer.joblib"
        bundle_path = model_dir / "detector_bundle.joblib"
        joblib.dump(self.transformer, transformer_path)
        joblib.dump(bundle, bundle_path)
        return DetectionArtifacts(
            threshold=self.threshold,
            sequence_threshold=self.sequence_threshold,
            transformer_path=transformer_path,
            bundle_path=bundle_path,
        )

    def replay(self, scored_frame: pd.DataFrame) -> dict[str, float]:
        metrics = replay_events(scored_frame)
        return {
            "avg_latency_ms": metrics.avg_latency_ms,
            "p50_latency_ms": metrics.p50_latency_ms,
            "p95_latency_ms": metrics.p95_latency_ms,
            "events_per_second": metrics.events_per_second,
        }
