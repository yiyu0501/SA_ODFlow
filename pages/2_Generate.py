from __future__ import annotations

from pathlib import Path

import streamlit as st

from ai.mock_parser import parse_meeting_minutes
from core.constants import EVALUATION_CATEGORIES, MEETING_TYPE_OPTIONS
from core.database import initialize_database
from core.document_schemas import (
    build_document_preview_blocks,
    derive_document_title,
    get_default_document_content,
    get_document_schema,
    get_recommended_evaluation_category,
    list_supported_document_types,
    normalize_document_content,
)
from core.document_service import (
    create_document,
    create_document_version,
    get_document_with_current_version,
    update_version_file_paths,
)
from core.meeting_minutes import people_list_to_text
from core.settings_service import get_club_settings
from core.ui_components import (
    badge_html,
    card_html,
    empty_state,
    inject_base_styles,
    panel_body_html,
    page_intro,
    render_stepper,
)
from generators.odt_generator import generate_document_odt
from generators.pdf_generator import generate_document_pdf


SUPPORTED_DOCUMENT_TYPES = list_supported_document_types()

DOCUMENT_TYPE_SUMMARIES = {
    "會議紀錄": "適合整理幹部會議、社員大會與活動檢討的正式紀錄。",
    "開會通知單": "用於正式通知會議時間、地點、事由與出列席者。",
    "會議議程": "先整理會前流程、提案與討論順序。",
    "活動企劃書": "整理活動主題、流程、工作分配與預算。",
    "活動成果報告": "彙整活動成果、回饋與後續追蹤事項。",
    "活動檢討會紀錄": "整理活動結束後的問題、改善與下次建議。",
    "年度計畫": "規劃學年度目標、重點活動與執行方向。",
}

FIELD_GROUPS = {
    "會議紀錄": {
        "基本資料": ["meeting_title", "meeting_date", "meeting_time", "location", "chair", "recorder"],
        "與會人員": ["attendees", "observers", "absentees"],
        "會議內容": ["opening_remarks", "reports", "motions", "adjournment_time", "next_meeting_time"],
        "備註": ["notes"],
    },
    "開會通知單": {
        "基本資料": ["organization_name", "recipient", "document_date", "document_number", "priority"],
        "通知內容": ["security_level", "attachments", "meeting_reason", "meeting_datetime", "meeting_location", "host"],
        "聯絡與名單": ["contact_person", "contact_phone", "attendees", "observers"],
        "備註": ["note"],
    },
    "會議議程": {
        "基本資料": ["meeting_title", "meeting_date", "meeting_time", "location", "chair", "recorder"],
        "備註": ["notes"],
    },
    "活動企劃書": {
        "基本資料": [
            "activity_name",
            "school_name",
            "activity_theme",
            "activity_date",
            "activity_time",
            "activity_location",
            "organizer",
            "co_organizer",
        ],
        "活動說明": [
            "advisor_unit",
            "target_audience",
            "expected_participants",
            "purpose",
            "activity_description",
            "activity_content",
            "expected_benefits",
            "expected_outcomes",
        ],
        "執行與資源": [
            "promotion_plan",
            "resource_needs",
            "equipment_list",
            "school_support",
            "attachments",
            "notes",
        ],
    },
    "活動成果報告": {
        "基本資料": ["activity_name", "activity_date", "location", "participant_count", "organizer", "responsible_person"],
        "成果內容": ["activity_summary", "outcomes", "photos_or_links", "feedback_summary", "expense_summary", "improvement_notes"],
        "備註": ["notes"],
    },
    "活動檢討會紀錄": {
        "基本資料": ["meeting_title", "meeting_date", "activity_name", "location", "chair", "recorder"],
        "與會人員": ["attendees"],
        "檢討內容": ["strengths", "problems", "next_time_suggestions"],
        "備註": ["notes"],
    },
    "年度計畫": {
        "基本資料": ["academic_year", "club_name"],
        "年度方向": ["annual_goal", "expected_outcomes", "resource_needs"],
        "備註": ["notes"],
    },
}


def _editor_rows_to_list(editor_value) -> list[dict]:
    if hasattr(editor_value, "to_dict"):
        return editor_value.to_dict("records")
    return [dict(row) for row in editor_value]


