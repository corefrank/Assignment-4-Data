CS336 A4 — full real Common Crawl WET local run
==============================================

Use Stanford's real downloaded file:
local-shared-data/CC/example.warc.wet.gz

1) Extract scripts/ into existing CS336 repository (back up local scripts first).
2) Run from repository root:

uv run python scripts/run_local_a4.py \
  local-shared-data/CC/example.warc.wet.gz \
  --work-dir data/a4_full_example

No --max-docs means ALL WET conversion records. Do NOT pass --quality-filter
unless you trained and validated a real fastText quality classifier.

3) Inspect real outputs and sample 5 kept + 5 discarded docs:

uv run python scripts/inspect_a4_run.py \
  --work-dir data/a4_full_example \
  --wet-path local-shared-data/CC/example.warc.wet.gz

Read:
data/a4_full_example/pipeline_report.json
data/a4_full_example/inspect_report.json
data/a4_full_example/audit_samples.md

This is a full-example-WET local reproduction, NOT Stanford's full 2500-file
English-filtered WET collection nor an official B200 training result.
Source scripts: CS336 assignment4-data (process and data format), with project
specific implementations; no synthetic training examples are introduced.
