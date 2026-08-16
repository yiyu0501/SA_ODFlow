from __future__ import annotations

import streamlit as st

from core.generate_native import render_generate_native
from core.exact_ui import (
    render_activities,
    render_dashboard,
    render_demo_login,
    render_evaluation,
    render_exact_page,
    render_files,
    render_home,
    render_public_landing,
    render_settings,
    render_templates,
)


def _first(value: object, default: str) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value) if value is not None else default


def _normalize_page(page_name: str) -> str:
    normalized = page_name.strip().lower()
    aliases = {
        "": "home",
        "首頁": "home",
        "landing": "landing",
        "dashboard": "dashboard",
        "activities": "activities",
        "activity": "activities",
        "generate": "generate",
        "templates": "templates",
        "files": "files",
        "evaluation": "evaluation",
        "settings": "settings",
        "projects": "activities",
    }
    return aliases.get(normalized, normalized)


def _navigate(query: dict[str, str]) -> None:
    st.query_params.clear()
    for key, value in query.items():
        st.query_params[key] = value
    st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="ODFlow", page_icon="📁", layout="wide", initial_sidebar_state="collapsed")

    params = st.query_params
    page = _first(params.get("page"), "landing")
    page_key = _normalize_page(page)
    workspace = _first(params.get("workspace"), "").strip().lower()
    workspace_active = workspace == "demo"
    target_page = _normalize_page(_first(params.get("next"), "home"))
    login_action = _first(params.get("action"), "").strip().lower()
    login_error = ""

    try:
        step = int(_first(params.get("step"), "1"))
    except ValueError:
        step = 1
    step = max(1, min(4, step))

    if not workspace_active and page_key == "login" and login_action == "login":
        email = _first(params.get("email"), "").strip()
        password = _first(params.get("password"), "").strip()
        if email and password:
            _navigate({"workspace": "demo", "page": target_page})
        login_error = "請先填入 Demo 信箱與密碼，再進入工作區。"

    workspace_pages = {"home", "dashboard", "activities", "templates", "generate", "files", "settings", "evaluation"}

    if workspace_active:
        if page_key in {"landing", "login"}:
            page_key = "home"

        if page_key == "home":
            html = render_home()
        elif page_key == "activities":
            html = render_activities()
        elif page_key == "dashboard":
            html = render_dashboard()
        elif page_key == "templates":
            html = render_templates()
        elif page_key == "generate":
            render_generate_native(initial_step=step)
            st.stop()
        elif page_key == "files":
            html = render_files()
        elif page_key == "settings":
            html = render_settings()
        elif page_key == "evaluation":
            html = render_evaluation()
        else:
            html = render_home()
    else:
        if page_key == "login":
            html = render_demo_login(target_page=target_page, error_message=login_error)
        elif page_key in {"landing", "home"}:
            html = render_public_landing()
        elif page_key in workspace_pages:
            html = render_demo_login(
                target_page=page_key,
                error_message="請先進入 Demo 工作區後，再使用這個模組。",
            )
        else:
            html = render_public_landing()

    render_exact_page(html)
