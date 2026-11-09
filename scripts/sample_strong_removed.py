"""Audit real documents kept by Baseline but rejected by Strong filtering."""
import json
import random
from collections import Counter
from pathlib import Path

BASE = Path('data/a4_full_example/filtered/kept.jsonl')
STRONG = Path('data/a4_full_strong/filtered/kept.jsonl')
REJECTED = Path('data/a4_full_strong/filtered/rejected.jsonl')
OUTPUT = Path('data/a4_full_strong/strong_removed_samples.md')


def read_jsonl(path):
    with path.open(encoding='utf-8') as file:
        for line in file:
            if line.strip():
                yield json.loads(line)


def key(doc):
    return (doc.get('url'), doc.get('text'))


strong_counts = Counter(key(doc) for doc in read_jsonl(STRONG))
removed = []
for doc in read_jsonl(BASE):
    identity = key(doc)
    if strong_counts[identity]:
        strong_counts[identity] -= 1
    else:
        removed.append(doc)

reasons = {}
if REJECTED.exists():
    for doc in read_jsonl(REJECTED):
        if doc.get('url'):
            reasons.setdefault(doc['url'], doc.get('reason', 'unknown'))

rng = random.Random(336)
samples = rng.sample(removed, min(5, len(removed)))
lines = [
    '# Baseline kept, Strong rejected — real WET sample audit',
    '',
    'These are real filtered documents, not fabricated examples.',
    f'Baseline-kept documents not found in Strong-kept: {len(removed)}',
    '',
]
for idx, doc in enumerate(samples, 1):
    url = doc.get('url')
    excerpt = ' '.join(doc.get('text', '').split())[:1100]
    lines += [
        f'## Sample {idx}',
        f'- URL: {url}',
        f'- Strong rejection reason: {reasons.get(url, "unknown")}',
        f'- Text excerpt: {excerpt}',
        '- Human verdict (justified / false positive / unclear): TODO',
        '',
    ]
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Baseline-kept but not Strong-kept: {len(removed)}')
print(f'Wrote {len(samples)} real examples to {OUTPUT}')
