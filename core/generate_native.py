from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from core.document_schemas import (
    build_document_preview_blocks,
    derive_document_title,
    get_default_document_content,
    get_document_schema,
    get_recommended_evaluation_category,
    normalize_document_content,
)
from core.exact_ui import (
    _loading_veil,
    _same_tab_links,
    _sidebar,
    _topbar,
    inject_exact_styles,
    nav_href,
)
from core.template_service import list_template_definitions
from generators.odt_generator import generate_document_odt


GENERATE_TYPES = {
    "會議紀錄",
    "開會通知單",
    "會議議程",
    "活動企劃書",
    "活動成果報告",
    "活動檢討會紀錄",
    "年度計畫",
}


def _inject_generate_native_styles() -> None:
    st.markdown(
        """
        <style>
        .odf-sidebar {
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            z-index: 50 !important;
        }
        .odf-topbar {
            position: fixed !important;
            left: var(--sidebar-w) !important;
            right: 0 !important;
            top: 0 !important;
            width: auto !important;
            z-index: 45 !important;
        }
        .block-container {
            padding: 108px 44px 56px calc(var(--sidebar-w) + 44px) !important;
            max-width: 100% !important;
        }
        .odf-native-content {
            width: min(1220px, calc(100vw - var(--sidebar-w) - 88px));
            margin: 0 auto;
            box-sizing: border-box;
        }
        .odf-native-card {
            background: rgba(255,255,255,.97);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: var(--shadow-soft);
            padding: 22px 24px;
            box-sizing: border-box;
            margin-bottom: 18px;
        }
        .odf-native-template-card {
            min-height: 190px;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: #fff;
            padding: 18px;
            box-shadow: var(--shadow-soft);
            box-sizing: border-box;
            margin-bottom: 16px;
        }
        .odf-native-template-card.selected {
            border-color: #1D6BFF;
            box-shadow: 0 0 0 3px rgba(29,107,255,.12), var(--shadow-soft);
        }
        .odf-native-stepper {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin: 0 0 24px 0;
        }
        .odf-native-step {
            height: 54px;
            border: 1px solid var(--border);
            border-radius: 14px;
            background: #fff;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0 16px;
            box-shadow: var(--shadow-soft);
            color: #64748B;
            font-weight: 850;
        }
        .odf-native-step.active {
            border-color: #1D6BFF;
            color: #1D6BFF;
            background: #EEF5FF;
        }
        .odf-native-step.done {
            color: #16A34A;
            border-color: #CCEFD7;
            background: #F0FDF4;
        }
        .odf-native-step-badge {
            width: 30px;
            height: 30px;
            border-radius: 999px;
            background: #EEF2F7;
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:900;
            flex: none;
        }
        .odf-native-step.active .odf-native-step-badge {
            background:#1D6BFF;
            color:#fff;
        }
        .odf-native-step.done .odf-native-step-badge {
            background:#DCFCE7;
            color:#16A34A;
        }
        .odf-native-preview-paper {
            background:#fff;
            border:1px solid #dbe7f4;
            border-radius: 14px;
            padding: 28px;
            box-shadow: 0 12px 24px rgba(15,23,42,.08);
            min-height: 560px;
        }
        .odf-native-preview-title {
            text-align:center;
            font-size: 26px;
            font-weight: 920;
            margin: 0 0 22px 0;
            letter-spacing: -.04em;
        }
        .odf-native-preview-heading {
            font-size: 18px;
            font-weight: 900;
            margin: 22px 0 10px 0;
            padding-left: 10px;
            border-left: 4px solid #1D6BFF;
        }
        .odf-native-preview-p {
            color:#334155;
            font-size: 14px;
            line-height: 1.8;
            margin: 6px 0;
            white-space: pre-wrap;
        }
        .odf-native-preview-list {
            margin: 8px 0 8px 20px;
            color:#334155;
            font-size: 14px;
            line-height: 1.8;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTimeInput"] input,
        div[data-testid="stTextArea"] textarea {
            border-radius: 12px !important;
            border-color: #dbe7f4 !important;
        }
        div[data-testid="stTextInput"] label,
        div[data-testid="stDateInput"] label,
        div[data-testid="stTimeInput"] label,
        div[data-testid="stTextArea"] label {
            font-weight: 850 !important;
            color: #334155 !important;
        }
        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 12px !important;
            font-weight: 850 !important;
            min-height: 42px !important;
        }
        @media (max-width: 1280px) {
            .block-container {
                padding: 100px 28px 48px calc(var(--sidebar-w) + 28px) !important;
            }
            .odf-native-content {
                width: min(100%, calc(100vw - var(--sidebar-w) - 56px));
            }
            .odf-native-stepper {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_shell_chrome() -> None:
    inject_exact_styles()
    _inject_generate_native_styles()
    st.markdown(_same_tab_links(_sidebar("Generate") + _topbar("Generate")), unsafe_allow_html=True)


def _page_header() -> None:
    st.markdown(
        """
        <div class="odf-native-content">
            <div class="odf-page-header">
                <div class="odf-page-eyebrow">Generate Document</div>
                <h1 class="odf-page-title">生成文件</h1>
                <p class="odf-page-desc">依照不同社團文件範本填寫專屬欄位，預覽後產出正式 ODT 文件。</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _stepper(step: int) -> None:
    labels = ["選擇範本", "填寫資料", "預覽確認", "下載文件"]
    html = '<div class="odf-native-content"><div class="odf-native-stepper">'
    for index, label in enumerate(labels, start=1):
        cls = "done" if index < step else "active" if index == step else ""
        badge = "✓" if index < step else str(index)
        html += f'<div class="odf-native-step {cls}"><span class="odf-native-step-badge">{badge}</span><span>{label}</span></div>'
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


def _available_templates() -> list[dict]:
    templates = []
    for template in list_template_definitions():
        document_type = template.get("linked_document_type") or template.get("name")
        if template.get("supports_generate_document") and document_type in GENERATE_TYPES:
            templates.append(template)
    return templates


def _selected_template() -> dict | None:
    templates = _available_templates()
    selected_id = st.session_state.get("generate_template_id")
    if selected_id:
        for template in templates:
            if str(template.get("id")) == str(selected_id):
                return template
    return templates[0] if templates else None


def _set_template(template: dict) -> None:
    document_type = template.get("linked_document_type") or template.get("name")
    st.session_state["generate_template_id"] = str(template.get("id"))
    st.session_state["generate_document_type"] = document_type
    st.session_state["generate_content"] = get_default_document_content(document_type)
    st.session_state["generate_step"] = 2


def _document_type_for_template(template: dict | None) -> str:
    if template is None:
        return ""
    return str(template.get("linked_document_type") or template.get("name") or "")


def _default_state_from_query(initial_step: int) -> None:
    if "generate_step" not in st.session_state:
        st.session_state["generate_step"] = int(initial_step or 1)
    templates = _available_templates()
    if templates and "generate_template_id" not in st.session_state:
        template_id = st.query_params.get("template_id")
        selected = next((t for t in templates if str(t.get("id")) == str(template_id)), templates[0])
        st.session_state["generate_template_id"] = str(selected.get("id"))
        document_type = _document_type_for_template(selected)
        st.session_state["generate_document_type"] = document_type
        st.session_state["generate_content"] = get_default_document_content(document_type)


def _rerun() -> None:
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun is not None:
        rerun()


def _coerce_date_value(value: Any) -> date:
    if isinstance(value, date):
        return value
    text = str(value or "").replace("/", "-").strip()
    if not text:
        return date.today()
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return date.today()


def _is_date_field(field: dict) -> bool:
    key = str(field.get("key", "")).lower()
    label = str(field.get("label", ""))
    return "date" in key or "日期" in label or "發文日期" in label


def _field_default(content: dict, field: dict) -> Any:
    value = content.get(field["key"], "")
    if field.get("input_type") == "people_list" and isinstance(value, list):
        return "\n".join(str(v) for v in value if str(v).strip())
    return value


def _render_field(field: dict, content: dict, key_prefix: str) -> Any:
    field_key = field["key"]
    label = field["label"]
    input_type = field.get("input_type", "text")
    default = _field_default(content, field)
    widget_key = f"{key_prefix}_{field_key}"

    if input_type == "textarea":
        return st.text_area(label, value=str(default or ""), height=120, key=widget_key)
    if input_type == "people_list":
        return st.text_area(
            label,
            value=str(default or ""),
            height=100,
            key=widget_key,
            help="一行一位，或用逗號分隔。",
        )
    if _is_date_field(field):
        picked = st.date_input(label, value=_coerce_date_value(default), key=widget_key)
        return picked.strftime("%Y/%m/%d")
    return st.text_input(label, value=str(default or ""), key=widget_key)


def _render_repeatable_section(section: dict, content: dict, key_prefix: str) -> list[dict]:
    rows = content.get(section["key"]) or []
    min_items = max(int(section.get("min_items", 1)), 1)
    columns = section.get("columns") or []
    while len(rows) < min_items:
        rows.append({column["key"]: "" for column in columns})

    st.markdown(f"#### {section['label']}")
    df = pd.DataFrame(rows)
    for column in columns:
        if column["key"] not in df.columns:
            df[column["key"]] = ""
    df = df[[column["key"] for column in columns]]
    df = df.rename(columns={column["key"]: column["label"] for column in columns})

    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key=f"{key_prefix}_{section['key']}",
    )
    edited = edited.rename(columns={column["label"]: column["key"] for column in columns})
    return edited.fillna("").to_dict("records")


