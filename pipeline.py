import json
import hashlib
from collections import Counter
from pathlib import Path

from warcio.archiveiterator import ArchiveIterator

from cs336_data.html_extract import extract_text_from_html_bytes
from cs336_data.identify_language import identify_language
from cs336_data.quality import gopher_quality_filter
from cs336_data.classify import classify_nsfw, classify_toxic_speech
from cs336_data.pii import mask_emails, mask_phone_numbers, mask_ips


INPUT = Path("local-shared-data/CC/example.warc.gz")
OUTPUT = Path("data/cleaned.jsonl")


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    stats = Counter()
    seen_hashes = set()

    with INPUT.open("rb") as stream, OUTPUT.open(
        "w", encoding="utf-8"
    ) as out:

        for record in ArchiveIterator(stream):

            if record.rec_type != "response":
                continue

            if record.http_headers is None:
                continue

            content_type = record.http_headers.get_header("Content-Type") or ""

            if "html" not in content_type.lower():
                continue

            stats["html"] += 1

            # 1. 提取网页正文
            try:
                html = record.content_stream().read()
                text = extract_text_from_html_bytes(html)
            except Exception:
                stats["extract_error"] += 1
                continue

            if not text or not text.strip():
                stats["empty"] += 1
                continue

            # 2. 语言识别
            label, score = identify_language(text.replace("\n", " "))

            if label != "en" or score < 0.7:
                stats["language_filtered"] += 1
                continue

            # 3. Gopher 质量过滤
            if not gopher_quality_filter(text):
                stats["quality_filtered"] += 1
                continue

            # 4. 有害内容过滤
            model_text = text.replace("\n", " ")

            nsfw_label, nsfw_score = classify_nsfw(model_text)
            toxic_label, toxic_score = classify_toxic_speech(model_text)

            if (
                (nsfw_label == "nsfw" and nsfw_score >= 0.8)
                or (toxic_label == "toxic" and toxic_score >= 0.8)
            ):
                stats["harmful_filtered"] += 1
                continue

            # 5. PII 脱敏
            text, n_email = mask_emails(text)
            text, n_phone = mask_phone_numbers(text)
            text, n_ip = mask_ips(text)

            stats["pii_replacements"] += n_email + n_phone + n_ip

            # 6. 文档级精确去重
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

            if digest in seen_hashes:
                stats["duplicate_filtered"] += 1
                continue

            seen_hashes.add(digest)

            # 7. 写入 JSONL
            item = {
                "id": record.rec_headers.get_header("WARC-Record-ID"),
                "text": text,
                "language": label,
            }

            out.write(json.dumps(item, ensure_ascii=False) + "\n")

            stats["kept"] += 1

    print("Pipeline statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()


'''
(cs336-data) nan@nan:~/projects/assignment4-data$ uv run python pipeline.py
Pipeline statistics:
html: 19871
language_filtered: 14473
pii_replacements: 4252
kept: 4351
empty: 550
quality_filtered: 475
harmful_filtered: 9
duplicate_filtered: 13
(cs336-data) nan@nan:~/projects/assignment4-data$ ls -lh data/cleaned.jsonl
-rw-r--r-- 1 nan nan 34M Nov  5 21:57 data/cleaned.jsonl
(cs336-data) nan@nan:~/projects/assignment4-data$ wc -l data/cleaned.jsonl
4351 data/cleaned.jsonl
'''