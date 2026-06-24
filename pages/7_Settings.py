from __future__ import annotations

import streamlit as st

from core.database import initialize_database


initialize_database()

st.title("Settings")
st.caption("Task 1 骨架頁面")

st.info("社團基本資料設定的儲存功能尚未實作，這一頁先定義欄位方向。")

with st.form("club_settings"):
    st.text_input("社團名稱")
    st.text_input("學年度")
    st.text_input("校區")
    st.text_input("社團性質")
    st.text_input("社長姓名")
    st.text_input("指導老師")
    st.text_input("文件命名規則", value="{民國年月日}_{社團名稱}_{文件類型}_{文件主題}_v{版本號}.{副檔名}")
    st.checkbox("啟用 AI 功能", value=False)
    st.form_submit_button("儲存設定", disabled=True)
