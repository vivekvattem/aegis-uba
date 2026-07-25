# Submission Checklist

- Total checklist items: `148`
- Complete count: `124`
- Partially verified count: `13`
- Missing count: `5`
- User-action count: `6`
- Blocking items: Missing portal-facing report PDF, missing portal-facing presentation PDF/PPTX, missing verified dashboard screenshots, missing final upload confirmation details.
- Non-blocking limitations: Dashboard visual verification is only startup/health-verified in this environment; replay is local simulation rather than external streaming infrastructure; the submission ZIP contains `.env.example` but no live `.env`.
- Submission readiness: `NOT READY`

This audit is evidence-based. Items are not marked complete based on README claims alone.

Status markers:

- `[x]` Complete and verified
- `[~]` Implemented but partially verified
- `[ ]` Missing or blocked
- `[U]` Requires user action

## A. Core Problem Requirements

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [x] | Models normal behaviour for users | Per-entity and peer baselines cover `user` entities in generator and profiling stack. | `src/aegis_ueba/data_generation/profiles.py`, `src/aegis_ueba/profiles/entity_profile.py`, `artifacts/default/metrics/dataset_summary.json` (`user: 47,796`) | Code present and default-run artifact confirms user population. | None. |
| [x] | Models normal behaviour for service accounts | Generator and profiles include `service_account` entity type. | `src/aegis_ueba/data_generation/profiles.py`, `src/aegis_ueba/profiles/peer_profile.py`, `artifacts/default/metrics/dataset_summary.json` (`service_account: 12,277`) | Code and artifact verified. | None. |
| [x] | Models normal behaviour for edge devices | Generator and profiles include `edge_device` entity type. | `src/aegis_ueba/data_generation/profiles.py`, `src/aegis_ueba/profiles/entity_profile.py`, `artifacts/default/metrics/dataset_summary.json` (`edge_device: 10,345`) | Code and artifact verified. | None. |
| [x] | Uses sequential access events | Chronological event generation, sequence builder, temporal features, and replay path. | `src/aegis_ueba/data_generation/generator.py`, `src/aegis_ueba/features/sequence_builder.py`, `src/aegis_ueba/streaming/replay.py`, `artifacts/default/metrics/dataset_summary.json` (`min/max timestamp`) | Code and generated chronology verified. | None. |
| [x] | Detects anomalies/intrusions | Hybrid detector emits anomaly labels, risk scores, metrics, and alert artifacts. | `src/aegis_ueba/detection/detector.py`, `artifacts/default/metrics/metrics.json`, `artifacts/default/sample_alerts/scored_test_events.csv` | Default-run metrics and scored alerts verified. | None. |
| [x] | Detects compromised-credential behaviour | Contextual rules and attacks cover brute force, credential stuffing, and impossible travel. | `src/aegis_ueba/detection/contextual_rules.py`, `src/aegis_ueba/data_generation/attacks.py`, `docs/attack_taxonomy.md` | Code verified for required compromised-credential patterns. | None. |
| [~] | Supports near-real-time scoring/replay | Local replay API, replay script, latency metrics, and dashboard replay tab exist. | `src/aegis_ueba/streaming/replay.py`, `scripts/replay_stream.py`, `artifacts/default/metrics/latency_metrics.json`, `dashboard/app.py` | Replay metrics are generated and tests pass, but no external stream connector or live UI verification was completed. | Manual replay/demo verification if required by judges. |
| [x] | Produces a 0-100 risk score | Risk engine fuses signals to a 0-100 score and tests bound it. | `src/aegis_ueba/detection/risk_engine.py`, `src/aegis_ueba/detection/detector.py`, `tests/test_risk_engine.py` | Code and bounds test verified. | None. |
| [x] | Classifies anomaly type | Random Forest classifier plus contextual override assign attack labels and confidence. | `src/aegis_ueba/models/attack_classifier.py`, `src/aegis_ueba/detection/contextual_rules.py`, `artifacts/default/metrics/classification_report.csv` | Code and classification artifact verified. | None. |
| [x] | Provides analyst-readable explanations | Reason codes, explanations, contributing factors, and alert text are produced. | `src/aegis_ueba/explainability/reason_codes.py`, `src/aegis_ueba/explainability/explanations.py`, `artifacts/default/sample_alerts/sample_alerts.json` | Code and sample alert outputs verified. | None. |
| [x] | Supports brute force | Attack injector, taxonomy, validation metrics, and contextual rule. | `src/aegis_ueba/data_generation/attacks.py`, `src/aegis_ueba/detection/contextual_rules.py`, `docs/attack_taxonomy.md`, `artifacts/default/metrics/dataset_summary.json` | Verified in code and dataset summary (`195` events). | None. |
| [x] | Supports impossible travel | Attack injector, geo-velocity features, contextual rule, and validation metrics. | `src/aegis_ueba/features/geographic.py`, `src/aegis_ueba/data_generation/attacks.py`, `tests/test_contextual_rules.py`, `artifacts/default/metrics/dataset_summary.json` | Verified in code, tests, and artifacts (`163` events). | None. |
| [x] | Supports credential stuffing | Attack injector, contextual rule, and validation signatures. | `src/aegis_ueba/data_generation/attacks.py`, `src/aegis_ueba/detection/contextual_rules.py`, `tests/test_validation.py`, `artifacts/default/metrics/dataset_summary.json` | Verified in code, tests, and artifacts (`192` events). | None. |
| [x] | Supports lateral movement | Attack injector, contextual rule, taxonomy, and dataset evidence. | `src/aegis_ueba/data_generation/attacks.py`, `src/aegis_ueba/detection/contextual_rules.py`, `docs/attack_taxonomy.md`, `artifacts/default/metrics/dataset_summary.json` | Verified in code and artifacts (`204` events). | None. |
| [x] | Supports device spoofing | Attack injector, contextual rule, taxonomy, and validation signature. | `src/aegis_ueba/data_generation/attacks.py`, `src/aegis_ueba/detection/contextual_rules.py`, `tests/test_validation.py`, `artifacts/default/metrics/dataset_summary.json` | Verified in code, tests, and artifacts (`159` events). | None. |
| [x] | Supports low-and-slow exfiltration | Attack injector, contextual rule, taxonomy, and dataset evidence. | `src/aegis_ueba/data_generation/attacks.py`, `src/aegis_ueba/detection/contextual_rules.py`, `docs/attack_taxonomy.md`, `artifacts/default/metrics/dataset_summary.json` | Verified in code and artifacts (`171` events). | None. |
| [x] | Supports insider drift as an edge case | Edge-case attack is generated, measured, and called out in taxonomy. | `src/aegis_ueba/data_generation/attacks.py`, `docs/attack_taxonomy.md`, `src/aegis_ueba/evaluation/validation.py`, `artifacts/default/metrics/dataset_summary.json` | Verified in code and artifacts (`66` events). | None. |

