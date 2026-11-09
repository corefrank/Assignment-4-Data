"""Small-scale CS336 A4 pipeline: filter -> deduplicate -> tokenize.

Use from repository root:
  uv run python scripts/run_local_a4.py local-shared-data/CC/example.warc.wet.gz \\
    --work-dir data/a4_run_1000 --max-docs 1000
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local WET-to-token-bin CS336 A4 pipeline")
    parser.add_argument("wet_path", type=Path)
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--max-docs", type=int, default=None, help="Optional smoke-test record limit; omit for the entire WET file")
    parser.add_argument("--quality-filter", action="store_true", help="Enable ONLY when using a trained quality model")
    args = parser.parse_args()
    if args.max_docs is not None and args.max_docs <= 0:
        parser.error("--max-docs must be > 0 when specified")

    root = Path(__file__).resolve().parents[1]
    stage_filter = root / "scripts" / "filter_wet_data.py"
    stage_dedup = root / "scripts" / "deduplicate_filtered_data.py"
    stage_tokenize = root / "scripts" / "tokenize_filtered_data.py"
    for script in (stage_filter, stage_dedup, stage_tokenize):
        if not script.is_file():
            parser.error(f"Missing script: {script}")

    work_dir = args.work_dir
    if work_dir.exists() and (not work_dir.is_dir() or any(work_dir.iterdir())):
        parser.error("Choose a fresh empty --work-dir (will not overwrite existing experiments)")
    work_dir.mkdir(parents=True, exist_ok=True)
    filtered_dir = work_dir / "filtered"
    dedup_dir = work_dir / "dedup"
    token_path = work_dir / "train.bin"

    steps = [
        [sys.executable, str(stage_filter), str(args.wet_path),
         "--output-dir", str(filtered_dir)],
        [sys.executable, str(stage_dedup), str(filtered_dir / "kept.jsonl"),
         "--output-dir", str(dedup_dir)],
        [sys.executable, str(stage_tokenize), str(dedup_dir / "deduped.jsonl"),
         "--output", str(token_path)],
    ]
    if args.max_docs is not None:
        steps[0].extend(["--max-docs", str(args.max_docs)])
    if args.quality_filter:
        steps[0].append("--quality-filter")

    for i, command in enumerate(steps, start=1):
        print(f"\n=== Stage {i}/3 ===", flush=True)
        print(" ".join(command), flush=True)
        subprocess.run(command, check=True, cwd=root)

    report = {
        "filter": json.loads((filtered_dir / "summary.json").read_text(encoding="utf-8")),
        "dedup": json.loads((dedup_dir / "summary.json").read_text(encoding="utf-8")),
        "tokenization": json.loads(token_path.with_suffix(".summary.json").read_text(encoding="utf-8")),
    }
    (work_dir / "pipeline_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nSUCCESS: {token_path}", flush=True)
    print(f"Report: {work_dir / 'pipeline_report.json'}", flush=True)


if __name__ == "__main__":
    main()
