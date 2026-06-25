# SA_ODFlow Setup Guide

## 目的

這份文件說明如何在本機啟動目前可展示的 ODFlow ODF 競賽展示版 MVP。

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
3. 到 Templates 產生 ODT / ODS 範本
4. 到 Generate 產生一份會議紀錄
5. 到 Files 管理版本與匯出 ODT / PDF
6. 到 Dashboard 查看社團評鑑資料完整度
7. 到 Evaluation 輸出 PDF 評鑑上傳包與 ODF 原始檔備份 ZIP

## 測試方式

```bash
.venv/bin/python -m unittest discover -s tests
```

## 目前限制

- 尚未串接 OpenAI API
- 尚未支援音檔轉文字
- 尚未實作登入系統與多人權限
- Projects 仍屬未來擴充頁面
- 目前是本機 ZIP 下載，不是雲端自動上傳
- 最完整的文件生成流程仍以會議紀錄為主
