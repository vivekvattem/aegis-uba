from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

from components import (
    SEVERITY_ORDER,
    build_attack_distribution_chart,
    empty_state,
    format_table,
    human_label,
    parse_structured,
    render_budget_section,
    render_metric_row,
    severity_color_map,
)
from styles import CYBER_CSS


ROOT = Path(__file__).resolve().parents[1]
LATEST_RUN = ROOT / "artifacts" / "latest_run.json"
DEFAULT_ARTIFACT_ROOT = ROOT / "artifacts" / "default"
if DEFAULT_ARTIFACT_ROOT.exists():
    ARTIFACT_ROOT = DEFAULT_ARTIFACT_ROOT
    latest = {"artifact_root": "artifacts/default", "run_name": "default"}
elif LATEST_RUN.exists():
    latest = json.loads(LATEST_RUN.read_text(encoding="utf-8"))
    ARTIFACT_ROOT = ROOT / latest["artifact_root"]
else:
    ARTIFACT_ROOT = DEFAULT_ARTIFACT_ROOT
    latest = {"artifact_root": "artifacts/default", "run_name": "default"}
SCORED_PATH = ARTIFACT_ROOT / "sample_alerts" / "scored_test_events.csv"
METRICS_PATH = ARTIFACT_ROOT / "metrics" / "metrics.json"
SAMPLE_ALERTS_PATH = ARTIFACT_ROOT / "sample_alerts" / "sample_alerts.json"
MODEL_BUNDLE_PATH = ARTIFACT_ROOT / "models" / "detector_bundle.joblib"

st.set_page_config(page_title="AegisUEBA", layout="wide", initial_sidebar_state="collapsed")
st.markdown(CYBER_CSS, unsafe_allow_html=True)
st.title("AegisUEBA: AI-Powered Behavioral Anomaly Detection")

if not SCORED_PATH.exists():
    st.warning("No scored artifacts found yet. Run `python scripts/run_pipeline.py --config configs/fast.yaml` first.")
    st.stop()

frame = pd.read_csv(SCORED_PATH)
frame["timestamp"] = pd.to_datetime(frame["timestamp"])
metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else {}
run_name = latest["run_name"] if LATEST_RUN.exists() else "default"
run_timestamp = pd.Timestamp(MODEL_BUNDLE_PATH.stat().st_mtime, unit="s").strftime("%Y-%m-%d %H:%M") if MODEL_BUNDLE_PATH.exists() else "Not available"

st.sidebar.markdown("### Filters")
demo_mode = st.sidebar.checkbox(
    "Evaluation / Demo mode",
    value=False,
    help="Demo mode reveals synthetic ground truth fields that are hidden in normal analyst mode.",
)
timestamp_min = frame["timestamp"].min().date()
timestamp_max = frame["timestamp"].max().date()
date_range = st.sidebar.date_input("Time range", value=(timestamp_min, timestamp_max), help="Filter the chronological test split by date.")
entity_types = ["All"] + sorted(frame["entity_type"].dropna().unique().tolist()) if "entity_type" in frame.columns else ["All"]
severities = ["All"] + [sev.title() for sev in SEVERITY_ORDER if sev in set(frame["severity"].dropna().str.lower())] if "severity" in frame.columns else ["All"]
attack_types = ["All"] + sorted(frame["predicted_attack_type"].dropna().unique().tolist()) if "predicted_attack_type" in frame.columns else ["All"]
entity_type_filter = st.sidebar.selectbox("Entity type", entity_types)
severity_filter = st.sidebar.selectbox("Severity", severities)
attack_filter = st.sidebar.selectbox("Predicted attack type", attack_types)

filtered = frame.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[(filtered["timestamp"].dt.date >= start_date) & (filtered["timestamp"].dt.date <= end_date)]
if entity_type_filter != "All" and "entity_type" in filtered.columns:
    filtered = filtered[filtered["entity_type"] == entity_type_filter]
if severity_filter != "All" and "severity" in filtered.columns:
    filtered = filtered[filtered["severity"].str.lower() == severity_filter.lower()]
if attack_filter != "All" and "predicted_attack_type" in filtered.columns:
    filtered = filtered[filtered["predicted_attack_type"] == attack_filter]

st.markdown(
    f"<div class='run-caption'>Model run: {run_name} · Chronological test split · "
    f"{'Synthetic ground truth visible' if demo_mode else 'Ground truth hidden'}</div>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<div class='subtle-caption'>Default evaluation run · {int(metrics.get('total_event_count', len(frame))):,} total events · "
    f"{len(frame):,} chronological test events · Artifact updated {run_timestamp}</div>",
    unsafe_allow_html=True,
)

render_metric_row(filtered, metrics)
render_budget_section(metrics)

if filtered.empty:
    empty_state("No events match the selected filters.")

