# UI_SPEC_v11_ODFlow_shell_recovery

## 修正範圍

本版只修 v10 造成「頁面幾乎空白、sidebar/main shell 壞掉」的問題。

## 問題原因

v10 為了讓自訂 HTML 連結在同一分頁開啟，使用了自動補 `target="_self"` 的 regex。

原本 regex 會錯誤匹配 `<aside>`，把：

```html
<aside class="odf-sidebar">
```

改壞成：

```html
<a target="_self"side class="odf-sidebar">
```

導致整個 App Shell 結構斷掉，所以畫面只剩部分文字與社團卡。

## 修正方式

- 只匹配真正的 `<a>` 標籤。
- 新 pattern：`<a(?=[\s>])(?![^>]*\btarget=)`
- 不再匹配 `<aside>`。
- 保留 v10 對以下問題的修正：
  - 首頁快速開始按鈕不裁切
  - 空白範本卡片按鈕不裁切
  - 生成文件 Step 1 按鈕不裁切
  - 連結維持同分頁開啟

## 驗收標準

- 首頁 sidebar 正常出現。
- 首頁主內容正常出現。
- 不再只看到 logo 與社團卡。
- 點擊導覽不開新分頁。
