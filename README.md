# Strong Filtering update for CS336 Assignment 4 local pipeline

This update changes only `scripts/filter_wet_data.py` and `scripts/run_local_a4.py`.
The original baseline behavior remains the default. Use `--strong-filter` to
activate the additional, transparent heuristics. It **does not** claim to use
an actual trained quality classifier.

## Install

From the CS336 project root, first back up your current files:

```bash
cp scripts/filter_wet_data.py scripts/filter_wet_data.baseline.py
cp scripts/run_local_a4.py scripts/run_local_a4.baseline.py
unzip -o a4_strong_filter_update.zip -d .
```

## Run the same original real WET input

```bash
uv run python scripts/run_local_a4.py \
  local-shared-data/CC/example.warc.wet.gz \
  --work-dir data/a4_full_strong \
  --strong-filter
```

Do not add `--quality-filter` unless you actually trained the fastText classifier.
Do not overwrite your existing `data/a4_full_example` baseline results.

## Compare results

```bash
uv run python - <<'PYCMD'
import json
from pathlib import Path
for p in [Path('data/a4_full_example/pipeline_report.json'), Path('data/a4_full_strong/pipeline_report.json')]:
    d=json.loads(p.read_text())
    print(p)
    print('seen=',d['filter']['documents_seen'],
          'kept=',d['filter']['documents_kept'],
          'rejected=',d['filter']['rejected_by_reason'],
          'after_dedup=',d['dedup']['documents_after_minhash'],
          'tokens=',d['tokenization']['tokens'],
          'runtime_s=',round(sum(d[k]['runtime_seconds'] for k in ('filter','dedup','tokenization')),2))
PYCMD
```

## Method

Rules inspect the original (real) WET text; they reject unusual scarcity of
alphabetic words, low lexical diversity, navigation-heavy documents, and highly
repeated three-word sequences. These are generic rules, not hard-coded URLs or
sample-specific markers. Any changes in the output must be checked by human
sampling. Lower token count is **not** direct evidence of higher LM quality.
