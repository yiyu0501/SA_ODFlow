# UI_SPEC_v12_ODFlow_real_shell_recovery

## 修正範圍

本版只修 v11 仍然空白的根本原因。

## 根本原因

v10/v11 為了讓 HTML `<a>` 連結在同一分頁開啟，加入了 `_same_tab_links()`。

v11 雖然嘗試避免 `<aside>` 被誤判，但實際 pattern 寫成：

```python
r'<a(?=[\\s>])...'
```

在 raw string 裡，`[\\s>]` 不是「空白或 >」，而是「反斜線、s、或 >」。  
因此 `<aside>` 的 `<a` 後面是 `s`，仍然會被匹配，導致：

```html
<aside class="odf-sidebar">
```

被改壞成類似：

```html
<a target="_self"side class="odf-sidebar">
```

App Shell 因此斷裂，畫面只剩部分 logo / 社團卡。

## 修正方式

改成真正只匹配 anchor tag：

```python
r'<a(?=\\s|>)(?![^>]*\\btarget=)'
```

意思是：

- `<a` 後面必須是空白或 `>`
- 不會匹配 `<aside>`
- 不會匹配 `<article>`
- 只會處理真正的 `<a href="...">`

## 驗收標準

- 首頁應恢復完整 sidebar / topbar / main content。
- HTML 中不得出現 `target="_self"side`。
- 點導覽仍維持同分頁切換。
- 保留 v09/v10 的響應式與按鈕不裁切修正。
