# UI_CHANGELOG_v13

## Summary

Polish release based on the now-stable v12 shell.

## Added

- Implemented a real Settings page.
- Added clickable top-right Help / Notifications / User drawer panels.
- Added root app query routing for smoother same-tab navigation.
- Added dynamic data loading for homepage, dashboard, and file library.
- Added clickable template category filters.

## Fixed

- Dashboard and homepage no longer display fake fixed numbers when there is no data.
- Empty states are shown when there are no documents or projects.
- Template category tabs can now be selected.
- Main navigation stays in the same tab and uses `/?page=...` routes.

## Not Changed

- ODT / ODS generation backend
- Template registry logic
- Database schema
- Generator architecture
