# AegisUEBA

AegisUEBA is a CPU-friendly UEBA demo system for synthetic cybersecurity telemetry. It generates behavioral event streams, injects attack campaigns, trains a hybrid anomaly detector, produces explainable risk scores, and exposes analyst artifacts for evaluation and a Streamlit dashboard.

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
