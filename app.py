from __future__ import annotations

import streamlit as st

from core.exact_ui import (
    render_dashboard,
    render_files,
    render_home,
    render_placeholder,
    render_settings,
    render_templates,
)
from core.generate_native import render_generate_native_content
from core.native_shell import (
    inject_native_shell_styles,
    render_html_content,
    render_native_sidebar,
    sync_page_from_query,
)

st.set_page_config(page_title="ODFlow", page_icon="📁", layout="wide", initial_sidebar_state="expanded")

active_page = sync_page_from_query()
inject_native_shell_styles()
render_native_sidebar(active_page)

if active_page in {"home", "", "首頁"}:
    render_html_content(render_home())
elif active_page == "Dashboard":
    render_html_content(render_dashboard())
elif active_page == "Templates":
    render_html_content(render_templates())
elif active_page == "Generate":
    render_generate_native_content()
elif active_page == "Files":
    render_html_content(render_files())
elif active_page == "Settings":
    render_html_content(render_settings())
elif active_page == "Evaluation":
    render_html_content(render_placeholder("Evaluation", "社團評鑑", "整理缺件、待補與待審核資料。"))
elif active_page == "Projects":
    render_html_content(render_placeholder("Projects", "專案", "整理社團專案、活動與階段進度。"))
else:
    render_html_content(render_home())
