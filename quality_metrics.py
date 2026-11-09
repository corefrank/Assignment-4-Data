stats = {
    "html": 19871,
    "empty": 550,
    "language_filtered": 14473,
    "quality_filtered": 475,
    "harmful_filtered": 9,
    "duplicate_filtered": 13,
    "pii_replacements": 4252,
    "kept": 4351,
}

stages = [
    ("Empty", "empty"),
    ("Language", "language_filtered"),
    ("Gopher", "quality_filtered"),
    ("Harmful", "harmful_filtered"),
    ("Deduplication", "duplicate_filtered"),
]

total = stats["html"]
remaining = total

for name, key in stages:
    dropped = stats[key]

    rejection_rate = dropped / remaining
    remaining -= dropped

    print(
        f"{name:15s} "
        f"Dropped: {dropped:6d} "
        f"Rejection Rate: {rejection_rate:.2%} "
        f"Remaining: {remaining}"
    )

assert remaining == stats["kept"]

retention_rate = stats["kept"] / total
print(f"\nOverall Retention Rate: {retention_rate:.2%}")

print(f"PII Replacements: {stats['pii_replacements']}")
"""
(cs336-data) nan@nan:~/projects/assignment4-data$ uv run python quality_metrics.py
Empty           Dropped:    550 Rejection Rate: 2.77% Remaining: 19321
Language        Dropped:  14473 Rejection Rate: 74.91% Remaining: 4848
Gopher          Dropped:    475 Rejection Rate: 9.80% Remaining: 4373
Harmful         Dropped:      9 Rejection Rate: 0.21% Remaining: 4364
Deduplication   Dropped:     13 Rejection Rate: 0.30% Remaining: 4351

Overall Retention Rate: 21.90%
PII Replacements: 4252
"""