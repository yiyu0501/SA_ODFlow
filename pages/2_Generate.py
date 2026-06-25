from __future__ import annotations

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
from core.document_service import create_document, create_document_version, get_document
from core.meeting_minutes import people_list_to_text


SUPPORTED_DOCUMENT_TYPES = list_supported_document_types()


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


def _render_document_editor_fields(document_type: str, content_json: dict, prefix: str) -> dict:
    schema = get_document_schema(document_type)
    edited = {}

    for field in schema["fields"]:
        key = field["key"]
        label = field["label"]
        input_type = field["input_type"]
        widget_key = f"{prefix}_{document_type}_{key}"
        current_value = content_json.get(key, "")

        if input_type == "textarea":
            edited[key] = st.text_area(
                label,
                value=str(current_value),
                height=120,
                key=widget_key,
            )
        elif input_type == "people_list":
            edited[key] = st.text_area(
                label,
                value=people_list_to_text(current_value),
                height=100,
                help="每行一位，或使用逗號分隔。",
                key=widget_key,
            )
        else:
            edited[key] = st.text_input(label, value=str(current_value), key=widget_key)

    for section in schema["repeatable_sections"]:
        edited[section["key"]] = _editor_rows_to_list(
            st.data_editor(
                content_json.get(section["key"], []),
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    column["key"]: column["label"] for column in section["columns"]
                },
                key=f"{prefix}_{document_type}_{section['key']}",
            )
        )

    return normalize_document_content(document_type, edited)


initialize_database()
_initialize_state()

generate_message = st.session_state.pop("generate_message", "")

st.title("生成文件")
st.caption("建立七種核心社團文件，並儲存為可持續編輯的草稿與版本")

if generate_message:
    st.success(generate_message)

selected_document_type = st.selectbox(
    "文件類型",
    options=SUPPORTED_DOCUMENT_TYPES,
    index=SUPPORTED_DOCUMENT_TYPES.index(st.session_state["generate_document_type"]),
)
_set_document_type(selected_document_type)

active_document_type = st.session_state["generate_document_type"]
active_document_id = st.session_state.get("generate_document_id")
recommended_category = get_recommended_evaluation_category(active_document_type)

if active_document_type == "會議紀錄":
    st.write("會議紀錄可先貼上逐字稿，用 mock parser 產生草稿，再進一步編輯與儲存。")
    with st.form("generate_meeting_minutes_parser"):
        meeting_date = st.text_input(
            "會議日期（可選填）",
            placeholder="例如：2026-06-24 或 6月24日",
        )
        meeting_name = st.text_input(
            "會議名稱（可選填）",
            placeholder="例如：第 3 次幹部會議",
        )
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
        parse_submitted = st.form_submit_button("產生會議紀錄草稿")

    create_blank_col, reset_col = st.columns(2)
    with create_blank_col:
        if st.button("建立空白會議紀錄草稿", use_container_width=True):
            st.session_state["generate_draft_content"] = get_default_document_content("會議紀錄")
            st.session_state["generate_document_id"] = None
            st.session_state["generate_evaluation_category"] = recommended_category
            st.session_state["generate_message"] = "已建立空白會議紀錄草稿。"
            st.rerun()
    with reset_col:
        if st.button("清除目前草稿", use_container_width=True):
            _reset_generate_state("會議紀錄")
            st.rerun()

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
else:
    st.write("這類文件採表單式產生，可直接填欄位建立草稿。")
    if st.session_state.get("generate_draft_content") is None:
        st.session_state["generate_draft_content"] = get_default_document_content(
            active_document_type
        )
    utility_col1, utility_col2 = st.columns(2)
    with utility_col1:
        if st.button("建立空白草稿", use_container_width=True):
            st.session_state["generate_draft_content"] = get_default_document_content(
                active_document_type
            )
            st.session_state["generate_document_id"] = None
            st.session_state["generate_evaluation_category"] = recommended_category
            st.session_state["generate_message"] = f"已建立「{active_document_type}」空白草稿。"
            st.rerun()
    with utility_col2:
        if st.button("清除目前草稿", use_container_width=True):
            _reset_generate_state(active_document_type)
            st.session_state["generate_draft_content"] = get_default_document_content(
                active_document_type
            )
            st.rerun()

draft_content = st.session_state.get("generate_draft_content")
current_document = get_document(active_document_id) if active_document_id is not None else None

if draft_content is None:
    st.info("請先建立草稿，再進行編輯與儲存。")
else:
    draft_content = normalize_document_content(active_document_type, draft_content)
    st.session_state["generate_draft_content"] = draft_content

    st.subheader("可編輯文件草稿")
    if current_document is None:
        st.info("這份草稿尚未儲存成文件。第一次儲存會建立 v1。")
    else:
        st.info(
            f"目前文件 ID：{current_document['id']}，狀態：{current_document['status']}，"
            f"目前版本：{current_document['current_version_label']}"
        )

    with st.expander("草稿預覽", expanded=False):
        _render_preview_blocks(active_document_type, draft_content)

    with st.form("document_editor"):
        selected_category = st.session_state.get(
            "generate_evaluation_category",
            recommended_category,
        )
        evaluation_category = st.selectbox(
            "對應評鑑分類",
            options=EVALUATION_CATEGORIES,
            index=EVALUATION_CATEGORIES.index(selected_category)
            if selected_category in EVALUATION_CATEGORIES
            else EVALUATION_CATEGORIES.index(recommended_category),
        )
        content_json = _render_document_editor_fields(
            active_document_type,
            draft_content,
            prefix="generate_editor",
        )
        version_note = st.text_input(
            "版本註記（可選填）",
            placeholder="例如：補上流程細節、更新分工",
        )
        save_submitted = st.form_submit_button(
            "儲存為新文件" if active_document_id is None else "儲存為新版本"
        )

    if save_submitted:
        document_title = derive_document_title(
            active_document_type,
            content_json,
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
