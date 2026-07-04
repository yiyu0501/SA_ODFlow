# UI_SPEC_v20_ODFlow_nav_perf_polish

## 版本定位

v20 基於 v19。  
v19 的重點是讓「生成文件」變成真正可填寫、可預覽、可產 ODT 的 schema-driven form。  
v20 的重點是減少頁面切換與下載時的白屏感，並降低不必要的頁面載入成本。

## 修改範圍

本版只處理：

- 頁面切換體感
- runtime data cache
- 空白範本下載的 lazy generate
- loading overlay
- 主內容淡入動畫

不重做首頁、儀表板、空白範本版面、檔案庫、設定頁，也不改資料庫 schema 與 ODT / ODS generator 架構。

## 1. Runtime cache 拆分

原本多數頁面會透過 `_runtime_state()` 一次載入：

- club settings
- documents
- evaluation summary
- templates

v20 改成拆分：

- `_load_settings_cached()`
- `_load_documents_cached()`
- `_load_summary_cached()`
- `_load_templates_cached()`

並分別設定 TTL：

- settings：60 秒
- documents：18 秒
- summary：18 秒
- templates：300 秒

好處是頁面只取自己需要的資料，避免切換空白範本頁時也讀文件與評鑑 summary。

## 2. 空白範本下載 lazy generate

v18 / v19 為了讓卡片按鈕直接下載，會在空白範本頁載入時產生各範本 data URI。  
這會拖慢 Template Center 初次載入。

v20 改成：

- 頁面載入時只顯示卡片，不先產檔。
- 點擊「準備下載」後，只產生被點擊的那一份範本。
- 下載連結顯示在 Template Center 內容區，不再使用全頁頂部 `st.download_button`。

這會稍微多一次「準備下載」步驟，但可避免每次開頁都預先產生所有 ODT / ODS。

## 3. Loading overlay

所有 HTML shell 頁面加入 ODFlow loading veil：

- 淡色遮罩
- ODFlow loading card
- 頂部 loading bar
- 載入後自動淡出

目的不是把 Streamlit 變成 SPA，而是降低切頁時的白屏感。

## 4. Content fade-in

主內容區加入短暫淡入動畫：

- 避免畫面突然白屏後跳出
- 讓頁面切換更像完整產品

## 5. 生成文件頁

`core/generate_native.py` 也加入同樣 loading veil，讓 v19 新的原生表單頁與其他頁面切換體感一致。

## 限制

Streamlit 每次互動仍會 rerun script，所以不能做到 React / Vue 那種完全無刷新 SPA。  
v20 的目標是：

- 減少不必要運算
- 讓切換畫面更平順
- 避免空白範本頁預先產生所有下載檔
- 用 loading overlay 降低白屏感
