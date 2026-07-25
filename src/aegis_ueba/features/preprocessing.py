from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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
    for window in [5, 15, 60, 1440]:
        counts = []
        for _, group in df.groupby("entity_id", sort=False):
            temp = group[["timestamp"]].copy()
            temp["counter"] = 1
            temp = temp.set_index(pd.to_datetime(temp["timestamp"]))
            rolled = temp["counter"].rolling(f"{window}min").sum()
            counts.append(pd.Series(rolled.to_numpy(), index=group.index))
        df[f"events_last_{window}m"] = pd.concat(counts).sort_index().fillna(1.0)
    return df


def build_transformer(frame: pd.DataFrame) -> PreprocessingArtifacts:
    feature_columns = [col for col in frame.columns if col not in FEATURE_EXCLUDE]
    numeric = [col for col in feature_columns if pd.api.types.is_numeric_dtype(frame[col])]
    categorical = [col for col in feature_columns if col not in numeric]
    transformer = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ]
    )
    transformer.fit(frame[feature_columns])
    return PreprocessingArtifacts(transformer=transformer, feature_columns=feature_columns)


def transform_features(frame: pd.DataFrame, artifacts: PreprocessingArtifacts) -> np.ndarray:
    return artifacts.transformer.transform(frame[artifacts.feature_columns])
