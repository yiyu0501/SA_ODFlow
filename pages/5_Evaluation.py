from __future__ import annotations

import streamlit as st

from core.exact_ui import render_exact_page, render_placeholder

st.set_page_config(page_title="社團評鑑｜ODFlow", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")
render_exact_page(render_placeholder("Evaluation", "社團評鑑", "整理缺件、待補與待審核資料。"))
