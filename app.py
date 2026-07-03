from __future__ import annotations

import streamlit as st

from core.exact_ui import (
    render_dashboard,
    render_exact_page,
    render_files,
    render_generate,
    render_home,
    render_placeholder,
    render_settings,
    render_templates,
)

st.set_page_config(page_title="ODFlow", page_icon="📁", layout="wide", initial_sidebar_state="collapsed")


def _first(value: object, default: str) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value) if value is not None else default


params = st.query_params
page = _first(params.get("page"), "home")
page_key = page.lower()

try:
    step = int(_first(params.get("step"), "1"))
except ValueError:
    step = 1
step = max(1, min(4, step))
fmt = _first(params.get("fmt"), "odt").lower()
template = _first(params.get("template"), "活動企劃書")

if page_key in {"home", "", "首頁"}:
    html = render_home()
elif page_key == "dashboard":
    html = render_dashboard()
elif page_key == "templates":
    html = render_templates()
elif page_key == "generate":
    html = render_generate(step=step, fmt=fmt, template=template)
elif page_key == "files":
    html = render_files()
elif page_key == "settings":
    html = render_settings()
elif page_key == "evaluation":
    html = render_placeholder("Evaluation", "社團評鑑", "整理缺件、待補與待審核資料。")
elif page_key == "projects":
    html = render_placeholder("Projects", "專案", "整理社團專案、活動與階段進度。")
else:
    html = render_home()

render_exact_page(html)
