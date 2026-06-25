from __future__ import annotations

import streamlit as st

from core.database import initialize_database
from core.demo_data import create_demo_data
from core.settings_service import get_club_settings, save_club_settings


def _sync_evaluation_export_state(settings: dict) -> None:
    st.session_state["evaluation_form_academic_year"] = settings["academic_year"]
    st.session_state["evaluation_form_campus"] = settings["campus"]
    st.session_state["evaluation_form_club_name"] = settings["club_name"]


initialize_database()
settings = get_club_settings()

st.title("社團設定")
st.caption("社團基本資料、評鑑匯出預設值與展示用示範資料")

settings_message = st.session_state.pop("settings_message", "")
if settings_message:
    st.success(settings_message)

st.subheader("社團基本資料")
with st.form("club_settings"):
    academic_year = st.text_input("學年度", value=settings["academic_year"])
    campus_options = [settings["campus"], "天母校區", "博愛校區"]
    campus = st.selectbox(
        "校區",
        options=list(dict.fromkeys(campus_options)),
        index=0,
    )
    club_name = st.text_input("社團名稱", value=settings["club_name"])
    club_type = st.text_input("社團類型（可選填）", value=settings["club_type"])
    president_name = st.text_input("負責人姓名（可選填）", value=settings["president_name"])
    advisor_name = st.text_input("指導老師（可選填）", value=settings["advisor_name"])
    save_submitted = st.form_submit_button("儲存社團基本資料")

if save_submitted:
    saved_settings = save_club_settings(
        academic_year=academic_year,
        campus=campus,
        club_name=club_name,
        club_type=club_type,
        president_name=president_name,
        advisor_name=advisor_name,
    )
    _sync_evaluation_export_state(saved_settings)
    st.session_state["settings_message"] = "社團基本資料已儲存。"
    st.rerun()

st.subheader("示範資料")
st.write(
    "建立 5 份展示用文件，涵蓋會議紀錄、年度計畫與活動成果報告。"
    "已存在的 `示範資料_` 文件不會重複建立。"
)

if st.button("建立示範資料", use_container_width=True):
    result = create_demo_data()
    if result["created_count"] == 0:
        st.info("示範資料已存在，本次未重複建立。")
    else:
        st.success(
            f"已建立 {result['created_count']} 份示範資料，"
            f"略過 {result['skipped_count']} 份既有資料。"
        )
    if result["created_titles"]:
        st.write("本次建立：")
        st.write("、".join(result["created_titles"]))
    if result["skipped_titles"]:
        with st.expander("查看已存在的示範資料", expanded=False):
            st.write("、".join(result["skipped_titles"]))

st.subheader("目前設定摘要")
st.dataframe(
    [
        {
            "學年度": settings["academic_year"],
            "校區": settings["campus"],
            "社團名稱": settings["club_name"],
            "社團類型": settings["club_type"] or "-",
            "負責人姓名": settings["president_name"] or "-",
            "指導老師": settings["advisor_name"] or "-",
        }
    ],
    hide_index=True,
    use_container_width=True,
)
