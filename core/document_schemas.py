from __future__ import annotations

from copy import deepcopy
from datetime import date

from core.filename import parse_meeting_date
from core.meeting_minutes import normalize_meeting_minutes_content, people_list_to_text, split_people_text


def _field(key: str, label: str, input_type: str = "text") -> dict:
    return {"key": key, "label": label, "input_type": input_type}


def _repeatable_section(
    key: str,
    label: str,
    columns: list[tuple[str, str]],
    min_items: int = 1,
) -> dict:
    return {
        "key": key,
        "label": label,
        "columns": [{"key": column_key, "label": column_label} for column_key, column_label in columns],
        "min_items": min_items,
    }


DOCUMENT_SCHEMAS = {
    "會議紀錄": {
        "document_type": "會議紀錄",
        "display_name": "會議紀錄",
        "default_title": "會議紀錄",
        "recommended_evaluation_category": "2.社團行政_管理運作",
        "fields": [
            _field("meeting_title", "會議名稱"),
            _field("meeting_date", "會議日期"),
            _field("meeting_time", "會議時間"),
            _field("location", "會議地點"),
            _field("chair", "主席"),
            _field("recorder", "紀錄"),
            _field("attendees", "出席人員", "people_list"),
            _field("absentees", "請假人員", "people_list"),
            _field("next_meeting_time", "下次會議時間"),
            _field("notes", "備註", "textarea"),
        ],
        "repeatable_sections": [
            _repeatable_section(
                "agenda_items",
                "討論事項",
                [
                    ("title", "議題"),
                    ("discussion", "討論"),
                    ("decision", "決議"),
                ],
            ),
            _repeatable_section(
                "action_items",
                "待辦事項",
                [
                    ("task", "待辦"),
                    ("owner", "負責人"),
                    ("deadline", "期限"),
                    ("note", "備註"),
                ],
            ),
        ],
        "output_formats": ["ODT", "PDF"],
    },
    "活動企劃書": {
        "document_type": "活動企劃書",
        "display_name": "活動企劃書",
        "default_title": "活動企劃書",
        "recommended_evaluation_category": "6.社團活動_社團活動",
        "fields": [
            _field("activity_name", "活動名稱"),
            _field("activity_date", "活動日期"),
            _field("activity_time", "活動時間"),
            _field("location", "活動地點"),
            _field("organizer", "主辦單位"),
            _field("target_audience", "活動對象"),
            _field("purpose", "活動目的", "textarea"),
            _field("activity_description", "活動說明", "textarea"),
            _field("expected_outcomes", "預期成果", "textarea"),
            _field("notes", "備註", "textarea"),
        ],
        "repeatable_sections": [
            _repeatable_section(
                "schedule_items",
                "流程規劃",
                [
                    ("time", "時間"),
                    ("item", "項目"),
                    ("owner", "負責人"),
                    ("note", "備註"),
                ],
            ),
            _repeatable_section(
                "staff_assignments",
                "工作分工",
                [
                    ("role", "角色"),
                    ("name", "姓名"),
                    ("task", "工作內容"),
                ],
            ),
            _repeatable_section(
                "budget_items",
                "預算規劃",
                [
                    ("item", "項目"),
                    ("amount", "金額"),
                    ("note", "備註"),
                ],
            ),
        ],
        "output_formats": ["ODT", "PDF"],
    },
    "活動成果報告": {
        "document_type": "活動成果報告",
        "display_name": "活動成果報告",
        "default_title": "活動成果報告",
        "recommended_evaluation_category": "6.社團活動_社團活動",
        "fields": [
            _field("activity_name", "活動名稱"),
            _field("activity_date", "活動日期"),
            _field("location", "活動地點"),
            _field("participant_count", "參與人數"),
            _field("organizer", "主辦單位"),
            _field("activity_summary", "活動摘要", "textarea"),
            _field("outcomes", "成果說明", "textarea"),
            _field("photos_or_links", "照片或連結", "textarea"),
            _field("feedback_summary", "回饋摘要", "textarea"),
            _field("expense_summary", "經費摘要", "textarea"),
            _field("improvement_notes", "改進建議", "textarea"),
            _field("notes", "備註", "textarea"),
        ],
        "repeatable_sections": [],
        "output_formats": ["ODT", "PDF"],
    },
    "活動檢討會紀錄": {
        "document_type": "活動檢討會紀錄",
        "display_name": "活動檢討會紀錄",
        "default_title": "活動檢討會紀錄",
        "recommended_evaluation_category": "6.社團活動_社團活動",
        "fields": [
            _field("meeting_title", "會議名稱"),
            _field("meeting_date", "會議日期"),
            _field("activity_name", "活動名稱"),
            _field("attendees", "與會人員", "people_list"),
            _field("strengths", "優點", "textarea"),
            _field("problems", "問題", "textarea"),
            _field("next_time_suggestions", "下次建議", "textarea"),
            _field("notes", "備註", "textarea"),
        ],
        "repeatable_sections": [
            _repeatable_section(
                "improvement_actions",
                "改善行動",
                [
                    ("issue", "問題"),
                    ("action", "改善方式"),
                    ("owner", "負責人"),
                    ("deadline", "期限"),
                ],
            ),
        ],
        "output_formats": ["ODT", "PDF"],
    },
    "年度計畫": {
        "document_type": "年度計畫",
        "display_name": "年度計畫",
        "default_title": "年度計畫",
        "recommended_evaluation_category": "4.社團行政_年度計畫",
        "fields": [
            _field("academic_year", "學年度"),
            _field("club_name", "社團名稱"),
            _field("annual_goal", "年度目標", "textarea"),
            _field("expected_outcomes", "預期成果", "textarea"),
            _field("resource_needs", "資源需求", "textarea"),
            _field("notes", "備註", "textarea"),
        ],
        "repeatable_sections": [
            _repeatable_section(
                "semester_plans",
                "學期規劃",
                [
                    ("semester", "學期"),
                    ("plan", "計畫"),
                    ("expected_month", "預計月份"),
                    ("owner", "負責人"),
                ],
            ),
            _repeatable_section(
                "key_activities",
                "重點活動",
                [
                    ("activity_name", "活動名稱"),
                    ("month", "月份"),
                    ("purpose", "目的"),
                ],
            ),
        ],
        "output_formats": ["ODT", "PDF"],
    },
}


