# UI_CHANGELOG_v19

## Summary

Rebuild Generate Document into a real schema-driven Streamlit flow.

## Added

- `core/generate_native.py`
- Native Streamlit generate flow:
  - Step 1: choose supported template
  - Step 2: schema-driven form fields
  - Step 3: dynamic preview from user input
  - Step 4: real ODT download from `generate_document_odt()`

## Fixed

- Template selection is now stored in `st.session_state`.
- Form fields are real Streamlit widgets and can be edited.
- Date fields use `st.date_input`.
- Repeatable sections use `st.data_editor`.
- Preview reflects the user's actual submitted content.
- ODT output uses the submitted content.

## Not Changed

- Homepage
- Dashboard
- Template Center
- File Library
- Settings Center
- Database schema
- Existing ODT generator architecture

## Test

- `python3 -m compileall app.py core pages`
- Generated sample ODT using existing generator.
