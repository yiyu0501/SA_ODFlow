from __future__ import annotations

import streamlit as st

from core.database import initialize_database
from core.evaluation_service import get_evaluation_summary
from core.settings_service import get_club_settings
from core.template_service import get_template_definition
from core.ui_components import (
    badge_html,
    card_html,
    category_badge_html,
    empty_state,
    inject_base_styles,
    page_intro,
)


COMMON_TEMPLATE_IDS = [
    "meeting_minutes_template_odt",
    "meeting_notice_odt",
    "activity_proposal_odt",
]


def _top_missing_categories(summary: dict) -> list[dict]:
    return sorted(
        [item for item in summary["category_summaries"] if item["missing_count"] > 0],
        key=lambda item: (item["missing_count"], item["weight"]),
        reverse=True,
    )[:3]


initialize_database()
inject_base_styles()

settings = get_club_settings()
summary = get_evaluation_summary()
priority_categories = _top_missing_categories(summary)
recent_documents = summary["recent_documents"]
common_templates = [get_template_definition(template_id) for template_id in COMMON_TEMPLATE_IDS]

page_intro(
    "儀表板",
    "查看社團日常文件狀態、近期工作與評鑑提醒。",
    eyebrow="Dashboard",
)

hero_col, eval_col = st.columns((2, 1), gap="large")
with hero_col:
    st.markdown(
        card_html(
            f"{settings['club_name']} 的日常營運總覽",
            "這裡聚焦最近文件、待補工作與常用範本。"
            " 七大評鑑完整度與 ZIP 打包細節，請到「社團評鑑」頁查看。",
            badges=[
                badge_html(settings["academic_year"], tone="neutral"),
                badge_html(settings["campus"], tone="neutral"),
            ],
        ),
        unsafe_allow_html=True,
    )
with eval_col:
    st.markdown(
        card_html(
            "社團評鑑資料完整度",
            f"目前完成 {summary['total_completed_documents']} / {summary['total_required_documents']} 份必要文件。",
            badges=[
                badge_html(f"{summary['overall_completion_percentage']}%", tone="primary"),
                badge_html(
                    f"草稿 / 待審 {summary['draft_or_pending_documents']} 份",
                    tone="warning" if summary["draft_or_pending_documents"] else "success",
                ),
            ],
        ),
        unsafe_allow_html=True,
    )
    st.progress(summary["overall_completion_rate"])

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4, gap="medium")
metrics = [
    ("最近文件", str(len(recent_documents)), "近五筆文件動態"),
    ("待補文件", str(len(summary["missing_requirements"])), "尚未完成的必要文件"),
    ("草稿 / 待審", str(summary["draft_or_pending_documents"]), "尚未計入完整度"),
    ("建議數", str(len(summary["recommendations"])), "目前系統建議"),
]
for column, (title, value, desc) in zip(
    [metric_col1, metric_col2, metric_col3, metric_col4], metrics
):
    with column:
        st.markdown(
            card_html(title, desc, badges=[badge_html(value, tone="primary")]),
            unsafe_allow_html=True,
        )

left_col, right_col = st.columns((1.45, 1), gap="large")
with left_col:
    st.markdown("### 最近文件")
    if recent_documents:
        st.dataframe(
            [
                {
                    "文件名稱": item["title"],
                    "文件類型": item["document_type"],
                    "狀態": item["status"],
                    "評鑑分類": item["evaluation_category"],
                    "修改時間": item["updated_at"],
                }
                for item in recent_documents
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        empty_state(
            "目前還沒有最近文件",
            "建議先到「社團設定」建立示範資料，或到「生成文件」建立第一份文件。",
            hint="建立文件後，這裡會顯示最近更新的內容。",
        )

    st.markdown("### 常用範本")
    template_cols = st.columns(3, gap="medium")
    for column, definition in zip(template_cols, common_templates):
        with column:
            st.markdown(
                card_html(
                    definition["name"],
                    definition["usage_description"],
                    badges=[
                        category_badge_html(definition["library_category"]),
                        badge_html(definition["suggested_format"], tone="neutral"),
                    ],
                ),
                unsafe_allow_html=True,
            )

with right_col:
    st.markdown("### 待補文件")
    if priority_categories:
        for category in priority_categories:
            matching_recommendation = next(
                (
                    item["message"]
                    for item in summary["recommendations"]
                    if item["category_name"] == category["category_name"]
                ),
                "建議優先補齊此項核心文件。",
            )
            st.markdown(
                card_html(
                    category["category_name"],
                    matching_recommendation,
                    badges=[
                        badge_html(
                            f"{category['completed_count']} / {category['required_count']}",
                            tone="primary",
                        ),
                        badge_html(f"缺 {category['missing_count']} 份", tone="warning"),
                    ],
                ),
                unsafe_allow_html=True,
            )
    else:
        empty_state(
            "目前沒有待補的必要文件",
            "七大評鑑項目的必要文件已補齊，可直接到「社團評鑑」檢查打包結果。",
            hint="建議持續把新文件存成正式版或已歸檔。",
        )

    st.markdown("### 評鑑提醒")
    reminder_text = (
        "目前有文件因草稿或待審狀態，不會進入 PDF 評鑑上傳包。"
        if summary["draft_or_pending_documents"] > 0
        else "目前沒有草稿 / 待審文件阻擋評鑑打包。"
    )
    st.markdown(
        card_html(
            "PDF 評鑑上傳包前檢查",
            reminder_text,
            badges=[
                badge_html(
                    f"缺漏 {len(summary['missing_requirements'])} 份",
                    tone="warning" if summary["missing_requirements"] else "success",
                )
            ],
        ),
        unsafe_allow_html=True,
    )
