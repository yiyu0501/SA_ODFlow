# UI_CHANGELOG_v10

## Summary

Bugfix release based on v09 responsive guard.

## Fixed

- Homepage quick action cards no longer clip the CTA buttons.
- Template center cards no longer clip the secondary button.
- Generate document Step 1 template cards no longer clip selection buttons.
- Custom HTML links now force `target="_self"` to avoid opening a new browser tab/window.
- Global card overflow no longer clips child controls.

## Changed

- `core/exact_ui.py`
- `docs/UI_SPEC_v10_ODFlow_bugfix.md`
- `UI_CHANGELOG_v10.md`

## Not Changed

- ODT/ODS generation logic
- Template registry
- Database schema
- Generator architecture
