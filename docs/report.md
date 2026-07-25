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

Run `python scripts/run_pipeline.py --config configs/fast.yaml` to populate `artifacts/metrics/` with actual metrics for this environment. This report intentionally avoids inventing numerical results before execution.

## Limitations

See `docs/limitations.md`.
