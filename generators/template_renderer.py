from __future__ import annotations

import re
import shutil
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, BadZipFile, ZipFile

from core.database import ROOT_DIR
from core.document_schemas import canonical_document_type, normalize_document_content
from core.meeting_minutes import people_list_to_text


class TemplateRenderError(ValueError):
    """Raised when template-based ODT rendering cannot complete safely."""


PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

DOCUMENT_TEMPLATE_PATHS = {
    "會議紀錄": ROOT_DIR / "templates" / "odt_placeholders" / "meeting_minutes_template.odt",
    "開會通知單": ROOT_DIR / "templates" / "odt_placeholders" / "meeting_notice_template.odt",
    "活動企劃書": ROOT_DIR / "templates" / "odt_placeholders" / "activity_proposal_template.odt",
}


def _resolve_template_path(template_path: Path | str) -> Path:
    path = Path(template_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path


def get_document_template_path(document_type: str) -> Path | None:
    return DOCUMENT_TEMPLATE_PATHS.get(canonical_document_type(document_type))


def load_odt_template(template_path: Path | str) -> dict[str, bytes]:
    path = _resolve_template_path(template_path)
    if not path.exists():
        raise TemplateRenderError(f"找不到 ODT 樣板：{path}")

    try:
        with ZipFile(path) as archive:
            file_map = {name: archive.read(name) for name in archive.namelist()}
    except (BadZipFile, OSError) as exc:
        raise TemplateRenderError(f"ODT 樣板無法讀取：{path}") from exc

    if "content.xml" not in file_map:
        raise TemplateRenderError(f"ODT 樣板缺少 content.xml：{path}")
    return file_map


def copy_odt_template(template_path: Path | str, output_path: Path | str) -> Path:
    source_path = _resolve_template_path(template_path)
    if not source_path.exists():
        raise TemplateRenderError(f"找不到 ODT 樣板：{source_path}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, output_path)
    return output_path


def render_document_odt_template(
    document_type: str,
    document: dict,
    content: dict,
    output_path: Path | str,
) -> Path | None:
    canonical_type = canonical_document_type(document_type)
    template_path = get_document_template_path(canonical_type)
    if template_path is None:
        return None

    normalized_content = normalize_document_content(canonical_type, content)
    context = build_document_template_context(canonical_type, document, normalized_content)
    return render_odt_template(template_path, output_path, context)


def render_odt_template(
    template_path: Path | str,
    output_path: Path | str,
    context: dict,
) -> Path:
    file_map = load_odt_template(template_path)
    content_xml = file_map["content.xml"].decode("utf-8")

    def replace(match: re.Match) -> str:
        key = match.group(1)
        return _odt_text(context.get(key, "無"))

    rendered_content = PLACEHOLDER_PATTERN.sub(replace, content_xml)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(output_path, "w") as archive:
        mimetype = file_map.get("mimetype")
        if mimetype:
            archive.writestr("mimetype", mimetype, compress_type=ZIP_STORED)
        for path, file_content in file_map.items():
            if path == "mimetype":
                continue
            if path == "content.xml":
                file_content = rendered_content.encode("utf-8")
            archive.writestr(path, file_content, compress_type=ZIP_DEFLATED)

    return output_path


def build_document_template_context(
    document_type: str,
    document: dict,
    content: dict,
) -> dict:
    canonical_type = canonical_document_type(document_type)
    if canonical_type == "會議紀錄":
        return _meeting_minutes_context(document, content)
    if canonical_type == "開會通知單":
        return _meeting_notice_context(document, content)
    if canonical_type == "活動企劃書":
        return _activity_proposal_context(document, content)
    raise TemplateRenderError(f"不支援樣板填入的文件類型：{document_type}")


def _text(value, empty: str = "無") -> str:
    if value is None:
        return empty
    if isinstance(value, list):
        return _format_list(value) or empty
    if isinstance(value, dict):
        return _format_dict(value) or empty
    text = str(value).strip()
    return text or empty


def _optional_text(value) -> str:
    return _text(value, empty="")


def _odt_text(value) -> str:
    escaped = escape(_text(value))
    return escaped.replace("\n", "<text:line-break/>")


def _people(values) -> str:
    return people_list_to_text(values) or "無"


def _format_list(values: list) -> str:
    rows = []
    for index, item in enumerate(values, start=1):
        if isinstance(item, dict):
            formatted = _format_dict(item)
        else:
            formatted = str(item).strip()
        if formatted:
            rows.append(f"{index}. {formatted}")
    return "\n".join(rows)


def _format_dict(value: dict) -> str:
    parts = []
    for key, item in value.items():
        text = str(item or "").strip()
        if text:
            parts.append(f"{key}：{text}")
    return "｜".join(parts)


def _meeting_minutes_context(document: dict, content: dict) -> dict:
    return {
        "organization_name": _text(document.get("club_name") or "ODFlow示範社團"),
        "club_name": _text(document.get("club_name") or "ODFlow示範社團"),
        "meeting_title": _text(content.get("meeting_title") or document.get("title")),
        "meeting_date": _text(content.get("meeting_date"), empty=""),
        "meeting_time": _text(content.get("meeting_time"), empty=""),
        "physical_location": _text(content.get("physical_location") or content.get("location"), empty=""),
        "online_location": _text(content.get("online_location"), empty=""),
        "chair": _text(content.get("chair"), empty=""),
        "recorder": _text(content.get("recorder"), empty=""),
        "attendees": _people(content.get("attendees")),
        "observers": _people(content.get("observers")),
        "absentees": _people(content.get("absentees")),
        "report_items": _text(content.get("reports")),
        "discussion_items": _format_agenda_items(content.get("agenda_items", [])),
        "motions": _text(content.get("motions")),
        "supplements": _meeting_supplements(content),
    }


def _meeting_notice_context(document: dict, content: dict) -> dict:
    organization_name = content.get("organization_name") or document.get("club_name") or "ODFlow示範社團"
    return {
        "organization_name": _text(organization_name),
        "club_name": _text(document.get("club_name") or organization_name),
        "recipient": _text(content.get("recipient"), empty=""),
        "document_date": _text(content.get("document_date"), empty=""),
        "document_number": _text(content.get("document_number"), empty=""),
        "priority": _text(content.get("priority"), empty=""),
        "security_level": _text(content.get("security_level"), empty=""),
        "attachments": _text(content.get("attachments"), empty=""),
        "meeting_reason": _text(content.get("meeting_reason"), empty=""),
        "meeting_datetime": _text(content.get("meeting_datetime"), empty=""),
        "meeting_location": _text(content.get("meeting_location"), empty=""),
        "host": _text(content.get("host"), empty=""),
        "contact_person": _text(content.get("contact_person"), empty=""),
        "contact_phone": _text(content.get("contact_phone"), empty=""),
        "attendees": _people(content.get("attendees")),
        "observers": _people(content.get("observers")),
        "note": _text(content.get("note"), empty=""),
    }


def _activity_proposal_context(document: dict, content: dict) -> dict:
    school_name = content.get("school_name") or "臺北市立大學"
    activity_location = content.get("activity_location") or content.get("location")
    return {
        "school_name": _text(school_name),
        "activity_name": _text(content.get("activity_name") or document.get("title")),
        "activity_theme": _text(content.get("activity_theme"), empty=""),
        "purpose": _text(content.get("purpose")),
        "expected_benefits": _text(content.get("expected_benefits") or content.get("expected_outcomes")),
        "advisor_unit": _text(content.get("advisor_unit"), empty=""),
        "organizer": _text(content.get("organizer"), empty=""),
        "co_organizer": _text(content.get("co_organizer"), empty=""),
        "target_audience": _text(content.get("target_audience"), empty=""),
        "activity_content": _text(content.get("activity_content") or content.get("activity_description")),
        "activity_location": _text(activity_location, empty=""),
        "schedule_table": _format_rows(
            content.get("schedule_items", []),
            [("time", "時間"), ("item", "內容"), ("owner", "負責人"), ("note", "備註")],
        ),
        "contact_table": _format_rows(
            content.get("contact_items", []),
            [("role", "職務"), ("name", "姓名"), ("phone", "電話"), ("email", "Email")],
        ),
        "promotion_plan": _text(content.get("promotion_plan")),
        "preparation_table": _format_rows(
            content.get("preparation_items") or content.get("staff_assignments", []),
            [("task", "工作項目"), ("owner", "負責人"), ("deadline", "預定進度"), ("note", "備註")],
            fallback_columns=[("role", "角色"), ("name", "姓名"), ("task", "工作內容")],
        ),
        "budget_table": _format_rows(
            content.get("budget_rows") or content.get("budget_items", []),
            [
                ("item", "項目"),
                ("description", "說明"),
                ("quantity", "數量"),
                ("unit_price", "單價"),
                ("amount", "金額"),
                ("funding_source", "經費來源"),
                ("note", "備註"),
            ],
        ),
        "equipment_list": _text(content.get("equipment_list") or content.get("resource_needs")),
        "school_support": _text(content.get("school_support")),
        "attachments": _text(content.get("attachments") or content.get("notes")),
    }


def _format_agenda_items(rows: list[dict]) -> str:
    output = []
    for index, item in enumerate(rows or [], start=1):
        title = _text(item.get("title"), empty=f"案由{index}")
        discussion = _text(item.get("discussion"))
        decision = _text(item.get("decision"))
        output.append(f"{index}. 案由：{title}\n   說明｜{discussion}\n   決議｜{decision}")
    return "\n\n".join(output) or "無"


def _meeting_supplements(content: dict) -> str:
    parts = []
    if content.get("notes"):
        parts.append(_text(content.get("notes")))
    if content.get("next_meeting_time"):
        parts.append(f"下次會議時間：{_text(content.get('next_meeting_time'))}")
    if content.get("adjournment_time"):
        parts.append(f"散會時間：{_text(content.get('adjournment_time'))}")
    return "\n".join(parts) or "無"


def _format_rows(
    rows: list[dict],
    columns: list[tuple[str, str]],
    fallback_columns: list[tuple[str, str]] | None = None,
) -> str:
    visible_rows = []
    for index, row in enumerate(rows or [], start=1):
        active_columns = columns
        if fallback_columns and not any(str((row or {}).get(key, "")).strip() for key, _ in columns):
            active_columns = fallback_columns
        values = [
            f"{label}：{_optional_text((row or {}).get(key))}"
            for key, label in active_columns
            if _optional_text((row or {}).get(key))
        ]
        if values:
            visible_rows.append(f"{index}. " + "｜".join(values))
    return "\n".join(visible_rows) or "無"
