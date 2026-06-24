from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.constants import DOCUMENT_STATUSES
from core.database import initialize_database
from core.document_service import (
    create_document_version,
    get_document_with_current_version,
    get_document_versions,
    list_documents,
    set_current_version,
    update_version_file_paths,
    update_document_status,
)
from core.meeting_minutes import normalize_meeting_minutes_content, people_list_to_text
from core.evaluation_service import COMPLETED_STATUSES, IN_PROGRESS_STATUSES
from core.settings_service import get_club_settings
from generators.odt_generator import generate_meeting_minutes_odt
from generators.pdf_generator import generate_meeting_minutes_pdf


def _editor_rows_to_list(editor_value) -> list[dict]:
    if hasattr(editor_value, "to_dict"):
        return editor_value.to_dict("records")
    return [dict(row) for row in editor_value]


def _render_meeting_minutes_content(content_json: dict) -> None:
    st.markdown(f"**會議名稱**：{content_json['meeting_title'] or '-'}")
    st.markdown(f"**會議日期**：{content_json['meeting_date'] or '-'}")
    st.markdown(f"**會議時間**：{content_json['meeting_time'] or '-'}")
    st.markdown(f"**會議地點**：{content_json['location'] or '-'}")
    st.markdown(f"**主席**：{content_json['chair'] or '-'}")
    st.markdown(f"**紀錄**：{content_json['recorder'] or '-'}")
    st.markdown(
        f"**出席人員**：{people_list_to_text(content_json['attendees']) or '-'}"
    )
    st.markdown(
        f"**請假人員**：{people_list_to_text(content_json['absentees']) or '-'}"
    )

    st.markdown("**討論與決議**")
    for index, item in enumerate(content_json["agenda_items"], start=1):
        st.markdown(f"{index}. {item['title'] or '未命名議題'}")
        st.write(f"討論：{item['discussion'] or '-'}")
        st.write(f"決議：{item['decision'] or '-'}")

    st.markdown("**待辦事項**")
    for index, item in enumerate(content_json["action_items"], start=1):
        st.write(
            f"{index}. {item['task'] or '未填寫'} / 負責人：{item['owner'] or '-'} "
            f"/ 期限：{item['deadline'] or '-'} / 備註：{item['note'] or '-'}"
        )

    st.markdown(f"**下次會議時間**：{content_json['next_meeting_time'] or '-'}")
    st.markdown(f"**備註**：{content_json['notes'] or '-'}")


def _resolve_download_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None

    path = Path(path_value)
    if not path.exists() or not path.is_file():
        return None
    return path


initialize_database()

files_message = st.session_state.pop("files_message", "")

st.title("Files")
st.caption("文件庫與版本管理")

if files_message:
    st.success(files_message)

documents = list_documents()
club_settings = get_club_settings()

if not documents:
    st.info("目前尚無文件。請先到 Generate 頁面建立會議紀錄。")
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
    current_content = (
        normalize_meeting_minutes_content(current_version["content_json"])
        if current_version is not None
        else None
    )

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
        else:
            _render_meeting_minutes_content(current_content)

    with tab_edit:
        if current_content is None:
            st.warning("目前版本不存在，暫時無法編輯。")
        else:
            with st.form(f"edit_document_{selected_document['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    edited_title = st.text_input("會議名稱", value=current_content["meeting_title"])
                    edited_date = st.text_input("會議日期", value=current_content["meeting_date"])
                    edited_time = st.text_input("會議時間", value=current_content["meeting_time"])
                    edited_location = st.text_input("會議地點", value=current_content["location"])
                    edited_chair = st.text_input("主席", value=current_content["chair"])
                    edited_recorder = st.text_input("紀錄", value=current_content["recorder"])
                with col2:
                    edited_attendees = st.text_area(
                        "出席人員",
                        value=people_list_to_text(current_content["attendees"]),
                        height=120,
                    )
                    edited_absentees = st.text_area(
                        "請假人員",
                        value=people_list_to_text(current_content["absentees"]),
                        height=120,
                    )
                    edited_next_meeting = st.text_input(
                        "下次會議時間",
                        value=current_content["next_meeting_time"],
                    )

                edited_agenda_items = st.data_editor(
                    current_content["agenda_items"],
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "title": "討論事項",
                        "discussion": "討論內容",
                        "decision": "決議事項",
                    },
                    key=f"files_agenda_items_{selected_document['id']}",
                )
                edited_action_items = st.data_editor(
                    current_content["action_items"],
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "task": "待辦事項",
                        "owner": "負責人",
                        "deadline": "期限",
                        "note": "備註",
                    },
                    key=f"files_action_items_{selected_document['id']}",
                )
                edited_notes = st.text_area("備註", value=current_content["notes"], height=120)
                version_note = st.text_input(
                    "版本註記（可選填）",
                    placeholder="例如：補充決議、更新待辦事項",
                )
                save_new_version = st.form_submit_button("儲存為新版本")

            if save_new_version:
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
                new_version = create_document_version(
                    document_id=selected_document["id"],
                    content_json=content_json,
                    note=version_note,
                )
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

        version_lookup = {
            version["version_label"]: version for version in versions
        }
        selected_version_label = st.selectbox(
            "選擇版本",
            options=list(version_lookup.keys()),
            key=f"version_select_{selected_document['id']}",
        )
        selected_version = version_lookup[selected_version_label]
        _render_meeting_minutes_content(selected_version["content_json"])

        if st.button("設定目前版本為正式版", key=f"set_current_official_{selected_document['id']}"):
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
            st.session_state["files_message"] = (
                f"文件狀態已更新為：{updated_document['status']}"
            )
            st.rerun()

    with tab_export:
        if current_version is None:
            st.warning("目前版本不存在，暫時無法產生或下載 ODT / PDF。")
        else:
            st.write(
                f"目前匯出版本：{current_version['version_label']} / "
                f"文件名稱：{selected_document['title']}"
            )
            odt_path = _resolve_download_path(current_version.get("odf_path"))
            pdf_path = _resolve_download_path(current_version.get("pdf_path"))

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("產生 / 更新 ODT", key=f"generate_odt_{selected_document['id']}"):
                    try:
                        output_path = generate_meeting_minutes_odt(
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
                    file_name=odt_path.name if odt_path is not None else "meeting_minutes.odt",
                    mime="application/vnd.oasis.opendocument.text",
                    disabled=odt_path is None,
                    key=f"download_odt_{selected_document['id']}",
                )

            with action_col2:
                if st.button("產生 / 更新 PDF", key=f"generate_pdf_{selected_document['id']}"):
                    try:
                        output_path = generate_meeting_minutes_pdf(
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
                    file_name=pdf_path.name if pdf_path is not None else "meeting_minutes.pdf",
                    mime="application/pdf",
                    disabled=pdf_path is None,
                    key=f"download_pdf_{selected_document['id']}",
                )

            st.caption(
                f"ODT：{odt_path if odt_path is not None else '尚未產生'}  |  "
                f"PDF：{pdf_path if pdf_path is not None else '尚未產生'}"
            )
