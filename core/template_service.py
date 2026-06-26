from __future__ import annotations

from pathlib import Path

from core.database import DATA_DIR
from core.filename import roc_date_string, sanitize_filename_component
from generators.ods_generator import generate_ods_template
from generators.odt_generator import generate_odt_template
from generators.template_renderer import copy_odt_template


TEMPLATE_LIBRARY_CATEGORIES = [
    "日常行政型",
    "專案活動型",
    "社團運作型",
    "財務與清冊型",
]

DEFAULT_TEMPLATE_OUTPUT_DIR = DATA_DIR / "generated" / "templates"


def _odt_template(
    template_id: str,
    name: str,
    template_type: str,
    usage_description: str,
    basic_fields: list[str],
    outline_fields: list[str],
    instructions: list[str],
    evaluation_category: str = "",
    linked_document_type: str | None = None,
    placeholder_template_path: str | None = None,
) -> dict:
    return {
        "id": template_id,
        "name": name,
        "library_category": "",
        "template_type": template_type,
        "suggested_format": "ODT",
        "evaluation_category": evaluation_category,
        "usage_description": usage_description,
        "basic_fields": basic_fields,
        "outline_fields": outline_fields,
        "instructions": instructions,
        "linked_document_type": linked_document_type,
        "placeholder_template_path": placeholder_template_path,
    }


def _ods_template(
    template_id: str,
    name: str,
    template_type: str,
    usage_description: str,
    basic_fields: list[str],
    table_headers: list[str],
    instructions: list[str],
    evaluation_category: str = "",
) -> dict:
    return {
        "id": template_id,
        "name": name,
        "library_category": "",
        "template_type": template_type,
        "suggested_format": "ODS",
        "evaluation_category": evaluation_category,
        "usage_description": usage_description,
        "basic_fields": basic_fields,
        "table_headers": table_headers,
        "instructions": instructions,
    }


