# AI Usage Statement

## 目前狀態

SA_ODFlow 在 Task 1 階段只建立 AI 模組骨架，尚未直接呼叫 OpenAI API。

目前 `ai/` 目錄包含：

- `mock_parser.py`
- `openai_parser.py`

其中：

- `mock_parser.py` 只提供可替換的輸入輸出結構
- `openai_parser.py` 目前明確標示為未實作

## 使用原則

- 在沒有 API key 的情況下，系統應維持可本機啟動
- 真正的 AI 文件抽取流程會在後續任務補上
- 後續若啟用外部 AI 服務，需另外補上金鑰管理、錯誤處理、成本控制與輸出驗證

## 本階段不包含

- OpenAI API 串接
- 音檔語音轉文字
- 自動評分預測
