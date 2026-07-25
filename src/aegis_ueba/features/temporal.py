from __future__ import annotations

import math

import pandas as pd


def add_temporal_columns(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    ts = pd.to_datetime(df["timestamp"])
    df["hour"] = ts.dt.hour
    df["day_of_week"] = ts.dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["hour_sin"] = df["hour"].map(lambda x: math.sin(2 * math.pi * x / 24))
    df["hour_cos"] = df["hour"].map(lambda x: math.cos(2 * math.pi * x / 24))
    df["weekday_sin"] = df["day_of_week"].map(lambda x: math.sin(2 * math.pi * x / 7))
    df["weekday_cos"] = df["day_of_week"].map(lambda x: math.cos(2 * math.pi * x / 7))
    return df
