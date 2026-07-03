# UI_CHANGELOG_v12

## Summary

Real recovery release for the App Shell blank-page regression.

## Fixed

- Corrected `_same_tab_links()` regex from a character class that still matched `<aside>` to a real anchor-only pattern.
- Verified `<aside>`, `<article>`, `<main>`, and `.odf-content` remain intact in generated home HTML.
- Preserved same-tab behavior for actual `<a>` tags.
- Preserved v09 responsive guard and v10 card/button clipping fixes.

## Changed

- `core/exact_ui.py`
- `docs/UI_SPEC_v12_ODFlow_real_shell_recovery.md`
- `UI_CHANGELOG_v12.md`

## Test

- Python HTML sanity checks for `_same_tab_links()`
- `python3 -m compileall app.py core pages`
- `git apply --check uiux_v12_real_shell_recovery.patch`
