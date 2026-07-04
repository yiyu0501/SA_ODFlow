from __future__ import annotations

import streamlit as st

from core.generate_native import render_generate_native

st.set_page_config(page_title="生成文件｜ODFlow", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")

params = st.query_params

def _first(value: object, default: str) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value) if value is not None else default

try:
    step = int(_first(params.get("step"), "1"))
except ValueError:
    step = 1
step = max(1, min(4, step))

render_generate_native(initial_step=step)