for schema in DOCUMENT_SCHEMAS.values():
    schema["storage_keys"] = [
        *(field["key"] for field in schema["fields"]),
        *(section["key"] for section in schema["repeatable_sections"]),
    ]


def list_document_schemas() -> list[dict]:
    return [deepcopy(schema) for schema in DOCUMENT_SCHEMAS.values()]


def list_supported_document_types() -> list[str]:
    return list(DOCUMENT_SCHEMAS.keys())


def get_document_schema(document_type: str) -> dict:
    schema = DOCUMENT_SCHEMAS.get(document_type)
    if schema is None:
        raise ValueError(f"不支援的文件類型: {document_type}")
    return deepcopy(schema)


def is_supported_document_type(document_type: str) -> bool:
    return document_type in DOCUMENT_SCHEMAS


def get_recommended_evaluation_category(document_type: str) -> str:
    return get_document_schema(document_type)["recommended_evaluation_category"]


def get_default_document_content(document_type: str) -> dict:
    schema = get_document_schema(document_type)
    content = {field["key"]: _default_value_for_field(field) for field in schema["fields"]}
    for section in schema["repeatable_sections"]:
        content[section["key"]] = _default_repeatable_rows(section)
    return content


def get_document_storage_keys(document_type: str) -> list[str]:
    if document_type not in DOCUMENT_SCHEMAS:
        return []
    return list(DOCUMENT_SCHEMAS[document_type]["storage_keys"])


