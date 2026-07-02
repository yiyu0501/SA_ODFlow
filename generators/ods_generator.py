from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from generators.document_layout import build_spreadsheet_template_spec
from generators.document_style import BODY_FONT_SIZE_PT, ODF_FONT_FAMILY, TABLE_FONT_SIZE_PT


INCOME_EXPENSE_CATEGORY_OPTIONS = [
    "結餘",
    "補助收入",
    "餐食費",
    "交通費",
    "保險費",
    "印刷費",
    "道具費",
    "活動費",
    "活動支出",
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
EXPENSE_BUDGET_CATEGORY_OPTIONS = [
    "場地費",
    "講師費",
    "交通費",
    "餐費",
    "保險費",
    "文宣費",
    "印刷費",
    "材料費",
    "器材費",
    "獎品費",
    "雜支",
    "其他",
]
EXPENSE_BUDGET_FUNDING_SOURCE_OPTIONS = [
    "學校補助",
    "社團會費",
    "校外補助",
    "自籌",
    "其他",
]
EXPENSE_BUDGET_SUBSIDY_OPTIONS = ["是", "否", "待確認"]
EXPENSE_SETTLEMENT_NOTE_OPTIONS = [
    "學校補助",
    "校外補助",
    "社團會費",
    "自籌",
    "其他",
]
REIMBURSEMENT_RECEIPT_TYPE_OPTIONS = [
    "發票",
    "電子發票證明聯",
    "收據",
    "免用統一發票收據",
    "匯款證明",
    "付款截圖",
    "領據",
    "其他",
]
REIMBURSEMENT_FUNDING_SOURCE_OPTIONS = [
    "學校補助",
    "校外補助",
    "社團會費",
    "自籌",
    "其他",
]
REIMBURSEMENT_PAYMENT_METHOD_OPTIONS = [
    "現金",
    "轉帳",
    "信用卡",
    "金融卡",
    "行動支付",
    "匯款",
    "其他",
]
REIMBURSEMENT_RECEIPT_STATUS_OPTIONS = [
    "已附",
    "待補",
    "遺失",
    "不核銷",
    "不適用",
]
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
EXPENSE_BUDGET_SHEET_NAME = "經費預算表"
EXPENSE_BUDGET_HEADERS = [
    "序號",
    "項目類別",
    "項目",
    "說明",
    "數量",
    "單位",
    "單價",
    "金額",
    "經費來源",
    "是否申請補助",
    "備註",
]
EXPENSE_BUDGET_FIRST_DATA_ROW = 8
EXPENSE_BUDGET_ROW_COUNT = 100
EXPENSE_BUDGET_LAST_DATA_ROW = EXPENSE_BUDGET_FIRST_DATA_ROW + EXPENSE_BUDGET_ROW_COUNT - 1
EXPENSE_SETTLEMENT_SHEET_NAME = "經費收支結算表"
EXPENSE_SETTLEMENT_HEADERS = [
    "項目",
    "預算通過金額",
    "實際支出金額",
    "備註",
]
EXPENSE_SETTLEMENT_FIRST_DATA_ROW = 8
EXPENSE_SETTLEMENT_ROW_COUNT = 10
EXPENSE_SETTLEMENT_LAST_DATA_ROW = (
    EXPENSE_SETTLEMENT_FIRST_DATA_ROW + EXPENSE_SETTLEMENT_ROW_COUNT - 1
)
REIMBURSEMENT_SHEET_NAME = "核銷明細表"
REIMBURSEMENT_HEADERS = [
    "序號",
    "支出日期",
    "對應經費項目",
    "品名／用途",
    "店家／受款單位",
    "單據類型",
    "單據號碼",
    "經費來源",
    "支付方式",
    "墊付款人",
    "金額",
    "憑證狀態",
    "附件檔名／連結",
    "備註",
]
REIMBURSEMENT_FIRST_DATA_ROW = 8
REIMBURSEMENT_ROW_COUNT = 100
REIMBURSEMENT_LAST_DATA_ROW = REIMBURSEMENT_FIRST_DATA_ROW + REIMBURSEMENT_ROW_COUNT - 1
ACTIVITY_SCHEDULE_OVERVIEW_SHEET_NAME = "粗流"
ACTIVITY_SCHEDULE_DETAIL_SHEET_NAME = "細流"
ACTIVITY_SCHEDULE_OVERVIEW_HEADERS = ["時間", "時長", "活動名稱", "場控／主持", "備註"]
ACTIVITY_SCHEDULE_DETAIL_HEADERS = [
    "大活動時間",
    "大活動名稱",
    "細時間",
    "組別／區域",
    "事項",
    "備註",
    "器材",
    "負責人",
    "人員",
]
ACTIVITY_SCHEDULE_OVERVIEW_ROW_COUNT = 20
ACTIVITY_SCHEDULE_DETAIL_ROW_COUNT = 80
WORK_ASSIGNMENT_PHASE_OPTIONS = ["活動前", "活動中", "活動後", "全程", "其他"]
WORK_ASSIGNMENT_GROUP_OPTIONS = [
    "總籌組",
    "行政組",
    "活動組",
    "場器組",
    "宣傳組",
    "報名組",
    "攝影組",
    "財務組",
    "文書組",
    "接待組",
    "機動組",
    "其他",
]
WORK_ASSIGNMENT_STATUS_OPTIONS = ["未開始", "處理中", "已完成", "待確認", "延後", "取消"]
WORK_ASSIGNMENT_PRIORITY_OPTIONS = ["高", "中", "低"]
WORK_ASSIGNMENT_SHEET_NAME = "工作分配總表"
WORK_ASSIGNMENT_SUMMARY_SHEET_NAME = "統計摘要"
WORK_ASSIGNMENT_HEADERS = [
    "序號",
    "階段",
    "組別",
    "工作項目",
    "工作內容",
    "負責人",
    "協助人員",
    "開始日期",
    "完成期限",
    "狀態",
    "優先程度",
    "所需資源",
    "對應流程時間",
    "備註",
]
WORK_ASSIGNMENT_HEADER_ROW = 7
WORK_ASSIGNMENT_FIRST_DATA_ROW = 8
WORK_ASSIGNMENT_ROW_COUNT = 100
WORK_ASSIGNMENT_LAST_DATA_ROW = WORK_ASSIGNMENT_FIRST_DATA_ROW + WORK_ASSIGNMENT_ROW_COUNT - 1
MEMBER_ROSTER_MEMBER_TYPE_OPTIONS = [
    "一般社員",
    "幹部",
    "社長",
    "副社長",
    "顧問",
    "畢業社員",
    "校外人士",
    "其他",
]
MEMBER_ROSTER_STATUS_OPTIONS = [
    "有效",
    "暫停",
    "退出",
    "畢業",
    "觀察中",
    "其他",
]
MEMBER_ROSTER_FEE_STATUS_OPTIONS = ["已繳", "未繳", "免繳", "部分繳交", "不適用"]
MEMBER_ROSTER_SHEET_NAME = "社員名冊"
MEMBER_ROSTER_SUMMARY_SHEET_NAME = "統計摘要"
MEMBER_ROSTER_HEADERS = [
    "序號",
    "姓名",
    "學號",
    "系級／班級",
    "身分別",
    "入社日期",
    "社員狀態",
    "社費狀態",
    "手機",
    "Email",
    "LINE ID／聯絡方式",
    "緊急聯絡人",
    "備註",
]
MEMBER_ROSTER_HEADER_ROW = 7
MEMBER_ROSTER_FIRST_DATA_ROW = 8
MEMBER_ROSTER_ROW_COUNT = 200
MEMBER_ROSTER_LAST_DATA_ROW = MEMBER_ROSTER_FIRST_DATA_ROW + MEMBER_ROSTER_ROW_COUNT - 1


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


def _blank_cell_xml(
    cell_style: str = "CellBody",
    paragraph_style: str = "PBody",
    *,
    validation_name: str | None = None,
) -> str:
    attrs = [f'table:style-name="{cell_style}"']
    if validation_name:
        attrs.append(f'table:content-validation-name="{_escape_attr(validation_name)}"')
    return f'<table:table-cell {" ".join(attrs)}>{_paragraph_xml("", paragraph_style)}</table:table-cell>'


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


def _validation_xml_with_message_type(
    name: str,
    options: list[str],
    message: str,
    message_type: str = "stop",
) -> str:
    quoted_items = ";".join(f'"{item}"' for item in options)
    condition = f"of:cell-content-is-in-list({quoted_items})"
    return (
        f'<table:content-validation table:name="{name}" '
        'table:allow-empty-cell="true" '
        'table:display-list="unsorted" '
        f'table:condition="{_escape_attr(condition)}">'
        f'<table:error-message table:display="true" table:message-type="{_escape_attr(message_type)}">'
        f'{_paragraph_xml(message, "PSmall")}'
        "</table:error-message>"
        "</table:content-validation>"
    )


def _detail_balance_formula(row_number: int) -> str:
    expense_ref = _same_sheet_ref("E", row_number)
    income_ref = _same_sheet_ref("F", row_number)
    if row_number == DETAIL_FIRST_DATA_ROW:
        previous_balance_ref = _same_sheet_ref("B", 5, absolute=True)
    else:
        previous_balance_ref = _same_sheet_ref("G", row_number - 1)

    return f"={previous_balance_ref}+N({income_ref})-N({expense_ref})"


def _work_assignment_title_range() -> str:
    return _sheet_range_ref(
        WORK_ASSIGNMENT_SHEET_NAME,
        "D",
        WORK_ASSIGNMENT_FIRST_DATA_ROW,
        "D",
        WORK_ASSIGNMENT_LAST_DATA_ROW,
    )


def _work_assignment_status_range() -> str:
    return _sheet_range_ref(
        WORK_ASSIGNMENT_SHEET_NAME,
        "J",
        WORK_ASSIGNMENT_FIRST_DATA_ROW,
        "J",
        WORK_ASSIGNMENT_LAST_DATA_ROW,
    )


def _work_assignment_priority_range() -> str:
    return _sheet_range_ref(
        WORK_ASSIGNMENT_SHEET_NAME,
        "K",
        WORK_ASSIGNMENT_FIRST_DATA_ROW,
        "K",
        WORK_ASSIGNMENT_LAST_DATA_ROW,
    )


def _work_assignment_deadline_range() -> str:
    return _sheet_range_ref(
        WORK_ASSIGNMENT_SHEET_NAME,
        "I",
        WORK_ASSIGNMENT_FIRST_DATA_ROW,
        "I",
        WORK_ASSIGNMENT_LAST_DATA_ROW,
    )


def _member_roster_name_range() -> str:
    return _sheet_range_ref(
        MEMBER_ROSTER_SHEET_NAME,
        "B",
        MEMBER_ROSTER_FIRST_DATA_ROW,
        "B",
        MEMBER_ROSTER_LAST_DATA_ROW,
    )


def _member_roster_department_range() -> str:
    return _sheet_range_ref(
        MEMBER_ROSTER_SHEET_NAME,
        "D",
        MEMBER_ROSTER_FIRST_DATA_ROW,
        "D",
        MEMBER_ROSTER_LAST_DATA_ROW,
    )


def _member_roster_member_type_range() -> str:
    return _sheet_range_ref(
        MEMBER_ROSTER_SHEET_NAME,
        "E",
        MEMBER_ROSTER_FIRST_DATA_ROW,
        "E",
        MEMBER_ROSTER_LAST_DATA_ROW,
    )


def _member_roster_status_range() -> str:
    return _sheet_range_ref(
        MEMBER_ROSTER_SHEET_NAME,
        "G",
        MEMBER_ROSTER_FIRST_DATA_ROW,
        "G",
        MEMBER_ROSTER_LAST_DATA_ROW,
    )


def _member_roster_fee_range() -> str:
    return _sheet_range_ref(
        MEMBER_ROSTER_SHEET_NAME,
        "H",
        MEMBER_ROSTER_FIRST_DATA_ROW,
        "H",
        MEMBER_ROSTER_LAST_DATA_ROW,
    )


def _income_expense_styles_xml(column_styles_xml: str) -> str:
    return f"""
    {column_styles_xml}
    <number:number-style style:name="NNumber">
      <number:number number:min-integer-digits="1" number:decimal-places="0"/>
    </number:number-style>
    <number:number-style style:name="NAmount">
      <number:number number:min-integer-digits="1" number:decimal-places="0" number:grouping="true"/>
    </number:number-style>
    <number:percentage-style style:name="NPercent">
      <number:number number:min-integer-digits="1" number:decimal-places="2"/>
      <number:text>%</number:text>
    </number:percentage-style>
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
    <style:style style:name="CellNumber" style:family="table-cell" style:data-style-name="NNumber">
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
    <style:style style:name="CellSummaryPercent" style:family="table-cell" style:data-style-name="NPercent">
      <style:table-cell-properties fo:border="0.03cm solid #cbd5e1" fo:padding="0.09cm" fo:background-color="#f8fafc"/>
    </style:style>
    <style:style style:name="CellBlank" style:family="table-cell">
      <style:table-cell-properties fo:border="none" fo:padding="0.08cm"/>
    </style:style>
"""


def _activity_schedule_table_styles_xml(column_styles_xml: str) -> str:
    return f"""
    {column_styles_xml}
    <style:style style:name="RowDefault" style:family="table-row">
      <style:table-row-properties style:row-height="0.7cm"/>
    </style:style>
    <style:style style:name="RowTitle" style:family="table-row">
      <style:table-row-properties style:row-height="0.88cm"/>
    </style:style>
    <style:style style:name="RowHeader" style:family="table-row">
      <style:table-row-properties style:row-height="0.78cm"/>
    </style:style>
    <style:style style:name="RowSummary" style:family="table-row">
      <style:table-row-properties style:row-height="0.72cm"/>
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
      <style:table-cell-properties fo:border="0.03cm solid #4b5563" fo:padding="0.14cm" fo:background-color="#f8fafc"/>
    </style:style>
    <style:style style:name="CellLabel" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #6b7280" fo:padding="0.12cm" fo:background-color="#eef2ff"/>
    </style:style>
    <style:style style:name="CellValue" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #9ca3af" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellHeader" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #374151" fo:padding="0.1cm" fo:background-color="#dbeafe"/>
    </style:style>
    <style:style style:name="CellBody" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #cbd5e1" fo:padding="0.09cm"/>
    </style:style>
    <style:style style:name="CellSummaryHeader" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #4b5563" fo:padding="0.1cm" fo:background-color="#e5e7eb"/>
    </style:style>
    <style:style style:name="CellSummaryText" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #cbd5e1" fo:padding="0.09cm"/>
    </style:style>
    <style:style style:name="CellBlank" style:family="table-cell">
      <style:table-cell-properties fo:border="none" fo:padding="0.08cm"/>
    </style:style>
"""


def _expense_budget_item_amount_formula(row_number: int) -> str:
    quantity_ref = _same_sheet_ref("E", row_number)
    unit_price_ref = _same_sheet_ref("G", row_number)
    return f"=N({quantity_ref})*N({unit_price_ref})"


def _expense_budget_value_label_row(
    left_label: str,
    right_label: str,
    *,
    left_value_style: str = "CellValue",
    right_value_style: str = "CellValue",
) -> str:
    return _row_xml(
        [
            _string_cell_xml(left_label, "CellLabel", "PLabel"),
            _string_cell_xml("", left_value_style),
            _string_cell_xml(right_label, "CellLabel", "PLabel"),
            _string_cell_xml("", right_value_style),
        ]
    )


def _expense_budget_summary_row(
    first_label: str,
    first_formula: str,
    second_label: str = "",
    second_formula: str | None = None,
    third_label: str = "",
    third_formula: str | None = None,
) -> str:
    cells = [
        _string_cell_xml(first_label, "CellSummaryText", "PLabel", span=2),
        _covered_cells_xml(1),
        _float_cell_xml(0, "CellSummaryFormula", formula=first_formula),
    ]
    if second_label:
        cells.extend(
            [
                _string_cell_xml(second_label, "CellSummaryText", "PLabel", span=2),
                _covered_cells_xml(1),
                _float_cell_xml(0, "CellSummaryFormula", formula=second_formula or "=0"),
            ]
        )
    else:
        cells.extend([_string_cell_xml("", "CellSummaryText", span=3), _covered_cells_xml(2)])
    if third_label:
        cells.extend(
            [
                _string_cell_xml(third_label, "CellSummaryText", "PLabel", span=2),
                _covered_cells_xml(1),
                _float_cell_xml(0, "CellSummaryFormula", formula=third_formula or "=0"),
            ]
        )
    else:
        cells.extend([_string_cell_xml("", "CellSummaryText", span=3), _covered_cells_xml(2)])
    return _row_xml(cells, "RowSummary")


def _expense_budget_summary_rows() -> list[str]:
    amount_range = (
        f"[.H{EXPENSE_BUDGET_FIRST_DATA_ROW}:.H{EXPENSE_BUDGET_LAST_DATA_ROW}]"
    )
    funding_range = (
        f"[.I{EXPENSE_BUDGET_FIRST_DATA_ROW}:.I{EXPENSE_BUDGET_LAST_DATA_ROW}]"
    )
    subsidy_range = (
        f"[.J{EXPENSE_BUDGET_FIRST_DATA_ROW}:.J{EXPENSE_BUDGET_LAST_DATA_ROW}]"
    )
    total_formula = f"=SUM({amount_range})"
    subsidy_total_formula = f'=SUMIF({subsidy_range};"是";{amount_range})'
    school_formula = f'=SUMIF({funding_range};"學校補助";{amount_range})'
    club_fee_formula = f'=SUMIF({funding_range};"社團會費";{amount_range})'
    external_formula = f'=SUMIF({funding_range};"校外補助";{amount_range})'
    self_funded_formula = f'=SUMIF({funding_range};"自籌";{amount_range})'
    other_formula = f'=SUMIF({funding_range};"其他";{amount_range})'
    self_total_formula = (
        f'=SUMIF({funding_range};"社團會費";{amount_range})+'
        f'SUMIF({funding_range};"自籌";{amount_range})'
    )
    ratio_formula = (
        f'=IF(SUM({amount_range})=0;0;('
        f'SUMIF({funding_range};"社團會費";{amount_range})+'
        f'SUMIF({funding_range};"自籌";{amount_range})'
        f')/SUM({amount_range}))'
    )
    pending_formula = f'=COUNTIF({subsidy_range};"待確認")'

    rows = [
        _expense_budget_summary_row(
            "活動總預算",
            total_formula,
            "申請補助總額",
            subsidy_total_formula,
            "自籌總額",
            self_total_formula,
        ),
        _expense_budget_summary_row(
            "學校補助預算",
            school_formula,
            "社團會費預算",
            club_fee_formula,
            "校外補助預算",
            external_formula,
        ),
        _expense_budget_summary_row(
            "自籌預算",
            self_funded_formula,
            "其他經費預算",
            other_formula,
            "待確認補助項目數",
            pending_formula,
        ),
    ]
    rows.append(
        _row_xml(
            [
                _string_cell_xml("自籌比例", "CellSummaryText", "PLabel", span=2),
                _covered_cells_xml(1),
                _float_cell_xml(0, "CellSummaryPercent", formula=ratio_formula),
                _string_cell_xml("以活動總預算為分母", "CellSummaryText", "PBody", span=8),
                _covered_cells_xml(7),
            ],
            "RowSummary",
        )
    )
    return rows


def _expense_budget_signature_rows() -> list[str]:
    return [
        _row_xml(
            [
                _string_cell_xml("製表人", "CellSummaryHeader", "PHeader", span=2),
                _covered_cells_xml(1),
                _string_cell_xml("社團負責人", "CellSummaryHeader", "PHeader", span=3),
                _covered_cells_xml(2),
                _string_cell_xml("指導老師", "CellSummaryHeader", "PHeader", span=3),
                _covered_cells_xml(2),
                _string_cell_xml("審核單位", "CellSummaryHeader", "PHeader", span=3),
                _covered_cells_xml(2),
            ],
            "RowHeader",
        ),
        _row_xml(
            [
                _string_cell_xml("", "CellSummaryText", "PBody", span=2),
                _covered_cells_xml(1),
                _string_cell_xml("", "CellSummaryText", "PBody", span=3),
                _covered_cells_xml(2),
                _string_cell_xml("", "CellSummaryText", "PBody", span=3),
                _covered_cells_xml(2),
                _string_cell_xml("", "CellSummaryText", "PBody", span=3),
                _covered_cells_xml(2),
            ],
            "RowSummary",
        ),
    ]


def _expense_settlement_value_label_row(
    left_label: str,
    right_label: str,
) -> str:
    return _row_xml(
        [
            _string_cell_xml(left_label, "CellLabel", "PLabel"),
            _string_cell_xml("", "CellValue"),
            _string_cell_xml(right_label, "CellLabel", "PLabel"),
            _string_cell_xml("", "CellValue"),
        ]
    )


def _expense_settlement_summary_formula_rows() -> list[str]:
    budget_range = f"[.B{EXPENSE_SETTLEMENT_FIRST_DATA_ROW}:.B{EXPENSE_SETTLEMENT_LAST_DATA_ROW}]"
    actual_range = f"[.C{EXPENSE_SETTLEMENT_FIRST_DATA_ROW}:.C{EXPENSE_SETTLEMENT_LAST_DATA_ROW}]"
    note_range = f"[.D{EXPENSE_SETTLEMENT_FIRST_DATA_ROW}:.D{EXPENSE_SETTLEMENT_LAST_DATA_ROW}]"

    approved_budget_total_formula = f"=SUM({budget_range})"
    actual_expense_total_formula = f"=SUM({actual_range})"
    approved_school_subsidy_formula = (
        f'=SUMIF({note_range};"學校補助";{budget_range})'
    )
    school_subsidy_actual_formula = (
        f'=SUMIF({note_range};"學校補助";{actual_range})'
    )
    execution_ratio_formula = (
        f"=IF(SUM({budget_range})=0;0;SUM({actual_range})/SUM({budget_range}))"
    )
    subsidy_cap_formula = (
        f'=IF(SUM({budget_range})=0;0;MIN('
        f'SUMIF({note_range};"學校補助";{budget_range});'
        f'SUMIF({note_range};"學校補助";{actual_range});'
        f'SUMIF({note_range};"學校補助";{budget_range})*(SUM({actual_range})/SUM({budget_range}))'
        "))"
    )

    return [
        _row_xml(
            [
                _string_cell_xml("支出金額總計", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=approved_budget_total_formula),
                _float_cell_xml(0, "CellSummaryFormula", formula=actual_expense_total_formula),
                _string_cell_xml("預算通過總額 / 實際支出總額", "CellSummaryText"),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("學校補助通過金額", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=approved_school_subsidy_formula),
                _string_cell_xml("", "CellSummaryText"),
                _string_cell_xml("備註為「學校補助」的預算通過金額總和", "CellSummaryText"),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("學校補助實際支出金額", "CellSummaryText", "PLabel"),
                _string_cell_xml("", "CellSummaryText"),
                _float_cell_xml(0, "CellSummaryFormula", formula=school_subsidy_actual_formula),
                _string_cell_xml("備註為「學校補助」的實際支出金額總和", "CellSummaryText"),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("實際執行比例", "CellSummaryText", "PLabel"),
                _string_cell_xml("", "CellSummaryText"),
                _float_cell_xml(0, "CellSummaryFormula", formula=execution_ratio_formula),
                _string_cell_xml("若預算通過總額為 0，比例顯示 0", "CellSummaryText"),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("學校補助核銷金額總計", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=subsidy_cap_formula),
                _string_cell_xml("", "CellSummaryText"),
                _string_cell_xml("採保守 MIN 公式計算", "CellSummaryText"),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("得補助金額上限：A × B / C", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=subsidy_cap_formula),
                _string_cell_xml("", "CellSummaryText"),
                _string_cell_xml("應以申請金額為上限", "CellSummaryText"),
            ],
            "RowSummary",
        ),
    ]


def _expense_settlement_signature_rows() -> list[str]:
    return [
        _row_xml(
            [
                _string_cell_xml("簽核區", "CellSummaryHeader", "PHeader", span=4),
                _covered_cells_xml(3),
            ],
            "RowHeader",
        ),
        _row_xml(
            [
                _string_cell_xml("活動承辦人", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("課外組承辦人", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("組長", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("學務長", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
            ]
        ),
    ]


def _reimbursement_value_label_row(
    left_label: str,
    right_label: str,
    *,
    left_value_style: str = "CellValue",
    right_value_style: str = "CellValue",
) -> str:
    return _row_xml(
        [
            _string_cell_xml(left_label, "CellLabel", "PLabel"),
            _string_cell_xml("", left_value_style),
            _string_cell_xml(right_label, "CellLabel", "PLabel"),
            _string_cell_xml("", right_value_style),
        ]
    )


def _reimbursement_summary_formula_rows() -> list[str]:
    funding_range = (
        f"[.H{REIMBURSEMENT_FIRST_DATA_ROW}:.H{REIMBURSEMENT_LAST_DATA_ROW}]"
    )
    amount_range = (
        f"[.K{REIMBURSEMENT_FIRST_DATA_ROW}:.K{REIMBURSEMENT_LAST_DATA_ROW}]"
    )
    status_range = (
        f"[.L{REIMBURSEMENT_FIRST_DATA_ROW}:.L{REIMBURSEMENT_LAST_DATA_ROW}]"
    )
    receipt_number_range = (
        f"[.G{REIMBURSEMENT_FIRST_DATA_ROW}:.G{REIMBURSEMENT_LAST_DATA_ROW}]"
    )

    return [
        _row_xml(
            [
                _string_cell_xml("支出總金額", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f"=SUM({amount_range})"),
                _string_cell_xml("學校補助支出總金額", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=SUMIF({funding_range};"學校補助";{amount_range})'),
                _string_cell_xml("校外補助支出總金額", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=SUMIF({funding_range};"校外補助";{amount_range})'),
                _string_cell_xml("社團會費支出總金額", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=SUMIF({funding_range};"社團會費";{amount_range})'),
                _string_cell_xml("自籌支出總金額", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=SUMIF({funding_range};"自籌";{amount_range})'),
                _string_cell_xml("其他支出總金額", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=SUMIF({funding_range};"其他";{amount_range})'),
                _string_cell_xml("", "CellSummaryText"),
                _string_cell_xml("", "CellSummaryText"),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("已附憑證筆數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"已附")'),
                _string_cell_xml("待補憑證筆數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"待補")'),
                _string_cell_xml("遺失憑證筆數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"遺失")'),
                _string_cell_xml("不核銷筆數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"不核銷")'),
                _string_cell_xml("單據張數合計", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=SUMPRODUCT(N(LEN({receipt_number_range})>0))'),
                _string_cell_xml("", "CellSummaryText"),
                _string_cell_xml("", "CellSummaryText"),
                _string_cell_xml("", "CellSummaryText"),
                _string_cell_xml("", "CellSummaryText"),
            ],
            "RowSummary",
        ),
    ]


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
                    _blank_cell_xml("CellMoney"),
                    _blank_cell_xml("CellMoney"),
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
        expense_formula = f"=SUMIF({criterion_range};{activity_ref};{expense_range})"
        income_formula = f"=SUMIF({criterion_range};{activity_ref};{income_range})"
        net_formula = f"={_same_sheet_ref('C', row_number)}-{_same_sheet_ref('B', row_number)}"
        unpaid_formula = (
            "=COUNTIFS("
            f"{criterion_range};{activity_ref};"
            f"{paid_status_range};\"否\""
            ")"
        )
        unsettled_formula = (
            "=COUNTIFS("
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
        expense_formula = f"=SUMIF({category_range};{category_ref};{expense_range})"
        income_formula = f"=SUMIF({category_range};{category_ref};{income_range})"
        net_formula = f"={_same_sheet_ref('C', index)}-{_same_sheet_ref('B', index)}"
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


def _expense_settlement_table_xml() -> str:
    column_widths = ["6.6cm", "3.6cm", "3.6cm", "5.0cm"]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [_string_cell_xml("臺北市立大學", "CellBlank", "PTitle", span=4), _covered_cells_xml(3)],
            "RowTitle",
        ),
        _row_xml(
            [_string_cell_xml("社團活動經費收支結算表", "CellBlank", "PTitle", span=4), _covered_cells_xml(3)],
            "RowTitle",
        ),
        _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(4)]),
        _expense_settlement_value_label_row("活動名稱", "活動日期"),
        _expense_settlement_value_label_row("活動地點", "參加人數"),
        _expense_settlement_value_label_row("記錄人", "結算日期"),
        _row_xml(
            [_string_cell_xml(header, "CellHeader", "PHeader") for header in EXPENSE_SETTLEMENT_HEADERS],
            "RowHeader",
        ),
    ]

    for _ in range(EXPENSE_SETTLEMENT_FIRST_DATA_ROW, EXPENSE_SETTLEMENT_LAST_DATA_ROW + 1):
        rows.append(
            _row_xml(
                [
                    _string_cell_xml("", "CellBody"),
                    _blank_cell_xml("CellMoney"),
                    _blank_cell_xml("CellMoney"),
                    _string_cell_xml("", "CellBody", validation_name="validation_settlement_note"),
                ]
            )
        )

    rows.extend(
        [
            _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(4)]),
            _row_xml(
                [
                    _string_cell_xml("結算公式區", "CellSummaryHeader", "PHeader", span=4),
                    _covered_cells_xml(3),
                ],
                "RowHeader",
            ),
            *_expense_settlement_summary_formula_rows(),
            _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(4)]),
            _row_xml(
                [
                    _string_cell_xml("補助公式備註", "CellSummaryHeader", "PHeader", span=4),
                    _covered_cells_xml(3),
                ],
                "RowHeader",
            ),
            _row_xml(
                [_string_cell_xml("得補助金額上限：A × B / C", "CellSummaryText", "PBody", span=4), _covered_cells_xml(3)],
                "RowSummary",
            ),
            _row_xml(
                [_string_cell_xml("A：學校補助通過金額", "CellSummaryText", "PBody", span=4), _covered_cells_xml(3)],
                "RowSummary",
            ),
            _row_xml(
                [_string_cell_xml("B：實際支出總額", "CellSummaryText", "PBody", span=4), _covered_cells_xml(3)],
                "RowSummary",
            ),
            _row_xml(
                [_string_cell_xml("C：預算通過總額", "CellSummaryText", "PBody", span=4), _covered_cells_xml(3)],
                "RowSummary",
            ),
            _row_xml(
                [_string_cell_xml("應以申請金額為上限", "CellSummaryText", "PBody", span=4), _covered_cells_xml(3)],
                "RowSummary",
            ),
            _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(4)]),
            *_expense_settlement_signature_rows(),
        ]
    )

    return (
        f'<table:table table:name="{EXPENSE_SETTLEMENT_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _expense_budget_table_xml() -> str:
    column_widths = [
        "1.1cm",
        "2.4cm",
        "3.1cm",
        "4.2cm",
        "1.7cm",
        "1.8cm",
        "2.1cm",
        "2.3cm",
        "2.5cm",
        "2.6cm",
        "3.0cm",
    ]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [_string_cell_xml("臺北市立大學", "CellBlank", "PTitle", span=11), _covered_cells_xml(10)],
            "RowTitle",
        ),
        _row_xml(
            [_string_cell_xml("「活動名稱」經費預算表", "CellBlank", "PTitle", span=11), _covered_cells_xml(10)],
            "RowTitle",
        ),
        _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(11)]),
        _expense_budget_value_label_row("活動名稱", "活動日期"),
        _expense_budget_value_label_row("主辦社團", "活動負責人"),
        _expense_budget_value_label_row("財務負責人", "製表日期", right_value_style="CellDate"),
        _row_xml(
            [_string_cell_xml(header, "CellHeader", "PHeader") for header in EXPENSE_BUDGET_HEADERS],
            "RowHeader",
        ),
    ]

    for row_number in range(EXPENSE_BUDGET_FIRST_DATA_ROW, EXPENSE_BUDGET_LAST_DATA_ROW + 1):
        serial_number = row_number - EXPENSE_BUDGET_FIRST_DATA_ROW + 1
        rows.append(
            _row_xml(
                [
                    _float_cell_xml(serial_number, "CellNumber"),
                    _string_cell_xml("", "CellBody", validation_name="validation_budget_category"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                    _blank_cell_xml("CellNumber"),
                    _string_cell_xml("", "CellBody"),
                    _blank_cell_xml("CellMoney"),
                    _float_cell_xml(0, "CellMoneyFormula", formula=_expense_budget_item_amount_formula(row_number)),
                    _string_cell_xml("", "CellBody", validation_name="validation_budget_funding_source"),
                    _string_cell_xml("", "CellBody", validation_name="validation_budget_subsidy"),
                    _string_cell_xml("", "CellBody"),
                ]
            )
        )

    rows.extend(
        [
            _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(11)]),
            _row_xml(
                [
                    _string_cell_xml("預算摘要", "CellSummaryHeader", "PHeader", span=11),
                    _covered_cells_xml(10),
                ],
                "RowHeader",
            ),
            *_expense_budget_summary_rows(),
            _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(11)]),
            _row_xml(
                [
                    _string_cell_xml("備註", "CellLabel", "PLabel"),
                    _string_cell_xml("", "CellValue", span=10),
                    _covered_cells_xml(9),
                ]
            ),
            _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(11)]),
            _row_xml(
                [
                    _string_cell_xml("簽核區", "CellSummaryHeader", "PHeader", span=11),
                    _covered_cells_xml(10),
                ],
                "RowHeader",
            ),
            *_expense_budget_signature_rows(),
        ]
    )

    return (
        f'<table:table table:name="{EXPENSE_BUDGET_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _build_expense_budget_content_xml() -> str:
    column_styles_xml, _ = _column_styles_xml(
        [
            "1.1cm",
            "2.4cm",
            "3.1cm",
            "4.2cm",
            "1.7cm",
            "1.8cm",
            "2.1cm",
            "2.3cm",
            "2.5cm",
            "2.6cm",
            "3.0cm",
        ]
    )
    validations_xml = "".join(
        [
            _validation_xml(
                "validation_budget_category",
                EXPENSE_BUDGET_CATEGORY_OPTIONS,
                "請從項目類別清單選擇。",
            ),
            _validation_xml(
                "validation_budget_funding_source",
                EXPENSE_BUDGET_FUNDING_SOURCE_OPTIONS,
                "請從經費來源清單選擇。",
            ),
            _validation_xml(
                "validation_budget_subsidy",
                EXPENSE_BUDGET_SUBSIDY_OPTIONS,
                "請從是否申請補助清單選擇。",
            ),
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
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
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
      {_expense_budget_table_xml()}
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _build_expense_settlement_content_xml() -> str:
    column_styles_xml, _ = _column_styles_xml(["6.6cm", "3.6cm", "3.6cm", "5.0cm"])
    validations_xml = _validation_xml_with_message_type(
        "validation_settlement_note",
        EXPENSE_SETTLEMENT_NOTE_OPTIONS,
        "建議從清單選擇補助來源分類；若需補充說明，可手動調整文字。",
        message_type="warning",
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
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
      {_expense_settlement_table_xml()}
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _reimbursement_detail_table_xml() -> str:
    column_widths = [
        "1.1cm",
        "2.2cm",
        "3.1cm",
        "3.3cm",
        "3.3cm",
        "2.9cm",
        "2.4cm",
        "2.6cm",
        "2.3cm",
        "2.6cm",
        "2.2cm",
        "2.4cm",
        "3.2cm",
        "2.8cm",
    ]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [_string_cell_xml("臺北市立大學", "CellBlank", "PTitle", span=14), _covered_cells_xml(13)],
            "RowTitle",
        ),
        _row_xml(
            [_string_cell_xml("社團活動核銷明細表", "CellBlank", "PTitle", span=14), _covered_cells_xml(13)],
            "RowTitle",
        ),
        _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(14)]),
        _reimbursement_value_label_row("活動名稱", "活動日期", right_value_style="CellDate"),
        _reimbursement_value_label_row("主辦社團", "活動負責人"),
        _reimbursement_value_label_row("財務負責人", "製表日期", right_value_style="CellDate"),
        _row_xml(
            [_string_cell_xml(header, "CellHeader", "PHeader") for header in REIMBURSEMENT_HEADERS],
            "RowHeader",
        ),
    ]

    for row_number in range(REIMBURSEMENT_FIRST_DATA_ROW, REIMBURSEMENT_LAST_DATA_ROW + 1):
        serial_number = row_number - REIMBURSEMENT_FIRST_DATA_ROW + 1
        rows.append(
            _row_xml(
                [
                    _float_cell_xml(serial_number, "CellBody"),
                    _string_cell_xml("", "CellDate"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody", validation_name="validation_receipt_type"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody", validation_name="validation_funding_source"),
                    _string_cell_xml("", "CellBody", validation_name="validation_payment_method"),
                    _string_cell_xml("", "CellBody"),
                    _blank_cell_xml("CellMoney"),
                    _string_cell_xml("", "CellBody", validation_name="validation_receipt_status"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                ]
            )
        )

    rows.extend(
        [
            _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(14)]),
            _row_xml(
                [
                    _string_cell_xml("統計摘要區", "CellSummaryHeader", "PHeader", span=14),
                    _covered_cells_xml(13),
                ],
                "RowHeader",
            ),
            *_reimbursement_summary_formula_rows(),
            _row_xml([_string_cell_xml("", "CellBlank", "PBody") for _ in range(14)]),
            _row_xml(
                [
                    _string_cell_xml("備註區", "CellSummaryHeader", "PHeader", span=14),
                    _covered_cells_xml(13),
                ],
                "RowHeader",
            ),
            _row_xml(
                [
                    _string_cell_xml("可在此補充單據遺失、補件進度、付款差異或附件說明。", "CellSummaryText", "PBody", span=14),
                    _covered_cells_xml(13),
                ],
                "RowSummary",
            ),
        ]
    )

    return (
        f'<table:table table:name="{REIMBURSEMENT_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _build_reimbursement_detail_content_xml() -> str:
    column_styles_xml, _ = _column_styles_xml(
        [
            "1.1cm",
            "2.2cm",
            "3.1cm",
            "3.3cm",
            "3.3cm",
            "2.9cm",
            "2.4cm",
            "2.6cm",
            "2.3cm",
            "2.6cm",
            "2.2cm",
            "2.4cm",
            "3.2cm",
            "2.8cm",
        ]
    )
    validations_xml = "".join(
        [
            _validation_xml("validation_receipt_type", REIMBURSEMENT_RECEIPT_TYPE_OPTIONS, "請從單據類型清單選擇。"),
            _validation_xml("validation_funding_source", REIMBURSEMENT_FUNDING_SOURCE_OPTIONS, "請從經費來源清單選擇。"),
            _validation_xml("validation_payment_method", REIMBURSEMENT_PAYMENT_METHOD_OPTIONS, "請從支付方式清單選擇。"),
            _validation_xml("validation_receipt_status", REIMBURSEMENT_RECEIPT_STATUS_OPTIONS, "請從憑證狀態清單選擇。"),
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
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
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
      {_reimbursement_detail_table_xml()}
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


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
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
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
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
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


def _work_assignment_content_validations_xml() -> str:
    return "".join(
        [
            _validation_xml("validation_work_phase", WORK_ASSIGNMENT_PHASE_OPTIONS, "請從階段清單選擇。"),
            _validation_xml("validation_work_group", WORK_ASSIGNMENT_GROUP_OPTIONS, "請從組別清單選擇，或依實際需要手動調整。"),
            _validation_xml("validation_work_status", WORK_ASSIGNMENT_STATUS_OPTIONS, "請從狀態清單選擇。"),
            _validation_xml("validation_work_priority", WORK_ASSIGNMENT_PRIORITY_OPTIONS, "請從優先程度清單選擇。"),
        ]
    )


def _work_assignment_main_table_xml() -> str:
    column_widths = [
        "1.2cm",
        "2.0cm",
        "2.3cm",
        "3.2cm",
        "4.8cm",
        "2.3cm",
        "2.8cm",
        "2.2cm",
        "2.2cm",
        "1.9cm",
        "1.9cm",
        "3.0cm",
        "2.8cm",
        "2.8cm",
    ]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [
                _string_cell_xml("工作分配表", "CellTitle", "PTitle", span=14),
                _covered_cells_xml(13),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("社團名稱", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("活動名稱", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("活動日期", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellDate"),
                _string_cell_xml("活動地點", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("主辦單位", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("活動總召", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("製表日期", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellDate"),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("備註", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=13),
                _covered_cells_xml(12),
            ]
        ),
        _row_xml([_string_cell_xml("", "CellBlank") for _ in range(14)]),
        _row_xml(
            [_string_cell_xml(header, "CellHeader", "PHeader") for header in WORK_ASSIGNMENT_HEADERS],
            "RowHeader",
        ),
    ]

    for row_number in range(WORK_ASSIGNMENT_FIRST_DATA_ROW, WORK_ASSIGNMENT_LAST_DATA_ROW + 1):
        serial_number = row_number - WORK_ASSIGNMENT_FIRST_DATA_ROW + 1
        rows.append(
            _row_xml(
                [
                    _float_cell_xml(serial_number, "CellNumber"),
                    _string_cell_xml("", "CellBody", validation_name="validation_work_phase"),
                    _string_cell_xml("", "CellBody", validation_name="validation_work_group"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellDate"),
                    _string_cell_xml("", "CellDate"),
                    _string_cell_xml("", "CellBody", validation_name="validation_work_status"),
                    _string_cell_xml("", "CellBody", validation_name="validation_work_priority"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                    _string_cell_xml("", "CellBody"),
                ],
                "RowDefault",
            )
        )

    rows.extend(
        [
            _row_xml([_string_cell_xml("", "CellBlank") for _ in range(14)]),
            _row_xml(
                [
                    _string_cell_xml("重要提醒", "CellSummaryHeader", "PHeader", span=14),
                    _covered_cells_xml(13),
                ],
                "RowHeader",
            ),
            _row_xml(
                [
                    _string_cell_xml("工作項目若延後或取消，請在備註補充原因與替代方案。", "CellSummaryText", "PBody", span=14),
                    _covered_cells_xml(13),
                ],
                "RowSummary",
            ),
            _row_xml(
                [
                    _string_cell_xml("聯絡窗口", "CellSummaryHeader", "PHeader", span=2),
                    _string_cell_xml("", "CellSummaryText", span=5),
                    _covered_cells_xml(4),
                    _string_cell_xml("活動負責人", "CellSummaryHeader", "PHeader", span=2),
                    _string_cell_xml("", "CellSummaryText", span=5),
                    _covered_cells_xml(4),
                ],
                "RowSummary",
            ),
            _row_xml(
                [
                    _string_cell_xml("製表人", "CellSummaryHeader", "PHeader", span=2),
                    _string_cell_xml("", "CellSummaryText", span=3),
                    _covered_cells_xml(2),
                    _string_cell_xml("社團負責人", "CellSummaryHeader", "PHeader", span=2),
                    _string_cell_xml("", "CellSummaryText", span=3),
                    _covered_cells_xml(2),
                    _string_cell_xml("指導老師", "CellSummaryHeader", "PHeader", span=2),
                    _string_cell_xml("", "CellSummaryText", span=2),
                    _covered_cells_xml(1),
                ],
                "RowSummary",
            ),
        ]
    )

    return (
        f'<table:table table:name="{WORK_ASSIGNMENT_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _work_assignment_summary_table_xml() -> str:
    column_widths = ["4.2cm", "2.6cm", "4.0cm", "4.2cm"]
    _, columns_xml = _column_styles_xml(column_widths)
    title_range = _work_assignment_title_range()
    status_range = _work_assignment_status_range()
    priority_range = _work_assignment_priority_range()
    deadline_range = _work_assignment_deadline_range()

    rows = [
        _row_xml(
            [
                _string_cell_xml("統計摘要", "CellTitle", "PTitle", span=4),
                _covered_cells_xml(3),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("統計項目", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("數值", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("統計項目", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("數值", "CellSummaryHeader", "PHeader"),
            ],
            "RowHeader",
        ),
        _row_xml(
            [
                _string_cell_xml("工作項目總數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f"=COUNTA({title_range})"),
                _string_cell_xml("未開始件數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"未開始")'),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("處理中件數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"處理中")'),
                _string_cell_xml("已完成件數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"已完成")'),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("待確認件數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"待確認")'),
                _string_cell_xml("延後件數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"延後")'),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("取消件數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"取消")'),
                _string_cell_xml("高優先工作數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({priority_range};"高")'),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("完成率", "CellSummaryText", "PLabel"),
                _float_cell_xml(
                    0,
                    "CellSummaryPercent",
                    formula=f'=IF(COUNTA({title_range})=0;0;COUNTIF({status_range};"已完成")/COUNTA({title_range}))',
                ),
                _string_cell_xml("逾期未完成件數", "CellSummaryText", "PLabel"),
                _float_cell_xml(
                    0,
                    "CellSummaryFormula",
                    formula=f'=COUNTIFS({deadline_range};"<"&TODAY();{status_range};"<>已完成";{status_range};"<>取消")',
                ),
            ],
            "RowSummary",
        ),
    ]

    return (
        f'<table:table table:name="{WORK_ASSIGNMENT_SUMMARY_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _build_work_assignment_content_xml() -> str:
    main_styles_xml, _ = _column_styles_xml(
        [
            "1.2cm",
            "2.0cm",
            "2.3cm",
            "3.2cm",
            "4.8cm",
            "2.3cm",
            "2.8cm",
            "2.2cm",
            "2.2cm",
            "1.9cm",
            "1.9cm",
            "3.0cm",
            "2.8cm",
            "2.8cm",
        ]
    )
    summary_styles_xml, _ = _column_styles_xml(["4.2cm", "2.6cm", "4.0cm", "4.2cm"])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles>
    {_income_expense_styles_xml(main_styles_xml + summary_styles_xml)}
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      {_work_assignment_content_validations_xml()}
      {_work_assignment_main_table_xml()}
      {_work_assignment_summary_table_xml()}
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _activity_schedule_overview_table_xml() -> str:
    column_widths = ["3.1cm", "2.2cm", "6.0cm", "3.6cm", "4.4cm"]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [
                _string_cell_xml("活動流程表", "CellTitle", "PTitle", span=5),
                _covered_cells_xml(4),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("社團名稱", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("活動名稱", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=2),
                _covered_cells_xml(1),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("活動日期", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("活動地點", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=2),
                _covered_cells_xml(1),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("主辦單位", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("活動負責人", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("", "CellValue"),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("聯絡方式", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("版本／修訂日期", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("", "CellValue"),
            ]
        ),
        _row_xml([_string_cell_xml("", "CellBlank") for _ in range(5)]),
        _row_xml(
            [_string_cell_xml(header, "CellHeader", "PHeader") for header in ACTIVITY_SCHEDULE_OVERVIEW_HEADERS],
            "RowHeader",
        ),
    ]
    rows.extend(
        _row_xml([_string_cell_xml("", "CellBody") for _ in ACTIVITY_SCHEDULE_OVERVIEW_HEADERS])
        for _ in range(ACTIVITY_SCHEDULE_OVERVIEW_ROW_COUNT)
    )
    rows.extend(
        [
            _row_xml([_string_cell_xml("", "CellBlank") for _ in range(5)]),
            _row_xml(
                [
                    _string_cell_xml("工作提醒", "CellSummaryHeader", "PHeader", span=5),
                    _covered_cells_xml(4),
                ],
                "RowHeader",
            ),
            _row_xml(
                [
                    _string_cell_xml("場地布置時間", "CellLabel", "PLabel"),
                    _string_cell_xml("", "CellValue"),
                    _string_cell_xml("報到時間", "CellLabel", "PLabel"),
                    _string_cell_xml("", "CellValue"),
                    _string_cell_xml("", "CellValue"),
                ]
            ),
            _row_xml(
                [
                    _string_cell_xml("活動開始時間", "CellLabel", "PLabel"),
                    _string_cell_xml("", "CellValue"),
                    _string_cell_xml("活動結束時間", "CellLabel", "PLabel"),
                    _string_cell_xml("", "CellValue"),
                    _string_cell_xml("", "CellValue"),
                ]
            ),
            _row_xml(
                [
                    _string_cell_xml("場復時間", "CellLabel", "PLabel"),
                    _string_cell_xml("", "CellValue"),
                    _string_cell_xml("重要注意事項", "CellLabel", "PLabel"),
                    _string_cell_xml("", "CellValue", span=2),
                    _covered_cells_xml(1),
                ]
            ),
            _row_xml(
                [
                    _string_cell_xml("製表人", "CellSummaryHeader", "PHeader"),
                    _string_cell_xml("", "CellSummaryText"),
                    _string_cell_xml("活動負責人", "CellSummaryHeader", "PHeader"),
                    _string_cell_xml("", "CellSummaryText"),
                    _string_cell_xml("", "CellSummaryText"),
                ],
                "RowSummary",
            ),
        ]
    )
    return (
        f'<table:table table:name="{ACTIVITY_SCHEDULE_OVERVIEW_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _activity_schedule_detail_table_xml() -> str:
    column_widths = ["3.1cm", "4.0cm", "2.4cm", "3.2cm", "5.0cm", "3.6cm", "3.6cm", "2.8cm", "3.8cm"]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [
                _string_cell_xml("活動流程表", "CellTitle", "PTitle", span=9),
                _covered_cells_xml(8),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("社團名稱", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=2),
                _covered_cells_xml(1),
                _string_cell_xml("活動名稱", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=2),
                _covered_cells_xml(1),
                _string_cell_xml("活動日期", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("活動地點", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=2),
                _covered_cells_xml(1),
                _string_cell_xml("主辦單位", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=2),
                _covered_cells_xml(1),
                _string_cell_xml("活動負責人", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
            ]
        ),
        _row_xml([_string_cell_xml("", "CellBlank") for _ in range(9)]),
        _row_xml(
            [_string_cell_xml(header, "CellHeader", "PHeader") for header in ACTIVITY_SCHEDULE_DETAIL_HEADERS],
            "RowHeader",
        ),
    ]
    rows.extend(
        _row_xml([_string_cell_xml("", "CellBody") for _ in ACTIVITY_SCHEDULE_DETAIL_HEADERS])
        for _ in range(ACTIVITY_SCHEDULE_DETAIL_ROW_COUNT)
    )
    rows.extend(
        [
            _row_xml([_string_cell_xml("", "CellBlank") for _ in range(9)]),
            _row_xml(
                [
                    _string_cell_xml("確認與簽核區", "CellSummaryHeader", "PHeader", span=9),
                    _covered_cells_xml(8),
                ],
                "RowHeader",
            ),
            _row_xml(
                [
                    _string_cell_xml("製表人", "CellSummaryHeader", "PHeader"),
                    _string_cell_xml("", "CellSummaryText"),
                    _string_cell_xml("活動負責人", "CellSummaryHeader", "PHeader"),
                    _string_cell_xml("", "CellSummaryText"),
                    _string_cell_xml("社團負責人", "CellSummaryHeader", "PHeader"),
                    _string_cell_xml("", "CellSummaryText"),
                    _string_cell_xml("指導老師", "CellSummaryHeader", "PHeader"),
                    _string_cell_xml("", "CellSummaryText", span=2),
                    _covered_cells_xml(1),
                ],
                "RowSummary",
            ),
        ]
    )
    return (
        f'<table:table table:name="{ACTIVITY_SCHEDULE_DETAIL_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _build_activity_schedule_content_xml() -> str:
    overview_styles_xml, _ = _column_styles_xml(["3.1cm", "2.2cm", "6.0cm", "3.6cm", "4.4cm"])
    detail_styles_xml, _ = _column_styles_xml(["3.1cm", "4.0cm", "2.4cm", "3.2cm", "5.0cm", "3.6cm", "3.6cm", "2.8cm", "3.8cm"])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles>
    {_activity_schedule_table_styles_xml(overview_styles_xml + detail_styles_xml)}
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      {_activity_schedule_overview_table_xml()}
      {_activity_schedule_detail_table_xml()}
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _member_roster_content_validations_xml() -> str:
    return "".join(
        [
            _validation_xml(
                "validation_member_type",
                MEMBER_ROSTER_MEMBER_TYPE_OPTIONS,
                "請從身分別清單選擇。",
            ),
            _validation_xml(
                "validation_member_status",
                MEMBER_ROSTER_STATUS_OPTIONS,
                "請從社員狀態清單選擇。",
            ),
            _validation_xml(
                "validation_fee_status",
                MEMBER_ROSTER_FEE_STATUS_OPTIONS,
                "請從社費狀態清單選擇。",
            ),
        ]
    )


def _member_roster_main_table_xml() -> str:
    column_widths = [
        "1.1cm",
        "2.4cm",
        "2.6cm",
        "3.0cm",
        "2.5cm",
        "2.6cm",
        "2.4cm",
        "2.5cm",
        "2.8cm",
        "4.0cm",
        "3.8cm",
        "3.4cm",
        "3.2cm",
    ]
    _, columns_xml = _column_styles_xml(column_widths)
    rows = [
        _row_xml(
            [
                _string_cell_xml("臺北市立大學", "CellTitle", "PTitle", span=13),
                _covered_cells_xml(12),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("{{club_name}} 社員名冊", "CellTitle", "PTitle", span=13),
                _covered_cells_xml(12),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("學年度", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("社團名稱", "CellLabel", "PLabel"),
                _string_cell_xml("臺北市立大學 {{club_name}}", "CellValue", span=3),
                _covered_cells_xml(2),
                _string_cell_xml("製表日期", "CellLabel", "PLabel"),
                _blank_cell_xml("CellDate"),
                _string_cell_xml("製表人", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=4),
                _covered_cells_xml(3),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("備註", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue", span=12),
                _covered_cells_xml(11),
            ]
        ),
        _row_xml([_string_cell_xml("", "CellBlank") for _ in range(13)]),
        _row_xml(
            [_string_cell_xml(header, "CellHeader", "PHeader") for header in MEMBER_ROSTER_HEADERS],
            "RowHeader",
        ),
    ]

    for row_number in range(MEMBER_ROSTER_FIRST_DATA_ROW, MEMBER_ROSTER_LAST_DATA_ROW + 1):
        serial_number = row_number - MEMBER_ROSTER_FIRST_DATA_ROW + 1
        rows.append(
            _row_xml(
                [
                    _float_cell_xml(serial_number, "CellNumber"),
                    _blank_cell_xml("CellBody"),
                    _blank_cell_xml("CellBody"),
                    _blank_cell_xml("CellBody"),
                    _blank_cell_xml("CellBody", validation_name="validation_member_type"),
                    _blank_cell_xml("CellBody"),
                    _blank_cell_xml("CellBody", validation_name="validation_member_status"),
                    _blank_cell_xml("CellBody", validation_name="validation_fee_status"),
                    _blank_cell_xml("CellBody"),
                    _blank_cell_xml("CellBody"),
                    _blank_cell_xml("CellBody"),
                    _blank_cell_xml("CellBody"),
                    _blank_cell_xml("CellBody"),
                ],
                "RowDefault",
            )
        )

    return (
        f'<table:table table:name="{MEMBER_ROSTER_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _member_roster_summary_table_xml() -> str:
    column_widths = ["4.4cm", "2.6cm", "4.4cm", "2.8cm"]
    _, columns_xml = _column_styles_xml(column_widths)
    name_range = _member_roster_name_range()
    department_range = _member_roster_department_range()
    member_type_range = _member_roster_member_type_range()
    status_range = _member_roster_status_range()
    fee_range = _member_roster_fee_range()

    rows = [
        _row_xml(
            [
                _string_cell_xml("統計摘要", "CellTitle", "PTitle", span=4),
                _covered_cells_xml(3),
            ],
            "RowTitle",
        ),
        _row_xml(
            [
                _string_cell_xml("學年度", "CellLabel", "PLabel"),
                _string_cell_xml("", "CellValue"),
                _string_cell_xml("社團名稱", "CellLabel", "PLabel"),
                _string_cell_xml("臺北市立大學 {{club_name}}", "CellValue"),
            ]
        ),
        _row_xml(
            [
                _string_cell_xml("製表日期", "CellLabel", "PLabel"),
                _blank_cell_xml("CellDate"),
                _string_cell_xml("製表人", "CellLabel", "PLabel"),
                _blank_cell_xml("CellValue"),
            ]
        ),
        _row_xml([_string_cell_xml("", "CellBlank") for _ in range(4)]),
        _row_xml(
            [
                _string_cell_xml("統計項目", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("數值", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("統計項目", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("數值", "CellSummaryHeader", "PHeader"),
            ],
            "RowHeader",
        ),
        _row_xml(
            [
                _string_cell_xml("社員總數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f"=COUNTA({name_range})"),
                _string_cell_xml("有效社員數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"有效")'),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("幹部人數", "CellSummaryText", "PLabel"),
                _float_cell_xml(
                    0,
                    "CellSummaryFormula",
                    formula=(
                        f'=COUNTIF({member_type_range};"幹部")+'
                        f'COUNTIF({member_type_range};"社長")+'
                        f'COUNTIF({member_type_range};"副社長")'
                    ),
                ),
                _string_cell_xml("已繳社費人數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({fee_range};"已繳")'),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("未繳社費人數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({fee_range};"未繳")'),
                _string_cell_xml("畢業社員數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"畢業")'),
            ],
            "RowSummary",
        ),
        _row_xml(
            [
                _string_cell_xml("退出社員數", "CellSummaryText", "PLabel"),
                _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({status_range};"退出")'),
                _string_cell_xml("各系級人數統計", "CellSummaryText", "PLabel"),
                _string_cell_xml("可依實際系級自行補齊", "CellSummaryText", "PBody"),
            ],
            "RowSummary",
        ),
        _row_xml([_string_cell_xml("", "CellBlank") for _ in range(4)]),
        _row_xml(
            [
                _string_cell_xml("各系級人數統計", "CellSummaryHeader", "PHeader", span=4),
                _covered_cells_xml(3),
            ],
            "RowHeader",
        ),
        _row_xml(
            [
                _string_cell_xml("系級／班級", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("人數", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("說明", "CellSummaryHeader", "PHeader"),
                _string_cell_xml("備註", "CellSummaryHeader", "PHeader"),
            ],
            "RowHeader",
        ),
    ]

    for _ in range(6):
        rows.append(
            _row_xml(
                [
                    _blank_cell_xml("CellSummaryText"),
                    _float_cell_xml(0, "CellSummaryFormula", formula=f'=COUNTIF({department_range};[.A{len(rows)+1}])'),
                    _blank_cell_xml("CellSummaryText"),
                    _blank_cell_xml("CellSummaryText"),
                ],
                "RowSummary",
            )
        )

    return (
        f'<table:table table:name="{MEMBER_ROSTER_SUMMARY_SHEET_NAME}">'
        f"{columns_xml}"
        f"{''.join(rows)}"
        "</table:table>"
    )


def _build_member_roster_content_xml() -> str:
    main_styles_xml, _ = _column_styles_xml(
        [
            "1.1cm",
            "2.4cm",
            "2.6cm",
            "3.0cm",
            "2.5cm",
            "2.6cm",
            "2.4cm",
            "2.5cm",
            "2.8cm",
            "4.0cm",
            "3.8cm",
            "3.4cm",
            "3.2cm",
        ]
    )
    summary_styles_xml, _ = _column_styles_xml(["4.4cm", "2.6cm", "4.4cm", "2.8cm"])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles>
    {_income_expense_styles_xml(main_styles_xml + summary_styles_xml)}
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      {_member_roster_content_validations_xml()}
      {_member_roster_main_table_xml()}
      {_member_roster_summary_table_xml()}
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _build_spreadsheet_content_xml(template_definition: dict) -> str:
    template_id = template_definition.get("id") or template_definition.get("template_key")
    if template_id == "expense_budget":
        return _build_expense_budget_content_xml()
    if template_id == "income_expense_statement":
        return _build_income_expense_statement_content_xml()
    if template_id == "expense_settlement":
        return _build_expense_settlement_content_xml()
    if template_id == "reimbursement_detail":
        return _build_reimbursement_detail_content_xml()
    if template_id == "activity_schedule":
        return _build_activity_schedule_content_xml()
    if template_id == "work_assignment":
        return _build_work_assignment_content_xml()
    if template_id in {"member_roster", "member_roster_ods"}:
        return _build_member_roster_content_xml()
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
