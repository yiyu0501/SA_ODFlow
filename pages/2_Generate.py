from __future__ import annotations

import streamlit as st

from ai.mock_parser import parse_meeting_minutes
from core.constants import MEETING_MINUTES_EVALUATION_CATEGORIES, MEETING_TYPE_OPTIONS
from core.database import initialize_database
from core.document_service import create_document, create_document_version, get_document
from core.meeting_minutes import normalize_meeting_minutes_content, people_list_to_text


def _editor_rows_to_list(editor_value) -> list[dict]:
    if hasattr(editor_value, "to_dict"):
        return editor_value.to_dict("records")
    return [dict(row) for row in editor_value]


def _draft_exists() -> bool:
    return bool(st.session_state.get("generate_has_draft"))


def _reset_generate_state() -> None:
    st.session_state["generate_has_draft"] = False
    st.session_state["generate_draft_content"] = None
    st.session_state["generate_document_id"] = None
    st.session_state["generate_evaluation_category"] = (
        MEETING_MINUTES_EVALUATION_CATEGORIES[0]
    )
    st.session_state["generate_message"] = ""


initialize_database()

if "generate_has_draft" not in st.session_state:
    _reset_generate_state()

generate_message = st.session_state.pop("generate_message", "")

st.title("Generate")
st.caption("會議紀錄生成與儲存")

if generate_message:
    st.success(generate_message)

with st.form("generate_meeting_minutes"):
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
    generate_submitted = st.form_submit_button("產生會議紀錄草稿")

if generate_submitted:
    draft = parse_meeting_minutes(
        transcript_text=transcript_text,
        meeting_date=meeting_date,
        meeting_name=meeting_name,
        meeting_type=meeting_type,
        instruction=instruction,
    )
    st.session_state["generate_has_draft"] = True
    st.session_state["generate_draft_content"] = draft
    st.session_state["generate_document_id"] = None
    st.session_state["generate_evaluation_category"] = (
        MEETING_MINUTES_EVALUATION_CATEGORIES[0]
    )
    st.session_state["generate_message"] = "已產生會議紀錄草稿，請確認內容後儲存。"
    st.rerun()

if _draft_exists():
    if st.button("開始新草稿"):
        _reset_generate_state()
        st.rerun()

    draft = normalize_meeting_minutes_content(
        st.session_state.get("generate_draft_content")
    )
    active_document_id = st.session_state.get("generate_document_id")
    selected_category = st.session_state.get(
        "generate_evaluation_category",
        MEETING_MINUTES_EVALUATION_CATEGORIES[0],
    )

    current_document = (
        get_document(active_document_id) if active_document_id is not None else None
    )

    st.subheader("可編輯會議紀錄草稿")
    if current_document is None:
        st.info("這份草稿尚未儲存成文件。第一次儲存會建立 v1。")
    else:
        st.info(
            f"目前文件 ID：{current_document['id']}，狀態：{current_document['status']}，"
            f"目前版本：{current_document['current_version_label']}"
        )

    with st.form("meeting_minutes_editor"):
        evaluation_category = st.selectbox(
            "對應評鑑分類",
            options=MEETING_MINUTES_EVALUATION_CATEGORIES,
            index=MEETING_MINUTES_EVALUATION_CATEGORIES.index(selected_category),
        )

        col1, col2 = st.columns(2)
        with col1:
            edited_title = st.text_input("會議名稱", value=draft["meeting_title"])
            edited_date = st.text_input("會議日期", value=draft["meeting_date"])
            edited_time = st.text_input("會議時間", value=draft["meeting_time"])
            edited_location = st.text_input("會議地點", value=draft["location"])
            edited_chair = st.text_input("主席", value=draft["chair"])
            edited_recorder = st.text_input("紀錄", value=draft["recorder"])
        with col2:
            edited_attendees = st.text_area(
                "出席人員",
                value=people_list_to_text(draft["attendees"]),
                height=120,
                help="每行一位，或使用逗號分隔。",
            )
            edited_absentees = st.text_area(
                "請假人員",
                value=people_list_to_text(draft["absentees"]),
                height=120,
                help="每行一位，或使用逗號分隔。",
            )
            edited_next_meeting = st.text_input(
                "下次會議時間",
                value=draft["next_meeting_time"],
            )

        edited_agenda_items = st.data_editor(
            draft["agenda_items"],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "title": "討論事項",
                "discussion": "討論內容",
                "decision": "決議事項",
            },
            key="generate_agenda_items",
        )
        edited_action_items = st.data_editor(
            draft["action_items"],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "task": "待辦事項",
                "owner": "負責人",
                "deadline": "期限",
                "note": "備註",
            },
            key="generate_action_items",
        )
        edited_notes = st.text_area("備註", value=draft["notes"], height=120)
        version_note = st.text_input(
            "版本註記（可選填）",
            placeholder="例如：補上出席名單、調整決議內容",
        )

        save_submitted = st.form_submit_button(
            "儲存為新文件" if active_document_id is None else "儲存為新版本"
        )

    if save_submitted:
        content_json = normalize_meeting_minutes_content(
            {
                "meeting_title": edited_title,
                "meeting_date": edited_date,
                "meeting_time": edited_time,
                "location": edited_location,
                "chair": edited_chair,
                "recorder": edited_recorder,
                "attendees": edited_attendees,
                "absentees": edited_absentees,
                "agenda_items": _editor_rows_to_list(edited_agenda_items),
                "action_items": _editor_rows_to_list(edited_action_items),
                "next_meeting_time": edited_next_meeting,
                "notes": edited_notes,
            }
        )

        document_title = content_json["meeting_title"] or "會議紀錄草稿"

        if active_document_id is None:
            created_document = create_document(
                title=document_title,
                document_type="會議紀錄",
                evaluation_category=evaluation_category,
                status="草稿",
            )
            created_version = create_document_version(
                document_id=created_document["id"],
                content_json=content_json,
                note=version_note,
            )
            st.session_state["generate_document_id"] = created_document["id"]
            message = (
                f"已建立文件 #{created_document['id']}，目前版本 {created_version['version_label']}。"
            )
        else:
            created_version = create_document_version(
                document_id=active_document_id,
                content_json=content_json,
                note=version_note,
            )
            message = f"已新增版本 {created_version['version_label']}。"

        st.session_state["generate_draft_content"] = content_json
        st.session_state["generate_evaluation_category"] = evaluation_category
        st.session_state["generate_message"] = message
        st.rerun()
else:
    st.info("請先輸入逐字稿或會議文字內容，再產生會議紀錄草稿。")
