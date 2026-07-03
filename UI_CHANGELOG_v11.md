# UI_CHANGELOG_v11

## Summary

Recovery release for the v10 App Shell regression.

## Fixed

- Fixed the same-tab link regex so it no longer corrupts `<aside>`.
- Restored the custom sidebar and main content shell.
- Preserved v10 card/button clipping fixes.
- Preserved same-tab navigation behavior for real `<a>` links only.

## Changed

- `core/exact_ui.py`
- `docs/UI_SPEC_v11_ODFlow_shell_recovery.md`
- `UI_CHANGELOG_v11.md`

## Test

- `python3 -m compileall app.py core pages`
- `git apply --check uiux_v11_shell_recovery.patch`
