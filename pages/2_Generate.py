from __future__ import annotations

import streamlit as st

from core.database import initialize_database


initialize_database()

st.title("Generate")
st.caption("Task 1 骨架頁面")

st.markdown(
    """
    這一頁預留三種模式：

    - 自然語言生成
    - 選範本生成
    - 上傳資料生成
    """
)

st.warning("OpenAI API 與文件生成流程尚未實作。音檔轉逐字稿功能目前僅保留後續 Beta 入口。")
