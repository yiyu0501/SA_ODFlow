from __future__ import annotations

import streamlit as st

from core.exact_ui import render_exact_page, render_files

if __name__ == "__main__":
    st.set_page_config(page_title="檔案庫｜ODFlow", page_icon="🗂️", layout="wide", initial_sidebar_state="collapsed")
    render_exact_page(render_files())
