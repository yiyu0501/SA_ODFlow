from __future__ import annotations

from pathlib import Path

from core.database import ROOT_DIR
from core.filename import build_versioned_filename
from core.document_schemas import (
    derive_document_title,
    get_document_primary_date,
    normalize_document_content,
)


DEFAULT_GENERATED_DIR = ROOT_DIR / "data" / "generated"
DEFAULT_CLUB_NAME = "未設定社團"


def validate_export_payload(document: dict, version: dict) -> tuple[dict, dict]:
    if not document:
        raise ValueError("文件不存在")
    if not version:
        raise ValueError("版本不存在")

    document_type = document.get("document_type") or "文件"
    content_json = version.get("content_json")
    if not isinstance(content_json, dict):
        raise ValueError("content_json 格式不完整")

    normalized_content = normalize_document_content(document_type, content_json)
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
    validated_document, normalized_version = validate_export_payload(document, version)

    output_dir_path = Path(output_dir) if output_dir is not None else DEFAULT_GENERATED_DIR
    output_dir_path.mkdir(parents=True, exist_ok=True)

    content_json = normalized_version["content_json"]
    document_type = validated_document.get("document_type") or "文件"
    filename = build_versioned_filename(
        club_name=validated_document.get("club_name") or DEFAULT_CLUB_NAME,
        document_type=document_type,
        subject=derive_document_title(
            document_type,
            content_json,
            fallback=validated_document.get("title") or "未命名文件",
        ),
        version=normalized_version["version_number"],
        extension=extension,
        target_date=get_document_primary_date(document_type, content_json),
    )
    return output_dir_path / filename