def _reset_generate_state(document_type: str) -> None:
    st.session_state["generate_document_type"] = document_type
    st.session_state["generate_document_id"] = None
    st.session_state["generate_evaluation_category"] = get_recommended_evaluation_category(
        document_type
    )
    st.session_state["generate_message"] = ""
    st.session_state["generate_draft_content"] = (
        None if document_type == "會議紀錄" else get_default_document_content(document_type)
    )


def _initialize_state() -> None:
    requested_document_type = st.session_state.pop("generate_requested_document_type", None)
    if "generate_document_type" not in st.session_state:
        _reset_generate_state("會議紀錄")

    if requested_document_type in SUPPORTED_DOCUMENT_TYPES:
        current_type = st.session_state.get("generate_document_type")
        if requested_document_type != current_type:
            _reset_generate_state(requested_document_type)
        st.session_state["generate_message"] = (
            f"已從「空白範本」帶入「{requested_document_type}」建立流程。"
        )


def _set_document_type(document_type: str) -> None:
    current_type = st.session_state.get("generate_document_type")
    if current_type != document_type:
        _reset_generate_state(document_type)
        st.rerun()


def _render_preview_blocks(document_type: str, content_json: dict) -> None:
    for block in build_document_preview_blocks(document_type, content_json):
        if block["kind"] == "title":
            st.subheader(block["text"])
        elif block["kind"] == "heading":
            st.markdown(f"**{block['text']}**")
        elif block["kind"] == "paragraph":
            st.write(block["text"])
        elif block["kind"] == "bullet_list":
            for item in block["items"]:
                st.write(f"• {item}")


def _render_field_widget(field: dict, current_value, widget_key: str):
    label = field["label"]
    input_type = field["input_type"]

    if input_type == "textarea":
        return st.text_area(label, value=str(current_value), height=120, key=widget_key)
    if input_type == "people_list":
        return st.text_area(
            label,
            value=people_list_to_text(current_value),
            height=96,
            help="每行一位，或使用逗號分隔。",
            key=widget_key,
        )
    return st.text_input(label, value=str(current_value), key=widget_key)


def _render_document_editor_fields(document_type: str, content_json: dict, prefix: str) -> dict:
    schema = get_document_schema(document_type)
    field_lookup = {field["key"]: field for field in schema["fields"]}
    edited = {}
    grouped_keys = set()

    for group_title, field_keys in FIELD_GROUPS.get(document_type, {}).items():
        st.markdown(f"**{group_title}**")
        group_fields = [field_lookup[key] for key in field_keys if key in field_lookup]
        if not group_fields:
            continue
        columns = st.columns(2, gap="medium")
        for index, field in enumerate(group_fields):
            grouped_keys.add(field["key"])
            with columns[index % 2]:
                edited[field["key"]] = _render_field_widget(
                    field,
                    content_json.get(field["key"], ""),
                    widget_key=f"{prefix}_{document_type}_{field['key']}",
                )

    remaining_fields = [field for field in schema["fields"] if field["key"] not in grouped_keys]
    if remaining_fields:
        st.markdown("**其他欄位**")
        columns = st.columns(2, gap="medium")
        for index, field in enumerate(remaining_fields):
            with columns[index % 2]:
                edited[field["key"]] = _render_field_widget(
                    field,
                    content_json.get(field["key"], ""),
                    widget_key=f"{prefix}_{document_type}_{field['key']}",
                )

    if schema["repeatable_sections"]:
        st.markdown("**表格 / 清單資料**")
    for section in schema["repeatable_sections"]:
        st.caption(section["label"])
        edited[section["key"]] = _editor_rows_to_list(
            st.data_editor(
                content_json.get(section["key"], []),
                num_rows="dynamic",
                use_container_width=True,
                column_config={column["key"]: column["label"] for column in section["columns"]},
                key=f"{prefix}_{document_type}_{section['key']}",
            )
        )

    return normalize_document_content(document_type, edited)


def _get_active_step_index(draft_content: dict | None, current_document: dict | None) -> int:
    if draft_content is None:
        return 0
    if current_document is None:
        return 1
    return 2


