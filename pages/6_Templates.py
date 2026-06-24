from __future__ import annotations

import streamlit as st

from core.database import initialize_database


initialize_database()

st.title("Templates")
st.caption("Task 1 骨架頁面")

st.markdown(
    """
    預定範本分類：

    - 日常行政型
    - 專案活動型
    - 社團評鑑型
    """
)

st.info("範本下載與使用此範本生成文件，會在後續任務逐步補上。")
