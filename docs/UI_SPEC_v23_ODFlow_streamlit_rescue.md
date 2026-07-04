# UI_SPEC_v23_ODFlow_streamlit_rescue

## Goal

Recover a stable Streamlit version for competition demonstration.

## Principle

This version does not redesign the sidebar. It keeps the original ODFlow HTML sidebar/topbar style because that was visually more stable.

## Main decisions

1. Do not use native Streamlit sidebar.
2. Do not keep the v20 loading overlay as the visible page-switch solution.
3. Keep the schema-driven Generate Document form.
4. Keep lazy blank-template downloads so the Template Center does not pre-generate every data URI at once.
5. Make Generate Step 2 use normal widgets outside `st.form`, so the user can leave the page more naturally.

## Scope

- `app.py`
- `core/exact_ui.py`
- `core/generate_native.py`
- `pages/2_Generate.py`

## Test

- `python3 -m compileall app.py core pages`
