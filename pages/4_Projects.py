from __future__ import annotations

import streamlit as st

from core.exact_ui import render_exact_page, render_placeholder

st.set_page_config(page_title="專案｜ODFlow", page_icon="🧭", layout="wide", initial_sidebar_state="collapsed")
render_exact_page(render_placeholder("Projects", "專案", "整理社團專案、活動與階段進度。"))