def normalize_document_content(document_type: str, content: dict | None) -> dict:
    if document_type == "會議紀錄":
        return normalize_meeting_minutes_content(content)

    if document_type not in DOCUMENT_SCHEMAS:
        return _normalize_generic_content(content)

    schema = DOCUMENT_SCHEMAS[document_type]
    normalized = get_default_document_content(document_type)
    content = content or {}

    for field in schema["fields"]:
        key = field["key"]
        input_type = field["input_type"]
        if input_type == "people_list":
            normalized[key] = split_people_text(content.get(key))
        else:
            normalized[key] = str(content.get(key, "")).strip()

    for section in schema["repeatable_sections"]:
        normalized[section["key"]] = _normalize_repeatable_rows(
            content.get(section["key"]),
            section,
        )

    if "document_title" in content:
        normalized["document_title"] = str(content.get("document_title", "")).strip()

    return normalized


def derive_document_title(
    document_type: str,
    content: dict | None,
    fallback: str | None = None,
) -> str:
    normalized = normalize_document_content(document_type, content)
    custom_title = str(normalized.get("document_title", "")).strip()
    if custom_title:
        return custom_title

    if document_type == "會議紀錄":
        title = normalized.get("meeting_title", "")
    elif document_type == "活動企劃書":
        activity_name = normalized.get("activity_name", "")
        title = f"{activity_name} 活動企劃書".strip() if activity_name else ""
    elif document_type == "活動成果報告":
        activity_name = normalized.get("activity_name", "")
        title = f"{activity_name} 活動成果報告".strip() if activity_name else ""
    elif document_type == "活動檢討會紀錄":
        title = normalized.get("meeting_title", "")
        if not title and normalized.get("activity_name"):
            title = f"{normalized['activity_name']} 活動檢討會紀錄"
    elif document_type == "年度計畫":
        academic_year = normalized.get("academic_year", "")
        club_name = normalized.get("club_name", "")
        if academic_year and club_name:
            title = f"{academic_year} {club_name} 年度計畫"
        elif club_name:
            title = f"{club_name} 年度計畫"
        else:
            title = ""
    else:
        title = _derive_generic_title(normalized)

    if title:
        return title
    if fallback:
        return str(fallback).strip()
    return DOCUMENT_SCHEMAS.get(document_type, {}).get("default_title", "文件")


def get_document_primary_date(document_type: str, content: dict | None) -> date | None:
    normalized = normalize_document_content(document_type, content)
    if document_type == "年度計畫":
        return None

    date_field = {
        "會議紀錄": "meeting_date",
        "活動企劃書": "activity_date",
        "活動成果報告": "activity_date",
        "活動檢討會紀錄": "meeting_date",
    }.get(document_type)
    if date_field is None:
        return None
    return parse_meeting_date(normalized.get(date_field))


def build_document_preview_blocks(
    document_type: str,
    content: dict | None,
    title_override: str | None = None,
) -> list[dict]:
    normalized = normalize_document_content(document_type, content)
    title = title_override or derive_document_title(document_type, normalized)

    builders = {
        "會議紀錄": _build_meeting_minutes_blocks,
        "活動企劃書": _build_activity_proposal_blocks,
        "活動成果報告": _build_activity_report_blocks,
        "活動檢討會紀錄": _build_activity_review_blocks,
        "年度計畫": _build_annual_plan_blocks,
    }
    builder = builders.get(document_type)
    if builder is None:
        raise ValueError(f"不支援此文件類型的預覽輸出: {document_type}")

    return [{"kind": "title", "text": title}, *builder(normalized)]


def _default_value_for_field(field: dict):
    if field["input_type"] == "people_list":
        return []
    return ""


def _default_repeatable_rows(section: dict) -> list[dict]:
    minimum = max(int(section.get("min_items", 1)), 1)
    template = {column["key"]: "" for column in section["columns"]}
    return [template.copy() for _ in range(minimum)]


def _normalize_repeatable_rows(rows, section: dict) -> list[dict]:
    normalized_rows = []
    for row in rows or []:
        normalized_row = {
            column["key"]: str((row or {}).get(column["key"], "")).strip()
            for column in section["columns"]
        }
        if any(normalized_row.values()):
            normalized_rows.append(normalized_row)

    return normalized_rows or _default_repeatable_rows(section)


