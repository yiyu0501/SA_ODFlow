from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from generators.document_layout import build_spreadsheet_template_spec
from generators.document_style import BODY_FONT_SIZE_PT, ODF_FONT_FAMILY, TABLE_FONT_SIZE_PT


INCOME_EXPENSE_CATEGORY_OPTIONS = [
    "結餘",
    "餐食費",
    "交通費",
    "保險費",
    "印刷費",
    "道具費",
    "活動費",
    "器材費",
    "場地費",
    "講師費",
    "文具費",
    "社費",
    "學校補助",
    "校外補助",
    "合作單位補助",
    "活動收入",
    "利息",
    "其他收入",
    "其他支出",
]
YES_NO_NA_OPTIONS = ["是", "否", "不適用"]
INCOME_EXPENSE_HEADERS = [
    "序號",
    "日期",
    "類別",
    "品項",
    "支出",
    "收入",
    "餘額",
    "代墊人",
    "是否已撥款",
    "是否已列入活動結算",
    "對應活動",
    "憑證／明細表",
    "備註",
]
DETAIL_SHEET_NAME = "收支明細"
ACTIVITY_SUMMARY_SHEET_NAME = "活動彙總"
CATEGORY_SUMMARY_SHEET_NAME = "類別彙總"
DETAIL_HEADER_ROW = 7
DETAIL_FIRST_DATA_ROW = 8
DETAIL_ROW_COUNT = 200
DETAIL_LAST_DATA_ROW = DETAIL_FIRST_DATA_ROW + DETAIL_ROW_COUNT - 1


def _escape_attr(value: str) -> str:
    return escape(str(value), {'"': "&quot;"})


def _paragraph_xml(value: str, style_name: str = "PBody") -> str:
    return f'<text:p text:style-name="{style_name}">{escape(str(value or ""))}</text:p>'


def _covered_cells_xml(count: int) -> str:
    return "<table:covered-table-cell/>" * max(count, 0)


def _row_xml(cells: list[str], style_name: str = "RowDefault") -> str:
    return f'<table:table-row table:style-name="{style_name}">{"".join(cells)}</table:table-row>'


def _string_cell_xml(
    value: str = "",
    cell_style: str = "CellBody",
    paragraph_style: str = "PBody",
    *,
    span: int = 1,
    validation_name: str | None = None,
) -> str:
    attrs = [
        f'table:style-name="{cell_style}"',
        'office:value-type="string"',
    ]
    if span > 1:
        attrs.append(f'table:number-columns-spanned="{span}"')
    if validation_name:
        attrs.append(f'table:content-validation-name="{_escape_attr(validation_name)}"')
    return f'<table:table-cell {" ".join(attrs)}>{_paragraph_xml(value, paragraph_style)}</table:table-cell>'


def _float_cell_xml(
    value: float = 0,
    cell_style: str = "CellMoney",
    paragraph_style: str = "PBody",
    *,
    formula: str | None = None,
) -> str:
    attrs = [
        f'table:style-name="{cell_style}"',
        'office:value-type="float"',
        f'office:value="{value}"',
    ]
    if formula:
        attrs.append(f'table:formula="{_escape_attr(formula)}"')
    return f'<table:table-cell {" ".join(attrs)}>{_paragraph_xml("", paragraph_style)}</table:table-cell>'


def _column_styles_xml(widths: list[str]) -> tuple[str, str]:
    styles = []
    columns = []
    for index, width in enumerate(widths, start=1):
        style_name = f"Co{index}"
        styles.append(
            f'<style:style style:name="{style_name}" style:family="table-column">'
            f'<style:table-column-properties style:column-width="{width}"/>'
            "</style:style>"
        )
        columns.append(f'<table:table-column table:style-name="{style_name}"/>')
    return "".join(styles), "".join(columns)


def _column_label(index: int) -> str:
    label = ""
    current = index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        label = chr(65 + remainder) + label
    return label


def _same_sheet_ref(column: str, row: int, *, absolute: bool = False) -> str:
    prefix = "$" if absolute else ""
    return f"[.{prefix}{column}{prefix}{row}]"


