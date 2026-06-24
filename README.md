# SA_ODFlow

學生社團 ODF 文件流與評鑑整理系統。

目前完成到 Task 4：會議紀錄生成、版本管理、ODT/PDF 基本匯出，以及評鑑完整度儀表板。這個版本提供可本機執行的 Streamlit 多頁面骨架、SQLite 資料庫初始化、mock 會議紀錄草稿生成、文件儲存、文件狀態與版本管理、目前版本的 ODT / PDF 產出與下載，以及七大評鑑項目的資料完整度檢核。

## 目前功能

- Streamlit 多頁面網站骨架
- SQLite schema 初始化與評鑑項目 seed
- 文字／逐字稿轉會議紀錄草稿
- 會議紀錄編輯與 SQLite 儲存
- Files 頁面的文件列表、狀態管理與版本管理
- Files 頁面的 ODT / PDF 產生與下載
- Dashboard 的整體完整度、缺漏文件提醒與下一步建議
- Evaluation 頁的七大評鑑項目檢核表與缺漏清單
- 七大社團評鑑分類與權重常數
- AI、文件匯出、文件服務的可替換模組骨架
- 本機安裝與 AI 使用邊界文件

## 尚未完成

- OpenAI API 串接
- 音檔轉文字
- Google Drive API
- 登入系統與多人權限
- 評鑑 ZIP 匯出

## 專案結構

```text
SA_ODFlow/
├─ app.py
├─ pages/
├─ core/
├─ ai/
├─ generators/
├─ templates/
├─ data/
├─ docs/
├─ tests/
└─ requirements.txt
```

## 本機執行

1. 建立虛擬環境並啟用
2. 安裝套件：`pip install -r requirements.txt`
3. 啟動應用程式：`streamlit run app.py`
4. 執行測試：`python -m unittest discover -s tests`

更完整步驟請見 [docs/setup_guide.md](/Users/yiyu/Documents/SA_OPFlow/docs/setup_guide.md)。

## 資料庫

- 預設資料庫位置：`data/odflow.sqlite3`
- 啟動 `app.py` 或任一頁面時，會自動建立資料庫與基本資料表
- `evaluation_items` 會自動寫入七大評鑑項目與權重
- Task 2 目前支援 `會議紀錄` 文件建立、版本保存與狀態切換

## 文件

- 開發規格書：[docs/product_spec.md](/Users/yiyu/Documents/SA_OPFlow/docs/product_spec.md)
- 安裝說明：[docs/setup_guide.md](/Users/yiyu/Documents/SA_OPFlow/docs/setup_guide.md)
- AI 使用聲明：[docs/ai_usage_statement.md](/Users/yiyu/Documents/SA_OPFlow/docs/ai_usage_statement.md)

## ODT / PDF 支援說明

- 目前只支援「會議紀錄」文件的目前版本匯出
- ODT 會輸出到 `data/generated/`
- PDF 會輸出到 `data/generated/`
- 檔案路徑會回寫到 `document_versions.odf_path` / `pdf_path`
- 評鑑 ZIP 匯出仍不在目前範圍內
