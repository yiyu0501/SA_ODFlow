# UI_CHANGELOG_v18

## Summary

Improve template downloads and make Generate Document Step 2/3 actually use user-entered form data.

## Changed

- `core/exact_ui.py`
- `docs/UI_SPEC_v18_ODFlow_direct_download_generate_form.md`
- `UI_CHANGELOG_v18.md`

## Fixed

- Template Center download buttons now download directly from the card via HTML `download` links.
- Removed the secondary "查看說明" button from template cards.
- Improved template download button styling.
- Generate Document Step 2 is now a real fillable HTML form.
- Generate Document Step 3 preview now reflects the user's submitted form data.
- Generate Document Step 4 ODT download attempts to use the submitted form data.

## Notes

- Browser security still requires the user to click a download button.
- PDF download remains intentionally disabled until real PDF export is wired.
