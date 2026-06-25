# ODFlow

ODFlow 是一套學生社團 ODF 文件流與評鑑整理系統，協助社團平時保存 ODF 原始檔，並在評鑑時輸出 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP。

## 線上展示

- Streamlit App：[https://sa-odflow.streamlit.app/](https://sa-odflow.streamlit.app/)
- 目前正進行 v0.3 介面與互動體驗升級，重點是中文介面、空白範本直接下載、儀表板與社團評鑑頁更直覺。

## 解決問題

學生社團常見的痛點不是「沒有文件」，而是：

- 平時文件分散在 Word、Excel、PDF、聊天紀錄與個人電腦
- 到評鑑前才臨時整理，常常找不到原始檔
- 明明需要上傳 PDF，卻沒有穩定保存 ODF 原始檔的流程
- 不知道哪些資料已完成、哪些還缺漏

ODFlow 要做的，是把這個流程變成日常可維護的文件流：

1. 平時生成與保存 ODF 原始檔
2. 用「檔案庫」「儀表板」「社團評鑑」管理資料狀態
3. 評鑑前一鍵輸出 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP

## ODF 競賽定位

ODFlow 對應 ODF 競賽學生組的三個方向：

- ODF 應用工具
- ODF 文件範本與輸出流程
- ODF 推廣與保存價值

這個作品不是把既有檔案「轉成 ODF」而已，而是讓 ODF 真正進入社團行政、活動與評鑑整理流程。

## 核心功能

- 社團基本資料設定
- 示範資料建立
- 中文介面導覽與首頁流程展示
- 五種日常社團文件生成：
  - 會議紀錄
  - 活動企劃書
  - 活動成果報告
  - 活動檢討會紀錄
  - 年度計畫
- 會議紀錄 mock parser 與其他文件表單式草稿生成
- 多文件編輯、版本管理、狀態管理
- ODT / PDF 匯出與下載
- 社團評鑑資料完整度儀表板
- 社團評鑑七大項目檢核
- PDF 評鑑上傳包匯出
- ODF 原始檔備份 ZIP 匯出
- 22 個空白 ODT / ODS 範本直接下載
- 5 個核心範本可直接建立文件

## 使用流程

1. 在「社團設定」設定社團基本資料
2. 建立示範資料
3. 在「空白範本」直接下載空白 ODT / ODS 範本，或用核心範本直接進入「生成文件」
4. 在「生成文件」選擇文件類型，建立會議紀錄、活動企劃書、活動成果報告、活動檢討會紀錄或年度計畫
5. 在「檔案庫」管理版本並匯出 ODT / PDF
6. 在「儀表板」查看社團評鑑資料完整度與缺漏
7. 在「社團評鑑」輸出 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP

## Demo 快速開始

1. 啟動系統後先進入「社團設定」
2. 輸入社團名稱、學年度、校區
3. 點擊「建立示範資料」
4. 到「空白範本」直接下載一份 ODT / ODS 範本，或用核心範本直接建立文件
5. 到「生成文件」產生一份會議紀錄或其他社團文件
6. 到「檔案庫」產生 ODT / PDF
7. 到「儀表板」看社團評鑑資料完整度
8. 到「社團評鑑」產生 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP

## 安裝方式

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

更完整的操作與展示細節請見 [docs/setup_guide.md](/Users/yiyu/Documents/SA_OPFlow/docs/setup_guide.md)。

## 頁面介紹

### 首頁

首頁說明 ODFlow 的作品定位、展示流程、目前已完成項目與系統狀態。

### 儀表板

顯示社團評鑑資料完整度、七大評鑑項目完成率、缺漏文件提醒與下一步建議。

### 生成文件

支援五種文件類型生成。會議紀錄可用逐字稿或會議摘要搭配 mock parser 產生草稿，其餘文件可直接用表單建立內容。

### 檔案庫

管理文件列表、版本、狀態，並匯出 ODT / PDF。

### 專案

目前仍是未來擴充頁面，尚未實作完整活動 / 專案管理。

### 社團評鑑

查看七大評鑑項目檢核、缺漏文件，並產生 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP。  
目前是本機 ZIP 下載，不是雲端自動上傳。

### 空白範本

提供 22 個空白 ODT / ODS 範本，分成：

- 日常行政
- 活動專案
- 社團評鑑
- 財務與清冊

目前可直接下載空白 ODT / ODS 範本，不需要先建立文件；另外也支援 5 個核心 ODT 範本直接「使用此範本建立文件」，帶入「生成文件」建立正式文件。

### 社團設定

設定社團基本資料，並建立示範資料，供儀表板、社團評鑑與展示流程使用。

## ODF 價值

- 平時保存 ODF 原始檔，不只留下 PDF
- 評鑑時輸出 PDF 評鑑上傳包，兼顧上傳需求
- 空白範本頁降低從 Word / Excel 轉向 ODF 的門檻
- 讓 ODF 不是最後才轉檔，而是一開始就進入社團行政流程

## AI 使用聲明

- 目前會議紀錄草稿流程使用 `ai/mock_parser.py`
- 尚未串接 OpenAI API
- 尚未支援音檔轉文字
- 其他文件類型目前以表單式生成為主，不需依賴 OpenAI 也可完成 ODF / PDF / ZIP 流程
- 若未來導入 AI，會限定在文字整理與會議紀錄草稿生成
- ODF / PDF / ZIP 流程目前仍由系統規則產生

詳見 [docs/ai_usage_statement.md](/Users/yiyu/Documents/SA_OPFlow/docs/ai_usage_statement.md)。

## 目前限制與未來規劃

目前尚未完成：

- OpenAI API 串接
- 音檔轉文字
- Google Drive API
- 登入系統與多使用者權限
- 專案頁完整管理能力
- 空白範本更完整樣式與更豐富範本管理
- 更多文件類型與更細緻的欄位驗證

這個版本的定位是 ODF 競賽展示版 MVP，不是完整商業產品。

## 文件

- 開發規格書：[docs/product_spec.md](/Users/yiyu/Documents/SA_OPFlow/docs/product_spec.md)
- 安裝說明：[docs/setup_guide.md](/Users/yiyu/Documents/SA_OPFlow/docs/setup_guide.md)
- 3 分鐘展示腳本：[docs/demo_script.md](/Users/yiyu/Documents/SA_OPFlow/docs/demo_script.md)
- 5 分鐘評審展示流程：[docs/judge_demo_flow.md](/Users/yiyu/Documents/SA_OPFlow/docs/judge_demo_flow.md)
- 截圖清單：[docs/screenshot_checklist.md](/Users/yiyu/Documents/SA_OPFlow/docs/screenshot_checklist.md)
- 提交前檢查表：[docs/submission_checklist.md](/Users/yiyu/Documents/SA_OPFlow/docs/submission_checklist.md)
- 比賽定位說明：[docs/competition_positioning.md](/Users/yiyu/Documents/SA_OPFlow/docs/competition_positioning.md)
- AI 使用聲明：[docs/ai_usage_statement.md](/Users/yiyu/Documents/SA_OPFlow/docs/ai_usage_statement.md)

## 參賽展示素材

- 7 分鐘簡報大綱：[docs/presentation_outline_7min.md](/Users/yiyu/Documents/SA_OPFlow/docs/presentation_outline_7min.md)
- 7 分鐘簡報逐字稿：[docs/presentation_script_7min.md](/Users/yiyu/Documents/SA_OPFlow/docs/presentation_script_7min.md)
- 操作影片腳本：[docs/demo_video_script.md](/Users/yiyu/Documents/SA_OPFlow/docs/demo_video_script.md)
- 評審 Q&A：[docs/judge_qna.md](/Users/yiyu/Documents/SA_OPFlow/docs/judge_qna.md)
- AI 使用聲明比賽版：[docs/ai_usage_competition_statement.md](/Users/yiyu/Documents/SA_OPFlow/docs/ai_usage_competition_statement.md)
- 最終提交檢查表：[docs/final_submission_checklist.md](/Users/yiyu/Documents/SA_OPFlow/docs/final_submission_checklist.md)