def _sheet_range_ref(
    sheet_name: str,
    start_column: str,
    start_row: int,
    end_column: str,
    end_row: int,
) -> str:
    return (
        f"['{sheet_name}'.${start_column}${start_row}:'{sheet_name}'.${end_column}${end_row}]"
    )


def _validation_xml(name: str, options: list[str], message: str) -> str:
    quoted_items = ";".join(f'"{item}"' for item in options)
    condition = f"of:cell-content-is-in-list({quoted_items})"
    return (
        f'<table:content-validation table:name="{name}" '
        'table:allow-empty-cell="true" '
        'table:display-list="unsorted" '
        f'table:condition="{_escape_attr(condition)}">'
        '<table:error-message table:display="true" table:message-type="stop">'
        f'{_paragraph_xml(message, "PSmall")}'
        "</table:error-message>"
        "</table:content-validation>"
    )


def _detail_balance_formula(row_number: int) -> str:
    expense_ref = _same_sheet_ref("E", row_number)
    income_ref = _same_sheet_ref("F", row_number)
    if row_number == DETAIL_FIRST_DATA_ROW:
        opening_balance_ref = _same_sheet_ref("B", 5, absolute=True)
        previous_balance_ref = opening_balance_ref
    else:
        previous_balance_ref = _same_sheet_ref("G", row_number - 1)

    return (
        "of:=IF("
        f"AND(ISBLANK({expense_ref});ISBLANK({income_ref}));"
        f"{previous_balance_ref};"
        f"{previous_balance_ref}"
        f"+IF(ISBLANK({income_ref});0;{income_ref})"
        f"-IF(ISBLANK({expense_ref});0;{expense_ref})"
        ")"
    )


def _income_expense_styles_xml(column_styles_xml: str) -> str:
    return f"""
    {column_styles_xml}
    <number:number-style style:name="NAmount">
      <number:number number:min-integer-digits="1" number:decimal-places="0" number:grouping="true"/>
    </number:number-style>
    <number:date-style style:name="NDate" number:automatic-order="true">
      <number:year number:style="long"/>
      <number:text>/</number:text>
      <number:month number:style="long"/>
      <number:text>/</number:text>
      <number:day number:style="long"/>
    </number:date-style>
    <style:style style:name="RowDefault" style:family="table-row">
      <style:table-row-properties style:row-height="0.72cm"/>
    </style:style>
    <style:style style:name="RowTitle" style:family="table-row">
      <style:table-row-properties style:row-height="0.95cm"/>
    </style:style>
    <style:style style:name="RowHeader" style:family="table-row">
      <style:table-row-properties style:row-height="0.82cm"/>
    </style:style>
    <style:style style:name="RowSummary" style:family="table-row">
      <style:table-row-properties style:row-height="0.75cm"/>
    </style:style>
    <style:style style:name="PTitle" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="15pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PHeader" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PLabel" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{BODY_FONT_SIZE_PT}pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PBody" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt"/>
    </style:style>
    <style:style style:name="PSmall" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="CellTitle" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #4b5563" fo:padding="0.16cm" fo:background-color="#f8fafc"/>
    </style:style>
    <style:style style:name="CellLabel" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #6b7280" fo:padding="0.12cm" fo:background-color="#eef2ff"/>
    </style:style>
    <style:style style:name="CellValue" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #9ca3af" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellDate" style:family="table-cell" style:data-style-name="NDate">
      <style:table-cell-properties fo:border="0.03cm solid #9ca3af" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellHeader" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #374151" fo:padding="0.1cm" fo:background-color="#dbeafe"/>
    </style:style>
    <style:style style:name="CellBody" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #cbd5e1" fo:padding="0.09cm"/>
    </style:style>
    <style:style style:name="CellMoney" style:family="table-cell" style:data-style-name="NAmount">
      <style:table-cell-properties fo:border="0.03cm solid #cbd5e1" fo:padding="0.09cm"/>
    </style:style>
    <style:style style:name="CellMoneyFormula" style:family="table-cell" style:data-style-name="NAmount">
      <style:table-cell-properties fo:border="0.03cm solid #94a3b8" fo:padding="0.09cm" fo:background-color="#f8fafc"/>
    </style:style>
    <style:style style:name="CellSummaryHeader" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #4b5563" fo:padding="0.1cm" fo:background-color="#e5e7eb"/>
    </style:style>
    <style:style style:name="CellSummaryText" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #cbd5e1" fo:padding="0.09cm"/>
    </style:style>
    <style:style style:name="CellSummaryMoney" style:family="table-cell" style:data-style-name="NAmount">
      <style:table-cell-properties fo:border="0.03cm solid #cbd5e1" fo:padding="0.09cm"/>
    </style:style>
    <style:style style:name="CellSummaryFormula" style:family="table-cell" style:data-style-name="NAmount">
      <style:table-cell-properties fo:border="0.03cm solid #cbd5e1" fo:padding="0.09cm" fo:background-color="#f8fafc"/>
    </style:style>
    <style:style style:name="CellBlank" style:family="table-cell">
      <style:table-cell-properties fo:border="none" fo:padding="0.08cm"/>
    </style:style>
"""


