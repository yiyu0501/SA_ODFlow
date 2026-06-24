from __future__ import annotations

import streamlit as st

from core.constants import EVALUATION_ITEMS
from core.database import initialize_database


initialize_database()

st.title("Dashboard")
st.caption("Task 1 骨架頁面")

st.info("這一頁目前只提供資訊骨架。評鑑完整度、最近文件、缺漏提醒會在 Task 4 之後逐步實作。")
st.table(EVALUATION_ITEMS)
