from __future__ import annotations

import pandas as pd
import streamlit as st


def render_metric_row(frame: pd.DataFrame) -> None:
    total = len(frame)
    alerts = int((frame["risk_score"] >= 60).sum())
    critical = int((frame["severity"] == "critical").sum())
    cols = st.columns(4)
    cols[0].metric("Total events", total)
    cols[1].metric("Alerts", alerts)
    cols[2].metric("Critical", critical)
    cols[3].metric("Alert rate", f"{(alerts / max(1, total)):.2%}")
