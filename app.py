from __future__ import annotations

import streamlit as st

from core.database import initialize_database
from core.document_service import list_documents
from core.evaluation_service import get_evaluation_summary
from core.settings_service import get_club_settings
from core.template_service import get_template_definition
from core.ui_components import (
    badge_html,
    category_badge_html,
    empty_state,
    hero_panel,
    inject_base_styles,
    panel_body_html,
    page_intro,
    render_sidebar_brand,
    render_workflow_steps,
    status_card_html,
)


st.set_page_config(
    page_title="ODFlow",
    page_icon="📁",
    layout="wide",
)


COMMON_TEMPLATE_IDS = [
    "meeting_minutes_template_odt",
    "meeting_notice_odt",
    "activity_proposal_odt",
]


def _go_to(page_path: str) -> None:
    if hasattr(st, "switch_page"):
        st.switch_page(page_path)


def _render_home() -> None:
    initialize_database()
    inject_base_styles()

    settings = get_club_settings()
    summary = get_evaluation_summary()
    recent_documents = list_documents()[:5]
    common_templates = [get_template_definition(template_id) for template_id in COMMON_TEMPLATE_IDS]

    page_intro(
        "社團文件工作台",
        "從空白範本、正式文件產出、版本管理到社團評鑑整理，讓社團文件更有效率、更有條理。",
        eyebrow="ODFlow",
    )

    hero_col, info_col = st.columns((2.2, 1), gap="large")
    with hero_col:
        hero_panel(
            "臺灣學生社團 ODF 文件工作台",
            "從空白範本、正式文件產出、版本管理到社團評鑑整理，"
            "ODFlow 把平時的 ODF 原始檔保存、PDF 匯出與社團評鑑整理串成同一條流程。",
            eyebrow="社團 ODF 文件流",
        )
    with info_col:
        st.markdown(
            status_card_html(
                "目前工作台狀態",
                summary["overall_completion_percentage"],
                f"{settings['club_name']} ｜ {settings['academic_year']} ｜ {settings['campus']}",
                badges=[
                    badge_html(
                        f"缺漏 {len(summary['missing_requirements'])} 份",
                        tone="warning" if summary["missing_requirements"] else "success",
                    ),
                    badge_html(
                        f"草稿 / 待審 {summary['draft_or_pending_documents']} 份",
                        tone="neutral",
                    ),
                ],
                note=(
                    "目前可開始整理 PDF 評鑑上傳包。"
                    if not summary["missing_requirements"]
                    else "先補齊必要文件後，再進行評鑑打包會更順。"
                ),
            ),
            unsafe_allow_html=True,
        )
        st.caption(
            "目前仍未串接 Google Drive 自動上傳與 OpenAI API。"
            " 但系統已可透過表單式流程完成 ODF / PDF / ZIP。"
        )

    st.markdown("### 三個主要行動")
    action_columns = st.columns(3, gap="large")
    actions = [
        (
            "下載空白範本",
            "先從空白範本中心挑選 ODT / ODS，快速開始日常行政與活動文件。",
            "前往空白範本",
            "pages/6_Templates.py",
            [category_badge_html("日常行政型"), badge_html("ODT / ODS", tone="neutral")],
        ),
        (
            "建立正式文件",
            "依文件類型填寫內容、儲存草稿，再進入檔案庫管理版本與輸出。",
            "開始建立文件",
            "pages/2_Generate.py",
            [badge_html("七種核心文件", tone="primary"), badge_html("草稿 / 版本", tone="neutral")],
        ),
        (
            "整理社團評鑑",
            "檢查哪些文件已可進入 PDF 評鑑上傳包，並匯出 ODF 原始檔備份 ZIP。",
            "前往社團評鑑",
            "pages/5_Evaluation.py",
            [badge_html("PDF 評鑑上傳包", tone="primary"), badge_html("ODF 備份 ZIP", tone="neutral")],
        ),
    ]
    for column, (title, description, button_label, page_path, badges) in zip(action_columns, actions):
        with column:
            with st.container(border=True):
                st.markdown(
                    panel_body_html(title, description, badges=badges, eyebrow="主要行動"),
                    unsafe_allow_html=True,
                )
                if st.button(
                    button_label,
                    key=f"home_action_{page_path}",
                    use_container_width=True,
                    type="primary",
                ):
                    _go_to(page_path)

    st.markdown("### 文件工作流程")
    render_workflow_steps(
        [
            {"title": "選範本", "description": "從空白範本中心直接下載 ODT / ODS，或使用核心範本帶入生成流程。"},
            {"title": "填資料", "description": "依文件類型填寫基本資料、內容欄位與表格清單，先完成草稿。"},
            {"title": "匯出 ODT / PDF", "description": "儲存版本後，可在生成流程或檔案庫輸出正式文件。"},
            {"title": "整理評鑑", "description": "依七大分類檢查缺件，最後匯出 PDF 評鑑上傳包與 ODF 備份 ZIP。"},
        ]
    )

    st.markdown("### 最近文件")
    if recent_documents:
        st.dataframe(
            [
                {
                    "文件名稱": item["title"],
                    "類型": item["document_type"],
                    "狀態": item["status"],
                    "最後更新": item["updated_at"],
                }
                for item in recent_documents
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        empty_state(
            "目前尚無文件",
            "你可以先到「社團設定」建立示範資料，或到「生成文件」建立第一份文件。",
            hint="建立第一份文件後，這裡會顯示最近更新的內容與後續工作動態。",
        )

    lower_left, lower_right = st.columns((1.35, 1), gap="large")
    with lower_left:
        st.markdown("### 常用範本")
        template_columns = st.columns(3, gap="medium")
        for column, definition in zip(template_columns, common_templates):
            with column:
                with st.container(border=True):
                    st.markdown(
                        panel_body_html(
                            definition["name"],
                            definition["usage_description"],
                            badges=[
                                category_badge_html(definition["library_category"]),
                                badge_html(definition["suggested_format"], tone="neutral"),
                            ],
                            eyebrow="常用空白範本",
                        ),
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "查看範本",
                        key=f"home_template_{definition['id']}",
                        use_container_width=True,
                        type="secondary",
                    ):
                        _go_to("pages/6_Templates.py")

    with lower_right:
        st.markdown("### 評鑑提醒")
        reminder_text = (
            f"目前仍有 {len(summary['missing_requirements'])} 份必要文件缺漏，建議先到「社團評鑑」查看不能打包的原因。"
            if summary["missing_requirements"]
            else "目前七大評鑑必要文件都已補齊，可到「社團評鑑」直接檢查打包結果。"
        )
        with st.container(border=True):
            st.markdown(
                panel_body_html(
                    "查看社團評鑑進度",
                    reminder_text,
                    badges=[
                        badge_html(
                            f"完整度 {summary['overall_completion_percentage']}%",
                            tone="primary",
                        ),
                        badge_html(
                            f"草稿 / 待審 {summary['draft_or_pending_documents']} 份",
                            tone="warning" if summary["draft_or_pending_documents"] else "success",
                        ),
                    ],
                    eyebrow="評鑑整理",
                ),
                unsafe_allow_html=True,
            )
            if st.button(
                "前往社團評鑑",
                key="home_eval_button",
                use_container_width=True,
                type="primary",
            ):
                _go_to("pages/5_Evaluation.py")

        with st.container(border=True):
            st.markdown(
                panel_body_html(
                    "第一次使用建議",
                    "先填社團設定，再建立示範資料，之後依序體驗空白範本、生成文件、檔案庫與社團評鑑。",
                    eyebrow="開始前",
                ),
                unsafe_allow_html=True,
            )


initialize_database()
inject_base_styles()
sidebar_settings = get_club_settings()
render_sidebar_brand(
    "ODFlow",
    "社團 ODF 文件工作台",
    sidebar_settings["club_name"],
    sidebar_settings["academic_year"],
    sidebar_settings["campus"],
)

navigation = st.navigation(
    {
        "工作台": [
            st.Page(_render_home, title="首頁", icon="🏠", default=True),
            st.Page("pages/1_Dashboard.py", title="儀表板", icon="📊"),
        ],
        "文件製作": [
            st.Page("pages/6_Templates.py", title="空白範本", icon="📚"),
            st.Page("pages/2_Generate.py", title="生成文件", icon="📝"),
            st.Page("pages/3_Files.py", title="檔案庫", icon="🗂️"),
        ],
        "評鑑整理": [
            st.Page("pages/5_Evaluation.py", title="社團評鑑", icon="📦"),
        ],
        "社團資料": [
            st.Page("pages/7_Settings.py", title="社團設定", icon="⚙️"),
        ],
        "未來擴充": [
            st.Page("pages/4_Projects.py", title="專案", icon="🧭"),
        ],
    },
    position="sidebar",
    expanded=True,
)

navigation.run()
