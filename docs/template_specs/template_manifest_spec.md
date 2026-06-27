# ODFlow 範本總索引規格書

## 一、文件目的

本文件定義 ODFlow 所有正式範本的總索引、分類、顯示順序、template key、檔案格式、重要性、是否支援空白範本下載、是否支援使用此範本建立文件，以及未來實作時應遵守的共通規則。

本文件不是使用者下載的 ODT 或 ODS 範本。
本文件是給開發者與 Codex 實作用的總控規格。

本文件的目的：

1. 統一所有範本的命名。
2. 統一所有範本的分類。
3. 統一所有範本的 `template_key`。
4. 統一空白範本中心顯示順序。
5. 統一 ODT / ODS 格式判斷。
6. 避免範本卡片顯示錯誤。
7. 避免生成文件頁找不到對應 renderer。
8. 避免正式文件本體出現 metadata 型文字。
9. 作為 Codex 實作所有範本時的總索引。

---

## 二、整體範本定位

ODFlow 是學生社團的 ODF 文件工作台與評鑑整理系統。

本系統範本分為四大類：

1. 日常行政型
2. 專案活動型
3. 社團運作型
4. 財務與清冊型

所有範本都應符合以下原則：

1. 文件打開後應像真的社團文件。
2. 不得是 metadata 說明頁。
3. 不得在正式 ODT / ODS 本體出現「範本類型、建議格式、對應評鑑分類、使用情境、使用說明」等文字。
4. 不得在正式 ODT / ODS 本體出現網頁 UI 操作文字。
5. 空白範本與生成文件應分開處理。
6. ODT 適合正式文字文件。
7. ODS 適合表格、清冊、財務與可計算資料。
8. 不得把字型檔 commit 進 repo。
9. ODT / ODS / PDF 匯出功能不得被破壞。

---

## 三、範本總數

目前正式範本總數為 22 份。

原本「經費收支表／經費收支結算表」在概念上容易混淆，因此正式拆成兩份：

1. 經費收支表：社團日常帳本。
2. 經費收支結算表：單一活動結束後的活動結算表。

因此本系統目前正式管理 22 份範本。

---

## 四、範本分類總覽

### 1. 日常行政型

| 顯示名稱    | template key      | 格式  | 重要性 |
| ------- | ----------------- | --- | --- |
| 會議紀錄    | meeting_minutes   | ODT | 最高  |
| 開會通知單   | meeting_notice    | ODT | 高   |
| 會議議程    | meeting_agenda    | ODT | 高   |
| 簽到表     | attendance_sheet  | ODT | 高   |
| 社團公告／通知 | club_announcement | ODT | 中高  |

---

### 2. 專案活動型

| 顯示名稱    | template key            | 格式  | 重要性 |
| ------- | ----------------------- | --- | --- |
| 活動企畫書   | activity_proposal       | ODT | 最高  |
| 活動申請表   | activity_application    | ODT | 最高  |
| 活動成果報告  | activity_result_report  | ODT | 最高  |
| 活動檢討會紀錄 | activity_review_minutes | ODT | 高   |
| 活動流程表   | activity_schedule       | ODS | 中   |
| 工作分配表   | work_assignment         | ODS | 高   |

---

### 3. 社團運作型

| 顯示名稱   | template key               | 格式  | 重要性 |
| ------ | -------------------------- | --- | --- |
| 年度計畫   | annual_plan                | ODT | 高   |
| 社團幹部名冊 | officer_roster             | ODS | 高   |
| 社員名冊   | member_roster              | ODS | 高   |
| 社課紀錄   | course_record              | ODT | 高   |
| 器材借用紀錄 | equipment_borrowing_record | ODS | 中高  |

---

### 4. 財務與清冊型

| 顯示名稱    | template key             | 格式  | 重要性 |
| ------- | ------------------------ | --- | --- |
| 經費預算表   | expense_budget           | ODS | 高   |
| 經費收支表   | income_expense_statement | ODS | 最高  |
| 經費收支結算表 | expense_settlement       | ODS | 最高  |
| 核銷明細表   | reimbursement_detail     | ODS | 高   |
| 財產清冊    | inventory                | ODS | 高   |
| 補助申請表   | subsidy_application      | ODT | 高   |

---

## 五、空白範本中心顯示順序

空白範本中心建議依以下順序呈現。

### 1. 日常行政型

1. 會議紀錄
2. 開會通知單
3. 會議議程
4. 簽到表
5. 社團公告／通知

### 2. 專案活動型

1. 活動企畫書
2. 活動申請表
3. 活動成果報告
4. 活動檢討會紀錄
5. 活動流程表
6. 工作分配表

