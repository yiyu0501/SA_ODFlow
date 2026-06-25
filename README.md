# ODFlow / SA_ODFlow

ODFlow 是一套學生社團 ODF 文件流與評鑑整理系統，協助社團平時生成與保存 ODF 原始檔，評鑑前再輸出 PDF 上傳包與 ODF 備份 ZIP。

## 比賽定位

- ODF 文件生成工具
- 學生社團評鑑資料整理工具
- ODF 原始檔保存與 PDF 上傳包輸出流程

ODFlow 的核心價值不是做完整專案管理平台，而是把社團最常痛苦的文件整理流程標準化：

1. 平時用系統整理會議與活動資料
2. 保存 ODF 原始檔，降低文件只剩 PDF 的風險
3. 評鑑前依七大項目整理成可直接上傳的 PDF ZIP

## 目前完成功能

- Streamlit 多頁面網站與 SQLite 本機資料庫
- 社團基本資料設定
- 示範資料建立
- Templates ODF 範本庫最小可展示版
- 五種日常社團文件生成：
  - 會議紀錄
  - 活動企劃書
  - 活動成果報告
  - 活動檢討會紀錄
  - 年度計畫
- 會議紀錄 mock parser 與其他文件表單式草稿生成
- 多文件編輯、版本管理、狀態管理
- Files 頁面的 ODT / PDF 匯出與下載
- Dashboard 評鑑完整度儀表板
- Evaluation 七大項目檢核、PDF 評鑑 ZIP 匯出、ODF 原始檔備份 ZIP 匯出

## 操作流程

1. 到 [pages/7_Settings.py](/Users/yiyu/Documents/SA_OPFlow/pages/7_Settings.py) 建立社團基本資料
2. 在 Settings 按「建立示範資料」
3. 到 [pages/6_Templates.py](/Users/yiyu/Documents/SA_OPFlow/pages/6_Templates.py) 產生並下載 ODT / ODS 範本，或用核心範本直接進入 Generate 建立文件
4. 到 [pages/2_Generate.py](/Users/yiyu/Documents/SA_OPFlow/pages/2_Generate.py) 選擇文件類型，建立會議紀錄、活動企劃書、活動成果報告、活動檢討會紀錄或年度計畫
5. 到 [pages/3_Files.py](/Users/yiyu/Documents/SA_OPFlow/pages/3_Files.py) 管理版本，匯出 ODT / PDF
6. 到 [pages/1_Dashboard.py](/Users/yiyu/Documents/SA_OPFlow/pages/1_Dashboard.py) 查看完整度與缺漏
7. 到 [pages/5_Evaluation.py](/Users/yiyu/Documents/SA_OPFlow/pages/5_Evaluation.py) 產生 PDF 評鑑 ZIP 與 ODF 原始檔備份 ZIP

## 本機安裝與執行

1. 建立虛擬環境

```bash
python3 -m venv .venv
```

2. 安裝依賴

```bash
.venv/bin/pip install -r requirements.txt
```

3. 啟動 Streamlit

```bash
.venv/bin/streamlit run app.py
```

4. 執行測試

```bash
.venv/bin/python -m unittest discover -s tests
```

更多細節請見 [docs/setup_guide.md](/Users/yiyu/Documents/SA_OPFlow/docs/setup_guide.md)。

## Demo 建議流程

3 分鐘展示可依這個順序進行：

1. 介紹 ODFlow 解決什麼問題
2. 在 Settings 確認社團基本資料
3. 點擊建立示範資料
4. 在 Templates 產生一份 ODT / ODS 範本
5. 在 Generate 產生一份會議紀錄或其他社團文件
6. 在 Files 匯出 ODT / PDF
7. 在 Dashboard 看完整度
8. 在 Evaluation 輸出 PDF 評鑑 ZIP 與 ODF 備份 ZIP

## Templates 頁用途

Templates 頁提供三大類 ODF 範本，讓社團平時就能以 ODT / ODS 開始整理資料，而不是先用 Word / Excel，最後才勉強轉檔。

- 日常行政型
- 專案活動型
- 社團評鑑型

目前支援 22 個 ODT / ODS 範本，包含會議通知、會議議程、會議紀錄、出席簽到表、幹部名冊、社員名冊、交接清冊、收支帳冊、活動企劃書、活動流程表、活動預算表、活動成果報告、社團評鑑資料檢核表、年度計畫、年度行事曆、年度收支總表等。

使用方式：

1. 進入 Templates 頁
2. 選擇範本分類
3. 點擊「產生範本」取得空白 ODT / ODS 範本
4. 或對 5 個核心 ODT 範本點擊「使用此範本建立文件」，直接進入 Generate 填表
5. 需要空白檔時再點擊「下載範本」

目前 Templates 仍屬最小可展示版，後續可再增加更多範本、版型樣式與欄位配置。

完整逐字腳本請見 [docs/demo_script.md](/Users/yiyu/Documents/SA_OPFlow/docs/demo_script.md)。

## AI 使用聲明

- 目前 MVP 使用 `ai/mock_parser.py` 做會議紀錄草稿整理
- 尚未串接 OpenAI API
- 尚未實作音檔轉文字
- 其他文件類型目前以表單式生成為主，不需依賴 OpenAI 即可完成 ODF / PDF / ZIP 流程
- 若未來導入 AI，範圍會限定在文字整理與會議紀錄草稿生成
- ODF / PDF / ZIP 匯出流程目前仍由系統規則與既有 generator 產生

詳見 [docs/ai_usage_statement.md](/Users/yiyu/Documents/SA_OPFlow/docs/ai_usage_statement.md)。

## 尚未完成與未來規劃

- OpenAI API 串接
- 音檔轉文字
- Google Drive API
- 登入系統與多使用者權限
- Projects 頁完整活動管理
- Templates 頁更完整的範本樣式、更多格式與可編輯範本管理
- 更多文件類型與更細緻的欄位驗證

這些目前都不在展示版 MVP 範圍內，README 與頁面會誠實保留為後續擴充方向。

## ODF 推廣價值

- 社團常常只在最後一刻整理 PDF，ODFlow 把 ODF 原始檔保存拉回日常流程
- ODF 原始檔可編輯、可持續維護，比只留 PDF 更有保存與再利用價值
- 系統同時照顧「平時可編修」與「評鑑要上傳 PDF」兩種需求
- 這讓 ODF 不只是檔案格式，而是社團文件治理流程的一部分

## 文件

- 開發規格書：[docs/product_spec.md](/Users/yiyu/Documents/SA_OPFlow/docs/product_spec.md)
- 安裝說明：[docs/setup_guide.md](/Users/yiyu/Documents/SA_OPFlow/docs/setup_guide.md)
- 展示腳本：[docs/demo_script.md](/Users/yiyu/Documents/SA_OPFlow/docs/demo_script.md)
- 比賽定位說明：[docs/competition_positioning.md](/Users/yiyu/Documents/SA_OPFlow/docs/competition_positioning.md)
- AI 使用聲明：[docs/ai_usage_statement.md](/Users/yiyu/Documents/SA_OPFlow/docs/ai_usage_statement.md)
