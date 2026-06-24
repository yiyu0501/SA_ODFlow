from __future__ import annotations

import streamlit as st

from core.constants import EVALUATION_ITEMS
from core.database import DEFAULT_DB_PATH, initialize_database


st.set_page_config(
    page_title="ODFlow",
    page_icon="📁",
    layout="wide",
)

initialize_database()

st.title("ODFlow / SA_ODFlow")
st.caption("學生社團 ODF 文件流與評鑑整理系統")

left_col, right_col = st.columns((2, 1))

with left_col:
    st.subheader("Task 1 目前完成")
    st.markdown(
        """
        - Streamlit 多頁面骨架
        - SQLite schema 初始化
        - 七大社團評鑑項目常數與 seed
        - AI / 匯出模組骨架
        """
    )

    st.subheader("後續任務")
    st.markdown(
        """
        - Task 2：文件生成、儲存、文件庫與版本管理
        - Task 3：ODF / PDF 匯出
        - Task 4：評鑑完整度儀表板
        - Task 5：評鑑 ZIP 匯出
        """
    )

with right_col:
    st.subheader("系統狀態")
    st.metric("資料庫", "已初始化")
    st.code(str(DEFAULT_DB_PATH), language="text")

st.subheader("七大社團評鑑項目")
st.table(EVALUATION_ITEMS)

st.info("請從左側頁面導覽列進入各功能頁。Task 1 只提供骨架與說明，不包含正式業務功能。")
