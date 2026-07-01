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
        "meeting_agenda_odt": lambda: build_document_render_spec(
            "會議議程",
            get_default_document_content("會議議程"),
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
