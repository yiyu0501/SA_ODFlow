from __future__ import annotations

from copy import deepcopy

from core.document_schemas import (
    canonical_document_type,
    derive_document_title,
    get_default_document_content,
    normalize_document_content,
)
from generators.document_style import (
    BLANK_LINE_PLACEHOLDER,
    TEXT_PLACEHOLDER,
    display_bullets,
    display_lines,
    display_people,
    display_text,
    ensure_table_rows,
)


def _section(kind: str, **kwargs) -> dict:
    return {"kind": kind, **kwargs}


def _info_rows(pairs: list[tuple[str, str]], columns_per_row: int = 2) -> list[list[str]]:
    rows = []
    row = []
    for label, value in pairs:
        row.extend([label, value])
        if len(row) == columns_per_row * 2:
            rows.append(row)
            row = []
    if row:
        while len(row) < columns_per_row * 2:
            row.extend(["", ""])
        rows.append(row)
    return rows


def build_document_render_spec(
    document_type: str,
    content: dict | None,
    title_override: str | None = None,
) -> dict:
    document_type = canonical_document_type(document_type)
    normalized = normalize_document_content(document_type, content)
    title = title_override or derive_document_title(document_type, normalized)

    builders = {
        "會議紀錄": _build_meeting_minutes_spec,
        "開會通知單": _build_meeting_notice_spec,
        "會議議程": _build_meeting_agenda_spec,
        "活動企劃書": _build_activity_proposal_spec,
        "活動成果報告": _build_activity_report_spec,
        "活動檢討會紀錄": _build_activity_review_spec,
        "年度計畫": _build_annual_plan_spec,
    }
    builder = builders.get(document_type)
    if builder is None:
        raise ValueError(f"不支援此文件類型的正式輸出：{document_type}")
    return {"title": title, "sections": builder(normalized)}


def build_template_render_spec(template_definition: dict) -> dict:
    if template_definition["id"] == "meeting_minutes_template_odt":
        return _build_meeting_minutes_template_spec(template_definition)
    if template_definition["id"] == "meeting_agenda_odt":
        return _build_meeting_agenda_template_spec(template_definition)
    if template_definition["id"] == "club_announcement":
        return _build_club_announcement_template_spec(template_definition)
    if template_definition["id"] == "annual_plan_odt":
        return _build_annual_plan_template_spec(template_definition)
    if template_definition["id"] == "course_record":
        return _build_course_record_template_spec(template_definition)
    if template_definition["id"] == "activity_application_odt":
        return _build_activity_application_template_spec(template_definition)
    if template_definition["id"] == "activity_review_minutes_odt":
        return _build_activity_review_minutes_template_spec(template_definition)

    linked_document_type = template_definition.get("linked_document_type")
    if linked_document_type:
        if template_definition["id"] == "activity_report_odt":
            return _build_activity_result_report_template_spec(template_definition)
        content = get_default_document_content(linked_document_type)
        title = template_definition["name"]
        spec = build_document_render_spec(linked_document_type, content, title_override=title)
        spec["sections"].append(
            _section(
                "note",
                heading="使用說明",
                text="；".join(template_definition.get("instructions", [])) or TEXT_PLACEHOLDER,
            )
        )
        return spec

    if template_definition["id"] == "attendance_sheet_ods":
        return _build_attendance_sheet_template_spec(template_definition)

    special_template_builders = {
        "meeting_notice_odt": lambda: build_document_render_spec(
            "開會通知單",
            get_default_document_content("開會通知單"),
            title_override=template_definition["name"],
        ),
    }
    builder = special_template_builders.get(template_definition["id"])
    if builder is not None:
        spec = builder()
        spec["sections"].append(
            _section(
                "note",
                heading="使用說明",
                text="；".join(template_definition.get("instructions", [])) or TEXT_PLACEHOLDER,
            )
        )
        return spec

    basic_rows = _info_rows(
        [(field, BLANK_LINE_PLACEHOLDER) for field in template_definition.get("basic_fields", [])],
        columns_per_row=1,
    )
    sections = [
        _section(
            "paragraph",
            heading="使用情境",
            paragraphs=[template_definition["usage_description"]],
        ),
        _section("info_table", heading="基本欄位", rows=basic_rows, columns=2),
    ]

    outline_fields = template_definition.get("outline_fields") or []
    if outline_fields:
        sections.append(
            _section(
                "bullet_list",
                heading="主要內容",
                items=[f"{item}：{BLANK_LINE_PLACEHOLDER}" for item in outline_fields],
            )
        )

    sections.append(
        _section(
            "note",
            heading="使用說明",
            text="；".join(template_definition.get("instructions", [])) or TEXT_PLACEHOLDER,
        )
    )
    return {"title": template_definition["name"], "sections": sections}


def build_spreadsheet_template_spec(template_definition: dict) -> dict:
    headers = template_definition.get("table_headers", [])
    title = template_definition["name"]
    base_fields = template_definition.get("basic_fields", [])
    metadata = "　".join(f"{field}：{BLANK_LINE_PLACEHOLDER}" for field in base_fields[:3]) or BLANK_LINE_PLACEHOLDER
    note = "；".join(template_definition.get("instructions", [])) or TEXT_PLACEHOLDER
    blank_rows = 40 if template_definition["id"] == "attendance_sheet_ods" else 8
    if template_definition["id"] == "attendance_sheet_ods":
        headers = ["編號", "姓名", "系級 / 單位", "學號", "聯絡方式", "簽到", "備註"]
    return {
        "title": title,
        "metadata": metadata,
        "note": note,
        "headers": headers,
        "blank_rows": blank_rows,
        "column_count": len(headers),
    }


