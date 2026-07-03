# UI_SPEC_v10_ODFlow_bugfix

## 修正範圍

本版只修 v09 使用者回報的四個 bug：

1. 首頁「快速開始」三張卡片按鈕被切掉 / 跑版。
2. 空白範本卡片按鈕被切掉 / 右側溢出。
3. 生成文件 Step 1 範本卡片按鈕被切掉 / 版面壓縮。
4. 自訂 HTML 導覽連結必須在同一個瀏覽器分頁內切換，不得開新分頁。

## 版面規格

### 首頁快速開始
- Action card 從固定 168px 改為 min-height 208px。
- Button 固定 46px。
- Card 內容區與按鈕區分開，避免按鈕被裁切。
- Card 不再使用 overflow hidden 裁切內容。

### 空白範本
- Template card 改用 `.odf-template-card`。
- Template card min-height 226px。
- 按鈕列改為 2 欄 grid，兩個按鈕各佔 1fr。
- 按鈕 width 100%、min-width 0，避免右側超出。

### 生成文件
- Step 1 template card 改用 `.odf-generate-template-card`。
- Card min-height 190px。
- 外層高度由 `height:600px` 改為 `min-height:640px`。
- 內容不足時可自然增高，不裁切。

### 導覽
- 所有 `<a>` 連結會自動補上 `target="_self"`。
- 確保首頁、儀表板、空白範本、生成文件、檔案庫等連結在同一分頁切換。
