from __future__ import annotations

import re

import streamlit as st

from core.exact_ui import inject_exact_styles


PAGES = [
    ("home", "🏠", "首頁", "工作台"),
    ("Dashboard", "📊", "儀表板", "工作台"),
    ("Templates", "📚", "空白範本", "文件製作"),
    ("Generate", "📝", "生成文件", "文件製作"),
    ("Files", "🗂️", "檔案庫", "文件製作"),
    ("Evaluation", "📦", "社團評鑑", "評鑑管理"),
    ("Settings", "⚙️", "社團設定", "社團資料"),
    ("Projects", "🧭", "專案", "系統支援"),
]


def _first(value: object, default: str = "home") -> str:
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value) if value is not None else default


def normalize_page(page: str) -> str:
    lowered = str(page or "home").lower()
    aliases = {
        "": "home",
        "首頁": "home",
        "dashboard": "Dashboard",
        "templates": "Templates",
        "generate": "Generate",
        "files": "Files",
        "evaluation": "Evaluation",
        "settings": "Settings",
        "projects": "Projects",
    }
    return aliases.get(lowered, page if page in {item[0] for item in PAGES} else "home")


def sync_page_from_query() -> str:
    query_page = normalize_page(_first(st.query_params.get("page"), "home"))
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = query_page
        st.session_state["_last_query_page"] = query_page
    elif query_page != st.session_state.get("_last_query_page"):
        st.session_state["active_page"] = query_page
        st.session_state["_last_query_page"] = query_page
    return normalize_page(st.session_state.get("active_page", "home"))


def go_page(page: str) -> None:
    normalized = normalize_page(page)
    st.session_state["active_page"] = normalized
    st.session_state["_last_query_page"] = normalized
    try:
        st.query_params["page"] = normalized
    except Exception:
        pass
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun is not None:
        rerun()


def inject_native_shell_styles() -> None:
    inject_exact_styles()
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            width: var(--sidebar-w) !important;
            min-width: var(--sidebar-w) !important;
            background: #ffffff !important;
            border-right: 1px solid var(--border) !important;
            box-shadow: 8px 0 22px rgba(15,23,42,.035) !important;
        }
        section[data-testid="stSidebar"] > div,
        div[data-testid="stSidebarContent"] {
            background: #ffffff !important;
            width: var(--sidebar-w) !important;
            padding: 18px 16px !important;
            box-sizing: border-box !important;
        }
        .block-container {
            max-width: 1368px !important;
            padding: 30px 36px 52px 36px !important;
        }
        .odf-native-sidebar-brand {
            display:flex;
            align-items:center;
            gap:12px;
            padding: 2px 4px 20px 4px;
            margin-bottom: 12px;
            border-bottom: 1px solid #eef2f7;
        }
        .odf-native-sidebar-logo {
            width: 42px;
            height:42px;
            border-radius: 14px;
            background: linear-gradient(135deg, #1D6BFF, #6D4CFF);
            display:flex;
            align-items:center;
            justify-content:center;
            color:#fff;
            font-size: 20px;
            box-shadow: 0 10px 22px rgba(29,107,255,.18);
        }
        .odf-native-sidebar-title {
            margin:0;
            font-size: 21px;
            font-weight: 950;
            color:#0f172a;
            letter-spacing:-.04em;
        }
        .odf-native-sidebar-section {
            font-size: 11px;
            font-weight: 900;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: .08em;
            margin: 18px 4px 8px 4px;
        }
        section[data-testid="stSidebar"] .stButton > button {
            width: 100% !important;
            justify-content: flex-start !important;
            min-height: 42px !important;
            border-radius: 13px !important;
            border: 1px solid transparent !important;
            background: transparent !important;
            color: #475569 !important;
            font-weight: 850 !important;
            padding-left: 12px !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #f3f7ff !important;
            color: #1d6bff !important;
            border-color: #d8e7ff !important;
        }
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: #eaf2ff !important;
            color: #1d6bff !important;
            border-color: #cfe1ff !important;
        }
        .odf-native-main-shell {
            width: min(1304px, 100%);
            margin: 0 auto;
            animation: odfNativePageIn .14s ease-out both;
        }
        @keyframes odfNativePageIn {
            from { opacity: .78; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_native_sidebar(active: str) -> None:
    active = normalize_page(active)
    with st.sidebar:
        st.markdown(
            """
            <div class="odf-native-sidebar-brand">
                <div class="odf-native-sidebar-logo">🏫</div>
                <div><h1 class="odf-native-sidebar-title">ODFlow</h1></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        current_group = None
        for page, icon, label, group in PAGES:
            if group != current_group:
                current_group = group
                st.markdown(f'<div class="odf-native-sidebar-section">{group}</div>', unsafe_allow_html=True)
            button_type = "primary" if normalize_page(page) == active else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{page}", type=button_type, use_container_width=True):
                go_page(page)


def extract_content(html: str) -> str:
    marker = '<div class="odf-content">'
    if marker in html and "</div></main>" in html:
        return html.split(marker, 1)[1].rsplit("</div></main>", 1)[0]
    html = re.sub(r'<aside class="odf-sidebar">.*?</aside>', "", html, flags=re.S)
    html = re.sub(r'<div class="odf-topbar">.*?</div>', "", html, flags=re.S)
    return html


def render_html_content(html: str) -> None:
    content = extract_content(html)
    st.markdown(f'<div class="odf-native-main-shell">{content}</div>', unsafe_allow_html=True)
