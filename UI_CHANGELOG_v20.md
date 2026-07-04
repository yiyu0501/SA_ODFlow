# UI_CHANGELOG_v20

## Summary

Improve navigation feel and reduce unnecessary work during page switches.

## Changed

- `core/exact_ui.py`
- `core/generate_native.py`
- `docs/UI_SPEC_v20_ODFlow_nav_perf_polish.md`
- `UI_CHANGELOG_v20.md`

## Performance

- Split runtime data loading into cached loaders:
  - settings
  - documents
  - evaluation summary
  - templates
- Template Center now uses lazy template generation.
- Template cards no longer pre-generate all download data URIs on page load.
- Dashboard, Files, Templates, and Settings use only the cached data they need.

## UX polish

- Added ODFlow loading overlay to reduce white-screen feeling during navigation.
- Added a top loading bar and loading card.
- Added short content fade-in animation.
- Applied the same loading veil to the native Generate Document page.

## Notes

- This does not turn Streamlit into a true SPA.
- PDF export remains unchanged.
- v20 is intended to be applied after v19. A combined v19+v20 patch is also provided for branches where v19 has not yet been merged.
