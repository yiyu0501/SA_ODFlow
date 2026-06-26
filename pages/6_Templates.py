from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

from core.database import initialize_database
from core.template_service import (
    TEMPLATE_LIBRARY_CATEGORIES,
    build_template_preview_data,
    generate_template_file,
    list_template_definitions,
)

CATEGORY_COLORS = {
    "日常行政型": "#c53d3d",
    "專案活動型": "#2f855a",
    "社團運作型": "#2b6cb0",
    "財務與清冊型": "#d97706",
}


def _category_badge(category_name: str) -> str:
    color = CATEGORY_COLORS.get(category_name, "#6b7280")
    return (
        "<span style='display:inline-flex;align-items:center;gap:0.4rem;"
        "padding:0.18rem 0.65rem;border:1px solid #e5e7eb;border-radius:999px;"
        "font-size:0.82rem;color:#1f2937;background:#ffffff;'>"
        f"<span style='display:inline-block;width:0.55rem;height:0.55rem;"
        f"border-radius:999px;background:{color};'></span>{escape(category_name)}</span>"
    )


def _info_badge(text: str) -> str:
    return (
        "<span style='display:inline-flex;align-items:center;padding:0.18rem 0.65rem;"
        "border:1px solid #e5e7eb;border-radius:999px;font-size:0.82rem;"
        "color:#4b5563;background:#f8fafc;'>"
        f"{escape(text)}</span>"
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


def _preview_row_html(label: str, value: str) -> str:
    safe_value = escape(value or "＿＿＿＿＿＿＿＿")
    return (
        "<tr>"
        f"<td style='width:28%;padding:0.48rem 0.65rem;border:1px solid #d1d5db;"
        f"background:#f8fafc;font-weight:600;color:#374151;'>{escape(label)}</td>"
        f"<td style='padding:0.48rem 0.65rem;border:1px solid #d1d5db;color:#111827;'>{safe_value}</td>"
        "</tr>"
    )


def _preview_table_html(table: dict) -> str:
    headers = "".join(
        (
            f"<th style='padding:0.42rem 0.5rem;border:1px solid #d1d5db;"
            f"background:#f8fafc;font-weight:600;color:#374151;'>{escape(header)}</th>"
        )
        for header in table.get("headers", [])
    )
    rows = []
    for row in table.get("rows", []):
        cells = "".join(
            (
                f"<td style='padding:0.42rem 0.5rem;border:1px solid #d1d5db;"
                f"color:#111827;min-width:4.4rem;'>{escape(cell or ' ')}</td>"
            )
            for cell in row
        )
        rows.append(f"<tr>{cells}</tr>")
    body = "".join(rows)
    return (
        f"<div style='margin-top:1rem;'><div style='font-weight:700;color:#111827;"
        f"margin-bottom:0.45rem;'>{escape(table['title'])}</div>"
        "<div style='overflow-x:auto;'><table style='width:100%;border-collapse:collapse;"
        "font-size:0.86rem;'><thead><tr>"
        f"{headers}</tr></thead><tbody>{body}</tbody></table></div></div>"
    )


def _render_preview_html(definition: dict) -> str:
    preview = build_template_preview_data(definition["id"])
    header_html = "".join(
        (
            f"<div style='text-align:center;font-weight:700;color:#111827;"
            f"font-size:{'1.15rem' if index == 0 else '1.05rem'};"
            f"margin-top:{'0' if index == 0 else '0.25rem'};'>{escape(line)}</div>"
        )
        for index, line in enumerate(preview.get("header_lines", []))
    )

    meta_rows = "".join(
        _preview_row_html(label, value)
        for label, value in preview.get("meta_rows", [])
    )
    meta_table_html = (
        "<table style='width:100%;border-collapse:collapse;font-size:0.88rem;"
        "margin-top:1rem;'><tbody>"
        f"{meta_rows}</tbody></table>"
        if meta_rows
        else ""
    )

    section_blocks = []
    for section in preview.get("sections", []):
        items_html = ""
        if section.get("items"):
            items_html = (
                "<ul style='margin:0.45rem 0 0 1rem;padding:0;color:#1f2937;'>"
                + "".join(
                    f"<li style='margin:0.18rem 0;'>{escape(item)}</li>"
                    for item in section["items"]
                )
                + "</ul>"
            )
        section_blocks.append(
            f"<div style='margin-top:1rem;'><div style='font-weight:700;color:#111827;'>"
            f"{escape(section['title'])}</div>{items_html}</div>"
        )
    sections_html = "".join(section_blocks)

    tables_html = "".join(
        _preview_table_html(table) for table in preview.get("tables", [])
    )

    binding_marks = preview.get("decor", {}).get("binding_marks", [])
    binding_html = ""
    if binding_marks:
        binding_html = (
            "<div style='position:absolute;left:-0.85rem;top:1.8rem;display:flex;"
            "flex-direction:column;gap:0.12rem;font-size:0.65rem;color:#6b7280;"
            "letter-spacing:0.12rem;'>"
            + "".join(f"<span>{escape(mark)}</span>" for mark in binding_marks)
            + "</div>"
            "<div style='position:absolute;left:0.15rem;top:1.35rem;bottom:1.35rem;"
            "width:1px;background:#d1d5db;'></div>"
        )

    footer_html = ""
    page_footer = preview.get("decor", {}).get("page_footer")
    if page_footer:
        footer_html = (
            f"<div style='margin-top:1rem;text-align:right;font-size:0.72rem;"
            f"color:#6b7280;'>{escape(page_footer)}</div>"
        )

    footnote = escape(preview.get("footnote", "此為版型預覽，實際格式以下載 ODT / ODS 為準。"))

    return (
        "<div style='padding:0.35rem 0 0.1rem;'>"
        "<div style='position:relative;margin:0 auto;max-width:760px;background:#ffffff;"
        "border:1px solid #d1d5db;border-radius:0.4rem;padding:1.5rem 1.3rem 1.2rem 1.5rem;"
        "box-shadow:0 1px 3px rgba(15, 23, 42, 0.08);'>"
        f"{binding_html}{header_html}{meta_table_html}{sections_html}{tables_html}{footer_html}"
        f"<div style='margin-top:1rem;font-size:0.74rem;color:#6b7280;'>{footnote}</div>"
        "</div></div>"
    )


initialize_database()
template_count = len(list_template_definitions())
st.session_state.setdefault("template_downloads", {})

st.title("空白範本")
st.caption("ODFlow 範本中心：可直接下載空白 ODF 範本，也可用核心範本建立文件")

st.write(
    f"目前支援 {template_count} 個空白 ODT / ODS 範本，"
    "分成日常行政型、專案活動型、社團運作型、財務與清冊型四類。"
)
st.info(
    "本頁可直接下載空白 ODT / ODS 範本；"
    "其中會議紀錄、開會通知單、活動企劃書三個核心文件已支援正式 ODT 樣板填入。"
)
st.caption(
    "「預覽」顯示的是文件版型近似預覽，實際格式以下載 ODT / ODS 為準。"
    "若範本已串接生成流程，可直接按「使用此範本建立文件」。"
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
                    st.markdown(
                        (
                            f"{_category_badge(definition['library_category'])} "
                            f"{_info_badge(definition['suggested_format'])}"
                        ),
                        unsafe_allow_html=True,
                    )
                with meta_col:
                    st.write(definition["usage_description"])
                    st.caption(
                        f"對應評鑑分類：{definition['evaluation_category'] or '不限定特定評鑑分類'}"
                    )
                    if definition.get("linked_document_type"):
                        st.caption(
                            f"可直接建立文件：{definition['linked_document_type']}"
                        )

                action_col1, action_col2, action_col3 = st.columns(3)
                with action_col1:
                    with st.popover("預覽", use_container_width=True):
                        st.markdown(_render_preview_html(definition), unsafe_allow_html=True)

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
