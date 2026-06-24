from __future__ import annotations

import streamlit as st

from core.database import DEFAULT_DB_PATH, initialize_database
from core.evaluation_service import get_evaluation_summary
from core.settings_service import get_club_settings


st.set_page_config(
    page_title="ODFlow",
    page_icon="📁",
    layout="wide",
)

initialize_database()
settings = get_club_settings()
summary = get_evaluation_summary()

st.title("ODFlow")
st.caption("學生社團 ODF 文件流與評鑑整理系統")

hero_col, status_col = st.columns((2, 1))
with hero_col:
    st.subheader("比賽展示定位")
    st.markdown(
        """
        - ODF 文件生成工具
        - 學生社團評鑑資料整理工具
        - ODF 原始檔保存與 PDF 上傳包輸出流程
        """
    )
    st.write(
        "ODFlow 讓社團在平時就把會議與活動資料整理成可保存的 ODF 原始檔，"
        "評鑑前再一鍵輸出 PDF 上傳包，降低臨時補件與分類整理成本。"
    )

with status_col:
    st.subheader("目前展示資料")
    st.metric("社團名稱", settings["club_name"])
    st.metric("學年度 / 校區", f"{settings['academic_year']} / {settings['campus']}")
    st.metric("資料完整度", f"{summary['overall_completion_percentage']}%")

flow_col1, flow_col2 = st.columns(2)
with flow_col1:
    st.subheader("完整 demo 流程")
    st.markdown(
        """
        1. 到 Settings 設定社團基本資料
        2. 建立示範資料
        3. 到 Templates 產生與下載 ODT / ODS 範本
        4. 到 Generate 產生會議紀錄
        5. 到 Files 管理版本並匯出 ODT / PDF
        6. 到 Dashboard 查看評鑑完整度
        7. 到 Evaluation 輸出 PDF 評鑑 ZIP 與 ODF 備份 ZIP
        """
    )

with flow_col2:
    st.subheader("目前已完成")
    st.markdown(
        """
        - 會議紀錄生成與編輯
        - 文件版本管理與狀態切換
        - ODT / PDF 匯出與下載
        - ODF Templates 範本庫最小展示版
        - 評鑑完整度 Dashboard
        - PDF 評鑑 ZIP 與 ODF 原始檔備份 ZIP
        - 社團基本資料設定與示範資料建立
        """
    )

st.subheader("導覽建議")
st.info(
    "第一次展示建議從 Settings 開始，先設定社團基本資料並建立示範資料，"
    "之後依序前往 Generate、Files、Dashboard、Evaluation。"
)

st.subheader("系統狀態")
st.code(str(DEFAULT_DB_PATH), language="text")