TEMPLATE_DEFINITIONS = {
    "日常行政型": [
        _odt_template(
            "meeting_notice_odt",
            "開會通知單",
            "行政通知",
            "用於正式通知開會時間、地點、事由、出席者與聯絡資訊。",
            ["受文者", "發文日期", "發文字號", "開會事由", "開會時間", "開會地點"],
            ["正式通知欄位", "出列席名單", "用印處"],
            ["請於寄送前補齊發文字號、聯絡電話與出席者。"],
            "2.社團行政_管理運作",
            linked_document_type="開會通知單",
            placeholder_template_path="templates/odt_placeholders/meeting_notice_template.odt",
        ),
        _odt_template(
            "meeting_agenda_odt",
            "會議議程",
            "會議文件",
            "用於會前整理議程順序、報告事項與討論重點。",
            ["會議名稱", "日期", "主席", "記錄人員", "出席對象"],
            ["報告事項", "討論事項", "臨時動議"],
            ["建議會前先編號各議案，方便會後整理紀錄。"],
            "2.社團行政_管理運作",
            linked_document_type="會議議程",
        ),
        _odt_template(
            "meeting_minutes_template_odt",
            "會議紀錄",
            "會議文件",
            "用於會後整理正式會議紀錄與決議事項。",
            ["會議名稱", "日期", "時間", "地點", "主席", "記錄人員"],
            ["出席與請假", "討論摘要", "決議事項", "待辦事項"],
            ["若已在 Generate 建立草稿，可再用此範本做手動整理。"],
            "2.社團行政_管理運作",
            linked_document_type="會議紀錄",
            placeholder_template_path="templates/odt_placeholders/meeting_minutes_template.odt",
        ),
        _ods_template(
            "attendance_sheet_ods",
            "出席簽到表",
            "名單表單",
            "用於會議或活動現場簽到、簽退與聯絡資料確認。",
            ["活動名稱", "日期", "地點"],
            ["序號", "姓名", "系級", "身分", "簽到", "簽退", "備註"],
            ["可於 LibreOffice 或 Google Sheets 直接補齊資料。"],
            "2.社團行政_管理運作",
        ),
        _ods_template(
            "cadre_roster_ods",
            "幹部名冊",
            "名冊管理",
            "用於整理幹部職稱、分工與聯絡資訊。",
            ["學年度", "社團名稱"],
            ["職稱", "姓名", "系級", "電話", "Email", "職責"],
            ["建議每次幹部改選後即更新。"],
            "3.社團行政_社團資料保存",
        ),
        _ods_template(
            "member_roster_ods",
            "社員名冊",
            "名冊管理",
            "用於整理社員基本資料與參與狀況。",
            ["學年度", "社團名稱"],
            ["姓名", "系級", "電話", "Email", "入社日期", "備註"],
            ["可依活動參與情形增加欄位。"],
            "3.社團行政_社團資料保存",
        ),
        _ods_template(
            "handover_inventory_ods",
            "交接清冊",
            "交接管理",
            "用於整理幹部交接項目、檔案位置與完成情況。",
            ["交接屆次", "交接日期"],
            ["項目", "內容說明", "前任負責人", "接手人", "檔案位置", "狀態"],
            ["建議與雲端資料夾連結或紙本存放位置一起記錄。"],
            "2.社團行政_管理運作",
        ),
    ],
    "專案活動型": [
        _odt_template(
            "activity_proposal_odt",
            "活動企劃書",
            "活動企劃",
            "用於整理活動目標、流程、分工、預算與風險控管。",
            ["活動名稱", "活動日期", "主辦單位", "活動地點", "活動對象"],
            ["活動目標", "流程規劃", "人力分工", "風險與備案"],
            ["企劃定稿後可另搭配預算表與流程表。"],
            "6.社團活動_社團活動",
            linked_document_type="活動企劃書",
            placeholder_template_path="templates/odt_placeholders/activity_proposal_template.odt",
        ),
        _ods_template(
            "activity_rundown_coarse_ods",
            "活動粗流程表",
            "活動執行",
            "用於安排活動主要時段、負責人與里程碑。",
            ["活動名稱", "活動日期", "總召"],
            ["時段", "流程名稱", "重點事項", "負責人", "備註"],
            ["適合先做大方向節奏安排。"],
            "6.社團活動_社團活動",
        ),
        _ods_template(
            "activity_rundown_detail_ods",
            "活動細流程表",
            "活動執行",
            "用於拆解現場節點、 cue 點與工作銜接。",
            ["活動名稱", "活動日期", "場地"],
            ["時間", "內容", "Cue", "負責人", "器材", "風險提醒"],
            ["活動前彩排時可直接使用。"],
            "6.社團活動_社團活動",
        ),
        _ods_template(
            "staff_assignment_ods",
            "工作分工表",
            "活動執行",
            "用於整理活動前、中、後各組分工。",
            ["活動名稱", "總召"],
            ["工作項目", "負責人", "協作者", "完成期限", "狀態", "備註"],
            ["建議與細流程表搭配使用。"],
            "6.社團活動_社團活動",
        ),
        _odt_template(
            "activity_report_odt",
            "活動成果報告",
            "成果整理",
            "用於整理活動成果、參與情形、照片說明與檢討。",
            ["活動名稱", "活動日期", "活動地點", "參與人數"],
            ["活動摘要", "成果亮點", "照片與附件說明", "後續建議"],
            ["可搭配簽到表、檢討會紀錄一同歸檔。"],
            "6.社團活動_社團活動",
            linked_document_type="活動成果報告",
        ),
        _odt_template(
            "activity_review_minutes_odt",
            "活動檢討會紀錄",
            "檢討文件",
            "用於活動結束後整理問題、經驗與改進方向。",
            ["活動名稱", "檢討日期", "主持人", "記錄人員"],
            ["流程檢討", "宣傳檢討", "行政與器材檢討", "待改善事項"],
            ["建議活動結束一週內完成。"],
            "6.社團活動_社團活動",
            linked_document_type="活動檢討會紀錄",
        ),
    ],
    "社團運作型": [
        _ods_template(
            "evaluation_checklist_ods",
            "社團評鑑資料檢核表",
            "評鑑整理",
            "用於盤點七大評鑑項目的必要文件與目前狀態。",
            ["學年度", "社團名稱"],
            ["評鑑分類", "必要文件", "目前狀態", "檔案位置", "備註"],
            ["可搭配 Dashboard 與 Evaluation 頁一起使用。"],
        ),
        _odt_template(
            "constitution_summary_odt",
            "組織章程整理表",
            "評鑑整理",
            "用於整理章程內容、修正紀錄與版本來源。",
            ["社團名稱", "整理日期", "最近修正日期"],
            ["章程重點", "修正紀錄", "附件說明"],
            ["可作為正式章程檔的輔助整理頁。"],
            "1.社團行政_組織章程",
        ),
        _odt_template(
            "annual_plan_odt",
            "年度計畫",
            "評鑑整理",
            "用於整理年度目標、重點活動與執行方向。",
            ["學年度", "社團名稱", "主要目標"],
            ["年度活動規劃", "組織運作重點", "預期成果"],
            ["可搭配年度行事曆與執行對照表。"],
            "4.社團行政_年度計畫",
            linked_document_type="年度計畫",
        ),
        _ods_template(
            "annual_calendar_ods",
            "年度行事曆",
            "評鑑整理",
            "用於整理全年活動時程、重要會議與交接節點。",
            ["學年度", "社團名稱"],
            ["月份", "日期", "活動 / 會議", "主責幹部", "備註"],
            ["建議與年度計畫同步維護。"],
            "4.社團行政_年度計畫",
        ),
        _ods_template(
            "activity_archive_list_ods",
            "活動資料保存清單",
            "評鑑整理",
            "用於列出各活動是否具備企劃、成果、照片、簽到等資料。",
            ["學年度", "社團名稱"],
            ["活動名稱", "企劃書", "成果報告", "照片", "簽到表", "備註"],
            ["適合檢查活動資料是否完整留存。"],
            "3.社團行政_社團資料保存",
        ),
        _odt_template(
            "service_learning_report_odt",
            "服務學習成果報告",
            "評鑑整理",
            "用於整理服務學習活動目標、執行過程與反思。",
            ["活動名稱", "服務日期", "服務地點", "合作單位"],
            ["服務內容", "成果與影響", "參與者反思", "後續建議"],
            ["若社團有服務性活動，建議固定用此類格式整理。"],
            "7.社團活動_服務學習",
        ),
    ],
    "財務與清冊型": [
        _ods_template(
            "ledger_ods",
            "收支帳冊",
            "財務表單",
            "用於平時記錄收入、支出、餘額與核銷狀態。",
            ["學年度", "社團名稱", "會計期間"],
            ["日期", "科目", "摘要", "收入", "支出", "餘額", "備註"],
            ["建議搭配單據保存總表與年度收支總表使用。"],
            "5.社團行政_財務管理",
        ),
        _ods_template(
            "activity_budget_ods",
            "活動預算表",
            "活動財務",
            "用於估算活動收入、支出與實際執行情況。",
            ["活動名稱", "預算版本"],
            ["項目", "分類", "預估金額", "實際金額", "差異", "備註"],
            ["可於活動結束後作為成果報告附件。"],
            "6.社團活動_社團活動",
        ),
        _ods_template(
            "annual_financial_summary_ods",
            "年度收支總表",
            "評鑑整理",
            "用於整理全年收入、支出與結餘統計。",
            ["學年度", "社團名稱"],
            ["月份", "收入", "支出", "結餘", "備註"],
            ["可由平時收支帳冊整理後彙整。"],
            "5.社團行政_財務管理",
        ),
    ],
}


