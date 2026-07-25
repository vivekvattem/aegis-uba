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

The latest verified default configuration run on Saturday, July 25, 2026 produced:

- Total events: `70,418`
- Anomalies: `1,150` (`1.63%`)
- Binary PR-AUC: `0.6175`
- Binary ROC-AUC: `0.9680`
- Precision: `0.5234`
- Recall: `0.5982`
- F1: `0.5583`
- False-positive rate: `0.0133`
- Precision at top `1%` alert budget: `0.7943`
- Recall at top `1%` alert budget: `0.3333`
- True attacks surfaced in top `1%`: `112`
- Average replay latency: `5.155 ms/event`
- p50 replay latency: `3.966 ms/event`
- p95 replay latency: `9.889 ms/event`

The multiclass classifier is materially better than the earlier fast-run baseline, with a low `unknown_anomaly_rate`, but it still underperforms on some categories. The strongest default-run classes are `device_spoofing`, `lateral_movement`, and `low_and_slow_exfiltration`, while `brute_force` remains the weakest class in the current taxonomy report.

These numbers come from executed artifacts under `artifacts/default/metrics/` and are not hand-entered estimates.

## Limitations

See `docs/limitations.md`.
