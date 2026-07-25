from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

from aegis_ueba.features.entity_features import add_entity_history_features
from aegis_ueba.features.temporal import add_temporal_columns


FEATURE_EXCLUDE = {"label", "is_anomaly", "anomaly_type", "synthetic_attack_id", "event_id", "session_id", "timestamp", "prev_timestamp"}


@dataclass
class PreprocessingArtifacts:
    transformer: ColumnTransformer
    feature_columns: list[str]

    def save(self, path: str) -> None:
        joblib.dump(self, path)


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = add_temporal_columns(frame)
    df = add_entity_history_features(df)
    df["upload_download_ratio"] = df["bytes_uploaded"] / (df["bytes_downloaded"] + 1.0)
    df["sequence_length"] = df["command_sequence"].fillna("").map(lambda x: len(str(x).split("|")))
    df["rare_command_indicator"] = df["command_sequence"].fillna("").map(lambda x: int("sudo_su" in str(x) or "dump_db" in str(x)))
    df["auth_failure_indicator"] = 1 - df["auth_success"]
    df["successful_after_failures"] = ((df["auth_success"] == 1) & (df["failed_attempt_count"] >= 3)).astype(int)
    df["off_hours_indicator"] = (~df["hour"].between(7, 19)).astype(int)
    for window in [5, 15, 60, 1440]:
        counts = []
        for _, group in df.groupby("entity_id", sort=False):
            temp = group[["timestamp"]].copy()
            temp["counter"] = 1
            temp = temp.set_index(pd.to_datetime(temp["timestamp"]))
            rolled = temp["counter"].rolling(f"{window}min").sum()
            counts.append(pd.Series(rolled.to_numpy(), index=group.index))
        df[f"events_last_{window}m"] = pd.concat(counts).sort_index().fillna(1.0)
    ip_entity_spread = []
    ip_failure_burst = []
    for _, group in df.sort_values("timestamp").groupby("source_ip", sort=False):
        seen_entities: set[str] = set()
        failure_count = 0
        for _, row in group.iterrows():
            seen_entities.add(str(row["entity_id"]))
            ip_entity_spread.append(len(seen_entities))
            failure_count = failure_count + 1 if int(row["auth_success"]) == 0 else max(0, failure_count - 1)
            ip_failure_burst.append(failure_count)
    df["distinct_entities_seen_by_ip"] = ip_entity_spread
    df["ip_failure_burst"] = ip_failure_burst
    rolling_upload = []
    for _, group in df.groupby("entity_id", sort=False):
        cumulative = 0.0
        for _, row in group.iterrows():
            if int(row["off_hours_indicator"]) == 1:
                cumulative += float(row["bytes_uploaded"])
            rolling_upload.append(cumulative)
    df["cumulative_off_hours_upload"] = rolling_upload
    return df


def build_transformer(frame: pd.DataFrame) -> PreprocessingArtifacts:
    feature_columns = [col for col in frame.columns if col not in FEATURE_EXCLUDE]
    numeric = [col for col in feature_columns if pd.api.types.is_numeric_dtype(frame[col])]
    categorical = [col for col in feature_columns if col not in numeric]
    transformer = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)), ("scaler", StandardScaler())]), categorical),
        ]
    )
    transformer.fit(frame[feature_columns])
    return PreprocessingArtifacts(transformer=transformer, feature_columns=feature_columns)


def transform_features(frame: pd.DataFrame, artifacts: PreprocessingArtifacts) -> np.ndarray:
    return artifacts.transformer.transform(frame[artifacts.feature_columns])
