from __future__ import annotations

import streamlit as st

from core.database import initialize_database


initialize_database()

st.title("Projects")
st.caption("Task 1 骨架頁面")

st.info("活動卡、文件完整度與相關文件列表會在後續任務實作。")
