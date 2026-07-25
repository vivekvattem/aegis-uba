# AegisUEBA Report

## Executive Summary

AegisUEBA demonstrates a hybrid UEBA pipeline that learns stable behavioral baselines, augments them with sequence-aware modeling, and produces explainable risk-ranked alerts for analysts.

## Problem Understanding

Traditional signatures fail on novel and low-and-slow behaviors. This project therefore models user, service-account, and device behavior over time and fuses contextual evidence with learned anomaly signals.

## Synthetic Data Methodology

The generator creates stable per-entity profiles and then samples chronological events around those priors before injecting controlled adversarial campaigns.

## Architecture

See `docs/architecture.md`.

## Metrics And Results

The latest verified fast configuration run on July 25, 2026 produced:

- Total events: `7,930`
- Anomalies: `158` (`1.99%`)
- Binary PR-AUC: `0.1955`
- Binary ROC-AUC: `0.9337`
- Precision: `0.1818`
- Recall: `0.0833`
- F1: `0.1143`
- False-positive rate: `0.0058`
- Precision at top `1%` alert budget: `0.1875`
- Recall at top `1%` alert budget: `0.125`
- True attacks surfaced in top `1%`: `3`
- Mean scoring latency: `6.27e-05 ms` in the current replay stub

The multiclass anomaly classifier remains the weakest component in the current fast-run results. The generated classification report under `artifacts/metrics/classification_report.csv` shows a high `unknown_anomaly_rate` and low per-class recall outside credential-stuffing.

These numbers come from executed artifacts under `artifacts/metrics/` and are not hand-entered estimates.

## Limitations

See `docs/limitations.md`.