def _ensure_export_file(document: dict, version: dict, export_type: str) -> tuple[str | None, str | None]:
    try:
        if export_type == "odt":
            output_path = generate_document_odt(document=document, version=version)
            updated_version = update_version_file_paths(
                document_id=document["id"],
                version_number=version["version_number"],
                odf_path=str(output_path),
            )
            return updated_version["odf_path"], None

        output_path = generate_document_pdf(document=document, version=version)
        updated_version = update_version_file_paths(
            document_id=document["id"],
            version_number=version["version_number"],
            pdf_path=str(output_path),
        )
        return updated_version["pdf_path"], None
    except (ValueError, TypeError) as exc:
        return None, str(exc)


initialize_database()
inject_base_styles()
_initialize_state()

club_settings = get_club_settings()
generate_message = st.session_state.pop("generate_message", "")

page_intro(
    "生成文件",
    "依三步驟完成文件建立、草稿編修與 ODT / PDF 匯出。",
    eyebrow="三步驟流程",
)
if generate_message:
    st.success(generate_message)

active_document_type = st.session_state["generate_document_type"]
active_document_id = st.session_state.get("generate_document_id")
draft_content = st.session_state.get("generate_draft_content")
current_document = (
    get_document_with_current_version(active_document_id) if active_document_id is not None else None
)

render_stepper(
    [
        {"title": "選擇文件", "note": "先決定要建立哪一種社團文件。"},
        {"title": "填寫內容", "note": "依欄位區塊填寫基本資料、內容與清單。"},
        {"title": "預覽與匯出", "note": "確認摘要、儲存版本，並匯出 ODT / PDF。"},
    ],
    _get_active_step_index(draft_content, current_document),
)

st.markdown("### Step 1｜選擇文件")
document_type_columns = st.columns(3, gap="medium")
for index, document_type in enumerate(SUPPORTED_DOCUMENT_TYPES):
    schema = get_document_schema(document_type)
    with document_type_columns[index % 3]:
        badges = [
            badge_html(schema["recommended_evaluation_category"], tone="neutral"),
            badge_html("/".join(schema["output_formats"]), tone="primary"),
        ]
        if active_document_type == document_type:
            badges.append(badge_html("目前選擇", tone="success"))
        with st.container(border=True):
            st.markdown(
                panel_body_html(
                    document_type,
                    DOCUMENT_TYPE_SUMMARIES.get(document_type, "建立正式社團文件。"),
                    badges=badges,
                    eyebrow="文件類型",
                ),
                unsafe_allow_html=True,
            )
            if st.button(
                "選擇這份文件",
                key=f"select_document_type_{document_type}",
                use_container_width=True,
                type="primary" if active_document_type == document_type else "secondary",
            ):
                _set_document_type(document_type)

st.markdown("### Step 2｜填寫內容")
st.caption(f"目前文件類型：{active_document_type} ｜ {DOCUMENT_TYPE_SUMMARIES.get(active_document_type, '')}")

recommended_category = get_recommended_evaluation_category(active_document_type)