def _normalize_generic_content(content: dict | None) -> dict:
    if not isinstance(content, dict):
        return {}

    normalized = {}
    for key, value in content.items():
        if isinstance(value, str):
            normalized[key] = value.strip()
        elif isinstance(value, list):
            normalized[key] = deepcopy(value)
        elif isinstance(value, dict):
            normalized[key] = deepcopy(value)
        else:
            normalized[key] = "" if value is None else str(value).strip()
    return normalized


def _derive_generic_title(content: dict) -> str:
    for key in ("title", "document_title", "name", "subject"):
        value = str(content.get(key, "")).strip()
        if value:
            return value
    return ""


def _paragraph(text: str) -> dict:
    return {"kind": "paragraph", "text": text}


def _heading(text: str, level: int = 2) -> dict:
    return {"kind": "heading", "text": text, "level": level}


def _list_block(items: list[str]) -> dict:
    return {"kind": "bullet_list", "items": items}


def _build_meeting_minutes_blocks(content: dict) -> list[dict]:
    blocks = _build_label_value_blocks(
        [
            ("會議名稱", content["meeting_title"]),
            ("會議日期", content["meeting_date"]),
            ("會議時間", content["meeting_time"]),
            ("會議地點", content["location"]),
            ("主席", content["chair"]),
            ("紀錄", content["recorder"]),
            ("出席人員", people_list_to_text(content["attendees"]) or "-"),
            ("請假人員", people_list_to_text(content["absentees"]) or "-"),
        ]
    )
    blocks.append(_heading("討論事項與決議"))
    for index, item in enumerate(content["agenda_items"], start=1):
        blocks.extend(
            [
                _paragraph(f"{index}. 議題：{item['title'] or '-'}"),
                _paragraph(f"討論：{item['discussion'] or '-'}"),
                _paragraph(f"決議：{item['decision'] or '-'}"),
            ]
        )
    blocks.append(_heading("待辦事項"))
    blocks.append(
        _list_block(
            [
                (
                    f"{index}. {item['task'] or '未填寫'} / 負責人：{item['owner'] or '-'} / "
                    f"期限：{item['deadline'] or '-'} / 備註：{item['note'] or '-'}"
                )
                for index, item in enumerate(content["action_items"], start=1)
            ]
        )
    )
    blocks.extend(
        _build_label_value_blocks(
            [
                ("下次會議時間", content["next_meeting_time"]),
                ("備註", content["notes"]),
            ]
        )
    )
    return blocks


def _build_activity_proposal_blocks(content: dict) -> list[dict]:
    blocks = _build_label_value_blocks(
        [
            ("活動名稱", content["activity_name"]),
            ("活動日期", content["activity_date"]),
            ("活動時間", content["activity_time"]),
            ("活動地點", content["location"]),
            ("主辦單位", content["organizer"]),
            ("活動對象", content["target_audience"]),
        ]
    )
    blocks.extend(
        [
            _heading("活動目的"),
            _paragraph(content["purpose"] or "-"),
            _heading("活動說明"),
            _paragraph(content["activity_description"] or "-"),
            _heading("流程規劃"),
            _list_block(
                [
                    (
                        f"{index}. 時間：{item['time'] or '-'} / 項目：{item['item'] or '-'} / "
                        f"負責人：{item['owner'] or '-'} / 備註：{item['note'] or '-'}"
                    )
                    for index, item in enumerate(content["schedule_items"], start=1)
                ]
            ),
            _heading("工作分工"),
            _list_block(
                [
                    (
                        f"{index}. 角色：{item['role'] or '-'} / 姓名：{item['name'] or '-'} / "
                        f"工作：{item['task'] or '-'}"
                    )
                    for index, item in enumerate(content["staff_assignments"], start=1)
                ]
            ),
            _heading("預算規劃"),
            _list_block(
                [
                    f"{index}. 項目：{item['item'] or '-'} / 金額：{item['amount'] or '-'} / 備註：{item['note'] or '-'}"
                    for index, item in enumerate(content["budget_items"], start=1)
                ]
            ),
            _heading("預期成果"),
            _paragraph(content["expected_outcomes"] or "-"),
            _heading("備註"),
            _paragraph(content["notes"] or "-"),
        ]
    )
    return blocks


