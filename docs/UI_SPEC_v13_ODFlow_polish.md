# UI_SPEC_v13_ODFlow_polish

## 修正範圍

本版基於 v12 可用版本，先修使用者回報的下一批可用性問題。

## 1. 社團設定頁

新增正式 `render_settings()`：

- 社團基本資料
  - 社團名稱
  - 社團類型
  - 社長 / 負責人
  - 指導老師
- 年度與校區
  - 學年度
  - 校區
  - 切換社團提示
- 文件狀態
  - 全部文件
  - 草稿
  - 待確認
  - 已完成
- 工作台偏好
- 快速操作

目前為設定總覽展示，尚未接可編輯 form；後續可接 `save_club_settings()`。

## 2. 右上角按鈕

右上角三個入口可點擊：

- 問號：使用說明 drawer
- 鈴鐺：通知中心 drawer
- 使用者：社團小幫手 / 社團資訊 drawer

Drawer 使用 query param `panel=help|notifications|profile`，不開新分頁。

## 3. 同頁切換與過渡

- 主要導覽改成 root app query router：
  - `/?page=Dashboard`
  - `/?page=Templates`
  - `/?page=Generate`
  - `/?page=Files`
  - `/?page=Settings`
- 避免 Streamlit multipage direct path 造成較重的切換感。
- 保留 `target="_self"`，不開新分頁。
- 保持 light background，降低切換時黑屏感知。

## 4. 資料動態化

首頁、儀表板、檔案庫改讀目前資料：

- `get_club_settings()`
- `list_documents()`
- `get_evaluation_summary()`
- `list_template_definitions()`

若無資料：

- 顯示 0
- 顯示 empty state
- 不再硬塞「4 個專案」「6 份文件」「較上週增加」等假數字。

## 5. 空白範本分類

空白範本分類可點擊：

- 全部範本
- 日常行政
- 專案活動
- 財務核銷
- 評鑑資料

透過 `cat` query param 篩選，並維持同頁切換。