if active_document_type == "會議紀錄":
    parser_col, helper_col = st.columns((1.35, 1), gap="large")
    with parser_col:
        with st.form("generate_meeting_minutes_parser"):
            meeting_date = st.text_input("會議日期（可選填）", placeholder="例如：2026-06-24 或 6月24日")
            meeting_name = st.text_input("會議名稱（可選填）", placeholder="例如：第 3 次幹部會議")
            meeting_type = st.selectbox("會議類型", options=MEETING_TYPE_OPTIONS, index=0)
            instruction = st.text_area(
                "補充指令",
                placeholder="例如：這是 6 月 24 日的幹部會議，請幫我做會議紀錄",
                height=100,
            )
            transcript_text = st.text_area(
                "逐字稿或會議文字內容",
                placeholder="請貼上逐字稿、會議摘要或條列內容",
                height=220,
            )
            parse_submitted = st.form_submit_button("產生會議紀錄草稿", type="primary")
        if parse_submitted:
            draft = parse_meeting_minutes(
                transcript_text=transcript_text,
                meeting_date=meeting_date,
                meeting_name=meeting_name,
                meeting_type=meeting_type,
                instruction=instruction,
            )
            st.session_state["generate_draft_content"] = normalize_document_content("會議紀錄", draft)
            st.session_state["generate_document_id"] = None
            st.session_state["generate_evaluation_category"] = recommended_category
            st.session_state["generate_message"] = "已產生會議紀錄草稿，請確認內容後儲存。"
            st.rerun()
    with helper_col:
        st.markdown(
            card_html(
                "會議文字轉草稿",
                "會議紀錄可先貼逐字稿或會議摘要，用 mock parser 快速產生第一版草稿，再到下方表單細修。",
                badges=[badge_html("mock parser", tone="warning"), badge_html("可手動修訂", tone="success")],
            ),
            unsafe_allow_html=True,
        )
        utility_col1, utility_col2 = st.columns(2, gap="small")
        with utility_col1:
            if st.button("建立空白草稿", use_container_width=True, type="secondary"):
                st.session_state["generate_draft_content"] = get_default_document_content("會議紀錄")
                st.session_state["generate_document_id"] = None
                st.session_state["generate_evaluation_category"] = recommended_category
                st.session_state["generate_message"] = "已建立空白會議紀錄草稿。"
                st.rerun()
        with utility_col2:
            if st.button("清除目前草稿", use_container_width=True, type="tertiary"):
                _reset_generate_state("會議紀錄")
                st.rerun()
else:
    st.markdown(
        card_html(
            "表單式建立流程",
            "這類文件不依賴 parser，直接依欄位區塊填寫內容即可建立草稿。",
            badges=[badge_html("表單式生成", tone="primary")],
        ),
        unsafe_allow_html=True,
    )
    if draft_content is None:
        st.session_state["generate_draft_content"] = get_default_document_content(active_document_type)
        draft_content = st.session_state["generate_draft_content"]
    utility_col1, utility_col2 = st.columns(2, gap="small")
    with utility_col1:
        if st.button("建立空白草稿", use_container_width=True, type="secondary"):
            st.session_state["generate_draft_content"] = get_default_document_content(active_document_type)
            st.session_state["generate_document_id"] = None
            st.session_state["generate_evaluation_category"] = recommended_category
            st.session_state["generate_message"] = f"已建立「{active_document_type}」空白草稿。"
            st.rerun()
    with utility_col2:
        if st.button("清除目前草稿", use_container_width=True, type="tertiary"):
            _reset_generate_state(active_document_type)
            st.session_state["generate_draft_content"] = get_default_document_content(active_document_type)
            st.rerun()

draft_content = st.session_state.get("generate_draft_content")

if draft_content is None:
    empty_state(
        "尚未建立草稿",
        "請先選擇文件並建立空白草稿，或在會議紀錄模式貼上逐字稿產生草稿。",
        hint="建立草稿後，這裡會出現可編輯欄位與預覽內容。",
    )
else:
    draft_content = normalize_document_content(active_document_type, draft_content)
    st.session_state["generate_draft_content"] = draft_content

    with st.form("document_editor"):
        selected_category = st.session_state.get("generate_evaluation_category", recommended_category)
        evaluation_category = st.selectbox(
            "對應評鑑分類",
            options=EVALUATION_CATEGORIES,
            index=EVALUATION_CATEGORIES.index(selected_category)
            if selected_category in EVALUATION_CATEGORIES
            else EVALUATION_CATEGORIES.index(recommended_category),
        )
        edited_content = _render_document_editor_fields(
            active_document_type,
            draft_content,
            prefix="generate_editor",
        )
        version_note = st.text_input(
            "版本註記（可選填）",
            placeholder="例如：補上流程細節、更新分工",
        )
        save_submitted = st.form_submit_button(
            "儲存為新文件" if active_document_id is None else "儲存為新版本",
            type="primary",
            use_container_width=True,
        )

    if save_submitted:
        document_title = derive_document_title(
            active_document_type,
            edited_content,
            fallback=get_document_schema(active_document_type)["default_title"],
        )
        if active_document_id is None:
            created_document = create_document(
                title=document_title,
                document_type=active_document_type,
                evaluation_category=evaluation_category,
                status="草稿",
            )
            created_version = create_document_version(
                document_id=created_document["id"],
                content_json=edited_content,
                note=version_note,
            )
            st.session_state["generate_document_id"] = created_document["id"]
            message = f"已建立文件 #{created_document['id']}，目前版本 {created_version['version_label']}。"
        else:
            created_version = create_document_version(
                document_id=active_document_id,
                content_json=edited_content,
                note=version_note,
            )
            message = f"已新增版本 {created_version['version_label']}。"

        st.session_state["generate_draft_content"] = edited_content
        st.session_state["generate_evaluation_category"] = evaluation_category
        st.session_state["generate_message"] = message
        st.rerun()

