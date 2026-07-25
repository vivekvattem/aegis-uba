# AegisUEBA

AegisUEBA is a CPU-friendly UEBA demo system for synthetic cybersecurity telemetry. It generates behavioral event streams, injects attack campaigns, trains a hybrid anomaly detector, produces explainable risk scores, and exposes analyst artifacts for evaluation and a Streamlit dashboard.

Latest verified fast-run results on July 25, 2026:

- Events: `7,930`
- Anomalies: `158` (`1.99%`)
- PR-AUC: `0.1955`
- ROC-AUC: `0.9337`
- Precision at top `1%` alert budget: `0.1875`
- Recall at top `1%` alert budget: `0.125`
- Streamlit health check: `HTTP 200` on `localhost:8501`
- Test status: `8 passed`

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/generate_data.py --config configs/fast.yaml
python scripts/run_pipeline.py --config configs/fast.yaml
streamlit run dashboard/app.py
pytest -q
```

## What Is Included

- Deterministic synthetic event generation with per-entity behavioral profiles.
- Required attack categories plus an insider drift edge case.
- Chronological train/validation/test splitting.
- Statistical, isolation-based, and GRU sequence-aware scoring components.
- Hybrid risk scoring, contextual evidence, severity mapping, and analyst-facing explanations.
- Streamlit dashboard tabs for overview, alerts, investigation, entity history, performance, and replay.
- Packaging support for ZIP submission artifacts.

## Constraints And Honesty Notes

- This repository is a submission-oriented prototype, not a production security platform.
- Metrics are only valid after the pipeline is actually run in the local environment.
- If PDF export tooling or an official presentation template is not present, the repository keeps print-ready markdown sources and a presentation outline instead.

## Project Layout

The implementation follows the requested separation across `src/`, `scripts/`, `dashboard/`, `tests/`, `docs/`, `artifacts/`, `data/`, and `submission/`.

## Current Limits

- The fast configuration is verified; the default configuration is configured for a larger run but was not fully executed in this continuation.
- Classification quality on rare anomaly classes is still weak, with a high `unknown_anomaly` rate in the current fast-run artifacts.
- No official organiser PowerPoint template was present in or near the repository on July 25, 2026, so only the outline is included.
