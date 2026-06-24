from __future__ import annotations

import streamlit as st

from core.database import initialize_database


initialize_database()

st.title("Files")
st.caption("Task 1 骨架頁面")

st.info("文件庫列表、狀態、版本與下載操作會在 Task 2 和 Task 3 實作。")
st.dataframe(
    [
        {
            "文件名稱": "尚未建立資料",
            "類型": "-",
            "對應評鑑項目": "-",
            "狀態": "-",
            "版本": "-",
        }
    ],
    hide_index=True,
    use_container_width=True,
)
