from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.database import initialize_database
from core.template_service import (
    TEMPLATE_LIBRARY_CATEGORIES,
    generate_template_file,
    list_template_definitions,
)


def _resolve_download_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None

    path = Path(path_value)
    if path.exists() and path.is_file():
        return path
    return None


initialize_database()
st.session_state.setdefault("template_downloads", {})
template_count = len(list_template_definitions())

st.title("Templates")
st.caption("ODF 範本庫最小可展示版")

st.write(
    "這一頁展示學生社團常用的 ODF 範本，分成日常行政型、專案活動型、社團評鑑型。"
    f"目前支援 {template_count} 個最小可展示版 ODT / ODS 範本，"
    "可直接產生與下載，後續可再擴充更多樣式與內容。"
)

category_tabs = st.tabs(TEMPLATE_LIBRARY_CATEGORIES)

for category_name, tab in zip(TEMPLATE_LIBRARY_CATEGORIES, category_tabs):
    with tab:
        templates = list_template_definitions(category_name)
        st.subheader(category_name)
        for definition in templates:
            with st.container(border=True):
                info_col, action_col = st.columns((3, 1))
                with info_col:
                    st.markdown(f"**{definition['name']}**")
                    st.write(
                        f"範本類型：{definition['template_type']}  |  "
                        f"建議格式：{definition['suggested_format']}  |  "
                        f"對應評鑑分類：{definition['evaluation_category'] or '-'}"
                    )
                    st.write(f"使用情境：{definition['usage_description']}")

                with action_col:
                    if st.button("產生範本", key=f"generate_{definition['id']}", use_container_width=True):
                        try:
                            output_path = generate_template_file(definition["id"])
                        except ValueError as exc:
                            st.error(str(exc))
                        else:
                            st.session_state["template_downloads"][definition["id"]] = str(output_path)
                            st.success(f"已產生：{output_path.name}")

                    download_path = _resolve_download_path(
                        st.session_state["template_downloads"].get(definition["id"])
                    )
                    mime = (
                        "application/vnd.oasis.opendocument.text"
                        if definition["suggested_format"] == "ODT"
                        else "application/vnd.oasis.opendocument.spreadsheet"
                    )
                    st.download_button(
                        "下載範本",
                        data=download_path.read_bytes() if download_path is not None else b"",
                        file_name=download_path.name if download_path is not None else "",
                        mime=mime,
                        disabled=download_path is None,
                        key=f"download_{definition['id']}",
                        use_container_width=True,
                    )
