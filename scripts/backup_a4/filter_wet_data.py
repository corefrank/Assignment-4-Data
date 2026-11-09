"""Small-scale Common Crawl WET filtering pipeline for CS336 A4.

Uses the project's already-tested tests/adapters.py functions as a temporary
integration bridge. Before production use, switch these imports to the
corresponding cs336_data implementations and train a real quality classifier.
"""

from __future__ import annotations

import argparse
import gzip
import json
import time
from collections import Counter
from pathlib import Path
from typing import Iterator

from warcio.archiveiterator import ArchiveIterator

# Temporary integration bridge: these functions already passed your A4 tests.
# Once the pipeline works, import them from their actual cs336_data modules.
from tests.adapters import (
    run_classify_nsfw,
    run_classify_quality,
    run_classify_toxic_speech,
    run_gopher_quality_filter,
    run_identify_language,
    run_mask_emails,
    run_mask_ips,
    run_mask_phone_numbers,
)


def iter_wet_documents(wet_path: Path) -> Iterator[tuple[str | None, str]]:
    """Yield (URL, text) from WET conversion records, one at a time."""
    open_stream = gzip.open if wet_path.suffix == ".gz" else open
    with open_stream(wet_path, "rb") as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type != "conversion":
                continue
            url = record.rec_headers.get_header("WARC-Target-URI")
            text = record.content_stream().read().decode("utf-8", errors="replace")
            yield url, text


def filter_document(
    text: str,
    counts: Counter,
    *,
    use_quality: bool,
) -> tuple[str | None, str | None]:
    """Return (masked_text, None) if kept, otherwise (None, reject_reason)."""
    language, language_score = run_identify_language(text)
    if language != "en" or language_score < 0.70:
        return None, "language"
    counts["passed_language"] += 1

    if not run_gopher_quality_filter(text):
        return None, "gopher"
    counts["passed_gopher"] += 1

    nsfw_label, nsfw_score = run_classify_nsfw(text)
    if nsfw_label == "nsfw" and nsfw_score >= 0.50:
        return None, "nsfw"
    counts["passed_nsfw"] += 1

    toxic_label, toxic_score = run_classify_toxic_speech(text)
    if toxic_label == "toxic" and toxic_score >= 0.50:
        return None, "toxic"
    counts["passed_toxic"] += 1

    # Avoid calling the unfinished quality classifier unless requested.
    if use_quality:
        label, score = run_classify_quality(text)
        if label != "wiki" or score < 0.50:
            return None, "quality"
        counts["passed_quality"] += 1

    # Mask PII AFTER classification; preserve original document line breaks.
    text, emails = run_mask_emails(text)
    text, phones = run_mask_phone_numbers(text)
    text, ips = run_mask_ips(text)
    counts["emails_masked"] += emails
    counts["phones_masked"] += phones
    counts["ips_masked"] += ips

    return text, None


def main() -> None:
    parser = argparse.ArgumentParser(description="Small WET -> filtered JSONL/text pipeline")
    parser.add_argument("wet_path", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-docs", type=int, default=100)
    parser.add_argument("--quality-filter", action="store_true")
    args = parser.parse_args()

    if not args.wet_path.is_file():
        parser.error(f"WET file not found: {args.wet_path}")
    if args.max_docs <= 0:
        parser.error("--max-docs must be > 0")
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error(f"Output directory is not empty: {args.output_dir}. Choose a new directory.")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    counts: Counter = Counter()
    reasons: Counter = Counter()

    kept_path = args.output_dir / "kept.jsonl"
    rejected_path = args.output_dir / "rejected.jsonl"
    text_path = args.output_dir / "filtered.txt"

    with (
        kept_path.open("w", encoding="utf-8") as kept_file,
        rejected_path.open("w", encoding="utf-8") as rejected_file,
        text_path.open("w", encoding="utf-8") as text_file,
    ):
        for url, original in iter_wet_documents(args.wet_path):
            if counts["documents_seen"] >= args.max_docs:
                break
            counts["documents_seen"] += 1

            filtered, reason = filter_document(original, counts, use_quality=args.quality_filter)
            if filtered is None:
                reasons[reason] += 1
                # Audit excerpts are also PII-masked to avoid logging raw contacts.
                safe_excerpt, _ = run_mask_emails(original)
                safe_excerpt, _ = run_mask_phone_numbers(safe_excerpt)
                safe_excerpt, _ = run_mask_ips(safe_excerpt)
                rejected_file.write(json.dumps({
                    "url": url,
                    "reason": reason,
                    "excerpt": " ".join(safe_excerpt.split())[:500],
                }, ensure_ascii=False) + "\n")
                continue

            counts["documents_kept"] += 1
            # JSONL preserves embedded newlines for next-stage line deduplication.
            kept_file.write(json.dumps({"url": url, "text": filtered}, ensure_ascii=False) + "\n")
            # One document per line for later tokenization; don't use this for line dedup.
            text_file.write(" ".join(filtered.split()) + "\n")

    report = {
        "input_wet": str(args.wet_path),
        "quality_filter_enabled": args.quality_filter,
        "documents_seen": counts["documents_seen"],
        "documents_kept": counts["documents_kept"],
        "documents_rejected": sum(reasons.values()),
        "keep_rate": round(counts["documents_kept"] / max(1, counts["documents_seen"]), 4),
        "rejected_by_reason": dict(sorted(reasons.items())),
        "passed_stage_counts": {k: v for k, v in sorted(counts.items()) if k.startswith("passed_")},
        "pii_masked": {
            "emails": counts["emails_masked"],
            "phones": counts["phones_masked"],
            "ips": counts["ips_masked"],
        },
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
