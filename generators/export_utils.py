from __future__ import annotations

from pathlib import Path

from core.database import ROOT_DIR
from core.filename import build_versioned_filename, parse_meeting_date
from core.meeting_minutes import normalize_meeting_minutes_content


DEFAULT_GENERATED_DIR = ROOT_DIR / "data" / "generated"
DEFAULT_CLUB_NAME = "未設定社團"
REQUIRED_CONTENT_KEYS = {
    "meeting_title",
    "meeting_date",
    "meeting_time",
    "location",
    "chair",
    "recorder",
    "attendees",
    "absentees",
    "agenda_items",
    "action_items",
    "next_meeting_time",
    "notes",
}


def validate_export_payload(document: dict, version: dict) -> tuple[dict, dict]:
    if not document:
        raise ValueError("文件不存在")
    if not version:
        raise ValueError("版本不存在")

    content_json = version.get("content_json")
    if not isinstance(content_json, dict):
        raise ValueError("content_json 格式不完整")
    missing_keys = REQUIRED_CONTENT_KEYS.difference(content_json)
    if missing_keys:
        raise ValueError(
            "content_json 格式不完整，缺少欄位："
            + ", ".join(sorted(missing_keys))
        )

    normalized_content = normalize_meeting_minutes_content(content_json)
    normalized_version = {**version, "content_json": normalized_content}

    if not normalized_version.get("version_number"):
        raise ValueError("版本資訊不完整")

    return document, normalized_version


def prepare_output_path(
    document: dict,
    version: dict,
    extension: str,
    output_dir: Path | str | None = None,
) -> Path:
    _, normalized_version = validate_export_payload(document, version)

    output_dir_path = Path(output_dir) if output_dir is not None else DEFAULT_GENERATED_DIR
    output_dir_path.mkdir(parents=True, exist_ok=True)

    content_json = normalized_version["content_json"]
    filename = build_versioned_filename(
        club_name=document.get("club_name") or DEFAULT_CLUB_NAME,
        document_type=document.get("document_type") or "文件",
        subject=content_json.get("meeting_title") or document.get("title") or "未命名會議",
        version=normalized_version["version_number"],
        extension=extension,
        target_date=parse_meeting_date(content_json.get("meeting_date")),
    )
    return output_dir_path / filename
