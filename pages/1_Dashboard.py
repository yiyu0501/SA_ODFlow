from __future__ import annotations

import streamlit as st

from core.database import initialize_database
from core.evaluation_service import get_evaluation_summary
from core.settings_service import get_club_settings


def _is_empty_workspace(summary: dict) -> bool:
    return (
        summary["total_completed_documents"] == 0
        and summary["draft_or_pending_documents"] == 0
        and not summary["recent_documents"]
    )


def _top_missing_categories(summary: dict) -> list[dict]:
    return sorted(
        [
            item
            for item in summary["category_summaries"]
            if item["missing_count"] > 0
        ],
        key=lambda item: (item["missing_count"], item["weight"]),
        reverse=True,
    )[:3]


initialize_database()
settings = get_club_settings()
summary = get_evaluation_summary()
is_empty_workspace = _is_empty_workspace(summary)

st.title("儀表板")
st.caption("社團評鑑資料完整度、缺漏提醒與下一步建議")

info_col1, info_col2, info_col3 = st.columns(3)
with info_col1:
    st.metric("社團名稱", settings["club_name"])
with info_col2:
    st.metric("學年度", settings["academic_year"])
with info_col3:
    st.metric("校區", settings["campus"])

with st.container(border=True):
    st.subheader("整體社團評鑑資料完整度")
    st.progress(summary["overall_completion_rate"])
    progress_col1, progress_col2, progress_col3 = st.columns(3)
    with progress_col1:
        st.metric("目前完成率", f"{summary['overall_completion_percentage']}%")
    with progress_col2:
        st.metric(
            "已完成 / 必要文件數",
            f"{summary['total_completed_documents']} / {summary['total_required_documents']}",
        )
    with progress_col3:
        st.metric("草稿或待審文件", summary["draft_or_pending_documents"])
    st.caption(
        "此進度代表七大評鑑項目的資料完整度，不是預測分數。"
    )

if is_empty_workspace:
    st.info(
        "目前還沒有任何文件資料。建議先到「社團設定」建立示範資料，"
        "或到「生成文件」建立第一份文件，再回來查看完整度。"
    )

st.subheader("七大評鑑項目進度")
for category_summary in summary["category_summaries"]:
    with st.container(border=True):
        title_col, stat_col = st.columns((2, 1))
        with title_col:
            st.markdown(f"**{category_summary['category_name']}**")
            st.write(
                f"配分權重：{category_summary['weight']}%  ｜  "
                f"已完成：{category_summary['completed_count']} / {category_summary['required_count']}  ｜  "
                f"進行中：{category_summary['in_progress_count']}"
            )
        with stat_col:
            st.metric("完成率", f"{category_summary['completion_percentage']}%")

        st.progress(category_summary["completion_rate"])
        if category_summary["missing_count"] > 0:
            st.caption(f"仍缺 {category_summary['missing_count']} 份必要文件")
        else:
            st.caption("目前此項必要文件已補齊")

st.subheader("最需要補齊的項目")
priority_categories = _top_missing_categories(summary)
if priority_categories:
    card_columns = st.columns(len(priority_categories))
    for column, category_summary in zip(card_columns, priority_categories):
        with column:
            with st.container(border=True):
                st.markdown(f"**{category_summary['category_name']}**")
                st.write(
                    f"目前完成 {category_summary['completed_count']} / "
                    f"{category_summary['required_count']}"
                )
                st.write(f"仍缺 {category_summary['missing_count']} 份必要文件")

                matching_recommendation = next(
                    (
                        item["message"]
                        for item in summary["recommendations"]
                        if item["category_name"] == category_summary["category_name"]
                    ),
                    "建議先補齊此項核心文件，再回頭檢查其他分類。",
                )
                st.caption(matching_recommendation)
else:
    st.success("目前七大評鑑項目的必要文件都已補齊。")

st.subheader("最近文件")
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
    st.info("目前尚無文件，尚無最近文件可顯示。")

st.subheader("缺漏文件提醒")
if summary["missing_requirements"]:
    st.dataframe(
        [
            {
                "評鑑項目": item["category_name"],
                "缺漏文件": item["requirement_name"],
            }
            for item in summary["missing_requirements"]
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.success("目前沒有缺漏文件。")

st.subheader("下一步建議")
recommendations = summary["recommendations"]
if recommendations:
    for recommendation in recommendations:
        with st.expander(recommendation["category_name"], expanded=False):
            st.write(recommendation["message"])
else:
    st.success("目前沒有額外建議，建議持續維護正式版與已歸檔文件。")
