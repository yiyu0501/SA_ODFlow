# UI_CHANGELOG_v17

## Summary

Fix sidebar brand spacing, wire template download buttons to the existing backend, and reduce page switch latency.

## Changed

- `core/exact_ui.py`
- `docs/UI_SPEC_v17_ODFlow_downloads_perf.md`
- `UI_CHANGELOG_v17.md`

## Fixes

- Removed the sidebar brand subtitle that was visually too close to the Workbench nav heading.
- Template Center download buttons now call the real `generate_template_file()` flow via `download_template`.
- Generate Document Step 1 now uses real template registry data for generatable templates.
- Generate Document Step 4 ODT / ODS download action now points to an actual generated file flow.
- Added cached runtime state with `st.cache_data(ttl=12)` to reduce repeated DB/template/evaluation loading during page switches.

## Notes

- PDF download in Generate Step 4 is still intentionally marked as not yet connected.
- Real document-content generation can be connected later when the form fields are wired into document versions.
