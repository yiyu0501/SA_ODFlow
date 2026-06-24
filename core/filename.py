from __future__ import annotations

import re
from datetime import date
from datetime import datetime


UNSAFE_FILENAME_CHARS_PATTERN = re.compile(r'[\\/:*?"<>|\r\n\t]+')


def sanitize_filename_component(value: str, fallback: str = "untitled") -> str:
    normalized = UNSAFE_FILENAME_CHARS_PATTERN.sub("_", str(value).strip())
    normalized = re.sub(r"\s+", " ", normalized).strip(" ._")
    return normalized or fallback


def parse_meeting_date(value: str | None) -> date | None:
    if not value:
        return None

    normalized = value.strip()
    for pattern in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(normalized, pattern).date()
        except ValueError:
            continue

    month_day_match = re.fullmatch(r"(\d{1,2})月(\d{1,2})日", normalized)
    if month_day_match:
        today = date.today()
        return date(today.year, int(month_day_match.group(1)), int(month_day_match.group(2)))

    return None


def roc_date_string(target_date: date | None = None) -> str:
    target_date = target_date or date.today()
    roc_year = target_date.year - 1911
    return f"{roc_year:03d}{target_date.month:02d}{target_date.day:02d}"


def build_versioned_filename(
    club_name: str,
    document_type: str,
    subject: str,
    version: int,
    extension: str,
    target_date: date | None = None,
) -> str:
    safe_extension = extension.lstrip(".")
    safe_club_name = sanitize_filename_component(club_name, fallback="未設定社團")
    safe_document_type = sanitize_filename_component(document_type, fallback="文件")
    safe_subject = sanitize_filename_component(subject, fallback="未命名主題")
    return (
        f"{roc_date_string(target_date)}_{safe_club_name}_{safe_document_type}_{safe_subject}"
        f"_v{version}.{safe_extension}"
    )
