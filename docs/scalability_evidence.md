# Scalability Evidence

## 1. Current Single-Process Prototype

AegisUEBA currently demonstrates local near-real-time feasibility as a single-process, CPU-based prototype. The benchmarked replay path loads the existing saved default-model artifacts, replays the saved default chronological test events, performs feature engineering, model scoring, anomaly classification, and explanation generation, and reports latency plus throughput metrics. It does not include training time, dataset generation, dashboard rendering, or any external streaming infrastructure.

## 2. Benchmark Methodology

- Date of benchmark: Sunday, July 26, 2026
- Configuration used: `configs/default.yaml`
- Artifact root used: `artifacts/default`
- Event source: `artifacts/default/sample_alerts/scored_test_events.csv`
- Saved model path: `artifacts/default/models/detector_bundle.joblib`
- Saved transformer path: `artifacts/default/preprocessors/transformer.joblib`
- Processing mode: local replay through the saved scoring path with `batch_size=50`
- Warm-up policy: one warm-up replay was executed first and excluded from the summary
- Measured runs: three
- Event count per measured run: `14,085`
- Included stages: batch iteration, feature engineering, model scoring, anomaly classification, and explanation generation
- Excluded stages: model training, dataset generation, dashboard rendering, and any production transport overhead

## 3. Benchmark Environment

The machine-readable environment record is saved at:

`artifacts/default/metrics/scalability/benchmark_environment.json`

Recorded environment:

- Operating system: `Darwin 26.5.2`
- Python version: `3.11.4`
- PyTorch version: `2.5.1`
- scikit-learn version: `1.5.2`
- Execution device: `CPU`
- Git commit: `d44cbed564dd61403a5bfd381be72b31445212d4`

Note: chip name, core counts, and total RAM were permission-limited in the benchmark environment and are therefore recorded as unavailable rather than guessed.

## 4. Three-Run Result Table

| Run | Events processed | Total duration (s) | Mean latency (ms/event) | p50 latency (ms/event) | p95 latency (ms/event) | Throughput (events/s) | Errors |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| 1 | 14,085 | 36.8307 | 2.6149 | 2.4737 | 4.0123 | 382.4258 | None |
| 2 | 14,085 | 38.6642 | 2.7451 | 2.5223 | 4.1073 | 364.2901 | None |
| 3 | 14,085 | 40.6289 | 2.8845 | 2.5718 | 4.3434 | 346.6748 | None |

Saved benchmark outputs:

- `artifacts/default/metrics/scalability/scalability_benchmark_runs.csv`
- `artifacts/default/metrics/scalability/scalability_benchmark_summary.json`

## 5. Interpretation of p50, p95 and Throughput

- Mean throughput across the three measured runs was `364.4635 events/second`.
- Throughput standard deviation was `17.8761 events/second`.
- Mean p50 latency was `2.5226 ms/event`.
- Mean p95 latency was `4.1543 ms/event`.

Interpretation:

- The p50 result shows that a typical event completed local scoring in about `2.52 ms`.
- The p95 result shows that slower-but-still-normal events remained near `4.15 ms` under the same local conditions.
- Throughput varied from `346.6748` to `382.4258 events/second`, which is honest, moderate run-to-run variation rather than a single cherry-picked best case.
- These numbers support credible local near-real-time feasibility for the current prototype, but they are not a production SLA.

## 6. Theoretical Daily Capacity Under Identical Local Conditions

Using the required extrapolation:

`mean measured events/second × 86,400`

`364.463546216249 × 86,400 = 31,489,650.393883914`

Theoretical daily capacity under the same local benchmark conditions:

- `31,489,650 events/day` theoretical extrapolation

This is a simple arithmetic extrapolation under identical local conditions and must not be interpreted as a production commitment.

## 7. Strong Warning: Not a Production SLA

This benchmark demonstrates only local replay feasibility on a single-process prototype. It does not measure multi-tenant load, external ingestion delays, persistent storage latency, alert-delivery overhead, fault recovery, or production security controls. The numbers therefore show prototype-level evidence, not a production service-level agreement.

## 8. Entity-Keyed Partitioning Strategy

The technically reasonable horizontal-scaling path is to partition incoming events by `entity_id` so that all events for the same user, service account, or device are routed to the same scoring worker. This preserves the local assumptions already present in AegisUEBA’s sequence construction, rolling windows, and profile updates.

## 9. Requirement to Preserve Per-Entity Chronological Order

Any distributed evolution must preserve per-entity chronological order inside each partition. That requirement is essential because AegisUEBA computes prior-event geographic movement, rolling counts, off-hours accumulation, device novelty, and GRU sequences from past context only.

## 10. Horizontal Scaling of Independent Entity Partitions

Independent entity partitions can be scaled horizontally by increasing the number of workers while keeping the entity-to-partition routing stable. This is a technically reasonable path because cross-entity coupling in the current scoring path is limited enough that most feature computation and scoring remain entity-local once shared reference state is available.

## 11. Shared Profile / Feature-Store Concept

The current prototype stores learned profile state locally. A production evolution would move mutable entity and peer profiles into a shared low-latency profile store so multiple workers can read and update the same profile state safely while still preserving the saved model artifacts separately from mutable runtime state.

## 12. GRU Micro-Batching Trade-Off

The replay benchmark used `batch_size=50`, which mirrors the current micro-batch configuration. A larger micro-batch may improve throughput by amortizing model overhead, but it can also increase queueing delay and tail latency. A smaller micro-batch may reduce latency while lowering throughput. This is a standard throughput-versus-latency trade-off, not an indication that batching beyond the current local configuration is already implemented or tuned for production.

## 13. Backpressure and Queue-Lag Monitoring

A production evolution should monitor queue lag, per-partition throughput, p50/p95 scoring latency, and dropped or retried events. Those signals would make backpressure visible and would allow the system to react before entity partitions become overloaded.

## 14. Profile-Update Concurrency Control

Profile updates would require concurrency control so that two workers do not race to mutate the same entity state. Reasonable approaches include partition-affine ownership, single-writer guarantees per entity, or version-checked updates in the shared store. The current prototype does not implement these distributed consistency controls.

## 15. Current Limitations

- Single local scoring process only
- No managed event stream or production queue
- No shared profile store
- No external alert persistence or SOC integration
- No production backpressure, retry, or dead-letter handling
- Benchmark environment hardware details were only partially observable due permission limits

## 16. Proposed Production Evolution

| Area | Current prototype | Proposed production evolution |
| ---- | ---- | ---- |
| Ingestion | Local chronological replay | Managed event stream or Kafka |
| Partitioning | Single scoring process | Entity-keyed partitions |
| Profiles | Local saved state | Shared low-latency profile store |
| Inference | CPU scoring process | Horizontally scaled workers |
| Sequences | Local GRU inference | Bounded micro-batching |
| Alerts | Saved artifacts and Streamlit | Persistent alert store and SOC integration |
| Monitoring | Saved latency metrics | Queue lag, drift, latency and model-health monitoring |
| Reliability | Local execution | Retries, replication and dead-letter handling |

The right-hand column is proposed architecture only and is not implemented in the current prototype.
