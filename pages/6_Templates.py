from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.database import initialize_database
from core.template_service import (
    TEMPLATE_LIBRARY_CATEGORIES,
    generate_template_file,
    list_template_definitions,
)


def _resolve_download_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None

    path = Path(path_value)
    if path.exists() and path.is_file():
        return path
    return None


def _ensure_template_download_path(definition: dict) -> tuple[Path | None, str | None]:
    cached_path = _resolve_download_path(
        st.session_state.setdefault("template_downloads", {}).get(definition["id"])
    )
    if cached_path is not None:
        return cached_path, None

    try:
        output_path = generate_template_file(definition["id"])
    except ValueError as exc:
        return None, str(exc)

    st.session_state["template_downloads"][definition["id"]] = str(output_path)
    return output_path, None


def _route_to_generate(definition: dict) -> None:
    linked_document_type = definition.get("linked_document_type")
    if not linked_document_type:
        return

    st.session_state["generate_requested_document_type"] = linked_document_type
    st.session_state["generate_message"] = (
        f"已選擇核心範本「{definition['name']}」，可直接前往「生成文件」建立 {linked_document_type}。"
    )
    if hasattr(st, "switch_page"):
        st.switch_page("pages/2_Generate.py")


def _preview_lines(definition: dict) -> list[str]:
    lines = []
    basic_fields = definition.get("basic_fields", [])
    outline_fields = definition.get("outline_fields", [])
    table_headers = definition.get("table_headers", [])
    instructions = definition.get("instructions", [])

    if basic_fields:
        lines.append("基本欄位：" + "、".join(basic_fields))
    if outline_fields:
        lines.append("主要段落：" + "、".join(outline_fields))
    if table_headers:
        lines.append("表格欄位：" + "、".join(table_headers))
    if instructions:
        lines.append("使用提醒：" + "；".join(instructions))
    return lines


initialize_database()
template_count = len(list_template_definitions())
st.session_state.setdefault("template_downloads", {})

st.title("空白範本")
st.caption("ODFlow 範本中心：可直接下載空白 ODF 範本，也可用核心範本建立文件")

st.write(
    f"目前支援 {template_count} 個空白 ODT / ODS 範本，"
    "分成日常行政、活動專案、社團評鑑、財務與清冊四類。"
)
st.info(
    "下載空白範本不需要先填資料，也不需要先建立文件。"
    "其中 7 個核心 ODT 範本另外提供「使用此範本建立文件」入口。"
)

category_tabs = st.tabs(TEMPLATE_LIBRARY_CATEGORIES)

for category_name, tab in zip(TEMPLATE_LIBRARY_CATEGORIES, category_tabs):
    with tab:
        templates = list_template_definitions(category_name)
        st.subheader(category_name)
        for definition in templates:
            download_path, download_error = _ensure_template_download_path(definition)
            mime = (
                "application/vnd.oasis.opendocument.text"
                if definition["suggested_format"] == "ODT"
                else "application/vnd.oasis.opendocument.spreadsheet"
            )

            with st.container(border=True):
                title_col, meta_col = st.columns((2, 3))
                with title_col:
                    st.markdown(f"**{definition['name']}**")
                    st.caption(
                        f"{definition['suggested_format']} ｜ {definition['template_type']}"
                    )
                with meta_col:
                    st.write(f"使用情境：{definition['usage_description']}")
                    st.write(
                        f"對應評鑑分類：{definition['evaluation_category'] or '不限定特定評鑑分類'}"
                    )
                    if definition.get("linked_document_type"):
                        st.caption(
                            f"此核心範本可直接建立文件：{definition['linked_document_type']}"
                        )

                action_col1, action_col2, action_col3 = st.columns(3)
                with action_col1:
                    with st.popover("預覽", use_container_width=True):
                        for line in _preview_lines(definition):
                            st.write(line)

                with action_col2:
                    st.download_button(
                        "下載空白範本",
                        data=download_path.read_bytes() if download_path is not None else b"",
                        file_name=download_path.name if download_path is not None else "",
                        mime=mime,
                        disabled=download_path is None,
                        key=f"download_{definition['id']}",
                        use_container_width=True,
                    )
                    if download_error:
                        st.caption(f"目前無法準備下載：{download_error}")
                    else:
                        st.caption("可直接下載空白範本，不需先建立文件。")

                with action_col3:
                    if definition.get("linked_document_type"):
                        if st.button(
                            "使用此範本建立文件",
                            key=f"use_template_{definition['id']}",
                            use_container_width=True,
                        ):
                            _route_to_generate(definition)
                            if not hasattr(st, "switch_page"):
                                st.success(
                                    "已帶入建立流程，請前往「生成文件」繼續。"
                                )
                    else:
                        st.button(
                            "使用此範本建立文件",
                            key=f"disabled_use_template_{definition['id']}",
                            disabled=True,
                            use_container_width=True,
                            help="此範本目前提供空白下載，尚未串接到生成文件流程。",
                        )
