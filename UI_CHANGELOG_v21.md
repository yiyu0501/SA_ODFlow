# UI_CHANGELOG_v21

## Summary

Replace HTML-link navigation with Streamlit native sidebar navigation.

## Added

- `core/native_shell.py`
  - Native sidebar page buttons
  - `st.session_state["active_page"]` routing
  - HTML content extraction from existing page shell
  - Native shell styling

## Changed

- `app.py`
  - Uses a single native router.
  - Renders native sidebar once.
  - Displays each page based on `active_page`.

- `core/generate_native.py`
  - Generate page no longer renders its own HTML sidebar/topbar.
  - It now renders only the schema-driven generate content.

- `pages/2_Generate.py`
  - Uses native shell and generate content.

## Fixed

- Generate Document Step 2 can now navigate away using sidebar buttons.
- Navigation no longer depends on HTML `<a href>` links as the primary route mechanism.
- Removed the need for v20 loading overlay as the main navigation fix.

## Notes

- v21 is based on v19.
- v20 should be skipped unless specifically needed for comparison.