def _income_expense_detail_table_xml() -> str:
    column_widths = [
        "1.15cm",
        "2.2cm",
        "2.4cm",
        "3.4cm",
        "2.2cm",
        "2.2cm",
        "2.4cm",
        "2.6cm",
        "2.6cm",
        "3.1cm",
        "3.0cm",
        "3.1cm",
        "3.0cm",
    ]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [
                _string_cell_xml("臺北市立大學 社團經費收支表", "CellTitle", "PTitle", span=13),
                _covered_cells_xml(12),
            ],
            "RowTitle",
        ),
        _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(13)]),
        _row_xml(
            [
                _string_cell_xml("學年度", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("學期", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("社團名稱", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=8),
                _covered_cells_xml(7),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("記帳期間", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=3),
                _covered_cells_xml(2),
                _string_cell_xml("財務負責人", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=3),
                _covered_cells_xml(2),
                _string_cell_xml("製表日期", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=4),
                _covered_cells_xml(3),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("期初餘額", "CellLabel", "PLabel"),
                _float_cell_xml(0, "CellMoney"),
                _string_cell_xml("備註", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=10),
                _covered_cells_xml(9),
            ]
        ),
        _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(13)]),
        _row_xml(
            [_string_cell_xml(header, "CellHeader", "PHeader") for header in INCOME_EXPENSE_HEADERS],
            "RowHeader",
        ),
    ]

    for row_number in range(DETAIL_FIRST_DATA_ROW, DETAIL_LAST_DATA_ROW + 1):
        serial_number = row_number - DETAIL_FIRST_DATA_ROW + 1
        rows.append(
            _row_xml(
                [
                    _float_cell_xml(serial_number, "CellBody"),
                    _string_cell_xml("", "CellDate"),
                    _string_cell_xml("", "CellBody", validation_name="validation_category"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellMoney"),
                    _string_cell_xml("", "CellMoney"),
                    _float_cell_xml(0, "CellMoneyFormula", formula=_detail_balance_formula(row_number)),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody", validation_name="validation_paid_status"),
                    _string_cell_xml("", "CellBody", validation_name="validation_settlement_status"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                ]
            )
        )

    return (
        f'<table:table table:name="{DETAIL_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _build_activity_summary_rows() -> str:
    rows = [
        _row_xml(
            [
                _string_cell_xml("活動彙總", "CellTitle", "PTitle", span=7),
                _covered_cells_xml(6),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("對應活動", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("支出總額", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("收入總額", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("活動淨額", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("未撥款筆數", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("未列入活動結算筆數", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("備註", "CellSummaryHeader", "PHeader"),
            ],
            "RowHeader",
        ),
    ]

    criterion_range = _sheet_range_ref(
        DETAIL_SHEET_NAME,
        "K",
        DETAIL_FIRST_DATA_ROW,
        "K",
        DETAIL_LAST_DATA_ROW,
    )
    expense_range = _sheet_range_ref(
        DETAIL_SHEET_NAME,
        "E",
        DETAIL_FIRST_DATA_ROW,
        "E",
        DETAIL_LAST_DATA_ROW,
    )
    income_range = _sheet_range_ref(
        DETAIL_SHEET_NAME,
        "F",
        DETAIL_FIRST_DATA_ROW,
        "F",
        DETAIL_LAST_DATA_ROW,
    )
    paid_status_range = _sheet_range_ref(
        DETAIL_SHEET_NAME,
        "I",
        DETAIL_FIRST_DATA_ROW,
        "I",
        DETAIL_LAST_DATA_ROW,
    )
    settlement_status_range = _sheet_range_ref(
        DETAIL_SHEET_NAME,
        "J",
        DETAIL_FIRST_DATA_ROW,
        "J",
        DETAIL_LAST_DATA_ROW,
    )

    for row_number in range(3, 33):
        activity_ref = _same_sheet_ref("A", row_number)
        expense_formula = f"of:=SUMIF({criterion_range};{activity_ref};{expense_range})"
        income_formula = f"of:=SUMIF({criterion_range};{activity_ref};{income_range})"
        net_formula = f"of:={_same_sheet_ref('C', row_number)}-{_same_sheet_ref('B', row_number)}"
        unpaid_formula = (
            "of:=COUNTIFS("
            f"{criterion_range};{activity_ref};"
            f"{paid_status_range};\"否\""
            ")"
        )
        unsettled_formula = (
            "of:=COUNTIFS("
            f"{criterion_range};{activity_ref};"
            f"{settlement_status_range};\"否\""
            ")"
        )
        rows.append(
            _row_xml(
                [
                    _string_cell_xml("", "CellSummaryText"),
                    _float_cell_xml(0, "CellSummaryFormula", formula=expense_formula),
                    _float_cell_xml(0, "CellSummaryFormula", formula=income_formula),
                    _float_cell_xml(0, "CellSummaryFormula", formula=net_formula),
                    _float_cell_xml(0, "CellSummaryFormula", formula=unpaid_formula),
                    _float_cell_xml(0, "CellSummaryFormula", formula=unsettled_formula),
                    _string_cell_xml("", "CellSummaryText"),
                ],
                "RowSummary",
            )
        )
    return "".join(rows)


def _income_expense_activity_summary_table_xml() -> str:
    column_widths = ["3.6cm", "2.6cm", "2.6cm", "2.6cm", "2.6cm", "3.2cm", "3.0cm"]
    _, columns_xml = _column_styles_xml(column_widths)
    return (
        f'<table:table table:name="{ACTIVITY_SUMMARY_SHEET_NAME}">'
        f"{columns_xml}"
        f"{_build_activity_summary_rows()}"
        "</table:table>"
    )


def _income_expense_category_summary_table_xml() -> str:
    column_widths = ["3.2cm", "2.6cm", "2.6cm", "2.6cm", "3.2cm"]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [
                _string_cell_xml("類別彙總", "CellTitle", "PTitle", span=5),
                _covered_cells_xml(4),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("類別", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("支出總額", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("收入總額", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("淨額", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("備註", "CellSummaryHeader", "PHeader"),
            ],
            "RowHeader",
        ),
    ]
    category_range = _sheet_range_ref(
        DETAIL_SHEET_NAME,
        "C",
        DETAIL_FIRST_DATA_ROW,
        "C",
        DETAIL_LAST_DATA_ROW,
    )
    expense_range = _sheet_range_ref(
        DETAIL_SHEET_NAME,
        "E",
        DETAIL_FIRST_DATA_ROW,
        "E",
        DETAIL_LAST_DATA_ROW,
    )
    income_range = _sheet_range_ref(
        DETAIL_SHEET_NAME,
        "F",
        DETAIL_FIRST_DATA_ROW,
        "F",
        DETAIL_LAST_DATA_ROW,
    )

    for index, category in enumerate(INCOME_EXPENSE_CATEGORY_OPTIONS, start=3):
        category_ref = _same_sheet_ref("A", index)
        expense_formula = f"of:=SUMIF({category_range};{category_ref};{expense_range})"
        income_formula = f"of:=SUMIF({category_range};{category_ref};{income_range})"
        net_formula = f"of:={_same_sheet_ref('C', index)}-{_same_sheet_ref('B', index)}"
        rows.append(
            _row_xml(
                [
                    _string_cell_xml(category, "CellSummaryText"),
                    _float_cell_xml(0, "CellSummaryFormula", formula=expense_formula),
                    _float_cell_xml(0, "CellSummaryFormula", formula=income_formula),
                    _float_cell_xml(0, "CellSummaryFormula", formula=net_formula),
                    _string_cell_xml("", "CellSummaryText"),
                ],
                "RowSummary",
            )
        )

    return (
        f'<table:table table:name="{CATEGORY_SUMMARY_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _build_income_expense_statement_content_xml() -> str:
    column_styles_xml, _ = _column_styles_xml(
        [
            "1.15cm",
            "2.2cm",
            "2.4cm",
            "3.4cm",
            "2.2cm",
            "2.2cm",
            "2.4cm",
            "2.6cm",
            "2.6cm",
            "3.1cm",
            "3.0cm",
            "3.1cm",
            "3.0cm",
        ]
    )
    validations_xml = "".join(
        [
            _validation_xml("validation_category", INCOME_EXPENSE_CATEGORY_OPTIONS, "請從類別清單選擇項目。"),
            _validation_xml("validation_paid_status", YES_NO_NA_OPTIONS, "請從撥款狀態清單選擇。"),
            _validation_xml("validation_settlement_status", YES_NO_NA_OPTIONS, "請從活動結算狀態清單選擇。"),
        ]
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles>
    {_income_expense_styles_xml(column_styles_xml)}
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      <table:content-validations>
        {validations_xml}
      </table:content-validations>
      {_income_expense_detail_table_xml()}
      {_income_expense_activity_summary_table_xml()}
      {_income_expense_category_summary_table_xml()}
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _cell_xml(
    value: str,
    cell_style: str = "CellBody",
    paragraph_style: str = "PBody",
    *,
    span: int = 1,
) -> str:
    span_attributes = f' table:number-columns-spanned="{span}"' if span > 1 else ""
    return (
        f'<table:table-cell table:style-name="{cell_style}" office:value-type="string"{span_attributes}>'
        f"{_paragraph_xml(value, paragraph_style)}"
        "</table:table-cell>"
    )


def _legacy_column_styles_xml(column_count: int) -> tuple[str, str]:
    styles = []
    columns = []
    for index in range(column_count):
        style_name = f"Co{index + 1}"
        width = "2.1cm" if index == 0 else "3.2cm"
        styles.append(
            f'<style:style style:name="{style_name}" style:family="table-column">'
            f'<style:table-column-properties style:column-width="{width}"/>'
            "</style:style>"
        )
        columns.append(f'<table:table-column table:style-name="{style_name}"/>')
    return "".join(styles), "".join(columns)


def _build_legacy_spreadsheet_content_xml(template_definition: dict) -> str:
    spec = build_spreadsheet_template_spec(template_definition)
    column_count = max(int(spec.get("column_count", 1)), 1)
    column_styles_xml, columns_xml = _legacy_column_styles_xml(column_count)

    title_row = _row_xml(
        [
            _cell_xml(spec["title"], "CellTitle", "PTitle", span=column_count),
            _covered_cells_xml(column_count - 1),
        ]
    )
    metadata_row = _row_xml(
        [
            _cell_xml(spec["metadata"], "CellMeta", "PMeta", span=column_count),
            _covered_cells_xml(column_count - 1),
        ],
        style_name="RowMeta",
    )
    note_row = _row_xml(
        [
            _cell_xml(f"使用說明：{spec['note']}", "CellNote", "PNote", span=column_count),
            _covered_cells_xml(column_count - 1),
        ]
    )
    spacer_row = _row_xml([_cell_xml("", "CellBlank", "PBody") for _ in range(column_count)])
    header_row = _row_xml(
        [_cell_xml(header, "CellHeader", "PHeader") for header in spec["headers"]],
        style_name="RowHeader",
    )
    blank_rows = [
        _row_xml(
            [_cell_xml("", "CellBody", "PBody") for _ in range(column_count)],
            style_name="RowData",
        )
        for _ in range(spec["blank_rows"])
    ]
    table_name = escape(spec["title"])

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles>
    {column_styles_xml}
    <style:style style:name="RowDefault" style:family="table-row">
      <style:table-row-properties style:row-height="0.7cm"/>
    </style:style>
    <style:style style:name="RowMeta" style:family="table-row">
      <style:table-row-properties style:row-height="0.8cm"/>
    </style:style>
    <style:style style:name="RowHeader" style:family="table-row">
      <style:table-row-properties style:row-height="0.75cm"/>
    </style:style>
    <style:style style:name="RowData" style:family="table-row">
      <style:table-row-properties style:row-height="0.72cm"/>
    </style:style>
    <style:style style:name="PTitle" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="16pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PMeta" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{BODY_FONT_SIZE_PT}pt"/>
    </style:style>
    <style:style style:name="PHeader" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PBody" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt"/>
    </style:style>
    <style:style style:name="PNote" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="10pt"/>
    </style:style>
    <style:style style:name="CellTitle" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #666666" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellMeta" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #666666" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellNote" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #666666" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellHeader" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #333333" fo:padding="0.1cm" fo:background-color="#d9d9d9"/>
    </style:style>
    <style:style style:name="CellBody" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #555555" fo:padding="0.1cm"/>
    </style:style>
    <style:style style:name="CellBlank" style:family="table-cell">
      <style:table-cell-properties fo:border="none" fo:padding="0.1cm"/>
    </style:style>
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      <table:table table:name="{table_name}">
        {columns_xml}
        {title_row}
        {metadata_row}
        {note_row}
        {spacer_row}
        {header_row}
        {''.join(blank_rows)}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _build_spreadsheet_content_xml(template_definition: dict) -> str:
    template_id = template_definition.get("id") or template_definition.get("template_key")
    if template_id == "income_expense_statement":
        return _build_income_expense_statement_content_xml()
    return _build_legacy_spreadsheet_content_xml(template_definition)


def _minimal_ods_files(content_xml: str) -> dict[str, str]:
    return {
        "mimetype": "application/vnd.oasis.opendocument.spreadsheet",
        "content.xml": content_xml,
        "styles.xml": f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    office:version="1.2">
  <office:styles>
    <style:default-style style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{BODY_FONT_SIZE_PT}pt"/>
    </style:default-style>
  </office:styles>
  <office:automatic-styles/>
  <office:master-styles/>
</office:document-styles>
""",
        "meta.xml": """<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    office:version="1.2">
  <office:meta/>
</office:document-meta>
""",
        "settings.xml": """<?xml version="1.0" encoding="UTF-8"?>
<office:document-settings
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    office:version="1.2">
  <office:settings/>
</office:document-settings>
""",
        "META-INF/manifest.xml": """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest
    xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
    manifest:version="1.2">
  <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.spreadsheet" manifest:full-path="/"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="meta.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="settings.xml"/>
</manifest:manifest>
""",
    }


def generate_ods_template(
    template_definition: dict,
    output_path: Path | str,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_map = _minimal_ods_files(_build_spreadsheet_content_xml(template_definition))

    with ZipFile(output_path, "w") as archive:
        archive.writestr("mimetype", file_map["mimetype"], compress_type=ZIP_STORED)
        for path, file_content in file_map.items():
            if path == "mimetype":
                continue
            archive.writestr(path, file_content, compress_type=ZIP_DEFLATED)

    return output_path
