# UI_CHANGELOG_v09

## Summary

Fixes v08 horizontal overflow by keeping the pixel-locked visual direction while adding responsive width guards.

## Changed

- `core/exact_ui.py`
- `docs/UI_SPEC_v09_ODFlow_responsive_pixel_guard.md`
- `UI_CHANGELOG_v09.md`

## Key Fixes

- Removed fixed `min-width: 1304px` from the main content container.
- Added no-horizontal-scroll guards to the app shell.
- Changed sidebar width to `clamp(272px, 18.2vw, 304px)`.
- Changed homepage top row from fixed `744px + 540px` to responsive proportions.
- Kept hero statistics from collapsing into vertical text.
- Made the evaluation card fit within the viewport instead of being clipped.
- Added responsive fallbacks for narrower browser widths.

## Not Changed

- Generator architecture
- ODT / ODS rendering logic
- Database schema
- Template registry / service
