# ODFlow / SA_ODFlow Codex 開發規格書 v0.2

> Repo name: `SA_ODFlow`
> 專案定位：學生社團 ODF 文件流與評鑑整理系統
> 技術方向：Streamlit + SQLite + ODF/PDF export + GitHub repo + Codex iterative development

---

## 0. 給 Codex 的總任務說明

請在 GitHub repository `SA_ODFlow` 中建立一個可本機執行的 Streamlit 專案。

ODFlow 不是完整專案管理平台，而是「文件生成、檔案管理、版本保存、社團評鑑輸出」系統。使用者平常開會、辦活動、產生財務與成果文件時，系統可以協助生成 ODF 原始檔並保存；到社團評鑑時，系統可以將已保存文件轉成 PDF，整理成臺北市立大學線上社團評鑑所需的資料夾結構，並輸出 ZIP。

請先完成 MVP，不要一次做太大。MVP 以「文字/逐字稿轉會議紀錄 → 儲存 → 編輯 → 版本管理 → ODF/PDF 下載 → 評鑑完整度儀表板 → 評鑑 ZIP 輸出」為主。

---

## 1. 核心產品定位

### 1.1 一句話

ODFlow 是一套學生社團 ODF 文件流與評鑑整理系統，協助學生會與社團將會議、活動、財務、成果資料透過 ODF 範本生成、保存、分類，並於評鑑時輸出符合學務處規範的 PDF 資料夾。

### 1.2 不做什麼

MVP 暫時不做：

1. 完整多人帳號權限系統
2. Google Drive API 直接串接
3. 線上 ODF 編輯器
4. 完整專案管理平台
5. 真正音檔語音轉文字
6. AI 自動評分預測

### 1.3 要做什麼

MVP 必做：

1. Streamlit 多頁面網站
2. SQLite 資料庫
3. 社團基本資料設定
4. 逐字稿/文字輸入生成會議紀錄
5. 文件內容可在網頁上修改
6. 文件版本管理
7. 文件庫列表
8. ODF/PDF 下載
9. 七大評鑑項目完整度儀表板
10. 評鑑資料夾 ZIP 輸出
11. README 與操作文件

---

## 2. 使用情境

### 2.1 會議紀錄生成

使用者開完會後，可以貼上逐字稿或會議摘要，例如：

「這是 6 月 24 日開的幹部會議，請幫我做會議紀錄。」

系統需要：

1. 判斷文件類型：會議紀錄
2. 擷取會議日期、會議名稱、主席、紀錄、出席人員、討論事項、決議事項、待辦事項
3. 產生可編輯草稿
4. 使用者可修改內容
5. 儲存為 v1 / v2 / v3
6. 可設定某版本為正式版
7. 產出 `.odt` 與 `.pdf`
8. 自動分類到：
   - `2.社團行政_管理運作`
   - `3.社團行政_社團資料保存`

### 2.2 文件保存與替換

不要直接刪除舊版本。請使用版本管理。

文件狀態：

- 草稿
- 待審
- 正式版
- 已歸檔

版本例：

- `1150624_學生會_會議紀錄_幹部會議_v1.odt`
- `1150624_學生會_會議紀錄_幹部會議_v2.odt`
- `1150624_學生會_會議紀錄_幹部會議_正式版.pdf`

### 2.3 活動資料歸檔

活動不是完整專案管理，而是文件完整度管理。

每個活動可以包含：

1. 活動企劃書
2. 活動粗流程表
3. 活動細流程表 Run-down
4. 工作人員名冊
5. 預算表
6. 代墊與核銷追蹤表
7. 活動簽到表
8. 活動檢討會紀錄
9. 活動成果報告
10. 活動照片與附件索引

活動頁顯示完成度，例如完成 7/10 = 70%。

### 2.4 社團評鑑輸出

評鑑輸出應產生 ZIP：

`114學年度臺北市立大學社團評鑑資料_天母校區_XXX社.zip`

解壓縮後：

```text
114學年度臺北市立大學社團評鑑資料_天母校區_XXX社/
├─ 1.社團行政_組織章程/
├─ 2.社團行政_管理運作/
├─ 3.社團行政_社團資料保存/
├─ 4.社團行政_年度計畫/
├─ 5.社團行政_財務管理/
├─ 6.社團活動_社團活動/
└─ 7.社團活動_服務學習/
```

