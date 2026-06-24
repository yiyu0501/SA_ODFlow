# SA_ODFlow Setup Guide

## 目的

這份文件說明如何在本機啟動 SA_ODFlow Task 1 骨架版本。

## 環境需求

- Python 3.11 以上
- `pip`

## 安裝步驟

1. 建立虛擬環境

```bash
python3 -m venv .venv
```

2. 啟用虛擬環境

```bash
source .venv/bin/activate
```

3. 安裝依賴

```bash
pip install -r requirements.txt
```

## 啟動方式

```bash
streamlit run app.py
```

啟動後會自動建立：

- `data/odflow.sqlite3`
- SQLite 基本資料表
- `evaluation_items` 七大評鑑項目 seed

## 測試方式

```bash
python -m unittest discover -s tests
```

## 目前限制

- 這是 Task 1 骨架版本
- 尚未串接 OpenAI API
- 尚未支援音檔轉文字
- 尚未實作文件生成、文件庫、版本管理、ODF/PDF 匯出與評鑑 ZIP 匯出