### 3. 社團運作型

1. 年度計畫
2. 社團幹部名冊
3. 社員名冊
4. 社課紀錄
5. 器材借用紀錄

### 4. 財務與清冊型

1. 經費預算表
2. 經費收支表
3. 經費收支結算表
4. 核銷明細表
5. 財產清冊
6. 補助申請表

---

## 六、實作優先順序

若 Codex 分階段實作，建議依以下順序處理。

### 第一階段：最核心活動與財務文件

優先原因：最常用，也最能展示 ODFlow 價值。

1. 活動企畫書
2. 活動申請表
3. 活動成果報告
4. 經費收支表
5. 經費收支結算表
6. 簽到表
7. 會議紀錄

---

### 第二階段：活動執行文件

優先原因：補足活動前、中、後流程。

1. 活動流程表
2. 工作分配表
3. 活動檢討會紀錄
4. 經費預算表
5. 核銷明細表

---

### 第三階段：社團運作文件

優先原因：支援社團長期營運與評鑑。

1. 年度計畫
2. 社團幹部名冊
3. 社員名冊
4. 社課紀錄
5. 器材借用紀錄
6. 財產清冊

---

### 第四階段：行政補強文件

優先原因：補完整體文件鏈。

1. 開會通知單
2. 會議議程
3. 社團公告／通知
4. 補助申請表

---

## 七、範本 metadata 欄位規格

每一份範本都應在程式層有統一 metadata。

建議欄位如下：

| 欄位                         | 說明            |
| -------------------------- | ------------- |
| template_key               | 系統內部唯一識別碼     |
| display_name               | 使用者看到的範本名稱    |
| aliases                    | 常見別名          |
| category                   | 四大分類之一        |
| format                     | ODT 或 ODS     |
| priority                   | 重要性           |
| supports_blank_download    | 是否支援空白範本下載    |
| supports_generate_document | 是否支援使用此範本建立文件 |
| spec_path                  | 對應規格書路徑       |
| blank_template_path        | 空白範本檔案路徑      |
| renderer                   | 生成文件 renderer |
| preview_type               | 空白範本中心預覽類型    |
| forbidden_body_text        | 正式文件本體禁止出現的文字 |

---

## 八、template key 對照表

| template key               | 顯示名稱    | 規格書路徑                                                  |
| -------------------------- | ------- | ------------------------------------------------------ |
| meeting_minutes            | 會議紀錄    | docs/template_specs/meeting_minutes_spec.md            |
| meeting_notice             | 開會通知單   | docs/template_specs/meeting_notice_spec.md             |
| meeting_agenda             | 會議議程    | docs/template_specs/meeting_agenda_spec.md             |
| attendance_sheet           | 簽到表     | docs/template_specs/attendance_sheet_spec.md           |
| club_announcement          | 社團公告／通知 | docs/template_specs/club_announcement_spec.md          |
| activity_proposal          | 活動企畫書   | docs/template_specs/activity_proposal_spec.md          |
| activity_application       | 活動申請表   | docs/template_specs/activity_application_spec.md       |
| activity_result_report     | 活動成果報告  | docs/template_specs/activity_result_report_spec.md     |
| activity_review_minutes    | 活動檢討會紀錄 | docs/template_specs/activity_review_minutes_spec.md    |
| activity_schedule          | 活動流程表   | docs/template_specs/activity_schedule_spec.md          |
| work_assignment            | 工作分配表   | docs/template_specs/work_assignment_spec.md            |
| annual_plan                | 年度計畫    | docs/template_specs/annual_plan_spec.md                |
| officer_roster             | 社團幹部名冊  | docs/template_specs/officer_roster_spec.md             |
| member_roster              | 社員名冊    | docs/template_specs/member_roster_spec.md              |
| course_record              | 社課紀錄    | docs/template_specs/course_record_spec.md              |
| equipment_borrowing_record | 器材借用紀錄  | docs/template_specs/equipment_borrowing_record_spec.md |
| expense_budget             | 經費預算表   | docs/template_specs/expense_budget_spec.md             |
| income_expense_statement   | 經費收支表   | docs/template_specs/income_expense_statement_spec.md   |
| expense_settlement         | 經費收支結算表 | docs/template_specs/expense_settlement_spec.md         |
| reimbursement_detail       | 核銷明細表   | docs/template_specs/reimbursement_detail_spec.md       |
| inventory                  | 財產清冊    | docs/template_specs/inventory_spec.md                  |
| subsidy_application        | 補助申請表   | docs/template_specs/subsidy_application_spec.md        |

---

