# UI_CHANGELOG_v23

## Summary

Streamlit rescue build. Keep the original ODFlow HTML sidebar/topbar and avoid the native-sidebar rewrite.

## Changed

- Keep original sidebar and visual shell.
- Remove the full-screen loading overlay to reduce perceived page-switch delay.
- Keep v19 schema-driven Generate Document flow.
- Keep v20 lazy template download behavior.
- Replace Generate Step 2 `st.form` with normal Streamlit widgets plus explicit Next/Back buttons, so sidebar links are less likely to feel blocked while editing fields.
- Preserve ODT generation from entered content.

## Not included

- No native Streamlit sidebar.
- No Go rewrite.
- No FastAPI rewrite.
- No database schema changes.
- No PDF export.
