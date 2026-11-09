
import re

# 1. 邮箱匹配规则
# 简化版
#EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9._%+-])"
    r"[A-Za-z0-9._%+-]+"
    r"@"
    r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*"
    r"\.[A-Za-z]{2,}"
    r"(?![A-Za-z0-9_-])"
)

# 2. 电话号码匹配规则（以作业中的10位号码为目标）

#PHONE_RE = re.compile(r"\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}")


PHONE_RE = re.compile(
    r"(?<!\w)(?:\(\d{3}\)[ -]?|\d{3}[ -]?)\d{3}[ -]?\d{4}(?!\w)"
)

# 3. IPv4 地址匹配规则

#IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

OCTET = r"(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)"

IP_RE = re.compile(
    rf"(?<![\w.]){OCTET}(?:\.{OCTET}){{3}}(?!\w|\.\d)"
)


def mask_emails(text: str) -> tuple[str, int]:
    return EMAIL_RE.subn("|||EMAIL_ADDRESS|||", text)


def mask_phone_numbers(text: str) -> tuple[str, int]:
    return PHONE_RE.subn("|||PHONE_NUMBER|||", text)


def mask_ips(text: str) -> tuple[str, int]:
    return IP_RE.subn("|||IP_ADDRESS|||", text)
