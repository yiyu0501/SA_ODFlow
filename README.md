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
- 文字／逐字稿轉會議紀錄草稿
- 會議紀錄編輯、版本管理、狀態管理
- Files 頁面的 ODT / PDF 匯出與下載
- Dashboard 評鑑完整度儀表板
- Evaluation 七大項目檢核、PDF 評鑑 ZIP 匯出、ODF 原始檔備份 ZIP 匯出

## 操作流程

1. 到 [pages/7_Settings.py](/Users/yiyu/Documents/SA_OPFlow/pages/7_Settings.py) 建立社團基本資料
2. 在 Settings 按「建立示範資料」
3. 到 [pages/2_Generate.py](/Users/yiyu/Documents/SA_OPFlow/pages/2_Generate.py) 產生一份會議紀錄
4. 到 [pages/3_Files.py](/Users/yiyu/Documents/SA_OPFlow/pages/3_Files.py) 管理版本，匯出 ODT / PDF
5. 到 [pages/1_Dashboard.py](/Users/yiyu/Documents/SA_OPFlow/pages/1_Dashboard.py) 查看完整度與缺漏
6. 到 [pages/5_Evaluation.py](/Users/yiyu/Documents/SA_OPFlow/pages/5_Evaluation.py) 產生 PDF 評鑑 ZIP 與 ODF 原始檔備份 ZIP

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
4. 在 Generate 產生一份會議紀錄
5. 在 Files 匯出 ODT / PDF
6. 在 Dashboard 看完整度
7. 在 Evaluation 輸出 PDF 評鑑 ZIP 與 ODF 備份 ZIP

完整逐字腳本請見 [docs/demo_script.md](/Users/yiyu/Documents/SA_OPFlow/docs/demo_script.md)。

## AI 使用聲明

- 目前 MVP 使用 `ai/mock_parser.py` 做會議紀錄草稿整理
- 尚未串接 OpenAI API
- 尚未實作音檔轉文字
- 若未來導入 AI，範圍會限定在文字整理與會議紀錄草稿生成
- ODF / PDF / ZIP 匯出流程目前仍由系統規則與既有 generator 產生

詳見 [docs/ai_usage_statement.md](/Users/yiyu/Documents/SA_OPFlow/docs/ai_usage_statement.md)。

## 尚未完成與未來規劃

- OpenAI API 串接
- 音檔轉文字
- Google Drive API
- 登入系統與多使用者權限
- Projects 頁完整活動管理
- Templates 頁完整範本庫
- 非會議紀錄類型文件的更完整產生流程

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