def _render_preview_blocks(blocks: list[dict]) -> None:
    html = '<div class="odf-native-preview-paper">'
    for block in blocks:
        kind = block.get("kind")
        if kind == "title":
            html += f'<h2 class="odf-native-preview-title">{block.get("text", "")}</h2>'
        elif kind == "heading":
            html += f'<h3 class="odf-native-preview-heading">{block.get("text", "")}</h3>'
        elif kind == "paragraph":
            html += f'<p class="odf-native-preview-p">{block.get("text", "")}</p>'
        elif kind == "bullet_list":
            html += '<ul class="odf-native-preview-list">'
            for item in block.get("items", []):
                html += f"<li>{item}</li>"
            html += "</ul>"
        else:
            html += f'<p class="odf-native-preview-p">{block.get("text", "")}</p>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _build_document_and_version(document_type: str, content: dict) -> tuple[dict, dict]:
    normalized = normalize_document_content(document_type, content)
    title = derive_document_title(document_type, normalized)
    document = {
        "id": 0,
        "title": title,
        "document_type": document_type,
        "evaluation_category": get_recommended_evaluation_category(document_type),
        "status": "正式版",
    }
    version = {
        "id": 0,
        "version_number": 1,
        "version_label": "v1",
        "content_json": normalized,
        "odf_path": "",
        "pdf_path": "",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    return document, version


def _render_step_1() -> None:
    templates = _available_templates()
    if not templates:
        st.warning("目前沒有可生成文件的範本。請先確認 template registry。")
        return

    st.markdown('<div class="odf-native-content">', unsafe_allow_html=True)
    st.markdown('<div class="odf-native-card"><h3 class="odf-section-title">選擇要生成的文件範本</h3><p class="odf-muted">這裡只列出已接上 schema 與 ODT 產出流程的核心文件。</p></div>', unsafe_allow_html=True)

    cols = st.columns(3)
    current_id = str(st.session_state.get("generate_template_id", ""))
    for index, template in enumerate(templates):
        document_type = _document_type_for_template(template)
        with cols[index % 3]:
            selected = str(template.get("id")) == current_id
            cls = "selected" if selected else ""
            st.markdown(
                f"""
                <div class="odf-native-template-card {cls}">
                    <div class="odf-tag odt">ODT</div>
                    <h3 style="margin:12px 0 8px 0;font-size:19px;">{template.get('name')}</h3>
                    <p class="odf-muted" style="min-height:44px;">{template.get('usage_description') or document_type}</p>
                    <p class="odf-mini">文件類型：{document_type}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("✓ 已選擇" if selected else "選擇這個範本", key=f"choose_{template.get('id')}", use_container_width=True):
                _set_template(template)
                _rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_step_2(template: dict) -> None:
    document_type = _document_type_for_template(template)
    schema = get_document_schema(document_type)
    content = st.session_state.get("generate_content") or get_default_document_content(document_type)
    key_prefix = f"gen_{template.get('id')}_{document_type}"

    st.markdown('<div class="odf-native-content">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="odf-native-card">
            <h3 class="odf-section-title">{schema.get('display_name', document_type)}：填寫資料</h3>
            <p class="odf-muted">每個範本都有自己的欄位。這些欄位會進入預覽與 ODT 下載，不再是固定假資料。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 基本欄位")
    fields = schema.get("fields", [])
    for row_index in range(0, len(fields), 2):
        cols = st.columns(2)
        for col, field in zip(cols, fields[row_index:row_index + 2]):
            with col:
                content[field["key"]] = _render_field(field, content, key_prefix)

    if schema.get("repeatable_sections"):
        st.markdown("### 表格欄位")
        for section in schema["repeatable_sections"]:
            content[section["key"]] = _render_repeatable_section(section, content, key_prefix)

    st.session_state["generate_content"] = content
    st.session_state["generate_document_type"] = document_type

    cols = st.columns([1, 1, 4])
    with cols[0]:
        if st.button("上一步", use_container_width=True):
            st.session_state["generate_step"] = 1
            _rerun()
    with cols[1]:
        if st.button("下一步：預覽確認", type="primary", use_container_width=True):
            st.session_state["generate_content"] = content
            st.session_state["generate_document_type"] = document_type
            st.session_state["generate_step"] = 3
            _rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_step_3(template: dict) -> None:
    document_type = _document_type_for_template(template)
    content = st.session_state.get("generate_content") or get_default_document_content(document_type)
    normalized = normalize_document_content(document_type, content)
    title = derive_document_title(document_type, normalized)

    st.markdown('<div class="odf-native-content">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="odf-native-card">
            <h3 class="odf-section-title">預覽確認</h3>
            <p class="odf-muted">以下預覽由你在上一頁填寫的資料產生。若內容不對，請返回修改。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    blocks = build_document_preview_blocks(document_type, normalized, title_override=title)
    _render_preview_blocks(blocks)

    cols = st.columns([1, 1, 4])
    with cols[0]:
        if st.button("上一步修改", use_container_width=True):
            st.session_state["generate_step"] = 2
            _rerun()
    with cols[1]:
        if st.button("確認並產生", type="primary", use_container_width=True):
            st.session_state["generate_content"] = normalized
            st.session_state["generate_step"] = 4
            _rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_step_4(template: dict) -> None:
    document_type = _document_type_for_template(template)
    content = st.session_state.get("generate_content") or get_default_document_content(document_type)
    normalized = normalize_document_content(document_type, content)
    document, version = _build_document_and_version(document_type, normalized)

    st.markdown('<div class="odf-native-content">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="odf-native-card">
            <h3 class="odf-section-title">文件已產生</h3>
            <p class="odf-muted">下載的是依照你填寫內容產生的 ODT 文件，不是固定假資料。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        output_path = Path(generate_document_odt(document, version, output_dir=Path("data/generated/documents")))
        st.success(f"已產生：{output_path.name}")
        st.download_button(
            "下載 ODT 文件",
            data=output_path.read_bytes(),
            file_name=output_path.name,
            mime="application/vnd.oasis.opendocument.text",
            type="primary",
            use_container_width=True,
        )
    except Exception as exc:
        st.error(f"產生 ODT 失敗：{exc}")

    st.info("PDF 匯出目前仍保留為下一階段功能，避免交付假的 PDF。")

    cols = st.columns([1, 1, 4])
    with cols[0]:
        if st.button("回到預覽", use_container_width=True):
            st.session_state["generate_step"] = 3
            _rerun()
    with cols[1]:
        if st.button("建立另一份", use_container_width=True):
            st.session_state["generate_step"] = 1
            _rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_generate_native(initial_step: int = 1) -> None:
    _default_state_from_query(initial_step)
    _render_shell_chrome()
    _page_header()

    step = int(st.session_state.get("generate_step", initial_step or 1))
    step = max(1, min(4, step))
    template = _selected_template()

    if template is None:
        _stepper(1)
        st.warning("目前沒有可生成文件的範本。")
        return

    _stepper(step)
    if step == 1:
        _render_step_1()
    elif step == 2:
        _render_step_2(template)
    elif step == 3:
        _render_step_3(template)
    else:
        _render_step_4(template)
