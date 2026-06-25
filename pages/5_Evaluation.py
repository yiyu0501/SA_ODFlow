from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.constants import EVALUATION_CATEGORIES
from core.database import initialize_database
from core.export_service import (
    PDF_EXPORTABLE_STATUSES,
    build_odf_backup_package,
    build_pdf_evaluation_package,
    collect_exportable_documents,
)
from core.evaluation_service import get_evaluation_summary
from core.settings_service import get_evaluation_export_defaults


def _resolve_download_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None

    path = Path(path_value)
    if path.exists() and path.is_file():
        return path
    return None


def _store_export_result(session_key: str, result: dict) -> None:
    st.session_state[session_key] = {
        **result,
        "zip_path": str(result["zip_path"]),
        "index_pdf_path": str(result["index_pdf_path"]),
        "index_csv_path": str(result["index_csv_path"]),
        "failed_report_path": str(result["failed_report_path"]),
    }


def _initialize_export_form_state() -> None:
    defaults = get_evaluation_export_defaults()
    st.session_state.setdefault("evaluation_form_academic_year", defaults["academic_year"])
    st.session_state.setdefault("evaluation_form_campus", defaults["campus"])
    st.session_state.setdefault("evaluation_form_club_name", defaults["club_name"])


def _classify_pdf_package_records(records: list[dict]) -> tuple[list[dict], list[dict]]:
    exportable = []
    blocked = []

    for record in records:
        if not record.get("evaluation_category"):
            blocked.append(
                {
                    "title": record["title"],
                    "document_type": record["document_type"],
                    "evaluation_category": "-",
                    "status": record["status"],
                    "reason": "尚未設定評鑑分類",
                }
            )
            continue

        if record["evaluation_category"] not in EVALUATION_CATEGORIES:
            blocked.append(
                {
                    "title": record["title"],
                    "document_type": record["document_type"],
                    "evaluation_category": record["evaluation_category"],
                    "status": record["status"],
                    "reason": "評鑑分類不在七大項目中",
                }
            )
            continue

        if record["status"] not in PDF_EXPORTABLE_STATUSES:
            blocked.append(
                {
                    "title": record["title"],
                    "document_type": record["document_type"],
                    "evaluation_category": record["evaluation_category"],
                    "status": record["status"],
                    "reason": "狀態不是正式版或已歸檔",
                }
            )
            continue

        if record.get("version_error"):
            blocked.append(
                {
                    "title": record["title"],
                    "document_type": record["document_type"],
                    "evaluation_category": record["evaluation_category"],
                    "status": record["status"],
                    "reason": record["version_error"],
                }
            )
            continue

        if record.get("version") is None:
            blocked.append(
                {
                    "title": record["title"],
                    "document_type": record["document_type"],
                    "evaluation_category": record["evaluation_category"],
                    "status": record["status"],
                    "reason": "找不到目前版本",
                }
            )
            continue

        if record.get("content_json") is None:
            blocked.append(
                {
                    "title": record["title"],
                    "document_type": record["document_type"],
                    "evaluation_category": record["evaluation_category"],
                    "status": record["status"],
                    "reason": "找不到 content_json",
                }
            )
            continue

        exportable.append(
            {
                "title": record["title"],
                "document_type": record["document_type"],
                "evaluation_category": record["evaluation_category"],
                "status": record["status"],
                "current_version_label": record["current_version_label"],
                "pdf_status": (
                    "已有 PDF"
                    if _resolve_download_path(record.get("pdf_path")) is not None
                    else "匯出時會自動補產生 PDF"
                ),
            }
        )

    return exportable, blocked


def _render_folder_preview() -> None:
    st.subheader("七大評鑑資料夾預覽")
    preview_columns = st.columns(2)
    for index, category in enumerate(EVALUATION_CATEGORIES):
        with preview_columns[index % 2]:
            with st.container(border=True):
                st.markdown(f"**{category}**")
                st.caption("PDF 評鑑上傳包與 ODF 原始檔備份 ZIP 都會依此分類整理。")


def _render_export_result(title: str, session_key: str, download_label: str, mime: str) -> None:
    result = st.session_state.get(session_key)
    if not result:
        return

    zip_path = _resolve_download_path(result.get("zip_path"))
    st.markdown(f"**{title}**")

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("成功輸出", str(result["exported_count"]))
    metric_col2.metric("未輸出", str(result["failed_count"]))
    metric_col3.metric("ZIP 檔名", result["zip_name"])

    categories = result.get("exported_categories") or []
    st.write(f"輸出分類：{'、'.join(categories) if categories else '本次沒有成功輸出的分類'}")

    st.download_button(
        download_label,
        data=zip_path.read_bytes() if zip_path is not None else b"",
        file_name=zip_path.name if zip_path is not None else result["zip_name"],
        mime=mime,
        disabled=zip_path is None,
        key=f"download_{session_key}",
    )

    with st.expander("查看本次輸出摘要", expanded=False):
        st.dataframe(
            [
                {
                    "文件名稱": row["title"],
                    "文件類型": row["document_type"],
                    "評鑑分類": row["evaluation_category"],
                    "狀態": row["status"],
                    "版本": row["current_version_label"],
                    "輸出檔名": row["output_filename"],
                    "是否成功輸出": "是" if row["exported"] else "否",
                    "備註": row["note"],
                }
                for row in result["documents"]
            ],
            hide_index=True,
            use_container_width=True,
        )

    if result["failed_documents"]:
        with st.expander("查看未輸出文件", expanded=False):
            st.dataframe(
                [
                    {
                        "文件名稱": row["title"],
                        "文件類型": row["document_type"],
                        "評鑑分類": row["evaluation_category"],
                        "狀態": row["status"],
                        "未輸出原因": row["reason"],
                    }
                    for row in result["failed_documents"]
                ],
                hide_index=True,
                use_container_width=True,
            )