def _build_meeting_minutes_spec(content: dict) -> list[dict]:
    agenda_rows = ensure_table_rows(
        [
            [
                str(index),
                display_text(item.get("title")),
                display_text(item.get("discussion")),
                display_text(item.get("decision")),
            ]
            for index, item in enumerate(content["agenda_items"], start=1)
        ],
        4,
        minimum_rows=2,
        placeholder="",
    )
    action_rows = ensure_table_rows(
        [
            [
                str(index),
                display_text(item.get("task")),
                display_text(item.get("owner")),
                display_text(item.get("deadline")),
                display_text(item.get("note")),
            ]
            for index, item in enumerate(content["action_items"], start=1)
        ],
        5,
        minimum_rows=3,
        placeholder="",
    )

    return [
        _section(
            "info_table",
            rows=_info_rows(
                [
                    ("會議名稱", display_text(content.get("meeting_title"))),
                    ("會議日期", display_text(content.get("meeting_date"))),
                    ("會議時間", display_text(content.get("meeting_time"))),
                    ("會議地點", display_text(content.get("location"))),
                    ("主席", display_text(content.get("chair"))),
                    ("記錄人員", display_text(content.get("recorder"))),
                    ("出席人員", display_people(content.get("attendees"))),
                    ("請假人員", display_people(content.get("absentees"))),
                    ("列席人員", display_people(content.get("observers"))),
                ]
            ),
            columns=4,
        ),
        _section("paragraph", heading="一、主席致詞", paragraphs=display_lines(content.get("opening_remarks"))),
        _section("paragraph", heading="二、報告事項", paragraphs=display_lines(content.get("reports"))),
        _section(
            "table",
            heading="三、討論事項",
            headers=["編號", "議題", "討論內容", "決議事項"],
            rows=agenda_rows,
        ),
        _section("paragraph", heading="四、決議事項", paragraphs=_decision_paragraphs(content["agenda_items"])),
        _section("paragraph", heading="五、臨時動議", paragraphs=display_lines(content.get("motions"))),
        _section(
            "table",
            heading="六、待辦事項",
            headers=["編號", "事項", "負責人", "期限", "狀態 / 備註"],
            rows=action_rows,
        ),
        _section(
            "lines",
            heading="七、散會與備註",
            lines=[
                f"散會時間：{display_text(content.get('adjournment_time'))}",
                f"下次會議時間：{display_text(content.get('next_meeting_time'))}",
                f"備註：{display_text(content.get('notes'))}",
            ],
        ),
    ]


def _build_meeting_notice_spec(content: dict) -> list[dict]:
    return [
        _section(
            "info_table",
            rows=_info_rows(
                [
                    ("發文單位", display_text(content.get("organization_name"))),
                    ("受文者", display_text(content.get("recipient"))),
                    ("發文日期", display_text(content.get("document_date"))),
                    ("發文字號", display_text(content.get("document_number"))),
                    ("速別", display_text(content.get("priority"))),
                    ("密等及解密條件或保密期限", display_text(content.get("security_level"))),
                    ("附件", display_text(content.get("attachments"))),
                    ("開會事由", display_text(content.get("meeting_reason"))),
                    ("開會時間", display_text(content.get("meeting_datetime"))),
                    ("開會地點", display_text(content.get("meeting_location"))),
                    ("主持人", display_text(content.get("host"))),
                    ("聯絡人", display_text(content.get("contact_person"))),
                    ("聯絡電話", display_text(content.get("contact_phone"))),
                    ("出席者", display_people(content.get("attendees"))),
                    ("列席者", display_people(content.get("observers"))),
                    ("備註", display_text(content.get("note"))),
                ],
                columns_per_row=1,
            ),
            columns=2,
        ),
        _section(
            "lines",
            heading="頁面標記",
            lines=[
                "左側保留小型裝訂標記。",
                "中下方保留用印處。",
            ],
        ),
    ]


def _build_meeting_agenda_spec(content: dict) -> list[dict]:
    schedule_rows = ensure_table_rows(
        [
            [
                display_text(item.get("time")),
                display_text(item.get("item")),
                display_text(item.get("owner")),
                display_text(item.get("note")),
            ]
            for item in content["agenda_items"]
        ],
        4,
        minimum_rows=4,
        placeholder="",
    )
    proposal_rows = ensure_table_rows(
        [
            [
                display_text(item.get("title")),
                display_text(item.get("discussion")),
                display_text(item.get("decision")),
                display_text(item.get("note")),
            ]
            for item in content["proposal_items"]
        ],
        4,
        minimum_rows=2,
        placeholder="",
    )
    return [
        _section(
            "info_table",
            rows=_info_rows(
                [
                    ("會議名稱", display_text(content.get("meeting_title"))),
                    ("日期", display_text(content.get("meeting_date"))),
                    ("時間", display_text(content.get("meeting_time"))),
                    ("地點", display_text(content.get("location"))),
                    ("主席", display_text(content.get("chair"))),
                    ("記錄人員", display_text(content.get("recorder"))),
                ]
            ),
            columns=4,
        ),
        _section(
            "table",
            heading="議程表",
            headers=["時間", "議程項目", "主持 / 報告人", "備註"],
            rows=schedule_rows,
        ),
        _section(
            "table",
            heading="討論提案表",
            headers=["案由", "說明", "擬辦", "備註"],
            rows=proposal_rows,
        ),
    ]


def _build_activity_proposal_spec(content: dict) -> list[dict]:
    schedule_rows = ensure_table_rows(
        [
            [
                display_text(item.get("time")),
                display_text(item.get("item")),
                display_text(item.get("owner")),
                display_text(item.get("note")),
            ]
            for item in content["schedule_items"]
        ],
        4,
        minimum_rows=4,
        placeholder="",
    )
    staff_rows = ensure_table_rows(
        [
            [
                display_text(item.get("role")),
                display_text(item.get("name")),
                display_text(item.get("task")),
            ]
            for item in content["staff_assignments"]
        ],
        3,
        minimum_rows=3,
        placeholder="",
    )
    budget_rows = ensure_table_rows(
        [
            [
                display_text(item.get("item")),
                display_text(item.get("quantity")),
                display_text(item.get("unit_price")),
                display_text(item.get("amount")),
                display_text(item.get("funding_source")),
                display_text(item.get("note")),
            ]
            for item in content["budget_items"]
        ],
        6,
        minimum_rows=3,
        placeholder="",
    )
    return [
        _section(
            "info_table",
            rows=_info_rows(
                [
                    ("活動名稱", display_text(content.get("activity_name"))),
                    ("活動主題", display_text(content.get("activity_theme"))),
                    ("主辦單位", display_text(content.get("organizer"))),
                    ("協辦單位", display_text(content.get("co_organizer"))),
                    ("活動時間", _combine_datetime(content.get("activity_date"), content.get("activity_time"))),
                    ("活動地點", display_text(content.get("activity_location") or content.get("location"))),
                    ("指導單位", display_text(content.get("advisor_unit"))),
                    ("活動對象", display_text(content.get("target_audience"))),
                    ("預計人數", display_text(content.get("expected_participants"))),
                ],
                columns_per_row=1,
            ),
            columns=2,
        ),
        _section("paragraph", heading="一、活動宗旨", paragraphs=display_lines(content.get("purpose"))),
        _section("paragraph", heading="二、活動說明", paragraphs=display_lines(content.get("activity_content") or content.get("activity_description"))),
        _section("table", heading="三、活動流程", headers=["時間", "流程項目", "負責人", "備註"], rows=schedule_rows),
        _section("table", heading="四、工作分工", headers=["角色", "姓名", "工作內容"], rows=staff_rows),
        _section("table", heading="五、經費預算", headers=["項目", "數量", "單價", "金額", "經費來源", "備註"], rows=budget_rows),
        _section("bullet_list", heading="六、預期效益", items=display_bullets(content.get("expected_benefits") or content.get("expected_outcomes"))),
        _section("paragraph", heading="七、宣傳方式", paragraphs=display_lines(content.get("promotion_plan"))),
        _section("paragraph", heading="八、所需設備清單", paragraphs=display_lines(content.get("equipment_list") or content.get("resource_needs"))),
        _section("paragraph", heading="九、需學校協助事項", paragraphs=display_lines(content.get("school_support"))),
        _section("paragraph", heading="十、附件", paragraphs=display_lines(content.get("attachments"))),
        _section("paragraph", heading="十一、備註", paragraphs=display_lines(content.get("notes"))),
    ]


