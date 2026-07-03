# UI_SPEC_v14_ODFlow_templates_generate

## 修正範圍

本版基於 v13，不再修改首頁與儀表板，只修兩個區塊：

1. 空白範本頁搜尋 / 分類 / 格式 / 使用情境 / 清除篩選可以使用。
2. 生成文件頁 stepper 跑版修正。

## 1. 空白範本頁

### 搜尋與篩選列

改為 HTML GET form：

- `q`：搜尋範本名稱、用途、分類、格式
- `cat`：分類
  - 全部範本
  - 日常行政
  - 專案活動
  - 財務核銷
  - 評鑑資料
- `fmt_filter`：格式
  - 全部格式
  - ODT
  - ODS
- `usage`：使用情境
  - 全部用途
  - 日常行政
  - 專案活動
  - 財務核銷
  - 評鑑資料
- 套用篩選：送出 GET query
- 清除篩選：回到 `/?page=Templates`

### 分類 Tabs

分類 Tabs 保留原本視覺，但會帶入目前搜尋與格式條件。

## 2. 生成文件頁

### Stepper

修正原本線條穿過文字的問題：

- label 改成 `.odf-step-label`
- stepper 改成 4 欄 grid
- 連線不再使用絕對定位跨過文字
- 連線改成 step item 第三欄
- 窄螢幕自動變成 2 欄

### 主內容

- Step 1 / Step 2 / Step 3 改用 `.odf-generate-shell`
- 避免固定高度導致上方 stepper 與內容互壓
- 保持左側範本摘要 + 右側內容卡的結構

## 不變

- 首頁不動
- 儀表板不動
- 檔案庫不動
- 社團設定不動
- ODT / ODS 後端生成邏輯不動
