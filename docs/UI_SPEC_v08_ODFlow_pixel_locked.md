# UI_SPEC_v08_ODFlow_pixel_locked

本版的唯一目標：讓 Streamlit 介面盡量貼近 `ODF網頁.zip` 內的九張參考圖，不再採用「大概像」的彈性排版。

## 0. 基準畫布

- 參考圖尺寸：1672 × 941 px。
- 桌機優先，不再為小螢幕犧牲桌機版精準度。
- App Shell 採固定寬度像素基準：
  - Sidebar：304px
  - Topbar：68px
  - Main content：1304px 固定寬
  - 主內容置中於 sidebar 右側剩餘空間
  - 主內容上方 padding：39px
  - 區塊間距：16 / 18 / 20 / 24 / 28 px
- 原生 Streamlit header/sidebar/toolbar 全部隱藏。
- 不使用 Streamlit 原生 sidebar；全部改為自訂 HTML/CSS。

## 1. 全站視覺 token

### 色彩
- Background：#F7FAFF
- Card：#FFFFFF
- Border：#E5EDF7
- Text：#0F172A
- Muted：#64748B
- Primary Blue：#1D6BFF
- Green：#16A34A
- Purple：#6D4CFF
- Coral：#FF5A7A
- Coral Dark：#EF476F

### 圓角
- Main cards：16px
- Buttons：10px
- Pills：999px
- Sidebar nav：11px

### 陰影
- Card shadow：0 8px 18px rgba(15, 23, 42, 0.045)
- Strong card shadow：0 12px 28px rgba(15, 23, 42, 0.055)

## 2. Sidebar 規格

- 寬度：304px
- 高度：100vh
- overflow：hidden，不准 sidebar 內部捲動
- padding：26px 22px 20px 22px
- Logo 區：
  - 高度 58px
  - icon 50px
  - title 25px / 900
  - subtitle 13px / 650
- Nav group：
  - group margin-bottom 26px
  - heading 14px / 850
  - nav item 高度 42px
  - item margin-bottom 6px
  - item padding 0 14px
- Bottom club card：
  - min-height 136px
  - padding 18px
  - 以 flex spacer 固定落在 sidebar 下方
- 「前往服務中心」放在 club card 下方，維持 44px 高度。
- 不顯示「舊版中心」。

## 3. Topbar 規格

- 高度：68px
- 靠右顯示：問號、鈴鐺、使用者 pill
- 圓形 icon 42px
- 使用者 pill 高度 42px
- 背景：rgba(255,255,255,.78)
- bottom border：#E7EDF4 78%

## 4. 首頁規格

### Page Header
- eyebrow：ODFLOW WORKBENCH
- H1：首頁，40px / 920
- desc：16px / 650

### 第一列
- grid：744px + 540px，gap 20px
- Hero card：
  - 高度 262px
  - padding 28px 32px
  - grid：190px + 1fr
  - 插圖 160px
  - 標題 22px
  - 說明 15px，line-height 1.7
  - 統計卡 4 欄，不准文字直排
  - 統計卡高度 74px
- 評鑑準備度卡：
  - 高度 262px
  - padding 22px 28px 24px
  - ring 132px
  - ring 使用真實百分比，0% 不顯示假進度
  - 狀態 pill 高度 40px
  - CTA 高度 46px
  - accent 使用 coral，不使用藍色

### 第二列：快速開始
- 三欄，每張 card 高度 168px
- 卡片 grid：88px + 1fr
- icon 72px
- button 44px

### 第三列
- grid：330px 330px 270px 270px，gap 14px
- 每張卡 min-height 230px
- 包含：常用範本、檔案庫快捷入口、評鑑提醒、第一次使用建議

## 5. 儀表板

- 第一列 KPI：4 欄，每張 124px
- 第二列：專案進度總覽 + 缺件待補清單
- 第三列：最近文件 + 工作提醒 + 快捷操作/本週摘要
- 不使用範本使用排行、文件分布圓餅圖。

## 6. 空白範本

- 搜尋列：5 欄
- 分類 tabs 高度 88px
- 提示 banner 高度 104px
- 範本 grid：4 欄
- 每張卡高度 206px
- 不出現本週 / 本月 / 本學期。

## 7. 生成文件

- 4-step wizard：
  1. 選擇範本
  2. 填寫資料
  3. 預覽確認
  4. 下載文件
- Step 4 根據 query params 的 `fmt` 判斷：
  - ODT：下載 ODT / 下載 PDF / 前往檔案庫
  - ODS：下載 ODS / 下載 PDF / 前往檔案庫
- 不顯示 ZIP。
- 不顯示「下一步您可以」。

## 8. 檔案庫

- 搜尋/篩選列：6 欄
- KPI：4 張
- 主內容：左分類 250px + 右表格
- 表格列高 58px
- 列表為主，不做卡片牆。

## 9. 驗收標準

- 首頁 hero 統計卡不可直排。
- 首頁評鑑卡狀態 pill 不可互壓。
- Sidebar 不可捲動。
- Sidebar 所有 nav item 可於 941px 高度內完整看到。
- 主內容第一屏接近參考圖比例。
- 所有 card 文字與 icon 不得重疊。
- 文字塞不下時，卡片加高或欄寬固定，不得壓縮成直排。