## B. Mandatory ML Challenges

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [x] | Extreme class imbalance | Generator defaults to low anomaly rate and metrics record imbalance. | `configs/default.yaml`, `artifacts/default/metrics/dataset_summary.json` (`1,150 / 70,418 anomalies`) | Config and artifact verified. | None. |
| [x] | Chronological evaluation | Pipeline uses chronological split summaries and dedicated split tests. | `src/aegis_ueba/evaluation/pipeline.py`, `artifacts/default/metrics/split_summary.csv`, `tests/test_split_integrity.py` | Code, artifact, and test verified. | None. |
| [~] | No label leakage | Features and validation tests are designed for leakage-safe processing. | `src/aegis_ueba/features/entity_features.py`, `src/aegis_ueba/evaluation/pipeline.py`, `tests/test_split_integrity.py` | There is strong code/test evidence, but no formal leakage audit report artifact. | Keep as partially verified unless a dedicated leakage report is added. |
| [x] | Past-only rolling features | Temporal/entity features are built from prior context and tested. | `src/aegis_ueba/features/temporal.py`, `src/aegis_ueba/features/entity_features.py`, `tests/test_features.py` | Code and tests verified. | None. |
| [x] | Concept-drift handling | Drift manager updates trusted profiles and records adaptive vs static results. | `src/aegis_ueba/profiles/drift_manager.py`, `artifacts/default/metrics/drift_metrics.json`, `tests/test_drift.py` | Code, artifact, and test verified. | None. |
| [x] | Cold-start handling | Cold-start entities fall back to peer/global baselines and are evaluated separately. | `src/aegis_ueba/profiles/entity_profile.py`, `src/aegis_ueba/detection/detector.py`, `artifacts/default/metrics/cold_start_metrics.json` | Code and artifact verified. | None. |
| [x] | Explainability | Explanations and factor breakdowns are part of scoring output and dashboard. | `src/aegis_ueba/explainability/explanations.py`, `artifacts/default/sample_alerts/sample_alerts.json`, `dashboard/app.py` | Code and sample artifacts verified. | None. |
| [x] | Analyst alert-budget evaluation | Top-1% alert budget metrics are computed and exposed in metrics/dashboard. | `src/aegis_ueba/evaluation/metrics.py`, `artifacts/default/metrics/metrics.json`, `dashboard/components.py` | Code and default-run metrics verified. | None. |

