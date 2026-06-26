# Template-Based Rendering 規格

## 1. 為什麼加入 template-based rendering

Task 14 的 generator 已經可以產出 ODT / PDF / ODS，也已比早期 MVP 更正式。但對三個最常展示、最常使用的核心文件來說，若完全由程式從零組版，版型仍容易帶有明顯的程式生成感，和真實校園社團文件常見的排版習慣仍有落差。

Task 15 因此補上 template-based rendering。做法是先準備乾淨、可公開的 ODT placeholder 樣板，再把 `content_json` 轉成對應 context 後填入。這樣可以更穩定保留文件標題、表格、欄位順序與校園行政文件感，同時維持 ODF 原始檔可編輯、可保存、可交接的特性。

## 2. 三個核心文件

目前 template-based rendering 優先支援三個核心文件：

- 會議紀錄
- 開會通知單
- 活動企劃書

這三種文件在 ODFlow 內屬於展示頻率最高、最容易被評審直接看到版型品質的文件，因此先升級為樣板填入路線。

## 3. 資料流程

目前資料流程如下：

`content_json`
→ `context mapping`
→ `ODT placeholder template`
→ `rendered ODT`
→ `fallback generator`

說明：

- `content_json` 是文件內容來源
- `context mapping` 會把內容轉成樣板需要的 placeholder key/value
- `ODT placeholder template` 是 repo 內保存的乾淨 ODT 樣板
- `rendered ODT` 是實際輸出的 ODF 原始檔
- 若樣板填入失敗，會 fallback 到既有 generator，避免匯出整體失敗

## 4. placeholder 原則

目前 placeholder 規則如下：

- placeholder 使用 `{{field_name}}`
- placeholder 應盡量避免被 ODT XML 拆成多段，否則會增加取代失敗風險
- 空值不得輸出 `None`、`[]` 或 Python list repr
- list / table-like 欄位目前先展開成可讀文字
- 未來可再擴充真正的 table row clone，讓多列資料能直接保留表格列結構

## 5. 樣板檔案原則

repo 內的 ODT 樣板必須符合以下原則：

- 只放乾淨、可公開、無個資的 ODT 樣板
- 不放使用者原始 docx / pdf / zip
- 不放真實會議紀錄、真實通知單、真實活動企劃書
- 不放電話、學號、email、簽名、帳戶資料
- 不加入字型檔

樣板是結構參考，不是實際使用者文件。

## 6. fallback 策略

目前 fallback 規則如下：

- 三核心文件的 ODT 匯出優先使用 template renderer
- 若 template renderer 失敗，回到 Task 14 的 generator
- 其他文件類型仍沿用 Task 14 generator

這樣做的目的是在提升版型品質的同時，不破壞既有匯出穩定性。

## 7. PDF 現況與限制

目前 PDF 仍沿用 Task 14 的 PDF generator，因此：

- PDF 不一定與 ODT 樣板版型完全一致
- PDF 內容仍會完整，但欄位排法與正式樣板可能略有差異

未來若需要讓 PDF 盡量與 ODT 樣板一致，可再評估 LibreOffice 的 ODT → PDF conversion 流程。

## 8. 未來擴充方向

後續可優先擴充的 template-based rendering 文件包含：

- 活動成果報告
- 會議議程
- 活動檢討會紀錄
- 年度計畫
- 出席簽到表
- 真正的 table row clone

目前空白範本頁提供的是版型近似預覽，實際格式以下載 ODT / ODS 為準。對三個核心文件來說，下載的已經是正式 ODT placeholder 樣板，而不是 metadata 型說明頁。
