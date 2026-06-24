from __future__ import annotations

import streamlit as st

from core.constants import EVALUATION_ITEMS
from core.database import initialize_database


initialize_database()

st.title("Evaluation")
st.caption("Task 1 骨架頁面")

st.info("七大項目檢核、缺漏清單與 ZIP 匯出會在 Task 4 和 Task 5 實作。")
st.dataframe(EVALUATION_ITEMS, hide_index=True, use_container_width=True)
