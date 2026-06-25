from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from core.constants import DOCUMENT_STATUSES
from core.database import initialize_database
from core.document_schemas import (
    build_document_preview_blocks,
    derive_document_title,
    get_document_schema,
    is_supported_document_type,
    normalize_document_content,
)
from core.document_service import (
    create_document_version,
    get_document_with_current_version,
    get_document_versions,
    list_documents,
    set_current_version,
    update_document_status,
    update_version_file_paths,
)
from core.evaluation_service import COMPLETED_STATUSES, IN_PROGRESS_STATUSES
from core.meeting_minutes import people_list_to_text
from core.settings_service import get_club_settings
from generators.odt_generator import generate_document_odt
from generators.pdf_generator import generate_document_pdf


def _editor_rows_to_list(editor_value) -> list[dict]:
    if hasattr(editor_value, "to_dict"):
        return editor_value.to_dict("records")
    return [dict(row) for row in editor_value]


def _resolve_download_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None

    path = Path(path_value)
    if not path.exists() or not path.is_file():
        return None
    return path


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


def _render_document_editor(document_type: str, content_json: dict, prefix: str) -> dict:
    if not is_supported_document_type(document_type):
        raw_json = st.text_area(
            "編輯 content_json",
            value=json.dumps(content_json, ensure_ascii=False, indent=2),
            height=420,
            key=f"{prefix}_{document_type}_json",
        )
        return json.loads(raw_json)

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

files_message = st.session_state.pop("files_message", "")

st.title("Files")
st.caption("文件庫、版本管理與 ODT/PDF 匯出")

if files_message:
    st.success(files_message)

documents = list_documents()
club_settings = get_club_settings()

if not documents:
    st.info("目前尚無文件。請先到 Generate 頁面建立文件。")
