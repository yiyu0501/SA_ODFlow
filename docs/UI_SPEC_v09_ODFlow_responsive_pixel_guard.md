# UI_SPEC_v09_ODFlow_responsive_pixel_guard

本版建立在 v08 的像素鎖定基礎上，但修正「固定 1304px 主內容造成水平捲動」的問題。

## 0. 核心修正

- 不允許水平捲動。
- `html`, `body`, `.stApp`, `.odf-main` 全部 `overflow-x: hidden`。
- Sidebar 仍以參考圖為基準，但寬度改為彈性：
  - `clamp(272px, 18.2vw, 304px)`
- Main content 不再使用 `min-width: 1304px`。
- Main content 改為：
  - `width: min(1304px, calc(100vw - sidebar - 56px))`
  - `min-width: 0`
- 卡片不再硬擠出右側畫面。
- 若視窗不足，內容縮小或增加垂直高度，不產生左右滑動。

## 1. 首頁

### 第一列
- Top row 改為彈性比例：
  - Hero：`minmax(0, 1.62fr)`
  - 評鑑卡：`minmax(360px, 0.98fr)`
- 低於 1500px 時：
  - Hero / 評鑑卡縮小 gap 與插圖尺寸
  - Ring 由 132px 降為 118px
  - Hero 統計卡縮小字級，但不允許直排
- 低於 1280px 時：
  - 第一列改為上下堆疊
  - 不產生水平捲動

### Hero 統計卡
- `grid-template-columns: repeat(4, minmax(86px, 1fr))`
- 每格最小 86px
- 數字 `white-space: nowrap`
- label 可換兩行，但不可直排

### 評鑑卡
- 狀態 pill 使用 `grid-template-columns: minmax(0, 1fr) auto`
- 防止文字與數字互壓
- 0% ring 不顯示假進度

## 2. Sidebar

- 不用 Streamlit 原生 sidebar。
- 預設最大 304px，視窗不足時最低 272px。
- 不允許 sidebar 自身捲動。
- 群組與 nav item 維持固定高度。
- 低於 1280px 才縮到 252px。

## 3. 第三列

- 首頁第三列不再固定 330 + 330 + 270 + 270。
- 改為比例欄：
  - `1fr 1fr .82fr .82fr`
- 低於 1500px 變兩欄。
- 低於 1280px 變一欄。

## 4. 驗收標準

- 1672px 寬參考視窗下不能有水平捲動。
- 右側評鑑卡不能被切掉。
- Hero 統計卡不能變直排。
- 按鈕不能被切掉。
- Sidebar 不出現內部捲動。
- 卡片內文與圖示不得重疊。
