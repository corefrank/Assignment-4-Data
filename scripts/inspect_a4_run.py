"""Audit real CS336 A4 WET outputs and verify compatibility with official get_batch.

This script NEVER fabricates documents. All audit examples come from the
Pipeline's deduped.jsonl and rejected.jsonl, sampled with seed 336.

Run from repository root:
  uv run python scripts/inspect_a4_run.py --work-dir data/a4_full_example \
    --wet-path local-shared-data/CC/example.warc.wet.gz
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

import numpy as np


def read_random_jsonl(path: Path, count: int = 5, seed: int = 336) -> tuple[list[dict], int]:
    """Reservoir sampling: uniform sample without loading all documents into RAM."""
    rng = random.Random(seed)
    selected: list[dict] = []
    seen = 0
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            entry = json.loads(line)
            if not isinstance(entry, dict):
                raise ValueError(f"Expected object at {path}:{line_number}")
            seen += 1
            if len(selected) < count:
                selected.append(entry)
            else:
                index = rng.randrange(seen)
                if index < count:
                    selected[index] = entry
    return selected, seen


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_bin(path: Path, *, batch_size: int = 2, context_length: int = 512) -> dict:
    """Match Stanford train.py's uint16 memmap and get_batch interface."""
    from cs336_basics.data import get_batch
    import torch

    if not path.is_file():
        raise FileNotFoundError(f"Token bin not found: {path}")
    if path.stat().st_size % 2 != 0:
        raise ValueError("Token file byte size is not divisible by 2 (uint16)")

    tokens = np.memmap(path, dtype=np.uint16, mode="r")
    if len(tokens) <= context_length:
        raise ValueError(f"Not enough tokens for context length {context_length}")
    if int(tokens.max()) >= 50257:
        raise ValueError("Token ID exceeds official GPT-2 vocab size 50257")

    x, y = get_batch(tokens, batch_size=batch_size, context_length=context_length, device="cpu")
    if tuple(x.shape) != (batch_size, context_length):
        raise ValueError("Unexpected get_batch shape")
    if not torch.equal(x[:, 1:], y[:, :-1]):
        raise ValueError("get_batch input/target token alignment is wrong")

    return {
        "file": str(path),
        "bytes": path.stat().st_size,
        "dtype": "uint16",
        "token_count": int(len(tokens)),
        "eos_token_id": 50256,
        "eos_occurrences": int(np.count_nonzero(tokens == 50256)),
        "batch_x_shape": list(x.shape),
        "batch_y_shape": list(y.shape),
        "compatible_with_cs336_get_batch": True,
    }


def write_review_template(path: Path, kept: list[dict], discarded: list[dict]) -> None:
    lines = [
        "# CS336 A4 — Real WET sample audit (seed=336)",
        "",
        "Source: actual pipeline outputs; examples are not fabricated.",
        "Please write 1–2 sentences of human judgment for each example, as required by A4.",
        "",
        "## Five randomly selected final kept examples",
    ]
    for index, item in enumerate(kept, 1):
        excerpt = " ".join(str(item.get("text", "")).split())[:600]
        lines.extend([
            f"### Kept {index}",
            f"- URL: {item.get('url')}",
            f"- Excerpt: {excerpt}",
            "- Human review: TODO — Is this useful for C4 100 domains LM training? Why?",
            "",
        ])
    lines.append("## Five randomly selected discarded examples")
    for index, item in enumerate(discarded, 1):
        excerpt = " ".join(str(item.get("excerpt", "")).split())[:600]
        lines.extend([
            f"### Rejected {index}",
            f"- URL: {item.get('url')}",
            f"- Rejection reason: {item.get('reason')}",
            f"- Excerpt: {excerpt}",
            "- Human review: TODO — Was rejection justified? Why?",
            "",
        ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify real A4 outputs and sample official audit examples")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--wet-path", type=Path, required=True)
    parser.add_argument("--valid-bin", type=Path, default=Path("local-shared-data/tokenized_paloma_c4_100_domains_validation.bin"))
    parser.add_argument("--sample-count", type=int, default=5)
    args = parser.parse_args()
    if args.sample_count <= 0:
        parser.error("--sample-count must be > 0")
    if not args.wet_path.is_file():
        parser.error(f"WET file does not exist: {args.wet_path}")

    work_dir = args.work_dir
    pipeline_report = json.loads((work_dir / "pipeline_report.json").read_text(encoding="utf-8"))
    kept, kept_count = read_random_jsonl(work_dir / "dedup/deduped.jsonl", args.sample_count, seed=336)
    rejected, rejected_count = read_random_jsonl(work_dir / "filtered/rejected.jsonl", args.sample_count, seed=336)
    train_stats = validate_bin(work_dir / "train.bin")
    if train_stats["eos_occurrences"] != kept_count:
        raise ValueError(f"EOS count {train_stats['eos_occurrences']} != kept documents {kept_count}")
    if kept_count != pipeline_report["dedup"]["documents_after_minhash"]:
        raise ValueError("Deduplicated document count differs from pipeline_report.json")

    report = {
        "real_source_wet_file": str(args.wet_path),
        "source_sha256": sha256_file(args.wet_path),
        "sampling_seed": 336,
        "kept_documents": kept_count,
        "rejected_documents": rejected_count,
        "train_bin": train_stats,
        "validation_bin": None,
        "validation_used_as_training_data": False,
    }
    if args.valid_bin.is_file():
        report["validation_bin"] = validate_bin(args.valid_bin)
    else:
        report["validation_bin_note"] = f"Not found (optional for preflight): {args.valid_bin}"

    (work_dir / "inspect_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_review_template(work_dir / "audit_samples.md", kept, rejected)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Human review template: {work_dir / 'audit_samples.md'}")


if __name__ == "__main__":
    main()
