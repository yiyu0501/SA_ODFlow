# UI_SPEC_v17_ODFlow_downloads_perf

## 修正範圍

本版基於 v16，只修三件事：

1. Sidebar 品牌區 subtitle 太低、靠近「工作台」標題。
2. 空白範本與生成文件的下載按鈕要連到實際後端產檔流程。
3. 頁面切換太慢，需要降低每次切換的重複資料讀取成本。

## 1. Sidebar 品牌區

- 移除 sidebar 頂部的「台灣學生社團 ODF 文件工作台」subtitle。
- 保留 ODFlow 主標與 logo。
- 避免 subtitle 與「工作台」分組標題位置過近。

## 2. 空白範本下載

- Template Center 的「下載範本」按鈕不再是 `#`。
- 若範本 `supports_blank_download=True`，按鈕會連到：
  - `/?page=Templates&download_template=<template_id>`
- 由 `core.template_service.generate_template_file()` 產生實際 ODT / ODS 檔案。
- 頁面上方會出現 Streamlit 原生 download button，下載實際產出的檔案。
- 若範本尚未開放下載，按鈕顯示「尚未開放」。

## 3. 生成文件下載

- Generate Step 1 改用 `list_template_definitions()` 中 `supports_generate_document=True` 的範本，不再硬寫固定假資料。
- 選擇範本時保留 `template_id`。
- Step 4 的 ODT / ODS 下載會連到：
  - `/?page=Generate&step=4&template_id=<id>&download_template=<id>`
- 目前接的是現有空白範本 / 產檔流程；PDF 仍標示為下一階段接入。

## 4. 效能

- `_runtime_state()` 改成 `st.cache_data(ttl=12, show_spinner=False)` 快取。
- 避免首頁、儀表板、空白範本、生成文件切換時重複初始化 DB 與重新讀取全部資料。
- 仍保留短 TTL，避免資料長時間不更新。

## 不變

- 首頁視覺不動
- 儀表板視覺不動
- 設定頁架構不動
- ODT / ODS generator backend 不重寫
- DB schema 不動