def _build_activity_report_blocks(content: dict) -> list[dict]:
    blocks = _build_label_value_blocks(
        [
            ("活動名稱", content["activity_name"]),
            ("活動日期", content["activity_date"]),
            ("活動地點", content["location"]),
            ("參與人數", content["participant_count"]),
            ("主辦單位", content["organizer"]),
        ]
    )
    blocks.extend(
        [
            _heading("活動摘要"),
            _paragraph(content["activity_summary"] or "-"),
            _heading("成果說明"),
            _paragraph(content["outcomes"] or "-"),
            _heading("照片或連結"),
            _paragraph(content["photos_or_links"] or "-"),
            _heading("回饋摘要"),
            _paragraph(content["feedback_summary"] or "-"),
            _heading("經費摘要"),
            _paragraph(content["expense_summary"] or "-"),
            _heading("改進建議"),
            _paragraph(content["improvement_notes"] or "-"),
            _heading("備註"),
            _paragraph(content["notes"] or "-"),
        ]
    )
    return blocks


def _build_activity_review_blocks(content: dict) -> list[dict]:
    blocks = _build_label_value_blocks(
        [
            ("會議名稱", content["meeting_title"]),
            ("會議日期", content["meeting_date"]),
            ("活動名稱", content["activity_name"]),
            ("與會人員", people_list_to_text(content["attendees"]) or "-"),
        ]
    )
    blocks.extend(
        [
            _heading("優點"),
            _paragraph(content["strengths"] or "-"),
            _heading("問題"),
            _paragraph(content["problems"] or "-"),
            _heading("改善行動"),
            _list_block(
                [
                    (
                        f"{index}. 問題：{item['issue'] or '-'} / 改善方式：{item['action'] or '-'} / "
                        f"負責人：{item['owner'] or '-'} / 期限：{item['deadline'] or '-'}"
                    )
                    for index, item in enumerate(content["improvement_actions"], start=1)
                ]
            ),
            _heading("下次建議"),
            _paragraph(content["next_time_suggestions"] or "-"),
            _heading("備註"),
            _paragraph(content["notes"] or "-"),
        ]
    )
    return blocks


def _build_annual_plan_blocks(content: dict) -> list[dict]:
    blocks = _build_label_value_blocks(
        [
            ("學年度", content["academic_year"]),
            ("社團名稱", content["club_name"]),
        ]
    )
    blocks.extend(
        [
            _heading("年度目標"),
            _paragraph(content["annual_goal"] or "-"),
            _heading("學期規劃"),
            _list_block(
                [
                    (
                        f"{index}. 學期：{item['semester'] or '-'} / 計畫：{item['plan'] or '-'} / "
                        f"預計月份：{item['expected_month'] or '-'} / 負責人：{item['owner'] or '-'}"
                    )
                    for index, item in enumerate(content["semester_plans"], start=1)
                ]
            ),
            _heading("重點活動"),
            _list_block(
                [
                    (
                        f"{index}. 活動：{item['activity_name'] or '-'} / 月份：{item['month'] or '-'} / "
                        f"目的：{item['purpose'] or '-'}"
                    )
                    for index, item in enumerate(content["key_activities"], start=1)
                ]
            ),
            _heading("預期成果"),
            _paragraph(content["expected_outcomes"] or "-"),
            _heading("資源需求"),
            _paragraph(content["resource_needs"] or "-"),
            _heading("備註"),
            _paragraph(content["notes"] or "-"),
        ]
    )
    return blocks


def _build_label_value_blocks(items: list[tuple[str, str]]) -> list[dict]:
    return [_paragraph(f"{label}：{value or '-'}") for label, value in items]