## 九、建議程式資料結構

可建立一個集中管理的 template registry。

建議資料結構如下：

```json
{
  "templates": [
    {
      "template_key": "meeting_minutes",
      "display_name": "會議紀錄",
      "aliases": ["會議記錄"],
      "category": "日常行政型",
      "format": "ODT",
      "priority": "最高",
      "supports_blank_download": true,
      "supports_generate_document": true,
      "spec_path": "docs/template_specs/meeting_minutes_spec.md",
      "blank_template_path": "templates/odt/meeting_minutes.odt",
      "renderer": "render_meeting_minutes",
      "preview_type": "odt_preview"
    }
  ]
}
```

實作時不一定要使用 JSON 檔，也可以使用 Python dict、YAML 或其他結構，但所有範本的欄位應保持一致。

---

## 十、檔案命名規則

### 1. 規格書命名

格式：

```text
docs/template_specs/{template_key}_spec.md
```

範例：

```text
docs/template_specs/activity_proposal_spec.md
```

---

### 2. ODT 空白範本命名

格式：

```text
templates/odt/{template_key}.odt
```

範例：

```text
templates/odt/activity_proposal.odt
```

---

### 3. ODS 空白範本命名

格式：

```text
templates/ods/{template_key}.ods
```

範例：

```text
templates/ods/income_expense_statement.ods
```

---

### 4. Renderer 命名

格式：

```text
render_{template_key}
```

範例：

```text
render_activity_proposal
render_income_expense_statement
```

---

## 十一、ODT / ODS 判斷原則

### 1. 使用 ODT 的範本

適合條件：

1. 正式文字文件。
2. 章節式內容。
3. 需要段落、表格、簽核欄、附件清單。
4. 不以公式計算為核心。

目前 ODT 範本：

* 會議紀錄
* 開會通知單
* 會議議程
* 簽到表
* 社團公告／通知
* 活動企畫書
* 活動申請表
* 活動成果報告
* 活動檢討會紀錄
* 年度計畫
* 社課紀錄
* 補助申請表

---

### 2. 使用 ODS 的範本

適合條件：

1. 表格型資料。
2. 需要公式。
3. 需要下拉選單。
4. 需要篩選或排序。
5. 需要金額、數量、統計摘要。

目前 ODS 範本：

* 活動流程表
* 工作分配表
* 社團幹部名冊
* 社員名冊
* 器材借用紀錄
* 經費預算表
* 經費收支表
* 經費收支結算表
* 核銷明細表
* 財產清冊

---

## 十二、空白範本下載共通規則

所有空白範本下載都應符合以下規則：

1. 下載後的檔案應是正式文件。
2. 不得是 metadata 說明頁。
3. 不得只列出欄位名稱與系統資訊。
4. 應能讓社團直接打開填寫。
5. 應可匯出 PDF。
6. ODS 應保留公式、下拉選單與欄寬。
7. ODT 應保留標題、章節、表格與頁尾。
8. 不得出現系統操作文字。
9. 不得出現開發者說明。
10. 不得嵌入字型檔。

---

## 十三、正式文件本體禁止文字

所有正式 ODT / ODS 文件本體不得出現以下文字：

* 範本類型
* 建議格式
* 對應評鑑分類
* 使用情境
* 使用說明
* 系統自動化說明
* 專案管理說明
* 新增項目
* 匯入資料
* 自動排序
* 自動產生評鑑 ZIP
* 生成文件頁
* template key
* metadata
* renderer

這些文字可以出現在：

1. 規格書。
2. ODFlow 網頁說明。
3. 範本卡片描述。
4. 生成文件頁 UI。
5. 開發文件。

但不能出現在正式下載的 ODT / ODS 文件本體。

---

## 十四、空白範本中心卡片欄位

空白範本中心每張卡片建議顯示以下資訊：

| 欄位        | 說明           |
| --------- | ------------ |
| 範本名稱      | 使用者看到的名稱     |
| 分類        | 四大分類之一       |
| 格式        | ODT 或 ODS    |
| 簡短說明      | 一句話說明用途      |
| 下載空白範本    | 下載 ODT / ODS |
| 使用此範本建立文件 | 進入生成文件頁      |

卡片上可以出現用途說明，但下載的正式文件本體不得出現用途說明。

---

## 十五、範本卡片簡短說明

建議卡片簡短說明如下。

### 日常行政型

| 範本      | 卡片說明                  |
| ------- | --------------------- |
| 會議紀錄    | 記錄會議報告、討論事項、決議與表決結果。  |
| 開會通知單   | 發送正式會議時間、地點、出席者與附件通知。 |
| 會議議程    | 安排會議流程、報告事項與討論事項。     |
| 簽到表     | 提供活動、社課或會議現場簽到使用。     |
| 社團公告／通知 | 發布一般社團公告、活動提醒與行政通知。   |