initialize_database()
_initialize_export_form_state()
summary = get_evaluation_summary()
records = collect_exportable_documents()
pdf_exportable_documents, pdf_blocked_documents = _classify_pdf_package_records(records)

st.title("社團評鑑")
st.caption("七大評鑑項目檢核、PDF 評鑑上傳包預覽與 ZIP 下載")

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric("七大評鑑項目", len(EVALUATION_CATEGORIES))
with metric_col2:
    st.metric("可進入 PDF 評鑑上傳包", len(pdf_exportable_documents))
with metric_col3:
    st.metric("目前不會被打包", len(pdf_blocked_documents))

_render_folder_preview()

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
            f"完成率：{category_summary['completion_percentage']}%  ｜  "
            f"已完成：{category_summary['completed_count']} / {category_summary['required_count']}  ｜  "
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

st.subheader("哪些文件會被打包進 PDF 評鑑上傳包")
if pdf_exportable_documents:
    st.dataframe(
        [
            {
                "文件名稱": row["title"],
                "文件類型": row["document_type"],
                "評鑑分類": row["evaluation_category"],
                "狀態": row["status"],
                "目前版本": row["current_version_label"],
                "PDF 狀態": row["pdf_status"],
            }
            for row in pdf_exportable_documents
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info(
        "目前沒有符合條件的文件可放入 PDF 評鑑上傳包。"
        "只有狀態為「正式版」或「已歸檔」且具備目前版本內容的文件才會被打包。"
    )

st.subheader("哪些文件目前不會被打包")
if pdf_blocked_documents:
    st.dataframe(
        [
            {
                "文件名稱": row["title"],
                "文件類型": row["document_type"],
                "評鑑分類": row["evaluation_category"],
                "狀態": row["status"],
                "原因": row["reason"],
            }
            for row in pdf_blocked_documents
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.success("目前沒有被排除的文件。")

st.subheader("匯出 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP")
st.caption("預設值會讀取「社團設定」的基本資料，但你仍可在此頁面暫時調整本次匯出名稱。")

package_col1, package_col2 = st.columns(2)
with package_col1:
    with st.container(border=True):
        st.markdown("**PDF 評鑑上傳包 ZIP**")
        st.write("提供學校評鑑上傳使用，只會收正式版或已歸檔文件。")
with package_col2:
    with st.container(border=True):
        st.markdown("**ODF 原始檔備份 ZIP**")
        st.write("提供社團保存與後續編輯使用，重點是保留 ODF 原始檔。")

field_col1, field_col2, field_col3 = st.columns(3)
with field_col1:
    academic_year = st.text_input("學年度", key="evaluation_form_academic_year")
with field_col2:
    current_campus = st.session_state.get("evaluation_form_campus", "天母校區")
    campus_options = list(dict.fromkeys([current_campus, "天母校區", "博愛校區"]))
    campus = st.selectbox("校區", options=campus_options, key="evaluation_form_campus")
with field_col3:
    club_name = st.text_input("社團名稱", key="evaluation_form_club_name")

action_col1, action_col2 = st.columns(2)
with action_col1:
    if st.button("產生 PDF 評鑑上傳包", use_container_width=True):
        try:
            result = build_pdf_evaluation_package(
                academic_year=academic_year,
                campus=campus,
                club_name=club_name,
            )
        except (RuntimeError, ValueError) as exc:
            st.error(str(exc))
        else:
            _store_export_result("evaluation_pdf_export", result)
            st.success(f"已建立 PDF 評鑑上傳包：{result['zip_name']}")

with action_col2:
    if st.button("產生 ODF 原始檔備份包", use_container_width=True):
        try:
            result = build_odf_backup_package(
                academic_year=academic_year,
                club_name=club_name,
            )
        except (RuntimeError, ValueError) as exc:
            st.error(str(exc))
        else:
            _store_export_result("evaluation_odf_export", result)
            st.success(f"已建立 ODF 原始檔備份包：{result['zip_name']}")

_render_export_result(
    "PDF 評鑑上傳包",
    "evaluation_pdf_export",
    "下載 PDF 評鑑上傳包 ZIP",
    "application/zip",
)
_render_export_result(
    "ODF 原始檔備份包",
    "evaluation_odf_export",
    "下載 ODF 原始檔備份 ZIP",
    "application/zip",
)
