from __future__ import annotations

import streamlit as st

from core.database import initialize_database


initialize_database()

st.title("專案")
st.caption("未來擴充頁：活動生命週期與相關文件整理")

st.info(
    "「專案」目前不是 ODFlow 的核心功能。"
    "這一頁保留給後續版本擴充活動生命週期管理，"
    "但本版不提供完整專案卡、時程追蹤或多人協作。"
)

overview_col, current_col = st.columns(2)
with overview_col:
    with st.container(border=True):
        st.subheader("未來可擴充方向")
        st.markdown(
            """
            - 單一活動的文件完整度追蹤
            - 活動相關文件集中檢視
            - 活動前、中、後文件的生命週期整理
            - 活動歸檔狀態與資料保存提醒
            """
        )

with current_col:
    with st.container(border=True):
        st.subheader("目前建議使用方式")
        st.markdown(
            """
            - 到「生成文件」建立會議紀錄、活動企劃書、成果報告等文件
            - 到「檔案庫」管理版本、狀態與 ODF / PDF 匯出
            - 到「社團評鑑」檢查哪些文件能進入 PDF 評鑑上傳包
            """
        )

st.warning(
    "如果你現在是第一次使用 ODFlow，建議先忽略這一頁，"
    "優先使用「社團設定」「生成文件」「檔案庫」「儀表板」「社團評鑑」。"
)
