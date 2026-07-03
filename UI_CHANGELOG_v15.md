# UI_CHANGELOG_v15

## Summary

Rebuilt the Settings page into an account-center style list layout.

## Changed

- `core/exact_ui.py`
- `docs/UI_SPEC_v15_ODFlow_settings_center.md`
- `UI_CHANGELOG_v15.md`

## Added

- Settings left navigation:
  - 社團與帳號
  - 成員與權限
  - 文件與輸出
  - 通知
  - 資料與備份
  - 系統資訊
- List-style setting rows with title, description, current value, and action.
- Query-driven Settings sections:
  - `/?page=Settings&section=club`
  - `/?page=Settings&section=members`
  - `/?page=Settings&section=documents`
  - `/?page=Settings&section=notifications`
  - `/?page=Settings&section=data`
  - `/?page=Settings&section=system`

## Removed from Settings IA

- 評鑑與流程
- 外觀與輔助

## Not Changed

- Homepage
- Dashboard
- Template Center
- Generate Document
- File Library
- ODT / ODS generation backend
- Database schema