def _build_activity_result_report_template_spec(template_definition: dict) -> dict:
    meeting_rows = _info_rows(
        [
            ("會議性質", "○籌備會議　○檢討會議　○其他"),
            ("其他會議性質說明", BLANK_LINE_PLACEHOLDER),
            ("開會日期", BLANK_LINE_PLACEHOLDER),
            ("開會地點", BLANK_LINE_PLACEHOLDER),
            ("會議開始時間", BLANK_LINE_PLACEHOLDER),
            ("會議結束時間", BLANK_LINE_PLACEHOLDER),
            ("主席", BLANK_LINE_PLACEHOLDER),
            ("記錄", BLANK_LINE_PLACEHOLDER),
            ("出席人員", BLANK_LINE_PLACEHOLDER),
        ],
        columns_per_row=1,
    )
    staff_rows = ensure_table_rows(
        [
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
        ],
        6,
        minimum_rows=4,
        placeholder="",
    )
    photo_rows = [
        [
            "照片黏貼處\n\n\n\n活動照片內容：",
            "照片黏貼處\n\n\n\n活動照片內容：",
        ],
        [
            "照片黏貼處\n\n\n\n活動照片內容：",
            "照片黏貼處\n\n\n\n活動照片內容：",
        ],
    ]

    return {
        "title": "臺北市立大學\n社團活動成果報告",
        "sections": [
            _section("info_table", heading="一、會議記錄", rows=meeting_rows, columns=2),
            _section("paragraph", heading="討論內容", paragraphs=[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER]),
            _section("paragraph", heading="臨時動議", paragraphs=[BLANK_LINE_PLACEHOLDER]),
            _section("paragraph", heading="決議", paragraphs=[BLANK_LINE_PLACEHOLDER]),
            _section("paragraph", heading="二、活動簡介與記錄", paragraphs=[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER]),
            _section(
                "table",
                heading="三、工作人員列表",
                headers=["工作職稱", "學號", "姓名", "工作職稱", "學號", "姓名"],
                rows=staff_rows,
            ),
            _section("paragraph", heading="四、社員心得", paragraphs=[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER]),
            _section(
                "table",
                heading="五、活動照片",
                headers=["照片一／照片二", "照片三／照片四"],
                rows=photo_rows,
            ),
            _section(
                "table",
                heading="六、經費使用摘要",
                headers=["預算金額", "實際支出", "補助金額", "自籌金額", "備註"],
                rows=[[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, "經費收支結算表另附。"]],
            ),
            _section("paragraph", heading="七、檢討與建議", paragraphs=[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER]),
            _section(
                "bullet_list",
                heading="八、附件清單",
                items=["簽到表", "活動照片", "經費收支結算表", "核銷明細", "其他附件"],
            ),
            _section(
                "table",
                heading="九、簽核區",
                headers=["製表人", "社團負責人", "指導老師", "審核單位"],
                rows=[[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER]],
            ),
        ],
    }