else:
    st.dataframe(
        [
            {
                "文件 ID": document["id"],
                "文件名稱": document["title"],
                "文件類型": document["document_type"],
                "對應評鑑項目": document["evaluation_category"],
                "狀態": document["status"],
                "評鑑計入狀態": (
                    "已完成"
                    if document["status"] in COMPLETED_STATUSES
                    else "進行中"
                    if document["status"] in IN_PROGRESS_STATUSES
                    else "未計入"
                ),
                "目前版本": document["current_version_label"],
                "建立時間": document["created_at"],
                "修改時間": document["updated_at"],
            }
            for document in documents
        ],
        hide_index=True,
        use_container_width=True,
    )

    labels = {
        f"#{document['id']} {document['title']} ({document['current_version_label']})": document["id"]
        for document in documents
    }
    selected_label = st.selectbox("選擇要管理的文件", options=list(labels.keys()))
    selected_document = get_document_with_current_version(labels[selected_label])
    export_document = {**selected_document, "club_name": club_settings["club_name"]}
    versions = get_document_versions(selected_document["id"])
    current_version = selected_document["current_version_data"]
    current_content = current_version["content_json"] if current_version is not None else None

    overview_col, status_col = st.columns((2, 1))
    with overview_col:
        st.subheader(selected_document["title"])
        st.write(
            f"文件類型：{selected_document['document_type']} / 對應評鑑項目："
            f"{selected_document['evaluation_category']}"
        )
    with status_col:
        st.metric("目前版本", selected_document["current_version_label"])
        st.metric("文件狀態", selected_document["status"])

    tab_view, tab_edit, tab_versions, tab_status, tab_export = st.tabs(
        ["查看內容", "編輯內容", "版本管理", "修改狀態", "匯出與下載"]
    )

    with tab_view:
        if current_content is None:
            st.warning("目前版本不存在，請先建立至少一個版本。")
        elif is_supported_document_type(selected_document["document_type"]):
            _render_preview_blocks(selected_document["document_type"], current_content)
        else:
            st.json(current_content)

    with tab_edit:
        if current_content is None:
            st.warning("目前版本不存在，暫時無法編輯。")
        else:
            with st.form(f"edit_document_{selected_document['id']}"):
                edited_content = _render_document_editor(
                    selected_document["document_type"],
                    current_content,
                    prefix=f"files_editor_{selected_document['id']}",
                )
                version_note = st.text_input(
                    "版本註記（可選填）",
                    placeholder="例如：補充流程、更新成果說明",
                )
                save_new_version = st.form_submit_button("儲存為新版本")

            if save_new_version:
                try:
                    new_version = create_document_version(
                        document_id=selected_document["id"],
                        content_json=edited_content,
                        note=version_note,
                    )
                except (ValueError, json.JSONDecodeError) as exc:
                    st.error(f"儲存失敗：{exc}")
                else:
                    st.session_state["files_message"] = (
                        f"已新增版本 {new_version['version_label']}。"
                    )
                    st.rerun()

    with tab_versions:
        st.dataframe(
            [
                {
                    "版本": version["version_label"],
                    "建立時間": version["created_at"],
                    "註記": version["note"] or "",
                }
                for version in versions
            ],
            hide_index=True,
            use_container_width=True,
        )

        version_lookup = {version["version_label"]: version for version in versions}
        selected_version_label = st.selectbox(
            "選擇版本",
            options=list(version_lookup.keys()),
            key=f"version_select_{selected_document['id']}",
        )
        selected_version = version_lookup[selected_version_label]
        if is_supported_document_type(selected_document["document_type"]):
            _render_preview_blocks(
                selected_document["document_type"],
                selected_version["content_json"],
            )
        else:
            st.json(selected_version["content_json"])

        if st.button(
            "設定目前版本為正式版",
            key=f"set_current_official_{selected_document['id']}",
        ):
            set_current_version(
                document_id=selected_document["id"],
                version_number=selected_version["version_number"],
            )
            update_document_status(selected_document["id"], "正式版")
            st.session_state["files_message"] = (
                f"已將 {selected_version['version_label']} 設為目前版本，並將文件狀態更新為正式版。"
            )
            st.rerun()

    with tab_status:
        with st.form(f"update_status_{selected_document['id']}"):
            next_status = st.selectbox(
                "文件狀態",
                options=DOCUMENT_STATUSES,
                index=DOCUMENT_STATUSES.index(selected_document["status"])
                if selected_document["status"] in DOCUMENT_STATUSES
                else 0,
            )
            status_submitted = st.form_submit_button("修改狀態")

        if status_submitted:
            updated_document = update_document_status(selected_document["id"], next_status)
            st.session_state["files_message"] = f"文件狀態已更新為：{updated_document['status']}"
            st.rerun()

    with tab_export:
        if current_version is None:
            st.warning("目前版本不存在，暫時無法產生或下載 ODT / PDF。")
        else:
            generated_title = derive_document_title(
                selected_document["document_type"],
                current_version["content_json"],
                fallback=selected_document["title"],
            )
            st.write(
                f"目前匯出版本：{current_version['version_label']} / "
                f"文件名稱：{generated_title}"
            )
            odt_path = _resolve_download_path(current_version.get("odf_path"))
            pdf_path = _resolve_download_path(current_version.get("pdf_path"))

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("產生 / 更新 ODT", key=f"generate_odt_{selected_document['id']}"):
                    try:
                        output_path = generate_document_odt(
                            export_document,
                            current_version,
                        )
                        update_version_file_paths(
                            document_id=selected_document["id"],
                            version_number=current_version["version_number"],
                            odf_path=str(output_path),
                        )
                    except (RuntimeError, ValueError) as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["files_message"] = f"已更新 ODT：{output_path.name}"
                        st.rerun()

                st.download_button(
                    "下載 ODT",
                    data=odt_path.read_bytes() if odt_path is not None else b"",
                    file_name=odt_path.name if odt_path is not None else "document.odt",
                    mime="application/vnd.oasis.opendocument.text",
                    disabled=odt_path is None,
                    key=f"download_odt_{selected_document['id']}",
                )

            with action_col2:
                if st.button("產生 / 更新 PDF", key=f"generate_pdf_{selected_document['id']}"):
                    try:
                        output_path = generate_document_pdf(
                            export_document,
                            current_version,
                        )
                        update_version_file_paths(
                            document_id=selected_document["id"],
                            version_number=current_version["version_number"],
                            pdf_path=str(output_path),
                        )
                    except (RuntimeError, ValueError) as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["files_message"] = f"已更新 PDF：{output_path.name}"
                        st.rerun()

                st.download_button(
                    "下載 PDF",
                    data=pdf_path.read_bytes() if pdf_path is not None else b"",
                    file_name=pdf_path.name if pdf_path is not None else "document.pdf",
                    mime="application/pdf",
                    disabled=pdf_path is None,
                    key=f"download_pdf_{selected_document['id']}",
                )

            st.caption(
                f"ODT：{odt_path if odt_path is not None else '尚未產生'}  |  "
                f"PDF：{pdf_path if pdf_path is not None else '尚未產生'}"
            )
