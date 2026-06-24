from __future__ import annotations

import streamlit as st

from core.database import initialize_database
from core.evaluation_service import get_evaluation_summary
from core.settings_service import get_club_settings


initialize_database()
settings = get_club_settings()
summary = get_evaluation_summary()

st.title("Dashboard")
st.caption("社團評鑑資料完整度儀表板")

info_col1, info_col2, info_col3 = st.columns(3)
with info_col1:
    st.metric("社團名稱", settings["club_name"])
with info_col2:
    st.metric("學年度", settings["academic_year"])
with info_col3:
    st.metric("校區", settings["campus"])

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric("整體資料完整度", f"{summary['overall_completion_percentage']}%")
with metric_col2:
    st.metric(
        "已完成文件數 / 必要文件數",
        f"{summary['total_completed_documents']} / {summary['total_required_documents']}",
    )
with metric_col3:
    st.metric("待審或草稿文件數", summary["draft_or_pending_documents"])

st.subheader("七大評鑑項目完成率")
for category_summary in summary["category_summaries"]:
    with st.container(border=True):
        info_col, progress_col = st.columns((2, 3))
        with info_col:
            st.markdown(f"**{category_summary['category_name']}**")
            st.write(
                f"配分權重：{category_summary['weight']}%  |  "
                f"已完成：{category_summary['completed_count']} / {category_summary['required_count']}  |  "
                f"進行中：{category_summary['in_progress_count']}"
            )
        with progress_col:
            st.progress(category_summary["completion_rate"])
            st.caption(f"完成率：{category_summary['completion_percentage']}%")

st.subheader("最近生成文件")
recent_documents = summary["recent_documents"]
if recent_documents:
    st.dataframe(
        [
            {
                "文件名稱": item["title"],
                "文件類型": item["document_type"],
                "評鑑分類": item["evaluation_category"],
                "狀態": item["status"],
                "評鑑計入狀態": item["evaluation_progress_status"],
                "目前版本": item["current_version_label"],
                "修改時間": item["updated_at"],
            }
            for item in recent_documents
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("目前尚無文件。")

st.subheader("缺漏文件提醒")
missing_requirements = summary["missing_requirements"]
if missing_requirements:
    st.dataframe(
        [
            {
                "評鑑項目": item["category_name"],
                "缺漏文件": item["requirement_name"],
            }
            for item in missing_requirements
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.success("目前七大評鑑項目的必要文件都已補齊。")

st.subheader("下一步建議")
recommendations = summary["recommendations"]
if recommendations:
    for recommendation in recommendations:
        with st.expander(recommendation["category_name"], expanded=False):
            st.write(recommendation["message"])
else:
    st.success("目前沒有額外建議，建議持續維護已完成文件的正式版與歸檔狀態。")