def _build_meeting_minutes_template_spec(template_definition: dict) -> dict:
    agenda_lines = [
        "案由一：＿＿＿＿＿＿＿＿＿＿",
        "說明：＿＿＿＿＿＿＿＿＿＿",
        "討論：＿＿＿＿＿＿＿＿＿＿",
        "決議：＿＿＿＿＿＿＿＿＿＿",
        "表決結果：同意＿＿票，不同意＿＿票，棄權＿＿票。",
        "負責人：＿＿＿＿＿＿＿＿＿＿",
        "執行期限：＿＿＿＿＿＿＿＿＿＿",
        "備註：＿＿＿＿＿＿＿＿＿＿",
    ]
    motion_lines = [
        "案由一：＿＿＿＿＿＿＿＿＿＿",
        "提案人：＿＿＿＿＿＿＿＿＿＿",
        "說明：＿＿＿＿＿＿＿＿＿＿",
        "討論：＿＿＿＿＿＿＿＿＿＿",
        "決議：＿＿＿＿＿＿＿＿＿＿",
        "表決結果：同意＿＿票，不同意＿＿票，棄權＿＿票。",
        "負責人：＿＿＿＿＿＿＿＿＿＿",
        "備註：＿＿＿＿＿＿＿＿＿＿",
    ]
    action_rows = ensure_table_rows(
        [["1", "", "", "", ""], ["2", "", "", "", ""], ["3", "", "", "", ""]],
        5,
        minimum_rows=3,
        placeholder="",
    )

    return {
        "title": "{{school_name}}{{club_name}}\n第{{meeting_number}}次{{meeting_type}}紀錄",
        "sections": [
            _section(
                "lines",
                lines=[
                    "{{school_name}}{{club_name}}",
                    "製作日期：{{document_date}}",
                ],
            ),
            _section(
                "info_table",
                heading="基本資料表",
                rows=_info_rows(
                    [
                        ("會議名稱", "{{meeting_title}}"),
                        ("會議日期", "{{meeting_date}}"),
                        ("會議時間", "{{start_time}} 至 {{end_time}}"),
                        ("會議地點", "{{location}}"),
                        ("主席", "{{chair}}"),
                        ("記錄人員", "{{recorder}}"),
                        ("出席人員", "{{attendees}}"),
                        ("列席人員", "{{observers}}"),
                        ("請假人員", "{{absentees}}"),
                        ("缺席人員", "{{missing_members}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "paragraph",
                heading="壹、會議開始",
                paragraphs=[
                    "一、上次會議決議追蹤",
                    BLANK_LINE_PLACEHOLDER,
                    "二、主席致詞",
                    BLANK_LINE_PLACEHOLDER,
                ],
            ),
            _section(
                "paragraph",
                heading="貳、報告事項",
                paragraphs=[
                    "一、報告主題：＿＿＿＿＿＿＿＿＿＿",
                    "報告人：＿＿＿＿＿＿＿＿＿＿",
                    "內容：＿＿＿＿＿＿＿＿＿＿",
                    "",
                    "二、報告主題：＿＿＿＿＿＿＿＿＿＿",
                    "報告人：＿＿＿＿＿＿＿＿＿＿",
                    "內容：＿＿＿＿＿＿＿＿＿＿",
                ],
            ),
            _section("paragraph", heading="參、討論事項", paragraphs=agenda_lines + ["", *agenda_lines]),
            _section(
                "table",
                heading="待辦事項",
                headers=["項次", "事項", "負責人", "期限", "備註"],
                rows=action_rows,
            ),
            _section("paragraph", heading="肆、臨時動議", paragraphs=motion_lines),
            _section(
                "paragraph",
                heading="伍、散會",
                paragraphs=[
                    "散會時間：{{end_time}}",
                    "下次會議時間：{{next_meeting_time}}",
                    "備註：{{notes}}",
                ],
            ),
            _section(
                "table",
                heading="簽核欄位",
                headers=["製表人", "主席", "社團負責人", "指導老師"],
                rows=[[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER]],
            ),
        ],
    }


def _build_meeting_agenda_template_spec(template_definition: dict) -> dict:
    schedule_rows = ensure_table_rows(
        [["1", "", "", "", "", "", ""], ["2", "", "", "", "", "", ""], ["3", "", "", "", "", "", ""]],
        7,
        minimum_rows=10,
        placeholder="",
    )
    discussion_rows = ensure_table_rows(
        [["案由一", "", "", ""], ["案由二", "", "", ""], ["案由三", "", "", ""]],
        4,
        minimum_rows=3,
        placeholder="",
    )
    signoff_rows = [
        ["主席", BLANK_LINE_PLACEHOLDER, "紀錄", BLANK_LINE_PLACEHOLDER],
        ["社團負責人", BLANK_LINE_PLACEHOLDER, "指導老師", BLANK_LINE_PLACEHOLDER],
    ]

    return {
        "title": "{{organization_name}}\n第{{meeting_number}}次{{meeting_type}}議程",
        "sections": [
            _section(
                "lines",
                lines=[
                    "{{organization_name}}",
                    "製作日期：{{document_date}}",
                ],
            ),
            _section(
                "info_table",
                heading="會議基本資料",
                rows=_info_rows(
                    [
                        ("社團名稱", "{{organization_name}}"),
                        ("會議名稱", "{{meeting_title}}"),
                        ("會議日期", "{{meeting_date}}"),
                        ("會議時間", "{{start_time}} 至 {{end_time}}"),
                        ("會議地點", "{{location}}"),
                        ("召集人", "{{convener}}"),
                        ("主席", "{{chair}}"),
                        ("紀錄", "{{recorder}}"),
                        ("出席人員", "{{attendees}}"),
                        ("列席人員", "{{observers}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "paragraph",
                heading="會議目的",
                paragraphs=["{{meeting_purpose}}"],
            ),
            _section(
                "table",
                heading="會議議程（議程表）",
                headers=["項次", "時間", "議程項目", "說明", "報告／負責人", "預計時間", "備註"],
                rows=schedule_rows,
            ),
            _section(
                "paragraph",
                heading="報告事項",
                paragraphs=[
                    "一、上次會議決議追蹤",
                    "報告人：＿＿＿＿＿＿＿＿＿＿",
                    "預計時間：＿＿＿＿＿＿＿＿＿＿",
                    "內容摘要：＿＿＿＿＿＿＿＿＿＿",
                    "相關附件：＿＿＿＿＿＿＿＿＿＿",
                    "",
                    "二、社團近期事項報告",
                    "報告人：＿＿＿＿＿＿＿＿＿＿",
                    "預計時間：＿＿＿＿＿＿＿＿＿＿",
                    "內容摘要：＿＿＿＿＿＿＿＿＿＿",
                    "相關附件：＿＿＿＿＿＿＿＿＿＿",
                    "",
                    "三、財務或活動進度報告",
                    "報告人：＿＿＿＿＿＿＿＿＿＿",
                    "預計時間：＿＿＿＿＿＿＿＿＿＿",
                    "內容摘要：＿＿＿＿＿＿＿＿＿＿",
                    "相關附件：＿＿＿＿＿＿＿＿＿＿",
                    "",
                    "四、其他報告事項",
                    "報告人：＿＿＿＿＿＿＿＿＿＿",
                    "預計時間：＿＿＿＿＿＿＿＿＿＿",
                    "內容摘要：＿＿＿＿＿＿＿＿＿＿",
                    "相關附件：＿＿＿＿＿＿＿＿＿＿",
                ],
            ),
            _section(
                "table",
                heading="討論事項",
                headers=["案由", "說明", "擬辦方式", "決議欄"],
                rows=discussion_rows,
            ),
            _section(
                "paragraph",
                heading="臨時動議",
                paragraphs=[
                    "一、臨時動議時間預留：＿＿＿＿＿＿＿＿＿＿",
                    "二、說明：臨時動議由出席人員於會議中提出，經主席確認後進行討論。",
                ],
            ),
            _section(
                "paragraph",
                heading="會前準備事項",
                paragraphs=[
                    "1. 詳閱附件資料。",
                    "2. 確認會議時間與地點。",
                    "3. 若無法出席，請提前向聯絡人請假。",
                    "4. 如需提案或補充資料，請於會前提供給主持人或承辦人。",
                    "5. 線上會議請提前確認網路、設備與會議連結。",
                ],
            ),
            _section(
                "paragraph",
                heading="附件資料",
                paragraphs=[
                    "附件一：上次會議紀錄",
                    "附件二：活動企畫書",
                    "附件三：經費預算表",
                    "附件四：工作分配表",
                    "附件五：其他附件",
                ],
            ),
            _section(
                "info_table",
                heading="簽核區",
                rows=signoff_rows,
                columns=4,
            ),
        ],
    }


def _build_club_announcement_template_spec(template_definition: dict) -> dict:
    schedule_rows = ensure_table_rows(
        [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
        5,
        minimum_rows=3,
        placeholder="",
    )
    action_rows = ensure_table_rows(
        [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
        5,
        minimum_rows=3,
        placeholder="",
    )
    contact_rows = ensure_table_rows(
        [["", "", "", ""], ["", "", "", ""]],
        4,
        minimum_rows=2,
        placeholder="",
    )
    attachment_rows = ensure_table_rows(
        [["", "", ""], ["", "", ""]],
        3,
        minimum_rows=2,
        placeholder="",
    )

    return {
        "title": "{{school_name}}{{club_name}}\n{{announcement_type}}：{{announcement_title}}",
        "sections": [
            _section(
                "info_table",
                heading="公告基本資料",
                rows=_info_rows(
                    [
                        ("公告類型", "{{announcement_type}}"),
                        ("公告日期", "{{announcement_date}}"),
                        ("發布單位", "{{publishing_unit}}"),
                        ("承辦人", "{{contact_person}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "info_table",
                heading="公告對象",
                rows=_info_rows(
                    [
                        ("公告對象", "{{announcement_targets}}"),
                        ("通知方式", "{{delivery_channels}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "paragraph",
                heading="公告主旨",
                paragraphs=["{{announcement_title}}"],
            ),
            _section(
                "paragraph",
                heading="公告內容",
                paragraphs=[
                    "一、公告事項",
                    "{{announcement_summary}}",
                    "",
                    "二、詳細說明",
                    "{{announcement_details}}",
                    "",
                    "三、注意事項",
                    "{{important_notes}}",
                ],
            ),
            _section(
                "table",
                heading="重要日期與時間",
                headers=["項目", "日期", "時間", "地點／方式", "備註"],
                rows=schedule_rows,
            ),
            _section(
                "table",
                heading="需要辦理事項",
                headers=["辦理事項", "對象", "截止時間", "辦理方式", "備註"],
                rows=action_rows,
            ),
            _section(
                "table",
                heading="聯絡方式",
                headers=["聯絡人", "職稱／組別", "聯絡方式", "備註"],
                rows=contact_rows,
            ),
            _section(
                "table",
                heading="附件清單",
                headers=["附件名稱", "說明／連結", "備註"],
                rows=attachment_rows,
            ),
            _section(
                "lines",
                heading="發布單位與發布日期",
                lines=[
                    "發布單位：{{publishing_unit}}",
                    "承辦人：{{contact_person}}",
                    "發布日期：{{announcement_date}}",
                ],
            ),
            _section(
                "paragraph",
                heading="備註",
                paragraphs=["{{remarks}}"],
            ),
        ],
    }


def _build_activity_application_template_spec(template_definition: dict) -> dict:
    evaluation_line = "前年社團評鑑：特優□　優等□　甲等□　乙等□"
    activity_type_lines = [
        "□ 幹訓或營隊：具學習目的者。",
        "□ 學術活動：講演、大型學術、研討座談、展覽、比賽、研習、成果展等。",
        "□ 刊物出版：週刊、月刊、校刊。",
        "□ 康樂活動：校內外演奏會、出國演出、參加或主辦校際性比賽。",
        "□ 社會服務活動：含平時與寒暑假期間。",
        "□ 發展社團特色活動。",
        "□ 其他符合社團宗旨之綜合性活動。",
        "□ 學校委辦或代表學校之活動",
    ]
    applicant_funding_rows = [
        ["活動申請人", "{{applicant_name}}", "系別", "{{applicant_department}}"],
        ["班別", "{{applicant_class}}", "手機", "{{applicant_phone}}"],
        ["活動費申請補助", "{{subsidy_amount}} 元", "活動費自籌經費", "{{self_funded_amount}} 元"],
        ["合計", "{{total_amount}} 元", "", ""],
    ]
    admin_rows = [
        ["本次使用種類", "", "一般補助", "", "專案補助", ""],
        ["額度", "", "已使用額度，含本次", "", "尚餘額度", ""],
        ["承辦人", "", "單位主管", "", "組長", ""],
        ["學務長", "", "會辦單位：總務處", "", "會辦單位：會計室", ""],
        ["校長", "", "", "", "", ""],
    ]

    return {
        "title": "臺北市立大學　社團活動申請表",
        "page_layout": {
            "orientation": "landscape",
            "page_width_cm": "29.7cm",
            "page_height_cm": "21cm",
            "margin_top_cm": "0.9cm",
            "margin_bottom_cm": "0.9cm",
            "margin_left_cm": "0.9cm",
            "margin_right_cm": "0.9cm",
        },
        "style_overrides": {
            "title_font_size_pt": 20,
            "section_font_size_pt": 11,
            "body_font_size_pt": 10,
            "table_font_size_pt": 10,
            "note_font_size_pt": 9,
            "footer_font_size_pt": 9,
        },
        "sections": [
            _section(
                "note",
                text="請於活動二週前完成申請並隨表附活動企畫書\n申請校內場地，請增附場地申請表",
            ),
            _section(
                "info_table",
                heading="申請基本資料",
                rows=_info_rows(
                    [
                        ("活動名稱", "{{activity_name}}"),
                        ("活動時間，起", "{{start_year}} 年 {{start_month}} 月 {{start_day}} 日 {{start_hour}} 時 {{start_minute}} 分"),
                        ("活動時間，止", "{{end_year}} 年 {{end_month}} 月 {{end_day}} 日 {{end_hour}} 時 {{end_minute}} 分"),
                        ("活動地點", "{{location}}"),
                        ("申請日期", "{{apply_year}} 年 {{apply_month}} 月 {{apply_day}} 日"),
                        ("主辦社團", "{{club_name}}"),
                        ("參加人數", "{{participant_count}} 人"),
                        ("社長", "{{president_name}}"),
                        ("社長電話", "{{president_phone}}"),
                        ("社團指導老師", "{{advisor_name}}"),
                        ("指導老師電話", "{{advisor_phone}}"),
                    ],
                    columns_per_row=2,
                ),
                columns=4,
            ),
            _section("paragraph", heading="前年社團評鑑", paragraphs=[evaluation_line]),
            _section("paragraph", heading="活動性質", paragraphs=activity_type_lines),
            _section(
                "paragraph",
                heading="宗旨與活動內容區",
                paragraphs=[
                    "宗旨：{{purpose_summary}}",
                    "活動內容或講題：{{content_summary}}",
                ],
            ),
            _section(
                "info_table",
                heading="申請人與經費區",
                rows=applicant_funding_rows,
                columns=4,
            ),
            _section(
                "info_table",
                heading="行政簽核保留區",
                rows=admin_rows,
                columns=6,
            ),
            _section(
                "note",
                text="使用種類與額度由課外活動組填寫",
            ),
        ],
    }


def _build_course_record_template_spec(template_definition: dict) -> dict:
    material_rows = ensure_table_rows(
        [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
        4,
        minimum_rows=3,
        placeholder="",
    )
    issue_rows = ensure_table_rows(
        [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
        5,
        minimum_rows=3,
        placeholder="",
    )
    follow_up_rows = ensure_table_rows(
        [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]],
        5,
        minimum_rows=3,
        placeholder="",
    )
    photo_rows = [
        [
            "照片黏貼處\n\n照片說明：",
            "照片黏貼處\n\n照片說明：",
        ],
        [
            "照片黏貼處\n\n照片說明：",
            "照片黏貼處\n\n照片說明：",
        ],
    ]

    return {
        "title": "{{school_name}}{{club_name}}\n「{{course_title}}」社課紀錄",
        "sections": [
            _section(
                "info_table",
                heading="社課基本資料",
                rows=_info_rows(
                    [
                        ("社課名稱", "{{course_title}}"),
                        ("社課日期", "{{course_date}}"),
                        ("社課時間", "{{course_start_time}} 至 {{course_end_time}}"),
                        ("社課地點", "{{course_location}}"),
                        ("主辦社團", "{{club_name}}"),
                        ("課程負責人", "{{course_owner}}"),
                        ("講師／帶領人", "{{instructor}}"),
                        ("記錄人", "{{recorder}}"),
                        ("社課類型", "{{course_type}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "info_table",
                heading="出席情形",
                rows=_info_rows(
                    [
                        ("應到人數", "{{expected_attendance}}"),
                        ("實到人數", "{{actual_attendance}}"),
                        ("請假人數", "{{leave_count}}"),
                        ("缺席人數", "{{absent_count}}"),
                        ("出席名單", "{{attendees}}"),
                        ("請假名單", "{{leave_members}}"),
                        ("缺席名單", "{{absent_members}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "paragraph",
                heading="社課內容紀錄",
                paragraphs=[
                    "社課主題：{{course_topic}}",
                    "課程目標：{{course_objectives}}",
                    "課程內容摘要：{{course_summary}}",
                    "進行方式：{{delivery_method}}",
                    "重要討論或學習重點：{{key_takeaways}}",
                ],
            ),
            _section(
                "table",
                heading="教材與器材",
                headers=["類型", "名稱", "用途", "備註"],
                rows=material_rows,
            ),
            _section(
                "paragraph",
                heading="執行情形與成果",
                paragraphs=[
                    "是否如期完成：是□　否□　部分完成□",
                    "實際執行情形：{{execution_summary}}",
                    "本次成果：{{course_outcomes}}",
                    "社員回饋摘要：{{member_feedback}}",
                ],
            ),
            _section(
                "table",
                heading="問題與改善建議",
                headers=["問題", "原因分析", "改善建議", "負責人", "追蹤期限"],
                rows=issue_rows,
            ),
            _section(
                "table",
                heading="後續追蹤事項",
                headers=["追蹤事項", "負責人", "完成期限", "狀態", "備註"],
                rows=follow_up_rows,
            ),
            _section(
                "table",
                heading="活動照片",
                headers=["照片一", "照片二"],
                rows=photo_rows,
            ),
            _section(
                "paragraph",
                heading="備註",
                paragraphs=["{{remarks}}"],
            ),
        ],
    }


def _build_activity_review_minutes_template_spec(template_definition: dict) -> dict:
    review_rows = ensure_table_rows(
        [["1", "", "", "", "", "", "", ""], ["2", "", "", "", "", "", "", ""], ["3", "", "", "", "", "", "", ""]],
        8,
        minimum_rows=3,
        placeholder="",
    )
    follow_up_rows = ensure_table_rows(
        [["1", "", "", "", "", ""], ["2", "", "", "", "", ""]],
        6,
        minimum_rows=2,
        placeholder="",
    )
    resolution_rows = ensure_table_rows(
        [["1", "", "", ""], ["2", "", "", ""]],
        4,
        minimum_rows=2,
        placeholder="",
    )

    return {
        "title": "{{school_name}}{{club_name}}\n「{{activity_name}}」活動檢討會紀錄",
        "sections": [
            _section(
                "info_table",
                heading="會議基本資料",
                rows=_info_rows(
                    [
                        ("社團名稱", "{{club_name}}"),
                        ("活動名稱", "{{activity_name}}"),
                        ("會議名稱", "「{{activity_name}}」活動檢討會"),
                        ("會議日期", "{{meeting_date}}"),
                        ("會議時間", "{{meeting_start_time}} 至 {{meeting_end_time}}"),
                        ("會議地點", "{{meeting_location}}"),
                        ("主席", "{{chair}}"),
                        ("紀錄", "{{recorder}}"),
                        ("出席人員", "{{attendees}}"),
                        ("列席人員", "{{observers}}"),
                        ("請假人員", "{{absentees}}"),
                        ("缺席人員", "{{missing_members}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "paragraph",
                heading="活動執行情形",
                paragraphs=[
                    "活動是否如期完成：{{completed_as_planned}}",
                    "實際參與人數：{{actual_participant_count}}",
                    "活動流程是否依原企畫執行：{{flow_followed_plan}}",
                    "與原企畫差異：{{plan_difference}}",
                    "重要成果：{{key_outcomes}}",
                    "特殊狀況：{{special_cases}}",
                ],
            ),
            _section(
                "table",
                heading="檢討事項",
                headers=["項次", "檢討項目", "實際情形", "問題說明", "改進建議", "負責人", "完成期限", "備註"],
                rows=review_rows,
            ),
            _section(
                "paragraph",
                heading="做得好的地方",
                paragraphs=[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER],
            ),
            _section(
                "paragraph",
                heading="各組回饋",
                paragraphs=[
                    "行政組：＿＿＿＿＿＿＿＿＿＿",
                    "場器組：＿＿＿＿＿＿＿＿＿＿",
                    "活動組：＿＿＿＿＿＿＿＿＿＿",
                    "財務組：＿＿＿＿＿＿＿＿＿＿",
                    "美宣組：＿＿＿＿＿＿＿＿＿＿",
                    "機動組：＿＿＿＿＿＿＿＿＿＿",
                ],
            ),
            _section(
                "table",
                heading="後續追蹤事項",
                headers=["項次", "待辦事項", "負責人", "預定完成日期", "追蹤狀態", "備註"],
                rows=follow_up_rows,
            ),
            _section(
                "paragraph",
                heading="下次活動建議",
                paragraphs=[
                    "可延續的做法：＿＿＿＿＿＿＿＿＿＿",
                    "應避免的問題：＿＿＿＿＿＿＿＿＿＿",
                    "需要提前準備的事項：＿＿＿＿＿＿＿＿＿＿",
                ],
            ),
            _section(
                "table",
                heading="會議決議",
                headers=["項次", "決議內容", "負責人", "完成期限"],
                rows=resolution_rows,
            ),
            _section(
                "paragraph",
                heading="臨時動議",
                paragraphs=[BLANK_LINE_PLACEHOLDER],
            ),
            _section(
                "paragraph",
                heading="散會時間",
                paragraphs=["本次會議於 {{meeting_end_time}} 散會。"],
            ),
            _section(
                "table",
                heading="簽核欄位",
                headers=["主席", "紀錄", "社團負責人", "指導老師"],
                rows=[[BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER, BLANK_LINE_PLACEHOLDER]],
            ),
        ],
    }


def _build_annual_plan_template_spec(template_definition: dict) -> dict:
    annual_activity_rows = ensure_table_rows(
        [["", "", "", "", "", "", "", ""] for _ in range(5)],
        8,
        minimum_rows=5,
        placeholder="",
    )
    regular_activity_rows = ensure_table_rows(
        [["", "", "", "", "", ""] for _ in range(4)],
        6,
        minimum_rows=4,
        placeholder="",
    )
    officer_rows = ensure_table_rows(
        [["", "", "", "", ""] for _ in range(5)],
        5,
        minimum_rows=5,
        placeholder="",
    )
    budget_rows = ensure_table_rows(
        [["", "", "", "", ""] for _ in range(4)],
        5,
        minimum_rows=4,
        placeholder="",
    )
    evaluation_rows = ensure_table_rows(
        [["", "", "", ""] for _ in range(5)],
        4,
        minimum_rows=5,
        placeholder="",
    )

    return {
        "title": "{{school_name}}{{club_name}}\n{{academic_year}}年度計畫",
        "sections": [
            _section(
                "info_table",
                heading="社團基本資料",
                rows=_info_rows(
                    [
                        ("學年度", "{{academic_year}} 學年度"),
                        ("社團名稱", "臺北市立大學 {{club_name}}"),
                        ("社團類別", "{{club_category}}"),
                        ("社長", "{{president}}"),
                        ("指導老師", "{{advisor}}"),
                        ("主要聯絡人", "{{contact_person}}"),
                        ("聯絡電話", "{{contact_phone}}"),
                        ("聯絡信箱", "{{contact_email}}"),
                        ("製表日期", "{{created_date}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "paragraph",
                heading="年度目標",
                paragraphs=[
                    "一、社團發展目標：{{development_goals}}",
                    "二、活動辦理目標：{{activity_goals}}",
                    "三、組織經營目標：{{organization_goals}}",
                ],
            ),
            _section(
                "table",
                heading="年度活動規劃",
                headers=["預計月份", "活動名稱", "活動類型", "活動目的", "預計對象", "預計人數", "負責組別", "備註"],
                rows=annual_activity_rows,
            ),
            _section(
                "table",
                heading="社課或例行活動規劃",
                headers=["預計週次／日期", "社課或例行活動名稱", "內容概要", "負責人", "預計地點", "備註"],
                rows=regular_activity_rows,
            ),
            _section(
                "table",
                heading="幹部與組別分工",
                headers=["職稱／組別", "姓名", "主要職責", "年度重點工作", "備註"],
                rows=officer_rows,
            ),
            _section(
                "table",
                heading="年度預算概估",
                headers=["類別", "項目", "預估金額", "經費來源", "備註"],
                rows=budget_rows,
            ),
            _section(
                "paragraph",
                heading="預期成果",
                paragraphs=[
                    "一、活動成果：{{activity_results}}",
                    "二、社員參與成果：{{member_participation_results}}",
                    "三、組織運作成果：{{organization_results}}",
                    "四、文件與評鑑成果：{{document_and_evaluation_results}}",
                ],
            ),
            _section(
                "table",
                heading="評鑑資料準備方向",
                headers=["評鑑資料類型", "預計蒐集內容", "負責人", "備註"],
                rows=evaluation_rows,
            ),
            _section(
                "paragraph",
                heading="備註",
                paragraphs=["{{notes}}"],
            ),
        ],
    }


def _build_attendance_sheet_template_spec(template_definition: dict) -> dict:
    sign_in_rows = ensure_table_rows(
        [["", "", "", ""] for _ in range(15)],
        4,
        minimum_rows=15,
        placeholder="",
    )
    summary_rows = [
        ["應到人數", BLANK_LINE_PLACEHOLDER, "實到人數", BLANK_LINE_PLACEHOLDER],
        ["請假人數", BLANK_LINE_PLACEHOLDER, "缺席人數", BLANK_LINE_PLACEHOLDER],
        ["備註", "請參與者依序填寫系級／單位與姓名。", "", ""],
    ]
    signoff_rows = [
        ["製表人", BLANK_LINE_PLACEHOLDER, "社團負責人", BLANK_LINE_PLACEHOLDER],
        ["指導老師", BLANK_LINE_PLACEHOLDER, "", ""],
    ]

    return {
        "title": "{{school_name}} {{club_name}}\n「{{event_name}}」簽到表",
        "sections": [
            _section(
                "info_table",
                heading="活動基本資料",
                rows=_info_rows(
                    [
                        ("日期與時間", "{{event_date}} {{start_time}} 至 {{end_time}}"),
                        ("活動地點", "{{location}}"),
                        ("活動名稱", "{{event_name}}"),
                        ("主辦單位", "{{organizer}}"),
                    ],
                    columns_per_row=1,
                ),
                columns=2,
            ),
            _section(
                "table",
                heading="簽到明細",
                headers=["系級／單位", "姓名", "系級／單位", "姓名"],
                rows=sign_in_rows,
            ),
            _section(
                "info_table",
                heading="統計與備註",
                rows=summary_rows,
                columns=4,
            ),
            _section(
                "info_table",
                heading="簽核欄位",
                rows=signoff_rows,
                columns=4,
            ),
        ],
    }


def _build_activity_report_spec(content: dict) -> list[dict]:
    follow_up_rows = ensure_table_rows(
        [
            [
                display_text(item.get("task")),
                display_text(item.get("owner")),
                display_text(item.get("deadline")),
                display_text(item.get("note")),
            ]
            for item in content["follow_up_items"]
        ],
        4,
        minimum_rows=2,
        placeholder="",
    )
    return [
        _section(
            "info_table",
            rows=_info_rows(
                [
                    ("活動名稱", display_text(content.get("activity_name"))),
                    ("活動日期", display_text(content.get("activity_date"))),
                    ("活動地點", display_text(content.get("location"))),
                    ("主辦單位", display_text(content.get("organizer"))),
                    ("參與人數", display_text(content.get("participant_count"))),
                    ("負責人", display_text(content.get("responsible_person"))),
                ]
            ),
            columns=4,
        ),
        _section("paragraph", heading="一、活動內容摘要", paragraphs=display_lines(content.get("activity_summary"))),
        _section("paragraph", heading="二、活動成果與效益", paragraphs=display_lines(content.get("outcomes"))),
        _section("paragraph", heading="三、活動照片或附件說明", paragraphs=display_lines(content.get("photos_or_links"))),
        _section("paragraph", heading="四、參與回饋摘要", paragraphs=display_lines(content.get("feedback_summary"))),
        _section("paragraph", heading="五、經費摘要", paragraphs=display_lines(content.get("expense_summary"))),
        _section("paragraph", heading="六、檢討與建議", paragraphs=display_lines(content.get("improvement_notes"))),
        _section("table", heading="七、後續追蹤事項", headers=["事項", "負責人", "期限", "備註"], rows=follow_up_rows),
        _section("paragraph", heading="八、備註", paragraphs=display_lines(content.get("notes"))),
    ]


def _build_activity_review_spec(content: dict) -> list[dict]:
    review_rows = ensure_table_rows(
        [
            [
                display_text(item.get("issue")),
                display_text(item.get("planned")),
                display_text(item.get("actual")),
                display_text(item.get("problem") or item.get("issue")),
                display_text(item.get("action")),
                display_text(item.get("owner")),
            ]
            for item in content["improvement_actions"]
        ],
        6,
        minimum_rows=3,
        placeholder="",
    )
    follow_up_rows = ensure_table_rows(
        [
            [
                display_text(item.get("action")),
                display_text(item.get("owner")),
                display_text(item.get("deadline")),
            ]
            for item in content["improvement_actions"]
        ],
        3,
        minimum_rows=2,
        placeholder="",
    )
    return [
        _section(
            "info_table",
            rows=_info_rows(
                [
                    ("活動名稱", display_text(content.get("activity_name"))),
                    ("檢討會日期", display_text(content.get("meeting_date"))),
                    ("檢討會地點", display_text(content.get("location"))),
                    ("主席", display_text(content.get("chair"))),
                    ("記錄人員", display_text(content.get("recorder"))),
                    ("出席人員", display_people(content.get("attendees"))),
                ],
                columns_per_row=1,
            ),
            columns=2,
        ),
        _section(
            "table",
            heading="檢討項目表",
            headers=["項目", "原規劃", "實際狀況", "問題", "改善建議", "負責人"],
            rows=review_rows,
        ),
        _section("paragraph", heading="補充優點", paragraphs=display_lines(content.get("strengths"))),
        _section("paragraph", heading="補充問題", paragraphs=display_lines(content.get("problems"))),
        _section("table", heading="結論與追蹤事項", headers=["後續改善事項", "負責人", "期限"], rows=follow_up_rows),
        _section("paragraph", heading="下次建議", paragraphs=display_lines(content.get("next_time_suggestions"))),
        _section("paragraph", heading="備註", paragraphs=display_lines(content.get("notes"))),
    ]


def _build_annual_plan_spec(content: dict) -> list[dict]:
    calendar_rows = ensure_table_rows(
        [
            [
                display_text(item.get("month")),
                display_text(item.get("activity_name")),
                display_text(item.get("activity_type")),
                display_text(item.get("target")),
                display_text(item.get("purpose") or item.get("expected_outcome")),
                display_text(item.get("note")),
            ]
            for item in content["key_activities"]
        ],
        6,
        minimum_rows=4,
        placeholder="",
    )
    cadre_rows = ensure_table_rows(
        [
            [
                display_text(item.get("role")),
                display_text(item.get("name")),
                display_text(item.get("task")),
            ]
            for item in content["cadre_assignments"]
        ],
        3,
        minimum_rows=3,
        placeholder="",
    )
    return [
        _section(
            "info_table",
            rows=_info_rows(
                [
                    ("學年度", display_text(content.get("academic_year"))),
                    ("社團名稱", display_text(content.get("club_name"))),
                ]
            ),
            columns=4,
        ),
        _section("paragraph", heading="一、社團宗旨", paragraphs=display_lines(content.get("club_purpose"))),
        _section("paragraph", heading="二、年度目標", paragraphs=display_lines(content.get("annual_goal"))),
        _section("bullet_list", heading="三、年度重點工作", items=_semester_plan_bullets(content.get("semester_plans", []))),
        _section(
            "table",
            heading="四、預定活動行事曆",
            headers=["月份", "活動名稱", "活動類型", "預定對象", "預期成果", "備註"],
            rows=calendar_rows,
        ),
        _section("table", heading="五、幹部與分工", headers=["職務", "姓名", "分工"], rows=cadre_rows),
        _section("paragraph", heading="六、預期成果", paragraphs=display_lines(content.get("expected_outcomes"))),
        _section("paragraph", heading="七、資源需求", paragraphs=display_lines(content.get("resource_needs"))),
        _section("paragraph", heading="八、備註", paragraphs=display_lines(content.get("notes"))),
    ]


def _decision_paragraphs(agenda_items: list[dict]) -> list[str]:
    decisions = [
        f"{index}. {display_text(item.get('decision'))}"
        for index, item in enumerate(agenda_items, start=1)
    ]
    return decisions or [TEXT_PLACEHOLDER]


def _semester_plan_bullets(rows: list[dict]) -> list[str]:
    bullets = [
        (
            f"{display_text(item.get('semester'))}：{display_text(item.get('plan'))}"
            f"（預計月份：{display_text(item.get('expected_month'))}／負責人：{display_text(item.get('owner'))}）"
        )
        for item in rows
    ]
    return bullets or [TEXT_PLACEHOLDER]


def _combine_datetime(date_text: str | None, time_text: str | None) -> str:
    left = str(date_text or "").strip()
    right = str(time_text or "").strip()
    if left and right:
        return f"{left} {right}"
    return display_text(left or right)