st.markdown("### Step 3｜預覽與匯出")
if draft_content is None:
    empty_state(
        "目前沒有可預覽內容",
        "請先在 Step 2 建立或產生草稿。",
        hint="完成草稿後，這裡會顯示文件摘要與匯出操作。",
    )
else:
    preview_col, export_col = st.columns((1.35, 1), gap="large")
    with preview_col:
        st.markdown(
            card_html(
                "文件預覽",
                "這裡先顯示摘要式預覽。正式版面仍以下載的 ODT / PDF 為準。",
                badges=[badge_html(active_document_type, tone="primary")],
            ),
            unsafe_allow_html=True,
        )
        _render_preview_blocks(active_document_type, draft_content)

    with export_col:
        current_document = (
            get_document_with_current_version(st.session_state["generate_document_id"])
            if st.session_state.get("generate_document_id") is not None
            else None
        )
        if current_document is None or current_document.get("current_version_data") is None:
            empty_state(
                "尚未可直接匯出",
                "請先把目前草稿儲存成文件，系統才會建立版本並提供 ODT / PDF 匯出。",
                hint="第一次儲存會建立 v1，之後可在這裡直接匯出，或到「檔案庫」管理版本。",
            )
        else:
            version = current_document["current_version_data"]
            export_document = {**current_document, "club_name": club_settings["club_name"]}
            st.markdown(
                card_html(
                    "匯出與加入檔案庫",
                    f"目前文件：{current_document['title']} ｜ {current_document['current_version_label']}",
                    badges=[
                        badge_html(current_document["status"], tone="neutral"),
                        badge_html(current_document["evaluation_category"], tone="neutral"),
                    ],
                ),
                unsafe_allow_html=True,
            )

            generate_col1, generate_col2 = st.columns(2, gap="small")
            with generate_col1:
                if st.button("產生 ODT", use_container_width=True, type="primary"):
                    odf_path, error = _ensure_export_file(export_document, version, "odt")
                    st.session_state["generate_message"] = (
                        f"已產生 ODT：{odf_path}" if error is None else f"產生 ODT 失敗：{error}"
                    )
                    st.rerun()
            with generate_col2:
                if st.button("產生 PDF", use_container_width=True, type="secondary"):
                    pdf_path, error = _ensure_export_file(export_document, version, "pdf")
                    st.session_state["generate_message"] = (
                        f"已產生 PDF：{pdf_path}" if error is None else f"產生 PDF 失敗：{error}"
                    )
                    st.rerun()

            refreshed_document = get_document_with_current_version(current_document["id"])
            refreshed_version = refreshed_document["current_version_data"]
            odf_path = refreshed_version.get("odf_path")
            pdf_path = refreshed_version.get("pdf_path")

            st.download_button(
                "下載 ODT",
                data=Path(odf_path).read_bytes() if odf_path else b"",
                file_name=Path(odf_path).name if odf_path else "document.odt",
                mime="application/vnd.oasis.opendocument.text",
                disabled=not odf_path,
                use_container_width=True,
                type="primary",
            )
            st.download_button(
                "下載 PDF",
                data=Path(pdf_path).read_bytes() if pdf_path else b"",
                file_name=Path(pdf_path).name if pdf_path else "document.pdf",
                mime="application/pdf",
                disabled=not pdf_path,
                use_container_width=True,
                type="secondary",
            )
            st.caption("如需進一步調整版本、狀態與正式版設定，請到「檔案庫」管理。")
