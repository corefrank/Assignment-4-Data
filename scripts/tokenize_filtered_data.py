"""CS336 A4: tokenize deduplicated JSONL into GPT-2 uint16 LM training data.

The tokenizer uses tiktoken's 'gpt2' encoding and writes one EOS (50256)
after each document. It also validates that the resulting .bin can be read.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import tiktoken


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert deduped.jsonl to GPT-2 uint16 token bin")
    parser.add_argument("input_jsonl", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.input_jsonl.is_file():
        parser.error(f"Input file not found: {args.input_jsonl}")
    if args.output.exists():
        parser.error(f"Refusing to overwrite existing output: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    tokenizer = tiktoken.get_encoding("gpt2")
    eos_id = tokenizer.eot_token   # 50256 in GPT-2
    documents = 0
    tokens = 0
    output_tmp = args.output.with_name(args.output.name + ".tmp")

    if output_tmp.exists():
        parser.error(f"Temporary file already exists: {output_tmp}")

    try:
        with args.input_jsonl.open("r", encoding="utf-8") as source, output_tmp.open("wb") as sink:
            for line_number, line in enumerate(source, 1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON at line {line_number}") from exc
                text = item.get("text")
                if not isinstance(text, str):
                    raise ValueError(f"Missing text field at line {line_number}")
                if not text.strip():
                    continue

                # Treat literal special-token strings in web text as ordinary text.
                ids = tokenizer.encode(text, disallowed_special=())
                ids.append(eos_id)
                np.asarray(ids, dtype="<u2").tofile(sink)
                documents += 1
                tokens += len(ids)
        output_tmp.replace(args.output)
    except BaseException:
        output_tmp.unlink(missing_ok=True)
        raise

    result = np.memmap(args.output, dtype="<u2", mode="r") if tokens else np.empty(0, dtype="<u2")
    eos_count = int(np.count_nonzero(result == eos_id))
    if len(result) != tokens or eos_count < documents:
        raise RuntimeError("Token bin validation failed")

    summary = {
        "input_jsonl": str(args.input_jsonl),
        "output_bin": str(args.output),
        "tokenizer": "gpt2",
        "dtype": "uint16",
        "documents": documents,
        "tokens": tokens,
        "eos_id": eos_id,
        "eos_occurrences": eos_count,
        "file_size_bytes": args.output.stat().st_size,
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }
    summary_path = args.output.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
