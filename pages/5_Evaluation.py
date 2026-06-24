from __future__ import annotations

import streamlit as st

from core.database import initialize_database
from core.evaluation_service import get_evaluation_summary


initialize_database()
summary = get_evaluation_summary()

st.title("Evaluation")
st.caption("七大評鑑項目檢核表")

st.subheader("七大評鑑項目檢核")
st.dataframe(
    [
        {
            "評鑑項目": item["category_name"],
            "配分權重": f"{item['weight']}%",
            "完成率": f"{item['completion_percentage']}%",
            "已完成 / 必要": f"{item['completed_count']} / {item['required_count']}",
            "進行中": item["in_progress_count"],
            "缺漏": item["missing_count"],
        }
        for item in summary["category_summaries"]
    ],
    hide_index=True,
    use_container_width=True,
)

for category_summary in summary["category_summaries"]:
    with st.expander(category_summary["category_name"], expanded=False):
        st.write(
            f"完成率：{category_summary['completion_percentage']}%  |  "
            f"已完成：{category_summary['completed_count']} / {category_summary['required_count']}  |  "
            f"進行中：{category_summary['in_progress_count']}"
        )

        st.markdown("**必要文件檢核**")
        st.dataframe(
            [
                {
                    "必要文件": requirement["requirement_name"],
                    "狀態": requirement["status"],
                    "對應文件": "、".join(
                        document["title"] for document in requirement["matched_documents"]
                    )
                    or "-",
                }
                for requirement in category_summary["required_documents"]
            ],
            hide_index=True,
            use_container_width=True,
        )

        st.markdown("**對應文件列表**")
        if category_summary["documents"]:
            st.dataframe(
                [
                    {
                        "文件名稱": document["title"],
                        "文件類型": document["document_type"],
                        "狀態": document["status"],
                        "目前版本": document["current_version_label"],
                        "修改時間": document["updated_at"],
                    }
                    for document in category_summary["documents"]
                ],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("目前此評鑑項目尚無文件。")

st.subheader("缺漏文件清單")
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
