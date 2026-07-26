from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

from aegis_ueba.config import load_config
from aegis_ueba.detection.detector import HybridDetector


def _run_command(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True).strip()
    except Exception:
        return None


def _build_environment(config_path: Path, artifact_root: Path) -> dict:
    import sklearn
    import torch

    os_version = _run_command(["sw_vers", "-productVersion"])
    cpu_name = _run_command(["sysctl", "-n", "machdep.cpu.brand_string"]) or _run_command(["sysctl", "-n", "hw.model"])
    logical_cpu = _run_command(["sysctl", "-n", "hw.logicalcpu"])
    physical_cpu = _run_command(["sysctl", "-n", "hw.physicalcpu"])
    mem_bytes = _run_command(["sysctl", "-n", "hw.memsize"])
    git_commit = _run_command(["git", "rev-parse", "HEAD"])
    execution_device = "cpu"
    if torch.cuda.is_available():
        execution_device = "cuda"
    elif getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        execution_device = "mps"

    return {
        "operating_system": platform.system(),
        "operating_system_version": os_version or platform.version(),
        "cpu_or_chip": cpu_name or "Not available",
        "logical_cores": int(logical_cpu) if logical_cpu else None,
        "physical_cores": int(physical_cpu) if physical_cpu else None,
        "total_ram_bytes": int(mem_bytes) if mem_bytes else None,
        "python_version": platform.python_version(),
        "pytorch_version": torch.__version__,
        "scikit_learn_version": sklearn.__version__,
        "execution_device": execution_device,
        "benchmark_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_hash": git_commit,
        "configuration_used": str(config_path.relative_to(ROOT)),
        "artifact_root": str(artifact_root.relative_to(ROOT)),
    }


def _math_close(lhs: float, rhs: float, tolerance: float = 1e-6) -> bool:
    return abs(lhs - rhs) <= max(tolerance, abs(rhs) * 1e-6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    args = parser.parse_args()

    config_path = ROOT / args.config
    config = load_config(config_path)
    artifact_root = ROOT / config.project["output_dir"]
    metrics_root = artifact_root / "metrics" / "scalability"
    metrics_root.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(artifact_root / "sample_alerts" / "scored_test_events.csv")
    detector = HybridDetector.load(artifact_root)
    benchmark_environment = _build_environment(config_path, artifact_root)
    (metrics_root / "benchmark_environment.json").write_text(json.dumps(benchmark_environment, indent=2), encoding="utf-8")

    # Warm-up run intentionally excluded from summary statistics.
    detector.replay(frame)

    measured_runs: list[dict] = []
    errors: list[str] = []
    for run_number in range(1, 4):
        try:
            replay_metrics = detector.replay(frame)
            expected_throughput = replay_metrics["events_processed"] / replay_metrics["total_duration_seconds"] if replay_metrics["total_duration_seconds"] else 0.0
            if not _math_close(replay_metrics["events_per_second"], expected_throughput):
                raise ValueError("throughput calculation mismatch")
            measured_runs.append(
                {
                    "run_number": run_number,
                    "events_processed": int(replay_metrics["events_processed"]),
                    "total_duration_seconds": float(replay_metrics["total_duration_seconds"]),
                    "mean_latency_ms_per_event": float(replay_metrics["avg_latency_ms"]),
                    "p50_latency_ms_per_event": float(replay_metrics["p50_latency_ms"]),
                    "p95_latency_ms_per_event": float(replay_metrics["p95_latency_ms"]),
                    "throughput_events_per_second": float(replay_metrics["events_per_second"]),
                    "errors_encountered": "",
                }
            )
        except Exception as exc:  # pragma: no cover - defensive reporting
            message = f"run {run_number}: {exc}"
            errors.append(message)
            measured_runs.append(
                {
                    "run_number": run_number,
                    "events_processed": int(len(frame)),
                    "total_duration_seconds": 0.0,
                    "mean_latency_ms_per_event": 0.0,
                    "p50_latency_ms_per_event": 0.0,
                    "p95_latency_ms_per_event": 0.0,
                    "throughput_events_per_second": 0.0,
                    "errors_encountered": message,
                }
            )

    run_columns = [
        "run_number",
        "events_processed",
        "total_duration_seconds",
        "mean_latency_ms_per_event",
        "p50_latency_ms_per_event",
        "p95_latency_ms_per_event",
        "throughput_events_per_second",
        "errors_encountered",
    ]
    with (metrics_root / "scalability_benchmark_runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=run_columns)
        writer.writeheader()
        writer.writerows(measured_runs)

    successful_runs = [run for run in measured_runs if not run["errors_encountered"]]
    throughput_values = [run["throughput_events_per_second"] for run in successful_runs]
    p50_values = [run["p50_latency_ms_per_event"] for run in successful_runs]
    p95_values = [run["p95_latency_ms_per_event"] for run in successful_runs]
    event_counts = sorted({run["events_processed"] for run in measured_runs})

    summary = {
        "measured_runs": len(successful_runs),
        "event_count_constant": len(event_counts) == 1,
        "events_processed_per_run": event_counts[0] if len(event_counts) == 1 else event_counts,
        "throughput_mean_events_per_second": statistics.mean(throughput_values) if throughput_values else 0.0,
        "throughput_stddev_events_per_second": statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0.0,
        "throughput_min_events_per_second": min(throughput_values) if throughput_values else 0.0,
        "throughput_max_events_per_second": max(throughput_values) if throughput_values else 0.0,
        "mean_p50_latency_ms_per_event": statistics.mean(p50_values) if p50_values else 0.0,
        "mean_p95_latency_ms_per_event": statistics.mean(p95_values) if p95_values else 0.0,
        "execution_device": benchmark_environment["execution_device"],
        "units": {
            "events_processed": "events",
            "total_duration_seconds": "seconds",
            "mean_latency_ms_per_event": "milliseconds per event",
            "p50_latency_ms_per_event": "milliseconds per event",
            "p95_latency_ms_per_event": "milliseconds per event",
            "throughput_events_per_second": "events per second",
        },
        "warmup_policy": "One warm-up replay was executed before the three measured runs and excluded from summary statistics.",
        "included_processing_stages": "Saved-model scoring replay only, including batch iteration, feature engineering, model scoring, and explanation generation. Excludes training time.",
        "errors_encountered": errors,
    }
    (metrics_root / "scalability_benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