### 專案活動型

| 範本      | 卡片說明                  |
| ------- | --------------------- |
| 活動企畫書   | 撰寫活動宗旨、內容、流程、分工與預算。   |
| 活動申請表   | 依學校格式整理活動申請與行政審核資料。   |
| 活動成果報告  | 整理活動紀錄、工作人員、心得與照片成果。  |
| 活動檢討會紀錄 | 記錄活動後檢討、改善建議與後續追蹤事項。  |
| 活動流程表   | 安排活動粗流、細流、器材與現場負責人。   |
| 工作分配表   | 追蹤活動前中後工作項目、負責人與完成狀態。 |

### 社團運作型

| 範本     | 卡片說明                   |
| ------ | ---------------------- |
| 年度計畫   | 規劃社團年度目標、活動、社課、分工與預算。  |
| 社團幹部名冊 | 整理幹部職稱、組別、聯絡方式與交接狀態。   |
| 社員名冊   | 管理社員資料、社員狀態、社費狀態與聯絡方式。 |
| 社課紀錄   | 記錄社課內容、出席情形、成果與後續追蹤。   |
| 器材借用紀錄 | 追蹤器材借出、歸還、逾期、損壞與遺失狀態。  |

### 財務與清冊型

| 範本      | 卡片說明                      |
| ------- | ------------------------- |
| 經費預算表   | 編列活動前預算、補助金額、自籌金額與總經費。    |
| 經費收支表   | 記錄社團日常收入、支出、餘額、代墊與活動結算狀態。 |
| 經費收支結算表 | 整理單一活動預算通過金額、實際支出與補助核銷。   |
| 核銷明細表   | 整理單據、發票、付款方式、墊付款人與憑證狀態。   |
| 財產清冊    | 管理社團財產、器材、數量、狀態、保管人與盤點結果。 |
| 補助申請表   | 整理補助申請原因、經費需求、預期效益與附件。    |

---

## 十六、生成文件頁共通規則

「使用此範本建立文件」應符合以下原則：

1. 表單欄位應依各規格書定義。
2. 使用者可新增多筆資料。
3. 使用者可刪除多筆資料。
4. 使用者可複製上一筆資料。
5. ODS 類範本應保留公式與下拉選單。
6. ODT 類範本應保留正式文件版面。
7. 生成結果應可下載。
8. 生成結果不應出現系統 UI 文字。
9. 若資料不足，空白欄位應保留可填寫空間。
10. 若使用者未填附件，附件欄應顯示「無」。

---

## 十七、未來評鑑 ZIP 串接規則

未來評鑑 ZIP 匯出時，應可依範本分類整理檔案。

建議 ZIP 目錄：

```text
評鑑資料/
├── 01_日常行政/
├── 02_專案活動/
├── 03_社團運作/
└── 04_財務與清冊/
```

每份文件可依 template category 放入對應資料夾。

若同一文件對應多個評鑑分類，v1 建議只放主要分類，避免檔案重複。

---

## 十八、實作驗收標準

完成 template manifest 後，應符合以下驗收標準：

1. 所有正式範本都有唯一 template key。
2. 所有正式範本都有 display name。
3. 所有正式範本都有 category。
4. 所有正式範本都有 format。
5. 所有正式範本都有 spec path。
6. 所有正式範本都可被空白範本中心讀取。
7. 所有正式範本都可依分類顯示。
8. 所有正式範本都可依指定順序排序。
9. ODT / ODS 類型不可混淆。
10. 空白範本下載按鈕應指向正確檔案。
11. 使用此範本建立文件應指向正確 renderer。
12. 範本卡片說明可以出現在 UI，但不得出現在正式文件本體。
13. 禁止文字規則應套用到所有正式文件本體。
14. 不得把字型檔 commit 進 repo。
15. 不得破壞既有 ODT / ODS / PDF 匯出功能。

---

## 十九、優先級與原因

優先級：最高

原因：

1. 目前範本數量已經增加到 22 份。
2. 若沒有總索引，Codex 很容易把 template key、分類、格式與檔案路徑寫亂。
3. 總索引可以作為空白範本中心的資料來源。
4. 總索引可以作為生成文件頁的路由來源。
5. 總索引可以作為評鑑 ZIP 分類依據。
6. 總索引可以避免 ODT / ODS 範本混淆。
7. 總索引可以讓後續實作更穩定、更容易測試。