for category_name, templates in TEMPLATE_DEFINITIONS.items():
    for template_definition in templates:
        template_definition["library_category"] = category_name

TEMPLATE_DEFINITIONS_BY_ID = {
    definition["id"]: definition
    for definitions in TEMPLATE_DEFINITIONS.values()
    for definition in definitions
}

TEMPLATE_DEFINITION_ALIASES = {
    "會議通知": "meeting_notice_odt",
}

for template_id, definition in TEMPLATE_DEFINITIONS_BY_ID.items():
    TEMPLATE_DEFINITION_ALIASES.setdefault(definition["name"], template_id)


def resolve_template_definition_id(template_id: str) -> str:
    return TEMPLATE_DEFINITION_ALIASES.get(template_id, template_id)


def list_template_definitions(category: str | None = None) -> list[dict]:
    if category is None:
        return [
            TEMPLATE_DEFINITIONS_BY_ID[template_id].copy()
            for template_id in TEMPLATE_DEFINITIONS_BY_ID
        ]

    if category not in TEMPLATE_DEFINITIONS:
        raise ValueError(f"不支援的範本分類: {category}")

    return [definition.copy() for definition in TEMPLATE_DEFINITIONS[category]]


def get_template_definition(template_id: str) -> dict:
    resolved_id = resolve_template_definition_id(template_id)
    definition = TEMPLATE_DEFINITIONS_BY_ID.get(resolved_id)
    if definition is None:
        raise ValueError(f"找不到範本: {template_id}")
    return definition.copy()


def build_template_preview_data(template_id: str) -> dict:
    resolved_id = resolve_template_definition_id(template_id)
    definition = get_template_definition(resolved_id)

    preview_builders = {
        "meeting_minutes_template_odt": _build_meeting_minutes_preview_data,
        "meeting_notice_odt": _build_meeting_notice_preview_data,
        "activity_proposal_odt": _build_activity_proposal_preview_data,
    }
    builder = preview_builders.get(resolved_id, _build_generic_preview_data)
    return builder(definition)


def generate_template_file(
    template_id: str,
    output_dir: Path | str | None = None,
) -> Path:
    definition = get_template_definition(template_id)
    output_dir_path = Path(output_dir) if output_dir is not None else DEFAULT_TEMPLATE_OUTPUT_DIR
    output_dir_path.mkdir(parents=True, exist_ok=True)
    filename = _build_template_filename(definition)
    output_path = output_dir_path / filename

    format_name = definition["suggested_format"].upper()
    if format_name == "ODT":
        if definition.get("placeholder_template_path"):
            return copy_odt_template(definition["placeholder_template_path"], output_path)
        return generate_odt_template(definition, output_path=output_path)
    if format_name == "ODS":
        return generate_ods_template(definition, output_path=output_path)
    raise ValueError(f"不支援的範本格式: {definition['suggested_format']}")


