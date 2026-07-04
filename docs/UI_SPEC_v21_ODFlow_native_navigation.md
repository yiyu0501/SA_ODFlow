# UI_SPEC_v21_ODFlow_native_navigation

## 版本定位

v21 不採用 v20 的 loading overlay 解法。  
v21 從 v19 繼續，保留 v19 的 schema-driven 生成文件流程，並重做全站導航層。

## 問題

v18 / v19 / v20 的 sidebar 主要是 HTML `<a href="/?page=...">` 導航。  
這會造成：

- 點頁面時像整頁重開。
- Streamlit 每次都重新跑 app.py。
- 生成文件 Step 2 使用 Streamlit 原生 form 時，HTML sidebar 與原生 widget 混用，容易出現切頁不穩。
- v20 的 loading overlay 只能遮白屏，不能解決架構問題。

## v21 解法

新增 `core/native_shell.py`，使用 Streamlit 原生 sidebar button 管理頁面切換。

### 核心狀態

- `st.session_state["active_page"]`

### 導航方式

不再以 HTML `<a href>` 作為主要導航，而是：

- `st.sidebar.button()`
- 點擊後更新 `st.session_state["active_page"]`
- 使用 `st.rerun()` 切換內容

### 路由

`app.py` 改成單一 Streamlit router：

- 先渲染 native sidebar
- 再依 `active_page` 顯示內容
- 一般 HTML 頁面會抽出原本 `odf-content`
- Generate 頁直接顯示 v19 的 schema-driven native form

## 修改檔案

- `app.py`
- `pages/2_Generate.py`
- `core/generate_native.py`
- `core/native_shell.py`

## 保留

- v19 生成文件 schema-driven form
- 不改 DB schema
- 不改 ODT generator 架構
- 不改空白範本 / 檔案庫 / 設定頁內容邏輯

## 預期改善

- 生成文件 Step 2 可穩定透過 sidebar 切換到其他頁。
- 頁面切換不再像瀏覽器整頁 URL 跳轉。
- sidebar 視覺與互動由 Streamlit 原生 widget 控制。
- 不使用 v20 的大型 loading overlay，避免錄影片時看到 loading 卡。
