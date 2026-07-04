# UI_SPEC_v19_ODFlow_schema_generate

## 修正範圍

本版只重做「生成文件」頁。首頁、儀表板、空白範本、檔案庫、設定頁不動。

## 為什麼要重做

v18 的生成文件頁使用 HTML form 與 query params 模擬互動，視覺可行，但不適合真正的文件生成：

- 範本選擇狀態不穩定。
- 表單欄位不是 Streamlit 原生 widget，編輯體驗不穩。
- 每個範本欄位不同，不能共用同一套活動基本資料。
- 預覽應該依照文件 schema 與使用者填寫內容生成。
- ODT 下載應該使用真正的 `generate_document_odt()`。

## v19 解法

新增 `core/generate_native.py`，生成文件頁改用 Streamlit 原生互動元件。

### Step 1：選擇範本

只列出 `supports_generate_document=True` 且已支援 schema 的核心 ODT 文件：

- 會議紀錄
- 開會通知單
- 會議議程
- 活動企劃書
- 活動成果報告
- 活動檢討會紀錄
- 年度計畫

選擇結果寫入：

- `st.session_state["generate_template_id"]`
- `st.session_state["generate_document_type"]`
- `st.session_state["generate_content"]`
- `st.session_state["generate_step"]`

### Step 2：填寫資料

依照 `core.document_schemas.get_document_schema(document_type)` 動態產生欄位。

支援欄位型態：

- 一般文字：`st.text_input`
- 長文字：`st.text_area`
- 人員清單：`st.text_area`
- 日期欄位：`st.date_input`
- repeatable_sections：`st.data_editor`

因此每個範本會出現不同欄位，不再用同一套固定活動資料硬套所有文件。

### Step 3：預覽確認

使用：

- `normalize_document_content()`
- `derive_document_title()`
- `build_document_preview_blocks()`

預覽內容會依照 Step 2 的填寫資料更新。

### Step 4：下載 ODT

使用：

- `normalize_document_content()`
- `derive_document_title()`
- `generate_document_odt()`

產出真正的 ODT 文件，並用 `st.download_button()` 下載。

PDF 仍保留為下一階段功能，不提供假 PDF。

## 修改檔案

- `app.py`
- `pages/2_Generate.py`
- `core/generate_native.py`

## 不動範圍

- 首頁
- 儀表板
- 空白範本
- 檔案庫
- 設定頁
- DB schema
- template registry
- ODT generator 架構
