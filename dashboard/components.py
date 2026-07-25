from __future__ import annotations

import json
import ast

import pandas as pd
import plotly.express as px
import streamlit as st


SEVERITY_ORDER = ["low", "medium", "high", "critical"]
SEVERITY_COLORS = {
    "low": "#4ea8ff",
    "medium": "#f7b955",
    "high": "#ff7a59",
    "critical": "#ff4d5a",
}


def parse_structured(value):
    if isinstance(value, (dict, list)):
        return value
    if pd.isna(value):
        return None
    text = str(value)
    for parser in (json.loads, ast.literal_eval):
        try:
            return parser(text)
        except Exception:
            continue
    return None


def human_label(name: str) -> str:
    mapping = {
        "risk_score": "Risk score",
        "severity": "Severity",
        "entity_type": "Entity type",
        "predicted_attack_type": "Predicted attack type",
        "count": "Number of events",
        "classifier_confidence": "Prediction confidence",
    }
    return mapping.get(name, name.replace("_", " ").title())


def render_metric_row(frame: pd.DataFrame, metrics: dict) -> None:
    total = len(frame)
    threshold = float(metrics.get("risk_threshold", metrics.get("threshold", 0.6) * 100.0))
    alerts = int((frame["risk_score"] >= threshold).sum())
    critical = int((frame["severity"] == "critical").sum()) if "severity" in frame.columns else 0
    cols = st.columns(4)
    cols[0].metric("Scored test events", f"{total:,}")
    cols[1].metric("Alerts above threshold", f"{alerts:,}")
    cols[2].metric("Critical alerts", f"{critical:,}")
    cols[3].metric("Operational alert rate", f"{(alerts / max(1, total)):.2%}")


def render_budget_section(metrics: dict) -> None:
    st.markdown("#### Top-1% Analyst Budget")
    st.caption("Evaluation of the highest-risk 1% of test events")
    cols = st.columns(4)
    cols[0].metric("Review budget", f"{int(metrics.get('budget_events', 0)):,} events")
    cols[1].metric("Precision at budget", f"{metrics.get('precision_at_budget', 0.0):.1%}")
    cols[2].metric("Recall at budget", f"{metrics.get('recall_at_budget', 0.0):.1%}")
    cols[3].metric("True attacks surfaced", f"{int(metrics.get('true_attacks_in_budget', 0)):,}")


def empty_state(message: str) -> None:
    st.info(message)


def severity_color_map():
    return SEVERITY_COLORS.copy()


def format_table(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rename_map = {col: human_label(col) for col in columns if col in frame.columns}
    return frame[rename_map.keys()].rename(columns=rename_map)


def build_attack_distribution_chart(frame: pd.DataFrame):
    if "predicted_attack_type" not in frame.columns or frame.empty:
        return None
    counts = (
        frame.groupby("predicted_attack_type", dropna=False)
        .size()
        .reset_index(name="count")
        .rename(columns={"predicted_attack_type": "Predicted attack type", "count": "Number of events"})
        .sort_values("Number of events", ascending=False)
    )
    return px.bar(
        counts,
        x="Predicted attack type",
        y="Number of events",
        title="Alerts by predicted attack type",
        height=340,
    )
