from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="submission/source_code.zip")
    args = parser.parse_args()
    root = ROOT
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = root / "submission" / "submission_manifest.md"
    required = [
        root / "README.md",
        root / "configs" / "fast.yaml",
        root / "configs" / "default.yaml",
        root / "scripts" / "run_pipeline.py",
        root / "dashboard" / "app.py",
        root / "docs" / "report.md",
        root / "artifacts" / "metrics" / "metrics.json",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required submission files: {missing}")
    included_files = []
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in root.rglob("*"):
            if any(part in {".venv", "__pycache__", ".pytest_cache"} for part in path.parts):
                continue
            if any(part.startswith(".git") for part in path.parts):
                continue
            if path.name == ".DS_Store":
                continue
            if ".mplconfig" in path.parts:
                continue
            if path.is_file() and path != output:
                rel = path.relative_to(root)
                archive.write(path, rel)
                included_files.append(str(rel))
    manifest.write_text(
        "\n".join(
            [
                "# Submission Manifest",
                "",
                f"- `source_code.zip`: packaged project source created on {__import__('datetime').datetime.utcnow().isoformat()}Z",
                "- `docs/report.md`: report source",
                "- `docs/presentation_outline.md`: presentation source",
                "- `artifacts/metrics/metrics.json`: generated metrics summary",
                "- `artifacts/sample_alerts/scored_test_events.csv`: dashboard input",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"zip_path": str(output), "zip_size_bytes": output.stat().st_size, "included_files": included_files[:200]}, indent=2))


if __name__ == "__main__":
    main()
