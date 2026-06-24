# SA_ODFlow Setup Guide

## 目的

這份文件說明如何在本機啟動目前可展示的 ODFlow MVP。

## 環境需求

- Python 3.11 以上
- `venv`
- 可安裝 `requirements.txt` 內依賴

## 安裝步驟

1. 建立虛擬環境

```bash
python3 -m venv .venv
```

2. 安裝依賴

```bash
.venv/bin/pip install -r requirements.txt
```

## 啟動方式

```bash
.venv/bin/streamlit run app.py
```

啟動後系統會自動建立：

- `data/odflow.sqlite3`
- SQLite 基本資料表
- `evaluation_items` 七大評鑑項目 seed

## 建議展示流程

1. 進入 Settings，填入社團基本資料
2. 點擊「建立示範資料」
3. 到 Generate 產生一份會議紀錄
4. 到 Files 管理版本與匯出 ODT / PDF
5. 到 Dashboard 查看完整度
6. 到 Evaluation 輸出 PDF 評鑑 ZIP 與 ODF 備份 ZIP

## 測試方式

```bash
.venv/bin/python -m unittest discover -s tests
```

## 目前限制

- 尚未串接 OpenAI API
- 尚未支援音檔轉文字
- 尚未實作登入系統與多人權限
- Projects / Templates 仍屬後續擴充骨架
- 目前最完整的可展示文件流程以會議紀錄為主