評鑑 ZIP 主要放 PDF。ODF 原始檔另輸出備份 ZIP。

---

## 3. 網站頁面設計

### 3.1 Dashboard 儀表板

顯示：

1. 社團名稱、學年度、校區
2. 評鑑資料完整度
3. 七大項目完成率
4. 最近生成文件
5. 最近活動
6. 缺漏文件提醒
7. 系統建議補件

注意：顯示「資料完整度」，不要顯示「預測得分」。

### 3.2 Generate 文件生成

支援三種模式：

#### A. 自然語言生成

使用者輸入一句話或一段描述，系統判斷要生成的文件。

#### B. 選範本生成

使用者選擇範本：

- 會議紀錄
- 會議議程
- 活動企劃書
- 活動成果報告
- 年度計畫
- 收支帳冊
- 社團評鑑總目錄

#### C. 上傳資料生成

MVP 先支援 `.txt` 逐字稿上傳。音檔上傳先做 UI，顯示 Beta 提醒。

### 3.3 Files 文件庫

欄位：

- 文件名稱
- 類型
- 對應評鑑項目
- 狀態
- 版本
- 建立時間
- 修改時間
- 操作：查看、編輯、下載 ODF、下載 PDF、設為正式版

### 3.4 Projects 活動/專案

顯示活動卡：

- 活動名稱
- 活動日期
- 活動類型
- 文件完整度
- 歸檔狀態
- 相關文件列表

### 3.5 Evaluation 社團評鑑

功能：

1. 七大評鑑項目檢核
2. 缺漏文件清單
3. 評鑑資料夾預覽
4. 一鍵輸出 PDF ZIP
5. 一鍵輸出 ODF 原始檔備份 ZIP

### 3.6 Templates ODF 範本庫

三大類：

1. 日常行政型
2. 專案活動型
3. 社團評鑑型

每個範本顯示：

- 範本名稱
- 格式
- 適用情境
- 對應評鑑項目
- 下載按鈕
- 使用此範本生成文件

### 3.7 Settings 設定

設定：

- 社團名稱
- 學年度
- 校區
- 社團性質
- 社長姓名
- 指導老師
- 文件命名規則
- 是否啟用 AI 功能

---

## 4. 評鑑分類與權重

```python
EVALUATION_CATEGORIES = [
    "1.社團行政_組織章程",
    "2.社團行政_管理運作",
    "3.社團行政_社團資料保存",
    "4.社團行政_年度計畫",
    "5.社團行政_財務管理",
    "6.社團活動_社團活動",
    "7.社團活動_服務學習",
]

WEIGHTS = {
    "1.社團行政_組織章程": 5,
    "2.社團行政_管理運作": 10,
    "3.社團行政_社團資料保存": 10,
    "4.社團行政_年度計畫": 10,
    "5.社團行政_財務管理": 15,
    "6.社團活動_社團活動": 35,
    "7.社團活動_服務學習": 15,
}
```

---

## 5. 資料模型

請使用 SQLite。

### clubs

- id
- club_name
- campus
- academic_year
- club_type
- president_name
- advisor_name
- created_at
- updated_at

### documents

- id
- title
- document_type
- evaluation_category
- project_id
- status
- current_version
- created_at
- updated_at

### document_versions

- id
- document_id
- version_number
- content_json
- odf_path
- pdf_path
- created_at
- note

### projects

- id
- project_name
- project_type
- start_date
- end_date
- owner
- status
- created_at
- updated_at

### templates

- id
- template_name
- template_type
- file_format
- template_path
- evaluation_category
- description

### evaluation_items

- id
- category_code
- category_name
- weight
- required_documents_json

---

## 6. 檔案命名規則

```text
{民國年月日}_{社團名稱}_{文件類型}_{文件主題}_v{版本號}.{副檔名}
```

範例：

```text
1150624_學生會_會議紀錄_幹部會議_v1.odt
1150624_學生會_會議紀錄_幹部會議_v1.pdf
1151020_學生會_活動企劃書_電影節_v2.odt
```

---

## 7. ODF / PDF 產出策略

MVP 請先確保流程穩定：

1. 使用者輸入資料
2. 系統儲存 content_json
3. 系統根據 content_json 產生文件
4. 文件可下載
5. 文件可重新產生新版本

