from __future__ import annotations

import streamlit as st

from core.database import initialize_database
from core.evaluation_service import get_evaluation_summary
from core.settings_service import get_club_settings


st.set_page_config(
    page_title="ODFlow",
    page_icon="📁",
    layout="wide",
)


def _render_home() -> None:
    initialize_database()
    settings = get_club_settings()
    summary = get_evaluation_summary()

    st.title("首頁")
    st.caption("ODFlow 是給學生社團使用的 ODF 文件流與社團評鑑整理工具。")

    hero_col, status_col = st.columns((2, 1))
    with hero_col:
        with st.container(border=True):
            st.subheader("用平時文件累積，直接接到評鑑輸出")
            st.write(
                "ODFlow 讓社團在日常就建立與保存 ODF 原始檔，"
                "需要評鑑時再一鍵輸出 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP，"
                "不必等到最後一週才重新補資料。"
            )
            st.markdown(
                "[線上展示網址](https://sa-odflow.streamlit.app/)  ｜  "
                "[README](https://github.com/yiyu0501/SA_ODFlow)"
            )

    with status_col:
        with st.container(border=True):
            st.subheader("目前展示資料")
            st.metric("社團名稱", settings["club_name"])
            st.metric("學年度 / 校區", f"{settings['academic_year']} / {settings['campus']}")
            st.metric("社團評鑑資料完整度", f"{summary['overall_completion_percentage']}%")

    st.subheader("四步完成主要流程")
    step_col1, step_col2, step_col3, step_col4 = st.columns(4)
    for column, title, description in [
        (
            step_col1,
            "1. 建立文件",
            "在「生成文件」建立會議紀錄、活動企劃書、活動成果報告、活動檢討會紀錄、年度計畫。",
        ),
        (
            step_col2,
            "2. 匯出 ODF / PDF",
            "在「檔案庫」管理版本、狀態，並輸出 ODF 原始檔與 PDF。",
        ),
        (
            step_col3,
            "3. 檢查評鑑完整度",
            "在「儀表板」查看七大評鑑項目的完成率、缺漏與下一步。",
        ),
        (
            step_col4,
            "4. 產生評鑑 ZIP",
            "在「社團評鑑」輸出 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP。",
        ),
    ]:
        with column:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.write(description)

    info_col, capability_col = st.columns((3, 2))
    with info_col:
        st.subheader("目前版本可做什麼")
        st.markdown(
            """
            - 生成會議紀錄、活動企劃書、活動成果報告、活動檢討會紀錄、年度計畫
            - 匯出 ODT / PDF
            - 下載 22 個空白 ODT / ODS 範本
            - 使用 5 個核心範本直接建立文件
            - 產生 PDF 評鑑上傳包
            - 產生 ODF 原始檔備份 ZIP
            """
        )

    with capability_col:
        st.subheader("目前提醒")
        st.warning(
            "Google Drive 自動上傳目前未串接。\n\n"
            "OpenAI API 目前未串接。\n\n"
            "即使不依賴 OpenAI，系統仍可透過表單式生成完成主要 ODF / PDF / ZIP 流程。"
        )

    st.subheader("第一次使用建議")
    guide_col1, guide_col2 = st.columns(2)
    with guide_col1:
        st.info(
            "建議先到「社團設定」填入學年度、校區與社團名稱，"
            "再建立示範資料，畫面會更容易看出完整流程。"
        )
    with guide_col2:
        st.info(
            "如果想快速展示，建議依序操作：社團設定 → 空白範本 / 生成文件 → "
            "檔案庫 → 儀表板 → 社團評鑑。"
        )


navigation = st.navigation(
    [
        st.Page(_render_home, title="首頁", icon="🏠", default=True),
        st.Page("pages/1_Dashboard.py", title="儀表板", icon="📊"),
        st.Page("pages/2_Generate.py", title="生成文件", icon="📝"),
        st.Page("pages/3_Files.py", title="檔案庫", icon="🗂️"),
        st.Page("pages/4_Projects.py", title="專案", icon="🧭"),
        st.Page("pages/5_Evaluation.py", title="社團評鑑", icon="📦"),
        st.Page("pages/6_Templates.py", title="空白範本", icon="📚"),
        st.Page("pages/7_Settings.py", title="社團設定", icon="⚙️"),
    ],
    position="sidebar",
)

navigation.run()
