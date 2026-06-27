from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

import core.template_service as template_service
from core.database import initialize_database
from core.ui_components import (
    badge_html,
    category_badge_html,
    inject_base_styles,
    panel_body_html,
    page_intro,
    paper_preview_shell,
)

TEMPLATE_LIBRARY_CATEGORIES = getattr(
    template_service,
    "TEMPLATE_LIBRARY_CATEGORIES",
    ["日常行政型", "專案活動型", "社團運作型", "財務與清冊型"],
)
generate_template_file = template_service.generate_template_file
list_template_definitions = template_service.list_template_definitions


def _fallback_template_preview_data(template_id: str) -> dict:
    definition = template_service.get_template_definition(template_id)
    table_headers = definition.get("table_headers", [])
    outline_fields = definition.get("outline_fields", [])
    sections = []
    tables = []

    if outline_fields:
        sections.append({"title": "主要章節", "items": outline_fields[:6]})
    if table_headers:
        tables.append(
            {
                "title": "主要欄位",
                "headers": table_headers[:6],
                "rows": [["" for _ in table_headers[:6]] for _ in range(3)],
            }
        )

    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": [definition["name"]],
        "meta_rows": [(field, "") for field in definition.get("basic_fields", [])[:6]],
        "sections": sections,
        "tables": tables,
        "decor": {},
        "footnote": "此為版型預覽，實際格式以下載 ODT 為準。",
    }