ODT 可以用 odfpy 或簡化模板實作。
PDF 可先使用 reportlab 或其他穩定套件輸出簡化版 PDF。

請在 README 說明目前 ODF/PDF 支援程度。

---

## 8. AI 功能設計

MVP 可先用 mock parser，不一定要真的串 OpenAI API。

請設計可替換架構：

- `ai/mock_parser.py`
- `ai/openai_parser.py`

自然語言輸入時，先抽取：

- document_type
- meeting_date
- meeting_name
- attendees
- chair
- recorder
- agenda_items
- decisions
- action_items
- project_name
- evaluation_category

若沒有 API key，使用 mock parser 產生示範資料。

---

## 9. 音檔轉會議紀錄

MVP 先建立 UI：

- 上傳音檔
- 顯示：「音檔轉逐字稿功能為 Beta，請先貼上逐字稿」
- 後續再串語音轉文字 API

請不要在 MVP 強制完成音檔功能。

---

## 10. 專案目錄結構

```text
SA_ODFlow/
├─ app.py
├─ pages/
│  ├─ 1_Dashboard.py
│  ├─ 2_Generate.py
│  ├─ 3_Files.py
│  ├─ 4_Projects.py
│  ├─ 5_Evaluation.py
│  ├─ 6_Templates.py
│  └─ 7_Settings.py
├─ core/
│  ├─ database.py
│  ├─ models.py
│  ├─ document_service.py
│  ├─ evaluation_service.py
│  ├─ export_service.py
│  ├─ template_service.py
│  └─ filename.py
├─ ai/
│  ├─ mock_parser.py
│  └─ openai_parser.py
├─ generators/
│  ├─ odt_generator.py
│  ├─ ods_generator.py
│  ├─ pdf_generator.py
│  └─ zip_generator.py
├─ templates/
│  ├─ daily_admin/
│  ├─ projects/
│  └─ evaluation/
├─ data/
│  ├─ odflow.sqlite3
│  └─ generated/
├─ docs/
│  ├─ product_spec.md
│  ├─ setup_guide.md
│  ├─ odf_optimization_suggestions.md
│  └─ ai_usage_statement.md
├─ tests/
├─ requirements.txt
├─ README.md
└─ .gitignore
```

---

## 11. Codex 開發任務拆分

### Task 1：建立專案骨架

請完成：

1. repo 目錄結構
2. requirements.txt
3. Streamlit 多頁面骨架
4. SQLite database 初始化
5. 七大社團評鑑項目常數
6. README 基礎版
7. docs/product_spec.md

不要先實作 AI API、音檔轉文字、Google Drive API。

完成後請開 PR，並在 PR 說明：

- 完成哪些檔案
- 如何本機執行
- 尚未完成事項

### Task 2：文件生成與文件庫

實作：

1. 逐字稿/文字輸入生成會議紀錄草稿
2. 文件儲存
3. 文件庫列表
4. 文件狀態
5. 版本管理

### Task 3：ODF/PDF 輸出

實作：

1. 會議紀錄 ODT 下載
2. 會議紀錄 PDF 下載
3. generators 模組
4. README 說明支援程度

### Task 4：評鑑儀表板

實作：

1. 七大項目資料完整度計算
2. 缺漏文件提醒
3. Dashboard 視覺化

### Task 5：評鑑上傳包

實作：

1. 一鍵輸出社團評鑑 PDF ZIP
2. 七大資料夾格式
3. ODF 原始檔備份 ZIP

---

## 12. 本機執行方式

預期安裝：

```bash
pip install -r requirements.txt
streamlit run app.py
```

如果失敗，請修正錯誤並更新 README。

---

## 13. README 必須包含

1. 專案介紹
2. 功能特色
3. 安裝方式
4. 啟動方式
5. 使用流程
6. 範例輸入
7. 範例輸出
8. ODF/PDF 支援說明
9. AI 使用聲明
10. 後續開發計畫
11. 比賽成果說明

---

## 14. 開發注意事項

1. 每完成一階段請 commit。
2. 不要把 API key 寫進 repo。
3. 不要要求使用者提供 GitHub 密碼。
4. 不要在 MVP 做超出範圍的功能。
5. 若功能暫時無法完成，請建立 TODO 與清楚的後續計畫。
6. 優先保證使用者可以跑起來。