def _build_template_filename(definition: dict) -> str:
    extension = definition["suggested_format"].lower()
    safe_name = sanitize_filename_component(definition["name"], fallback="template")
    safe_category = sanitize_filename_component(
        definition["library_category"],
        fallback="templates",
    )
    return f"{roc_date_string()}_{safe_category}_{safe_name}.{extension}"


def _build_meeting_minutes_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["{{organization_name}}文件", "{{meeting_title}}會議紀錄"],
        "meta_rows": [
            ("會議時間", "{{meeting_date}} {{meeting_time}}"),
            ("會議地點", "實體：{{physical_location}} / 線上：{{online_location}}"),
            ("主席", "{{chair}}"),
            ("出席人員", "{{attendees}}"),
            ("列席人員", "{{observers}}"),
            ("請假人員", "{{absentees}}"),
            ("記錄人員", "{{recorder}}"),
        ],
        "sections": [
            {
                "title": "壹、會議議程",
                "items": ["一、報告事項", "二、討論事項", "三、臨時動議", "四、申明與補述"],
            }
        ],
        "tables": [],
        "decor": {},
        "footnote": "此為版型預覽，實際格式以下載 ODT 為準。",
    }


def _build_meeting_notice_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["{{organization_name}} 開會通知單"],
        "meta_rows": [
            ("受文者", "{{recipient}}"),
            ("發文日期", "{{document_date}}"),
            ("發文字號", "{{document_number}}"),
            ("速別", "{{priority}}"),
            ("密等及解密條件或保密期限", "{{security_level}}"),
            ("附件", "{{attachments}}"),
            ("開會事由", "{{meeting_reason}}"),
            ("開會時間", "{{meeting_datetime}}"),
            ("開會地點", "{{meeting_location}}"),
            ("主持人", "{{host}}"),
            ("聯絡人及電話", "{{contact_person}} / {{contact_phone}}"),
            ("出席者", "{{attendees}}"),
            ("列席者", "{{observers}}"),
            ("備註", "{{note}}"),
        ],
        "sections": [],
        "tables": [],
        "decor": {
            "binding_marks": ["裝", "訂"],
            "page_footer": "第1頁　共1頁",
        },
        "footnote": "此為版型預覽，實際格式以下載 ODT 為準。",
    }


def _build_activity_proposal_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["{{school_name}}「{{activity_name}}」活動企劃書"],
        "meta_rows": [],
        "sections": [
            {
                "title": "主要章節",
                "items": [
                    "1、活動主題",
                    "2、活動宗旨",
                    "3、預期效益",
                    "4、指導單位",
                    "5、主辦單位",
                    "6、協辦單位",
                    "7、活動對象",
                    "8、活動內容",
                    "9、活動地點",
                    "10、活動時間流程表",
                    "11、聯絡方式",
                    "12、宣傳方式",
                    "13、工作人員、內容分配與預定進度",
                    "14、活動預算",
                    "15、所需設備清單",
                    "16、需學校協助事項",
                    "17、附件",
                ],
            }
        ],
        "tables": [
            {
                "title": "活動時間流程表",
                "headers": ["時間", "內容", "負責人", "備註"],
                "rows": [["18:00", "報到與入場", "活動組", ""], ["18:30", "活動流程", "主持人", ""]],
            },
            {
                "title": "活動預算",
                "headers": ["項目", "說明", "數量 / 單位", "單價", "金額", "預算來源", "備註"],
                "rows": [["", "", "", "", "", "", ""], ["", "", "", "", "", "", ""]],
            },
        ],
        "decor": {},
        "footnote": "此為版型預覽，實際格式以下載 ODT 為準。",
    }


def _build_generic_preview_data(definition: dict) -> dict:
    meta_rows = [
        (field, "＿＿＿＿＿＿＿＿")
        for field in definition.get("basic_fields", [])[:6]
    ]
    sections = []
    outline_fields = definition.get("outline_fields", [])
    if outline_fields:
        sections.append(
            {
                "title": "主要章節",
                "items": [f"{index}. {field}" for index, field in enumerate(outline_fields, start=1)],
            }
        )

    tables = []
    table_headers = definition.get("table_headers", [])
    if table_headers:
        tables.append(
            {
                "title": "表格欄位",
                "headers": table_headers,
                "rows": [["" for _ in table_headers] for _ in range(3)],
            }
        )

    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": [definition["name"]],
        "meta_rows": meta_rows,
        "sections": sections,
        "tables": tables,
        "decor": {},
        "footnote": (
            f"此為版型預覽，實際格式以下載 {definition['suggested_format']} 為準。"
        ),
    }