build_template_preview_data = getattr(
    template_service,
    "build_template_preview_data",
    _fallback_template_preview_data,
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

    sections_html = "".join(
        (
            "<div style='margin-top:1rem;'>"
            f"<div style='font-weight:700;color:#111827;'>{escape(section['title'])}</div>"
            + (
                "<ul style='margin:0.45rem 0 0 1rem;padding:0;color:#1f2937;'>"
                + "".join(
                    f"<li style='margin:0.18rem 0;'>{escape(item)}</li>"
                    for item in section.get("items", [])
                )
                + "</ul>"
                if section.get("items")
                else ""
            )
            + "</div>"
        )
        for section in preview.get("sections", [])
    )
    tables_html = "".join(_preview_table_html(table) for table in preview.get("tables", []))

    binding_marks = preview.get("decor", {}).get("binding_marks", [])
    binding_html = ""
    if binding_marks:
        binding_html = (
            "<div style='position:absolute;left:-0.8rem;top:1.65rem;display:flex;"
            "flex-direction:column;gap:0.1rem;font-size:0.62rem;color:#6b7280;"
            "letter-spacing:0.12rem;'>"
            + "".join(f"<span>{escape(mark)}</span>" for mark in binding_marks)
            + "</div>"
            "<div style='position:absolute;left:0.2rem;top:1.2rem;bottom:1.2rem;"
            "width:1px;background:#d1d5db;'></div>"
        )

    footer_html = ""
    page_footer = preview.get("decor", {}).get("page_footer")
    if page_footer:
        footer_html = (
            f"<div style='margin-top:1rem;text-align:right;font-size:0.72rem;"
            f"color:#6b7280;'>{escape(page_footer)}</div>"
        )

    inner_html = (
        f"<div style='position:relative;'>{binding_html}{header_html}"
        f"{meta_table_html}{sections_html}{tables_html}{footer_html}</div>"
    )
    return paper_preview_shell(
        inner_html,
        note=preview.get("footnote", "此為版型預覽，實際格式以下載 ODT 為準。"),
    )


def _matches_search(definition: dict, keyword: str) -> bool:
    if not keyword:
        return True
    haystack = " ".join(
        [
            definition["name"],
            definition["usage_description"],
            definition.get("evaluation_category", ""),
            definition.get("linked_document_type", ""),
        ]
    ).lower()
    return keyword.lower() in haystack


initialize_database()
inject_base_styles()

all_templates = list_template_definitions()
template_count = len(all_templates)
st.session_state.setdefault("template_downloads", {})
st.session_state.setdefault("template_selected_id", all_templates[0]["id"] if all_templates else "")

page_intro(
    "空白範本中心",
    "直接下載空白 ODT / ODS 範本，或用核心範本帶入生成文件流程。",
    eyebrow="ODFlow",
)
st.caption(
    "本頁可直接下載空白 ODT / ODS 範本；三個核心文件已支援正式 ODT 樣板填入。"
)

tool_col1, tool_col2 = st.columns((1.6, 0.9), gap="medium")
with tool_col1:
    keyword = st.text_input(
        "搜尋範本 🔎",
        placeholder="輸入關鍵字，例如：會議、企劃、名冊、年度計畫",
    )
with tool_col2:
    category_options = ["全部", *TEMPLATE_LIBRARY_CATEGORIES]
    selected_category = st.selectbox(
        "分類篩選",
        options=category_options,
    )

filtered_templates = [
    definition
    for definition in all_templates
    if (selected_category == "全部" or definition["library_category"] == selected_category)
    and _matches_search(definition, keyword)
]

if filtered_templates and st.session_state["template_selected_id"] not in {
    definition["id"] for definition in filtered_templates
}:
    st.session_state["template_selected_id"] = filtered_templates[0]["id"]

selected_definition = None
if filtered_templates:
    selected_definition = next(
        (
            definition
            for definition in filtered_templates
            if definition["id"] == st.session_state["template_selected_id"]
        ),
        filtered_templates[0],
    )
    st.session_state["template_selected_id"] = selected_definition["id"]

summary_col1, summary_col2 = st.columns((1.5, 1), gap="medium")
with summary_col1:
    with st.container(border=True):
        st.markdown(
            panel_body_html(
                "目前支援的空白範本",
                f"共 {template_count} 個空白 ODT / ODS 範本，依日常行政、專案活動、社團運作與財務清冊快速開始。",
                badges=[
                    badge_html(f"目前顯示 {len(filtered_templates)} 個", tone="primary"),
                    badge_html("A4 文件版型近似預覽", tone="neutral"),
                ],
                eyebrow="Template Center",
            ),
            unsafe_allow_html=True,
        )
with summary_col2:
    with st.container(border=True):
        st.markdown(
            panel_body_html(
                "範本使用方式",
                "先看右側文件版型近似預覽，再決定直接下載空白範本，或用核心範本進入生成文件流程。",
                badges=[badge_html("ODT / ODS", tone="neutral")],
                eyebrow="使用說明",
            ),
            unsafe_allow_html=True,
        )

left_col, right_col = st.columns((1.02, 1.18), gap="large")

with left_col:
    st.markdown("### 範本列表")
    if not filtered_templates:
        st.info("目前沒有符合搜尋條件的範本。請調整關鍵字或分類。")
    else:
        quick_select_options = {
            f"{definition['name']}｜{definition['suggested_format']}": definition["id"]
            for definition in filtered_templates
        }
        selected_label = next(
            (
                label
                for label, template_id in quick_select_options.items()
                if template_id == st.session_state["template_selected_id"]
            ),
            next(iter(quick_select_options)),
        )
        picked_label = st.selectbox(
            "快速切換預覽",
            options=list(quick_select_options.keys()),
            index=list(quick_select_options.keys()).index(selected_label),
        )
        selected_from_picker = quick_select_options[picked_label]
        if selected_from_picker != st.session_state["template_selected_id"]:
            st.session_state["template_selected_id"] = selected_from_picker
            st.rerun()

    for definition in filtered_templates:
        download_path, download_error = _ensure_template_download_path(definition)
        mime = (
            "application/vnd.oasis.opendocument.text"
            if definition["suggested_format"] == "ODT"
            else "application/vnd.oasis.opendocument.spreadsheet"
        )
        is_selected = st.session_state["template_selected_id"] == definition["id"]
        badges = [
            category_badge_html(definition["library_category"]),
            badge_html(definition["suggested_format"], tone="neutral"),
        ]
        if definition.get("evaluation_category"):
            badges.append(badge_html(definition["evaluation_category"], tone="neutral"))
        if is_selected:
            badges.append(badge_html("目前預覽中", tone="primary"))

        with st.container(border=True):
            st.markdown(
                panel_body_html(
                    definition["name"],
                    definition["usage_description"],
                    badges=badges,
                    eyebrow="空白範本",
                ),
                unsafe_allow_html=True,
            )
            action_col1, action_col2, action_col3 = st.columns((0.78, 1.22, 1.24), gap="small")
            with action_col1:
                if st.button(
                    "預覽",
                    key=f"preview_{definition['id']}",
                    use_container_width=True,
                    type="tertiary",
                ):
                    st.session_state["template_selected_id"] = definition["id"]
                    st.rerun()
            with action_col2:
                st.download_button(
                    "下載空白範本",
                    data=download_path.read_bytes() if download_path is not None else b"",
                    file_name=download_path.name if download_path is not None else "",
                    mime=mime,
                    disabled=download_path is None,
                    key=f"download_{definition['id']}",
                    use_container_width=True,
                    type="primary",
                )
            with action_col3:
                if definition.get("linked_document_type"):
                    if st.button(
                        "使用此範本建立文件",
                        key=f"use_{definition['id']}",
                        use_container_width=True,
                        type="secondary",
                    ):
                        _route_to_generate(definition)
                        if not hasattr(st, "switch_page"):
                            st.success("已帶入建立流程，請前往「生成文件」繼續。")
                else:
                    st.button(
                        "使用此範本建立文件",
                        key=f"disabled_use_{definition['id']}",
                        disabled=True,
                        use_container_width=True,
                        type="secondary",
                        help="此範本目前提供空白下載，尚未串接到生成文件流程。",
                    )
        if download_error:
            st.caption(f"目前無法準備下載：{download_error}")

with right_col:
    st.markdown("### 文件版型近似預覽")
    if selected_definition is None:
        st.info("請先從左側選擇一份範本。")
    else:
        with st.container(border=True):
            st.markdown(
                panel_body_html(
                    selected_definition["name"],
                    selected_definition["usage_description"],
                    badges=[
                        category_badge_html(selected_definition["library_category"]),
                        badge_html(selected_definition["suggested_format"], tone="neutral"),
                        badge_html("目前預覽中", tone="primary"),
                    ],
                    eyebrow="文件版型近似預覽",
                ),
                unsafe_allow_html=True,
            )
        st.markdown(_render_preview_html(selected_definition), unsafe_allow_html=True)
