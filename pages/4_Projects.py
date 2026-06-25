from __future__ import annotations

import streamlit as st

from core.database import initialize_database


initialize_database()

st.title("Projects")
st.caption("未來擴充：活動 / 專案文件整理頁")

st.info(
    "Projects 目前尚未實作完整活動 / 專案管理。"
    "這一頁會在後續版本補上活動卡、文件完整度、相關文件列表與歸檔狀態。"
)
