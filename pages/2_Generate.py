from __future__ import annotations

import streamlit as st

from core.generate_native import render_generate_native_content
from core.native_shell import inject_native_shell_styles, render_native_sidebar

st.set_page_config(page_title="生成文件｜ODFlow", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

st.session_state["active_page"] = "Generate"
inject_native_shell_styles()
render_native_sidebar("Generate")
render_generate_native_content()