tabs = st.tabs(["Security Overview", "Ranked Alert Queue", "Alert Investigation", "Entity Behaviour", "Model Performance", "Live Replay"])

with tabs[0]:
    st.subheader("Security Overview")
    if filtered.empty:
        empty_state("No events match the selected filters.")
    else:
        st.plotly_chart(
            px.histogram(
                filtered,
                x="risk_score",
                nbins=30,
                color="severity",
                category_orders={"severity": SEVERITY_ORDER},
                color_discrete_map=severity_color_map(),
                labels={"risk_score": "Risk score", "severity": "Severity"},
                title="Event distribution by risk score and severity",
                height=360,
            ),
            use_container_width=True,
        )
        trend = filtered.groupby(filtered["timestamp"].dt.date)["risk_score"].mean().reset_index()
        st.plotly_chart(
            px.line(
                trend,
                x="timestamp",
                y="risk_score",
                labels={"timestamp": "Date", "risk_score": "Risk score"},
                title="Average risk over time",
                height=320,
            ),
            use_container_width=True,
        )
        attack_chart = build_attack_distribution_chart(filtered[filtered["risk_score"] >= float(metrics.get("risk_threshold", 0.0))])
        if attack_chart is not None:
            attack_chart.update_layout(margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(attack_chart, use_container_width=True)

with tabs[1]:
    st.subheader("Ranked Alert Queue")
    if filtered.empty:
        empty_state("No events match the selected filters.")
    else:
        view = filtered.sort_values(["risk_score", "timestamp"], ascending=[False, False])
        cols = ["timestamp", "entity_id", "entity_type", "risk_score", "severity", "predicted_attack_type", "classifier_confidence", "reasons"]
        if demo_mode:
            cols.extend(["label", "is_anomaly"])
        display = format_table(view, cols)
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.download_button("Export filtered alerts CSV", display.to_csv(index=False).encode("utf-8"), file_name="filtered_alerts.csv", mime="text/csv")

with tabs[2]:
    st.subheader("Alert Investigation")
    preferred = filtered[filtered["predicted_attack_type"].isin(["device_spoofing", "lateral_movement", "low_and_slow_exfiltration"])] if "predicted_attack_type" in filtered.columns else filtered
    options_source = preferred if not preferred.empty else filtered
    if options_source.empty:
        empty_state("No events match the selected filters.")
    else:
        selected_event = st.selectbox("Select alert", options_source.sort_values("risk_score", ascending=False)["event_id"].head(200))
        selected = filtered[filtered["event_id"] == selected_event].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Entity", f"{selected.get('entity_id', 'Not available')}")
        c2.metric("Risk score", f"{float(selected.get('risk_score', 0.0)):.2f}")
        c3.metric("Severity", str(selected.get("severity", "Not available")).title())
        st.caption(
            f"Entity type: {selected.get('entity_type', 'Not available')} · "
            f"Timestamp: {selected.get('timestamp', 'Not available')} · "
            f"Predicted attack type: {selected.get('predicted_attack_type', 'Not available')} · "
            f"Prediction confidence: {float(selected.get('classifier_confidence', 0.0)):.2f}"
        )
        st.caption(
            f"Cold start: {'Yes' if int(selected.get('cold_start', 0)) == 1 else 'No'} · "
            f"Baseline source: {selected.get('baseline_source', 'Not available')} · "
            f"Classification source: {selected.get('classification_source', 'Not available')}"
        )
        left, right = st.columns([1.2, 1.8])
        with left:
            top_factors = parse_structured(selected.get("top_contributing_factors")) or []
            if top_factors:
                factors_frame = pd.DataFrame(top_factors).rename(columns={"component": "Factor", "contribution": "Risk contribution"})
                st.markdown("**Top contributing factors**")
                st.dataframe(factors_frame, use_container_width=True, hide_index=True)
            else:
                st.markdown("**Top contributing factors**")
                st.write("Not available")
            components = parse_structured(selected.get("risk_components")) or {}
            if components:
                component_rows = pd.DataFrame(
                    [{"Component": human_label(k), "Risk contribution": float(v)} for k, v in components.items()]
                ).sort_values("Risk contribution", ascending=False)
                st.markdown("**Risk contributions**")
                st.dataframe(component_rows, use_container_width=True, hide_index=True)
            else:
                st.markdown("**Risk contributions**")
                st.write("Not available")
        with right:
            st.markdown("**Observed values**")
            observed_rows = [
                {"Field": "Source IP", "Observed value": selected.get("source_ip", "Not available"), "Expected / baseline": "Not available"},
                {"Field": "Geo velocity (km/h)", "Observed value": selected.get("geo_velocity_kmh", "Not available"), "Expected / baseline": "Below threshold"},
                {"Field": "Failed attempts", "Observed value": selected.get("failed_attempt_count", "Not available"), "Expected / baseline": "Low recent failure count"},
                {"Field": "Resource accessed", "Observed value": selected.get("resource_accessed", "Not available"), "Expected / baseline": "Typical entity resource set"},
                {"Field": "Device fingerprint", "Observed value": selected.get("device_fingerprint", "Not available"), "Expected / baseline": "Previously seen trusted fingerprint"},
                {"Field": "Off-hours upload", "Observed value": selected.get("cumulative_off_hours_upload", "Not available"), "Expected / baseline": "Near entity baseline"},
            ]
            st.dataframe(pd.DataFrame(observed_rows), use_container_width=True, hide_index=True)
            st.markdown("**Plain-English explanation**")
            reasons = str(selected.get("reasons", "Not available")).strip() or "Not available"
            st.write(reasons)
        history = filtered[filtered["entity_id"] == selected.get("entity_id")].sort_values("timestamp", ascending=False).head(12)
        st.markdown("**Recent entity-event history**")
        if history.empty:
            st.write("Not available")
        else:
            st.dataframe(
                format_table(history, ["timestamp", "resource_accessed", "risk_score", "severity", "predicted_attack_type", "reasons"]),
                use_container_width=True,
                hide_index=True,
            )
        if demo_mode:
            st.markdown("**Synthetic ground truth (demo mode)**")
            st.json({k: selected.get(k, "Not available") for k in ["label", "is_anomaly", "anomaly_type", "synthetic_attack_id"]})

with tabs[3]:
    st.subheader("Entity Behaviour")
    if filtered.empty:
        empty_state("No events match the selected filters.")
    else:
        entity_id = st.selectbox("Entity", sorted(filtered["entity_id"].unique()))
        entity_frame = filtered[filtered["entity_id"] == entity_id].sort_values("timestamp", ascending=False)
        if entity_frame.empty:
            empty_state("No events match the selected filters.")
        else:
            summary = entity_frame.iloc[0]
            st.caption(
                f"Entity type: {summary.get('entity_type', 'Not available')} · "
                f"Cold start: {'Yes' if int(summary.get('cold_start', 0)) == 1 else 'No'} · "
                f"Drift state: {summary.get('drift_badge', 'Not available')} · "
                f"Profile confidence: {float(summary.get('profile_confidence', 0.0)):.2f}"
            )
            st.dataframe(
                format_table(entity_frame, ["timestamp", "resource_accessed", "risk_score", "severity", "cold_start", "drift_badge", "reasons"]),
                use_container_width=True,
                hide_index=True,
            )

with tabs[4]:
    st.subheader("Model Performance")
    if METRICS_PATH.exists():
        metric_rows = pd.DataFrame(
            [
                {"Metric": "PR-AUC", "Value": f"{metrics.get('pr_auc', 0.0):.4f}"},
                {"Metric": "ROC-AUC", "Value": f"{metrics.get('roc_auc', 0.0):.4f}"},
                {"Metric": "Precision", "Value": f"{metrics.get('precision', 0.0):.4f}"},
                {"Metric": "Recall", "Value": f"{metrics.get('recall', 0.0):.4f}"},
                {"Metric": "F1", "Value": f"{metrics.get('f1', 0.0):.4f}"},
                {"Metric": "Macro F1", "Value": f"{metrics.get('macro_f1', 0.0):.4f}"},
                {"Metric": "Weighted F1", "Value": f"{metrics.get('weighted_f1', 0.0):.4f}"},
                {"Metric": "Unknown anomaly rate", "Value": f"{metrics.get('unknown_anomaly_rate', 0.0):.2%}"},
            ]
        )
        st.dataframe(metric_rows, use_container_width=True, hide_index=True)
    else:
        st.info("Evaluation metrics will appear after the pipeline runs.")
    if SAMPLE_ALERTS_PATH.exists():
        st.subheader("Sample Alerts By Attack Type")
        st.json(json.loads(SAMPLE_ALERTS_PATH.read_text(encoding="utf-8")))

with tabs[5]:
    st.subheader("Live Replay")
    replay_view = filtered.sort_values("timestamp").tail(50)
    if replay_view.empty:
        empty_state("No events match the selected filters.")
    else:
        st.plotly_chart(
            px.line(
                replay_view,
                x="timestamp",
                y="risk_score",
                color="severity",
                category_orders={"severity": SEVERITY_ORDER},
                color_discrete_map=severity_color_map(),
                labels={"timestamp": "Timestamp", "risk_score": "Risk score", "severity": "Severity"},
                title="Recent scored events in chronological order",
                height=320,
            ),
            use_container_width=True,
        )
        st.dataframe(
            format_table(replay_view, ["timestamp", "entity_id", "risk_score", "severity", "predicted_attack_type"]),
            use_container_width=True,
            hide_index=True,
        )
