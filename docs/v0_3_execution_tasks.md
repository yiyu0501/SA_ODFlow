# ODFlow v0.3 執行任務拆分

## 拆分原則

v0.3 不再把工作拆得太碎，避免消耗過多 Codex 迭代在切任務與回補上下文。

本版建議只拆成兩個大任務：

1. Task 13：介面與互動體驗升級
2. Task 14：核心範本品質升級

---

## Task 13：介面與互動體驗升級

### 目標

把目前偏工程感的展示流程整理成更容易理解的中文化產品介面，但不做大型 UI 重構、不改資料庫 schema、不改核心功能流程。

### 內容範圍

1. 中文側邊欄
2. 首頁流程卡與主線導覽
3. Dashboard 視覺化
4. 社團評鑑 ZIP 匯出摘要與預覽
5. Templates 頁 UX 改版
6. 空白範本直接下載入口優化
7. Projects 頁標示未來擴充

### 不包含

1. OpenAI API
2. 音檔轉文字
3. Google Drive
4. Projects 完整專案管理
5. ODT / PDF 產生器重寫

### 驗收重點

1. 側邊欄與頁面名稱全面中文化
2. 首頁能清楚說明主要流程
3. Dashboard 更容易看出社團評鑑資料完整度
4. 社團評鑑頁匯出前後摘要更清楚
5. Templates 頁可清楚分辨下載空白範本與建立文件
6. Projects 頁不再誤導為已完成主功能

### 可直接交給 Codex 的 prompt 草稿

```md
請閱讀 README.md、docs/v0_3_product_upgrade_plan.md、docs/v0_3_sidebar_and_page_naming.md、pages、core/evaluation_service.py 與目前 Streamlit App 結構，開始執行 Task 13。

請建立新的 branch：
task13-ui-and-ux-upgrade

這次只做介面與互動體驗升級，不要修改資料庫 schema，不要重寫核心服務，不要做 OpenAI API、音檔轉文字、Google Drive、登入系統、多使用者權限，也不要做 Projects 完整專案管理。

Task 13 目標：
1. 側邊欄中文化
2. 首頁流程卡
3. Dashboard 視覺化
4. 社團評鑑 ZIP 匯出摘要與預覽
5. Templates 頁 UX 改版
6. 空白範本直接下載入口優化
7. Projects 標示未來擴充

請先以目前 origin/main 為基底，不要重做既有功能。
完成後請跑測試、compileall、streamlit 啟動檢查並建立 PR。
```

---

## Task 14：核心範本品質升級

### 目標

把核心範本與核心輸出文件提升到更接近正式校園社團文件的品質，同時維持目前 ODF / PDF / ZIP 流程相容。

### 內容範圍

1. 會議紀錄 ODT
2. 會議通知 ODT
3. 會議議程 ODT
4. 活動企劃書 ODT
5. 活動成果報告 ODT
6. 活動檢討會紀錄 ODT
7. 年度計畫 ODT
8. 出席簽到表 ODS
9. 其餘範本標準化
10. 標楷體 / 12pt / A4 / 表格線清楚

### 不包含

1. 全部 22 個範本逐一做到高保真美編
2. 新增更多文件類型
3. 重構 document schema
4. 引入新的雲端或 AI 依賴

### 驗收重點

1. 核心範本可正常開啟
2. 核心文件格式更接近正式校園社團文件
3. 內文、標題、表格規則一致
4. ODT / ODS 與既有 PDF 匯出流程相容
5. 既有五種文件生成與評鑑 ZIP 流程不被破壞

### 可直接交給 Codex 的 prompt 草稿

```md
請閱讀 README.md、docs/v0_3_product_upgrade_plan.md、docs/v0_3_template_quality_spec.md、core/template_service.py、core/document_schemas.py、generators/odt_generator.py、generators/ods_generator.py、generators/pdf_generator.py、pages/2_Generate.py、pages/6_Templates.py，開始執行 Task 14。

請建立新的 branch：
task14-core-template-quality-upgrade

這次只做核心範本品質升級，不要修改資料庫 schema，不要做 OpenAI API、音檔轉文字、Google Drive、登入系統、多使用者權限，也不要做 Projects 完整專案管理。

Task 14 目標：
1. 精修核心 ODT / ODS 範本格式
2. 讓核心文件輸出更接近台灣校園正式文件
3. 維持現有 ODF / PDF / ZIP 流程相容

請以標楷體、12pt、A4、標題置中、表格線清楚為基本規格。
完成後請跑測試、compileall、streamlit 啟動檢查並建立 PR。
```

---

## 建議執行順序

建議先做 Task 13，再做 Task 14。

原因：

1. 先把展示動線整理好，能先提升評審理解度
2. 再投入核心範本精修，效果會更集中
3. 若先做範本品質，UI 入口仍混亂，展示效果會被吃掉
