"""从 CS336 示例 WARC 中随机抽取 20 篇发生 PII 替换的网页，生成审核表。

在 assignment4-data 项目根目录运行：uv run python sample_pii_audit.py
只用于本地审核。结果可能含有真实敏感信息，不要公开上传。
"""
import csv
import gzip
import random
from pathlib import Path

from warcio.archiveiterator import ArchiveIterator
from cs336_data.html_extract import extract_text_from_html_bytes
from cs336_data.pii import mask_emails, mask_phone_numbers, mask_ips

WARC_PATH = Path("local-shared-data/CC/example.warc.gz")
OUTPUT_PATH = Path("pii_audit.csv")
SAMPLE_SIZE = 20
rng = random.Random(336)


def main() -> None:
    if not WARC_PATH.exists():
        raise FileNotFoundError(
            f"找不到 {WARC_PATH}。先执行 ls -lh {WARC_PATH}，"
            "确认是否已下载官方 WARC 示例文件。"
        )

    samples = []
    html_count = 0
    matched_count = 0
    extraction_errors = 0

    with gzip.open(WARC_PATH, "rb") as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type != "response":
                continue

            content_type = ""
            if record.http_headers is not None:
                content_type = record.http_headers.get_header("Content-Type") or ""
            if "html" not in content_type.lower():
                continue

            html_count += 1
            try:
                html_bytes = record.content_stream().read()
                original = extract_text_from_html_bytes(html_bytes)
            except Exception:
                extraction_errors += 1
                continue

            if not original or not original.strip():
                continue

            masked, n_emails = mask_emails(original)
            masked, n_phones = mask_phone_numbers(masked)
            masked, n_ips = mask_ips(masked)
            if n_emails + n_phones + n_ips == 0:
                continue

            matched_count += 1
            item = {
                "url": record.rec_headers.get_header("WARC-Target-URI") or "",
                "email_count": n_emails,
                "phone_count": n_phones,
                "ip_count": n_ips,
                "original_text": original,
                "masked_text": masked,
                "manual_result": "",
                "error_notes": "",
            }

            # 蓄水池抽样：所有符合条件的网页被抽中的机会相同
            if len(samples) < SAMPLE_SIZE:
                samples.append(item)
            else:
                index = rng.randrange(matched_count)
                if index < SAMPLE_SIZE:
                    samples[index] = item

    fieldnames = [
        "sample_id", "url", "email_count", "phone_count", "ip_count",
        "original_text", "masked_text", "manual_result", "error_notes",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for i, item in enumerate(samples, start=1):
            writer.writerow({"sample_id": i, **item})

    print(f"读取到的 HTML 响应记录：{html_count}")
    print(f"HTML 提取异常记录：{extraction_errors}")
    print(f"至少发生 1 次脱敏的网页：{matched_count}")
    print(f"随机抽样的网页：{len(samples)}")
    print(f"审核表已保存：{OUTPUT_PATH.resolve()}")
    if len(samples) < SAMPLE_SIZE:
        print("提示：样本不足 20；需要更多 WARC 数据，不能假称已完成 20 条审核。")


if __name__ == "__main__":
    main()