## C. Synthetic Data Generator

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [x] | Configurable random seed | Config and reproducibility utility wire deterministic seeds. | `configs/default.yaml`, `src/aegis_ueba/utils/reproducibility.py`, `scripts/generate_data.py` | Code verified. | None. |
| [x] | Configurable anomaly rate | Config controls anomaly mix and rates. | `configs/default.yaml`, `configs/fast.yaml`, `src/aegis_ueba/data_generation/generator.py` | Config and generator code verified. | None. |
| [x] | Per-entity normal profiles | Generator derives stable entity behaviour priors. | `src/aegis_ueba/data_generation/profiles.py`, `docs/behavioural_assumptions.md` | Code and documentation verified. | None. |
| [x] | Chronologically ordered events | Generated events span ordered timestamps and split summaries preserve chronology. | `src/aegis_ueba/data_generation/generator.py`, `artifacts/default/metrics/dataset_summary.json`, `tests/test_split_integrity.py` | Artifact and test verified. | None. |
| [x] | Controlled attack injection | Dedicated injector module mutates normal streams into labeled campaigns. | `src/aegis_ueba/data_generation/attacks.py`, `configs/default.yaml` | Code verified. | None. |
| [x] | Separate attack campaigns | Campaign IDs are retained for injected attacks. | `src/aegis_ueba/data_generation/attacks.py`, `artifacts/default/metrics/dataset_summary.json` (`synthetic_attack_id` retained for anomalies) | Code and artifact verified. | None. |
| [x] | Campaign integrity across splits | Chronological split integrity tests and split summaries exist. | `tests/test_split_integrity.py`, `artifacts/default/metrics/split_summary.csv`, `artifacts/default/metrics/split_label_counts.csv` | Tests and artifacts verified. | None. |
| [x] | Ground-truth labels retained for evaluation | Generator includes `label`, `is_anomaly`, and `anomaly_type` for evaluation paths. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json`, `artifacts/default/sample_alerts/scored_test_events.csv` | Schema and artifacts verified. | None. |
| [~] | Inference-safe unlabeled data | Dashboard hides ground truth by default and packaging excludes raw inference folders. | `dashboard/app.py`, `scripts/package_submission.py` | UI hides labels by default, but no separate unlabeled exported inference dataset is present in `submission/`. | Add an explicit unlabeled inference sample if required. |
| [x] | No personal or organisational data | Dataset is synthetic and driven by generated profiles/telemetry fields. | `src/aegis_ueba/data_generation/generator.py`, `docs/behavioural_assumptions.md`, `data/README.md` | Code/docs verified. | None. |
| [x] | Required field: `entity_id` | Schema and null-count artifact include `entity_id`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `entity_type` | Schema and null-count artifact include `entity_type`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `timestamp` | Schema and chronology artifacts include `timestamp`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `source_ip` | Schema and null-count artifact include `source_ip`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `geo_location` | Schema and null-count artifact include `geo_location`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `resource_accessed` | Schema and null-count artifact include `resource_accessed`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `auth_method` | Schema and null-count artifact include `auth_method`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `session_duration` | Schema and null-count artifact include `session_duration`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `command_sequence` | Schema and null-count artifact include `command_sequence`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `device_fingerprint` | Schema and null-count artifact include `device_fingerprint`. | `src/aegis_ueba/schemas.py`, `artifacts/default/metrics/dataset_summary.json` | Null check verified (`0`). | None. |
| [x] | Required field: `label` for training/evaluation only | Labeled evaluation data exists and dashboard hides it unless demo mode is enabled. | `src/aegis_ueba/schemas.py`, `dashboard/app.py`, `artifacts/default/sample_alerts/scored_test_events.csv` | Code and artifact verified. | None. |
| [x] | Unique `event_id` | Dataset summary tracks duplicate IDs. | `artifacts/default/metrics/dataset_summary.json` (`duplicate_event_id_count: 0`) | Artifact verified. | None. |
| [x] | Required-field null checks | Dataset summary reports null counts for required fields. | `artifacts/default/metrics/dataset_summary.json` | Artifact verified; required fields are `0`. | None. |
| [x] | Dataset distribution | Dataset summary records totals and percentages. | `artifacts/default/metrics/dataset_summary.json` | Artifact verified. | None. |
| [x] | Anomaly distribution | Summary records counts by anomaly type. | `artifacts/default/metrics/dataset_summary.json` | Artifact verified. | None. |
| [x] | Entity-type distribution | Summary records counts by entity type. | `artifacts/default/metrics/dataset_summary.json` | Artifact verified. | None. |
| [x] | Behavioural signature validation | Validation module and saved signatures check attack fingerprints. | `src/aegis_ueba/evaluation/validation.py`, `artifacts/default/metrics/behavioural_signatures.json`, `tests/test_validation.py` | Code, artifact, and test verified. | None. |

## D. Required Deliverables

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [x] | 1. Synthetic data generator | Generator, attack injectors, configs, dataset summary, assumptions, and taxonomy are present. | `scripts/generate_data.py`, `src/aegis_ueba/data_generation/*`, `configs/default.yaml`, `artifacts/default/metrics/dataset_summary.json`, `docs/behavioural_assumptions.md`, `docs/attack_taxonomy.md` | Evidence present and verified. | None. |
| [x] | 2. Baseline behavioural profiling model | Entity profile, peer profile, statistical baseline, isolation baseline, and saved bundle exist. | `src/aegis_ueba/profiles/entity_profile.py`, `src/aegis_ueba/profiles/peer_profile.py`, `src/aegis_ueba/models/statistical_baseline.py`, `src/aegis_ueba/models/isolation_baseline.py`, `artifacts/default/models/detector_bundle.joblib` | Code and saved artifact verified. | None. |
| [~] | 3. Sequence-aware detection model | GRU autoencoder, sequence builder, training path, and saved bundle are present. | `src/aegis_ueba/models/gru_autoencoder.py`, `src/aegis_ueba/features/sequence_builder.py`, `scripts/train.py`, `artifacts/default/models/detector_bundle.joblib`, `tests/test_models.py` | Implemented and included in the detector, but there is no dedicated artifact proving the GRU contribution independently inside the saved bundle. | Add a targeted integration assertion or saved ablation note if stricter proof is required. |
| [x] | 4. Anomaly classification | Supported classes, classifier, taxonomy integration, per-class report, confidence, and unknown-anomaly handling exist. | `src/aegis_ueba/models/attack_classifier.py`, `src/aegis_ueba/detection/contextual_rules.py`, `docs/attack_taxonomy.md`, `artifacts/default/metrics/classification_report.csv`, `tests/test_models.py` | Evidence verified. | None. |
| [x] | 5. Explainability layer | Reason codes, factors, observed values, baseline hints, contributions, English explanations, and sample alerts exist. | `src/aegis_ueba/explainability/*`, `artifacts/default/sample_alerts/sample_alerts.json`, `dashboard/app.py` | Evidence verified. | None. |
| [~] | 6. Analyst-facing dashboard | Ranked queue, risk/severity/prediction, factors, investigation, entity history, cold-start, drift, performance, replay, CSV export, hidden ground truth, and startup health exist. | `dashboard/app.py`, `dashboard/components.py`, `artifacts/default/sample_alerts/scored_test_events.csv`, successful `streamlit run ...` + `curl -I http://127.0.0.1:8501` | Features and health check verified, but dashboard screenshots are missing and full interactive tab-by-tab visual verification was not completed in-browser. | Capture real screenshots and perform manual tab walkthrough. |
| [ ] | 7. Report | Markdown report source exists, but final report PDF does not. | `docs/report.md`; no `submission/AegisUEBA_Technical_Report.pdf` found | Source verified; portal-facing PDF missing. | Generate and verify final report PDF. |
| [ ] | 8. Presentation | Only an outline exists; no official-template PPTX/PDF deliverables were found. | `docs/presentation_outline.md`; no `.pptx` or presentation PDF under `submission/` | Outline verified; required final deck artifacts missing. | Build final 6-slide deck in official template, export PPTX/PDF, and verify visually. |

## E. Evaluation Criteria

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [x] | PR-AUC | Binary metric is computed and saved. | `artifacts/default/metrics/metrics.json` (`0.6183347613`) | Artifact verified. | None. |
| [x] | Precision | Binary precision is computed and saved. | `artifacts/default/metrics/metrics.json` (`0.5246753247`) | Artifact verified. | None. |
| [x] | Recall | Binary recall is computed and saved. | `artifacts/default/metrics/metrics.json` (`0.6011904762`) | Artifact verified. | None. |
| [x] | F1 | Binary F1 is computed and saved. | `artifacts/default/metrics/metrics.json` (`0.5603328710`) | Artifact verified. | None. |
| [x] | ROC-AUC | Binary ROC-AUC is computed and saved. | `artifacts/default/metrics/metrics.json` (`0.9675658230`) | Artifact verified. | None. |
| [x] | False-positive rate | FPR is computed and saved. | `artifacts/default/metrics/metrics.json` (`0.0133100589`) | Artifact verified. | None. |
| [x] | False-negative rate | FNR is computed and saved. | `artifacts/default/metrics/metrics.json` (`0.3988095238`) | Artifact verified. | None. |
| [x] | Confusion matrix | Binary confusion matrix artifact is saved. | `artifacts/default/metrics/confusion_matrix.csv` | Artifact verified. | None. |
| [x] | Top-1% budget size | Budget size is computed and exposed. | `artifacts/default/metrics/metrics.json` (`141`) | Artifact verified. | None. |
| [x] | Precision at top 1% | Budget precision is saved. | `artifacts/default/metrics/metrics.json` (`0.7943262411`) | Artifact verified. | None. |
| [x] | Recall at top 1% | Budget recall is saved. | `artifacts/default/metrics/metrics.json` (`0.3333333333`) | Artifact verified. | None. |
| [x] | True attacks surfaced | Count in top-1% budget is saved. | `artifacts/default/metrics/metrics.json` (`112`) | Artifact verified. | None. |
| [x] | Alerts per 10,000 events | Alert-budget metrics CSV is saved. | `artifacts/default/metrics/alert_budget_metrics.csv` | Artifact exists and was generated by the pipeline. | None. |
| [x] | Macro F1 | Multiclass metric is saved. | `artifacts/default/metrics/metrics.json` (`0.6387870528`) | Artifact verified. | None. |
| [x] | Weighted F1 | Multiclass metric is saved. | `artifacts/default/metrics/metrics.json` (`0.6300000962`) | Artifact verified. | None. |
| [x] | Per-class precision | Classification report CSV exists. | `artifacts/default/metrics/classification_report.csv` | Artifact verified. | None. |
| [x] | Per-class recall | Classification report CSV exists. | `artifacts/default/metrics/classification_report.csv` | Artifact verified. | None. |
| [x] | Per-class F1 | Classification report CSV exists. | `artifacts/default/metrics/classification_report.csv` | Artifact verified. | None. |
| [x] | Multiclass confusion matrix | Classification confusion matrix artifact exists. | `artifacts/default/metrics/confusion_matrix.csv`, `artifacts/default/metrics/classification_report.csv` | Confusion artifact verified, though naming is shared with binary outputs. | None. |
| [x] | Unknown-anomaly rate | Unknown rate is computed and saved. | `artifacts/default/metrics/metrics.json` (`0.0`) | Artifact verified. | None. |
| [x] | Total replay duration | Replay metrics JSON stores total duration. | `artifacts/default/metrics/latency_metrics.json` (`60.736663958 s`) | Artifact verified. | None. |
| [x] | Average latency | Replay metrics JSON stores average latency in ms. | `artifacts/default/metrics/latency_metrics.json` (`4.3121522157 ms`) | Artifact verified. | None. |
| [x] | p50 latency | Replay metrics JSON stores p50 in ms. | `artifacts/default/metrics/latency_metrics.json` (`3.9198125000 ms`) | Artifact verified. | None. |
| [x] | p95 latency | Replay metrics JSON stores p95 in ms. | `artifacts/default/metrics/latency_metrics.json` (`7.0742063750 ms`) | Artifact verified. | None. |
| [x] | Events per second | Replay throughput is computed and saved. | `artifacts/default/metrics/latency_metrics.json` (`231.9027599168 eps`) | Artifact verified. | None. |
| [x] | Correct units and formulas | Streaming replay math has a dedicated consistency test. | `tests/test_streaming.py` | Test verified. | None. |
| [x] | Cold-start entity count | Cold-start metrics JSON stores entity count. | `artifacts/default/metrics/cold_start_metrics.json` (`52`) | Artifact verified. | None. |
| [x] | Cold-start event count | Cold-start metrics JSON stores event count. | `artifacts/default/metrics/cold_start_metrics.json` (`446`) | Artifact verified. | None. |
| [x] | Cold-start false-positive rate | Cold-start metrics JSON stores FPR. | `artifacts/default/metrics/cold_start_metrics.json` (`0.0162601626`) | Artifact verified. | None. |
| [x] | Static-versus-adaptive drift results | Drift metrics JSON stores static/adaptive mean risk comparison. | `artifacts/default/metrics/drift_metrics.json` | Artifact verified. | None. |
| [x] | High-risk quarantine | Drift manager quarantines risky updates and tests cover it. | `src/aegis_ueba/profiles/drift_manager.py`, `tests/test_drift.py`, `artifacts/default/metrics/drift_metrics.json` | Code, test, and artifact verified. | None. |
| [x] | Ablation results | Ablation outputs are saved as CSV and figure. | `artifacts/default/metrics/ablation_results.csv`, `artifacts/default/figures/ablation_comparison.png`, `src/aegis_ueba/evaluation/ablation.py` | Artifact verified. | None. |
| [x] | Baseline-versus-final comparison | Ablation comparison artifact provides comparative evidence. | `artifacts/default/metrics/ablation_results.csv`, `artifacts/default/figures/ablation_comparison.png` | Artifact verified. | None. |

## F. Testing

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [x] | Deterministic generation | Generator tests cover deterministic output behaviour. | `tests/test_generator.py` | Test suite present and passing. | None. |
| [x] | Required schema | Schema/data generation tests exist. | `tests/test_generator.py`, `src/aegis_ueba/schemas.py` | Test and schema verified. | None. |
| [x] | Attack injectors | Generator/validation tests cover injected attacks. | `tests/test_generator.py`, `tests/test_validation.py` | Tests verified. | None. |
| [x] | Behavioural attack signatures | Validation tests assert behavioural signatures. | `tests/test_validation.py` | Test verified. | None. |
| [x] | Chronological split integrity | Dedicated split integrity test exists. | `tests/test_split_integrity.py` | Test verified. | None. |
| [x] | Campaign separation | Split integrity and generator logic cover campaign handling. | `tests/test_split_integrity.py`, `src/aegis_ueba/data_generation/attacks.py` | Test/code verified. | None. |
| [~] | No label leakage | Leakage-safe design is indirectly tested through split/features tests. | `tests/test_split_integrity.py`, `tests/test_features.py` | No dedicated test named for label leakage was found. | Add an explicit leakage test if stricter proof is required. |
| [x] | Past-only rolling features | Feature tests cover temporal feature behaviour. | `tests/test_features.py` | Test verified. | None. |
| [x] | Haversine/geo-velocity logic | Geographic/contextual logic is covered. | `src/aegis_ueba/features/geographic.py`, `tests/test_contextual_rules.py`, `tests/test_features.py` | Code and tests verified. | None. |
| [x] | Contextual rules | Dedicated contextual rule tests exist. | `tests/test_contextual_rules.py` | Test verified. | None. |
| [x] | Risk-score bounds | Dedicated risk engine bounds test exists. | `tests/test_risk_engine.py` | Test verified. | None. |
| [x] | Classification behaviour | Model tests cover classifier behaviour and unknown labels. | `tests/test_models.py` | Test verified. | None. |
| [~] | GRU/model behaviour | Model tests exist, but there is no dedicated end-to-end assertion isolating GRU contribution. | `tests/test_models.py`, `src/aegis_ueba/models/gru_autoencoder.py` | Partial verification only. | Add a GRU integration-focused test if required. |
| [x] | Cold-start fallback | Cold-start logic is reflected in detector/profile code and metrics. | `src/aegis_ueba/profiles/entity_profile.py`, `src/aegis_ueba/detection/detector.py`, `artifacts/default/metrics/cold_start_metrics.json` | Code/artifact verified. | None. |
| [x] | Drift updates | Dedicated drift tests exist. | `tests/test_drift.py` | Test verified. | None. |
| [x] | High-risk quarantine | Drift test covers quarantine behaviour. | `tests/test_drift.py` | Test verified. | None. |
| [x] | Latency-unit correctness | Streaming replay math test exists. | `tests/test_streaming.py` | Test verified. | None. |
| [x] | Pipeline outputs | Dedicated pipeline output tests exist. | `tests/test_pipeline_outputs.py` | Test verified. | None. |
| [x] | Streaming/replay | Replay test exists. | `tests/test_streaming.py` | Test verified. | None. |
| [x] | End-to-end smoke test | Smoke pipeline test exists. | `tests/test_smoke_pipeline.py` | Test verified. | None. |
| [x] | Exact pytest result | Full suite was executed on Saturday, July 25, 2026. | Successful command: `.venv/bin/pytest -q` | Result: `13 passed, 0 failed, 0 skipped, 0 xfailed, 14 warnings in 82.11s (0:01:22)`. | None. |

## G. Documentation

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [x] | README | Project overview and run commands exist. | `README.md` | File verified. | None. |
| [x] | Architecture documentation | Architecture doc exists. | `docs/architecture.md` | File verified. | None. |
| [x] | Data dictionary | Data dictionary exists. | `docs/data_dictionary.md` | File verified. | None. |
| [x] | Behavioural assumptions | Assumptions doc exists. | `docs/behavioural_assumptions.md` | File verified. | None. |
| [x] | Attack taxonomy | Attack taxonomy doc exists. | `docs/attack_taxonomy.md` | File verified. | None. |
| [x] | Model card | Model card exists. | `docs/model_card.md` | File verified. | None. |
| [x] | Limitations | Limitations doc exists. | `docs/limitations.md` | File verified. | None. |
| [x] | Deployment/scalability discussion | Deployment doc exists. | `docs/deployment.md` | File verified. | None. |
| [x] | Report | Markdown report source exists. | `docs/report.md` | Source verified. | Generate final PDF if required for portal. |
| [~] | Presentation | Only an outline exists. | `docs/presentation_outline.md` | Outline verified; final deck missing. | Create final PPTX/PDF. |
| [~] | Submission manifest | Manifest exists but does not list every final portal-facing deliverable because several are missing. | `submission/submission_manifest.md` | File verified. | Update after PDFs/final files exist. |
| [x] | Exact setup/run commands | Quick-start commands are documented. | `README.md` | File verified. | None. |
| [~] | macOS instructions | Generic local commands work on macOS, but there is no dedicated macOS section. | `README.md`, successful local runs in `.venv` | Partially verified. | Add explicit macOS notes if required. |
| [x] | Fast/default configuration explanation | README and configs distinguish fast/default runs. | `README.md`, `configs/fast.yaml`, `configs/default.yaml` | Files verified. | None. |
| [ ] | GitHub repository link | No repository URL was found in docs/submission artifacts. | Search across `README.md`, `docs/`, `submission/` | Missing. | Add final repo URL if required by submission. |

## H. Submission Format

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [ ] | Portal-facing presentation is PDF | Expected file is absent. | No `submission/AegisUEBA_Idea_Presentation.pdf` found | Missing. | Generate and verify PDF. |
| [ ] | Report is PDF | Expected file is absent. | No `submission/AegisUEBA_Technical_Report.pdf` found | Missing. | Generate and verify PDF. |
| [x] | Source code is ZIP | Packaged ZIP exists. | `submission/source_code.zip` | File verified. | None. |
| [x] | ZIP opens successfully | ZIP was opened and inspected programmatically. | Successful `.venv/bin/python` `zipfile.ZipFile('submission/source_code.zip')` check | Verified. | None. |
| [x] | ZIP excludes `.venv` | Packaging script excludes `.venv`; ZIP inspection found none. | `scripts/package_submission.py`, ZIP inspection result | Verified. | None. |
| [x] | ZIP excludes `.env` | ZIP contains no `.env`; only `.env.example` is included. | ZIP inspection result, `submission/source_code.zip` | Verified for live `.env`; `.env.example` remains intentionally. | None. |
| [~] | ZIP excludes secrets | No obvious secret files were found, but no automated secret scan artifact exists. | `submission/source_code.zip`, repo inventory | Partially verified. | Run a secret scan if stricter evidence is required. |
| [x] | ZIP excludes caches | ZIP inspection found no `.pytest_cache`, `__pycache__`, or `.DS_Store`. | `scripts/package_submission.py`, ZIP inspection result | Verified. | None. |
| [x] | ZIP excludes `.git` | Packaging script excludes `.git`; ZIP inspection found none. | `scripts/package_submission.py`, ZIP inspection result | Verified. | None. |
| [x] | ZIP excludes unnecessary temporary files | Packaging script filters caches/temp-like files. | `scripts/package_submission.py`, ZIP inspection result | Verified for the checked temp/cache entries. | None. |
| [~] | Manifest lists every deliverable | Manifest exists, but missing portal-facing PDFs because those files do not yet exist. | `submission/submission_manifest.md` | Partial only. | Update manifest after final deliverables are created. |
| [x] | Files use clear names | Existing submission filenames are readable and specific. | `submission/source_code.zip`, `submission/submission_manifest.md` | Verified. | None. |
| [~] | Final file sizes are recorded | ZIP size was measured, but missing PDFs mean the final submission set is incomplete. | `submission/source_code.zip` (`20,853,678 bytes`) | Partial only. | Record sizes after PDF deliverables exist. |
| [U] | Portal expects separate uploads or permits them together | Repository does not contain portal submission UI instructions. | No portal instruction artifact found in repo | User/portal confirmation required. | Confirm portal upload rules before final submission. |

## I. Required User Inputs

| Status | Requirement | Implementation | Evidence | Verification | Remaining action |
| ---- | ---- | ---- | ---- | ---- | ---- |
| [U] | Problem Statement ID | Not present in repository metadata. | No value found in `README.md`, `docs/`, or `submission/` | User input required. | Provide final ID and insert into report/presentation if needed. |
| [U] | Theme | Not present in repository metadata. | No value found in `README.md`, `docs/`, or `submission/` | User input required. | Provide final theme and insert into submission files if needed. |
| [U] | Student ID | Not present in repository metadata. | No value found in `README.md`, `docs/`, or `submission/` | User input required. | Provide final student ID and insert into submission files if needed. |
| [U] | Final manual portal upload | Upload is intentionally out of scope for Codex. | N/A | User action required. | Upload final files to the portal. |
| [U] | Final confirmation that uploaded files open correctly | Cannot be verified before manual upload. | N/A | User action required. | Open each uploaded file in the portal and confirm integrity. |

## J. Final Upload List

| File | Format | Purpose | Exists | Verified | Upload |
| ---- | ------ | ------- | ------ | -------- | ------ |
| `submission/AegisUEBA_Idea_Presentation.pdf` | PDF | Portal-facing presentation | No | No | Yes, after creation and visual verification |
| `submission/AegisUEBA_Technical_Report.pdf` | PDF | Portal-facing technical report | No | No | Yes, after creation and verification |
| `submission/source_code.zip` | ZIP | Source code and generated evidence bundle | Yes | Yes | Yes |

## Final Audit Notes

- Verified local commands:
  - `.venv/bin/pytest -q`
  - `.venv/bin/streamlit run dashboard/app.py --server.headless true --server.port 8501`
  - `curl -I http://127.0.0.1:8501`
  - `.venv/bin/python` ZIP inspection for `submission/source_code.zip`
- Verified missing deliverables:
  - No `.pptx` found under `submission/` or `docs/`
  - No report PDF found under `submission/`
  - No dashboard screenshot evidence found at the requested submission paths
- Dashboard screenshot files expected by the polish task are still absent:
  - `artifacts/figures/dashboard/security_overview.png`
  - `artifacts/figures/dashboard/alert_investigation.png`
