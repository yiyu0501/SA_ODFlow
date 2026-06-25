from __future__ import annotations

from typing import Iterable


PAGE_MARGIN_CM = "2.2cm"
PAGE_WIDTH_CM = "21cm"
PAGE_HEIGHT_CM = "29.7cm"

ODF_FONT_FAMILY = "DFKai-SB, BiauKai, Noto Serif CJK TC, Noto Sans CJK TC, serif"
ODF_SANS_FONT_FAMILY = "Noto Sans CJK TC, Microsoft JhengHei, sans-serif"

TITLE_FONT_SIZE_PT = 18
SECTION_FONT_SIZE_PT = 14
BODY_FONT_SIZE_PT = 12
TABLE_FONT_SIZE_PT = 11
NOTE_FONT_SIZE_PT = 10

PDF_FONT_CANDIDATES = [
    "MSung-Light",
    "STSong-Light",
    "HeiseiMin-W3",
    "HYSMyeongJo-Medium",
]

TEXT_PLACEHOLDER = "待補"
BLANK_LINE_PLACEHOLDER = "＿＿＿＿＿＿＿＿＿＿"


def display_text(value, placeholder: str = TEXT_PLACEHOLDER) -> str:
    text = str(value or "").strip()
    return text or placeholder


def display_people(values: Iterable[str] | None, placeholder: str = TEXT_PLACEHOLDER) -> str:
    people = [str(item).strip() for item in (values or []) if str(item).strip()]
    return "、".join(people) if people else placeholder


def display_lines(value, placeholder: str = TEXT_PLACEHOLDER) -> list[str]:
    if isinstance(value, list):
        lines = [str(item).strip() for item in value if str(item).strip()]
    else:
        lines = [line.strip() for line in str(value or "").replace("\r", "").split("\n") if line.strip()]
    return lines or [placeholder]


def display_bullets(value, placeholder: str = TEXT_PLACEHOLDER) -> list[str]:
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return items or [placeholder]
    lines = display_lines(value, placeholder=placeholder)
    if len(lines) == 1 and lines[0] == placeholder:
        return lines
    return lines


def ensure_table_rows(
    rows: list[list[str]],
    column_count: int,
    minimum_rows: int = 1,
    placeholder: str = "",
) -> list[list[str]]:
    normalized = []
    for row in rows:
        values = [str(item or "").strip() for item in row[:column_count]]
        if len(values) < column_count:
            values.extend([placeholder] * (column_count - len(values)))
        normalized.append(values)

    target_count = max(minimum_rows, len(normalized))
    while len(normalized) < target_count:
        normalized.append([placeholder] * column_count)
    return normalized


def register_pdf_font(reportlab) -> str:
    last_error: Exception | None = None
    for font_name in PDF_FONT_CANDIDATES:
        try:
            reportlab["registerFont"](reportlab["UnicodeCIDFont"](font_name))
            return font_name
        except Exception as exc:  # pragma: no cover - fallback path is env-specific
            last_error = exc

    if last_error is not None:
        raise RuntimeError("找不到可用的中文 PDF 字體 fallback。") from last_error
    raise RuntimeError("找不到可用的中文 PDF 字體 fallback。")
