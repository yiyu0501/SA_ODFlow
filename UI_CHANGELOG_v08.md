# UI_CHANGELOG_v08

## Summary

Rebuilt the Streamlit UI as a pixel-locked custom HTML/CSS shell based on the uploaded `ODF網頁.zip` reference images.

## Changed

- `app.py`
- `core/exact_ui.py`
- `pages/1_Dashboard.py`
- `pages/2_Generate.py`
- `pages/3_Files.py`
- `pages/4_Projects.py`
- `pages/5_Evaluation.py`
- `pages/6_Templates.py`
- `pages/7_Settings.py`
- `docs/UI_SPEC_v08_ODFlow_pixel_locked.md`

## UI Fixes

- Hide native Streamlit sidebar/header/toolbar.
- Replace all layout with custom fixed-width App Shell.
- Sidebar width locked to 304px with no internal scroll.
- Main content width locked to 1304px.
- Homepage hero and evaluation card locked to reference image proportions.
- Prevent hero stat cards from collapsing into vertical text.
- Evaluation ring uses real percentage; 0% means no fake progress fill.
- Generation Step 4 switches ODT/ODS download cards based on selected template format.

## Not Changed

- `generators/`
- `core/template_registry.py`
- `core/template_service.py`
- `core/document_service.py`
- Database schema
- ODT/ODS generator architecture
