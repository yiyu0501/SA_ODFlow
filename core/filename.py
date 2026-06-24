from __future__ import annotations

from datetime import date


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
    return (
        f"{roc_date_string(target_date)}_{club_name}_{document_type}_{subject}"
        f"_v{version}.{safe_extension}"
    )
