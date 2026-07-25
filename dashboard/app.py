from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

from components import render_metric_row
from styles import CYBER_CSS


ROOT = Path(__file__).resolve().parents[1]
LATEST_RUN = ROOT / "artifacts" / "latest_run.json"
if LATEST_RUN.exists():
    latest = json.loads(LATEST_RUN.read_text(encoding="utf-8"))
    ARTIFACT_ROOT = ROOT / latest["artifact_root"]
else:
    ARTIFACT_ROOT = ROOT / "artifacts" / "default"
SCORED_PATH = ARTIFACT_ROOT / "sample_alerts" / "scored_test_events.csv"
METRICS_PATH = ARTIFACT_ROOT / "metrics" / "metrics.json"
SAMPLE_ALERTS_PATH = ARTIFACT_ROOT / "sample_alerts" / "sample_alerts.json"

st.set_page_config(page_title="AegisUEBA", layout="wide")
st.markdown(CYBER_CSS, unsafe_allow_html=True)
st.title("AegisUEBA: AI-Powered Behavioral Anomaly Detection")

if not SCORED_PATH.exists():
    st.warning("No scored artifacts found yet. Run `python scripts/run_pipeline.py --config configs/fast.yaml` first.")
    st.stop()

frame = pd.read_csv(SCORED_PATH)
frame["timestamp"] = pd.to_datetime(frame["timestamp"])
demo_mode = st.sidebar.checkbox("Evaluation / demo mode", value=False, help="Reveal ground truth fields for demo and evaluation only.")
render_metric_row(frame)

tabs = st.tabs(["Security Overview", "Ranked Alert Queue", "Alert Investigation", "Entity Behaviour", "Model Performance", "Live Replay"])

with tabs[0]:
    st.subheader("Security Overview")
    st.plotly_chart(px.histogram(frame, x="risk_score", nbins=30, color="severity"), use_container_width=True)
    trend = frame.groupby(frame["timestamp"].dt.date)["risk_score"].mean().reset_index()
    st.plotly_chart(px.line(trend, x="timestamp", y="risk_score", title="Average risk over time"), use_container_width=True)

with tabs[1]:
    st.subheader("Ranked Alert Queue")
    severity = st.selectbox("Severity filter", ["all", "critical", "high", "medium", "low"])
    view = frame if severity == "all" else frame[frame["severity"] == severity]
    view = view.sort_values(["risk_score", "timestamp"], ascending=[False, False])
    cols = ["timestamp", "entity_id", "entity_type", "risk_score", "severity", "predicted_attack_type", "classifier_confidence", "reasons"]
    if demo_mode:
        cols.extend(["label", "is_anomaly"])
    st.dataframe(view[cols], use_container_width=True)
    st.download_button("Export filtered alerts CSV", view[cols].to_csv(index=False).encode("utf-8"), file_name="filtered_alerts.csv", mime="text/csv")

with tabs[2]:
    st.subheader("Alert Investigation")
    selected_event = st.selectbox("Event", frame.sort_values("risk_score", ascending=False)["event_id"].head(200))
    selected = frame[frame["event_id"] == selected_event].iloc[0]
    payload = selected.to_dict()
    if not demo_mode:
        payload.pop("label", None)
        payload.pop("is_anomaly", None)
        payload.pop("anomaly_type", None)
        payload.pop("synthetic_attack_id", None)
    st.json(payload)

with tabs[3]:
    st.subheader("Entity Behaviour")
    entity_id = st.selectbox("Entity", sorted(frame["entity_id"].unique()))
    entity_frame = frame[frame["entity_id"] == entity_id]
    st.dataframe(entity_frame[["timestamp", "resource_accessed", "risk_score", "cold_start", "drift_badge", "reasons"]], use_container_width=True)

with tabs[4]:
    st.subheader("Model Performance")
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        st.json(metrics)
    else:
        st.info("Evaluation metrics will appear after the pipeline runs.")
    if SAMPLE_ALERTS_PATH.exists():
        st.subheader("Sample Alerts By Attack Type")
        st.json(json.loads(SAMPLE_ALERTS_PATH.read_text(encoding="utf-8")))

with tabs[5]:
    st.subheader("Live Replay")
    replay_view = frame.sort_values("timestamp").tail(50)
    st.plotly_chart(px.line(replay_view, x="timestamp", y="risk_score", color="severity"), use_container_width=True)
    st.dataframe(replay_view[["timestamp", "entity_id", "risk_score", "severity", "predicted_attack_type"]], use_container_width=True)
