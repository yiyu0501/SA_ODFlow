from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from core.database import DATA_DIR
from core.filename import roc_date_string, sanitize_filename_component
from core.template_registry import (
    FORMAL_TEMPLATE_FORBIDDEN_BODY_TEXT,
    FORMAL_TEMPLATE_REGISTRY,
    FORMAL_TEMPLATE_REGISTRY_BY_KEY,
    TEMPLATE_LIBRARY_CATEGORIES,
)
from generators.ods_generator import generate_ods_template
from generators.odt_generator import generate_odt_template
from generators.template_renderer import copy_odt_template


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


LEGACY_TEMPLATE_DEFINITIONS = {
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
        _odt_template(
            "activity_application_odt",
            "活動申請表",
            "行政申請",
            "用於送交學校行政流程審核的一頁式活動申請表。",
            ["活動名稱", "活動時間", "活動地點", "申請日期", "主辦社團", "參加人數"],
            ["前年社團評鑑", "活動性質", "宗旨", "活動內容或講題", "活動申請人", "行政簽核保留區"],
            ["應維持 A4 橫式一頁，行政欄位由學校審核單位填寫。"],
            "6.社團活動_社團活動",
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


for category_name, templates in LEGACY_TEMPLATE_DEFINITIONS.items():
    for template_definition in templates:
        template_definition["library_category"] = category_name

LEGACY_TEMPLATE_DEFINITIONS_BY_ID = {
    definition["id"]: definition
    for definitions in LEGACY_TEMPLATE_DEFINITIONS.values()
    for definition in definitions
}


def _build_formal_definition(registry_entry: dict) -> dict:
    definition = {
        "id": registry_entry["template_key"],
        "template_key": registry_entry["template_key"],
        "name": registry_entry["display_name"],
        "display_name": registry_entry["display_name"],
        "aliases": list(registry_entry["aliases"]),
        "library_category": registry_entry["category"],
        "category": registry_entry["category"],
        "template_type": "正式範本",
        "suggested_format": registry_entry["format"],
        "format": registry_entry["format"],
        "priority": registry_entry["priority"],
        "supports_blank_download": registry_entry["supports_blank_download"],
        "supports_generate_document": registry_entry["supports_generate_document"],
        "spec_path": registry_entry["spec_path"],
        "blank_template_path": registry_entry["blank_template_path"],
        "renderer": registry_entry["renderer"],
        "preview_type": registry_entry["preview_type"],
        "implementation_status": registry_entry["implementation_status"],
        "usage_description": registry_entry["short_description"],
        "linked_document_type": registry_entry.get("linked_document_type"),
        "evaluation_category": registry_entry.get("evaluation_category", ""),
        "legacy_definition_id": registry_entry.get("legacy_definition_id"),
        "forbidden_body_text": list(FORMAL_TEMPLATE_FORBIDDEN_BODY_TEXT),
        "basic_fields": [],
        "outline_fields": [],
        "table_headers": [],
        "instructions": [],
    }

    legacy_definition_id = registry_entry.get("legacy_definition_id")
    if legacy_definition_id and legacy_definition_id in LEGACY_TEMPLATE_DEFINITIONS_BY_ID:
        legacy_definition = LEGACY_TEMPLATE_DEFINITIONS_BY_ID[legacy_definition_id]
        for field_name in [
            "template_type",
            "basic_fields",
            "outline_fields",
            "table_headers",
            "instructions",
            "placeholder_template_path",
        ]:
            if field_name in legacy_definition:
                definition[field_name] = deepcopy(legacy_definition[field_name])
        if not definition["evaluation_category"]:
            definition["evaluation_category"] = legacy_definition.get("evaluation_category", "")

    return definition


FORMAL_TEMPLATE_DEFINITIONS = {
    category: []
    for category in TEMPLATE_LIBRARY_CATEGORIES
}
for registry_entry in FORMAL_TEMPLATE_REGISTRY:
    FORMAL_TEMPLATE_DEFINITIONS[registry_entry["category"]].append(
        _build_formal_definition(registry_entry)
    )

TEMPLATE_DEFINITIONS = FORMAL_TEMPLATE_DEFINITIONS
TEMPLATE_DEFINITIONS_BY_ID = {
    definition["id"]: definition
    for definitions in TEMPLATE_DEFINITIONS.values()
    for definition in definitions
}


TEMPLATE_DEFINITION_ALIASES: dict[str, str] = {}
for registry_entry in FORMAL_TEMPLATE_REGISTRY:
    template_key = registry_entry["template_key"]
    TEMPLATE_DEFINITION_ALIASES[template_key] = template_key
    TEMPLATE_DEFINITION_ALIASES[registry_entry["display_name"]] = template_key
    for alias in registry_entry["aliases"]:
        TEMPLATE_DEFINITION_ALIASES[alias] = template_key


def resolve_template_definition_id(template_id: str) -> str:
    if template_id in LEGACY_TEMPLATE_DEFINITIONS_BY_ID:
        return template_id
    if template_id in TEMPLATE_DEFINITION_ALIASES:
        return TEMPLATE_DEFINITION_ALIASES[template_id]
    if template_id in TEMPLATE_DEFINITIONS_BY_ID:
        return template_id
    return template_id


def list_template_definitions(category: str | None = None) -> list[dict]:
    if category is None:
        return [
            deepcopy(TEMPLATE_DEFINITIONS_BY_ID[entry["template_key"]])
            for entry in FORMAL_TEMPLATE_REGISTRY
        ]

    if category not in TEMPLATE_DEFINITIONS:
        raise ValueError(f"不支援的範本分類: {category}")

    return [deepcopy(definition) for definition in TEMPLATE_DEFINITIONS[category]]


def get_template_definition(template_id: str) -> dict:
    resolved_id = resolve_template_definition_id(template_id)
    if resolved_id in TEMPLATE_DEFINITIONS_BY_ID:
        return deepcopy(TEMPLATE_DEFINITIONS_BY_ID[resolved_id])
    if resolved_id in LEGACY_TEMPLATE_DEFINITIONS_BY_ID:
        return deepcopy(LEGACY_TEMPLATE_DEFINITIONS_BY_ID[resolved_id])
    raise ValueError(f"找不到範本: {template_id}")


def get_template_registry_entry(template_key: str) -> dict:
    registry_entry = FORMAL_TEMPLATE_REGISTRY_BY_KEY.get(template_key)
    if registry_entry is None:
        raise ValueError(f"找不到範本 registry: {template_key}")
    return deepcopy(registry_entry)


def _get_generation_definition(template_id: str) -> tuple[dict, dict]:
    resolved_id = resolve_template_definition_id(template_id)
    if resolved_id in TEMPLATE_DEFINITIONS_BY_ID:
        canonical_definition = TEMPLATE_DEFINITIONS_BY_ID[resolved_id]
        if not canonical_definition["supports_blank_download"]:
            raise ValueError(
                f"範本「{canonical_definition['name']}」目前僅完成 registry 登錄，尚未提供正式空白範本下載。"
            )
        legacy_definition_id = canonical_definition.get("legacy_definition_id")
        if legacy_definition_id and legacy_definition_id in LEGACY_TEMPLATE_DEFINITIONS_BY_ID:
            return canonical_definition, LEGACY_TEMPLATE_DEFINITIONS_BY_ID[legacy_definition_id]
        return canonical_definition, canonical_definition

    if resolved_id in LEGACY_TEMPLATE_DEFINITIONS_BY_ID:
        legacy_definition = LEGACY_TEMPLATE_DEFINITIONS_BY_ID[resolved_id]
        return legacy_definition, legacy_definition

    raise ValueError(f"找不到範本: {template_id}")


def build_template_preview_data(template_id: str) -> dict:
    resolved_id = resolve_template_definition_id(template_id)
    definition = get_template_definition(resolved_id)

    preview_builders = {
        "meeting_minutes": _build_meeting_minutes_preview_data,
        "meeting_notice": _build_meeting_notice_preview_data,
        "attendance_sheet": _build_attendance_sheet_preview_data,
        "activity_proposal": _build_activity_proposal_preview_data,
        "activity_application": _build_activity_application_preview_data,
        "activity_schedule": _build_activity_schedule_preview_data,
        "activity_result_report": _build_activity_result_report_preview_data,
        "expense_budget": _build_expense_budget_preview_data,
        "income_expense_statement": _build_income_expense_statement_preview_data,
        "expense_settlement": _build_expense_settlement_preview_data,
        "reimbursement_detail": _build_reimbursement_detail_preview_data,
    }
    builder = preview_builders.get(resolved_id, _build_generic_preview_data)
    return builder(definition)


def generate_template_file(
    template_id: str,
    output_dir: Path | str | None = None,
) -> Path:
    definition, generation_definition = _get_generation_definition(template_id)
    output_dir_path = Path(output_dir) if output_dir is not None else DEFAULT_TEMPLATE_OUTPUT_DIR
    output_dir_path.mkdir(parents=True, exist_ok=True)
    filename = _build_template_filename(definition)
    output_path = output_dir_path / filename

    format_name = definition["suggested_format"].upper()
    if format_name == "ODT":
        placeholder_template_path = generation_definition.get("placeholder_template_path")
        if placeholder_template_path:
            return copy_odt_template(placeholder_template_path, output_path)
        return generate_odt_template(generation_definition, output_path=output_path)
    if format_name == "ODS":
        return generate_ods_template(generation_definition, output_path=output_path)
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
        "header_lines": ["{{school_name}}{{club_name}}", "第{{meeting_number}}次{{meeting_type}}紀錄"],
        "meta_rows": [
            ("頁首資訊", "{{school_name}}{{club_name}}　製作日期：{{document_date}}"),
            ("會議名稱", "{{meeting_title}}"),
            ("會議日期", "{{meeting_date}}"),
            ("會議時間", "{{start_time}} 至 {{end_time}}"),
            ("會議地點", "{{location}}"),
            ("主席", "{{chair}}"),
            ("記錄人員", "{{recorder}}"),
            ("出席人員", "{{attendees}}"),
            ("列席人員", "{{observers}}"),
            ("請假人員", "{{absentees}}"),
            ("缺席人員", "{{missing_members}}"),
        ],
        "sections": [
            {
                "title": "壹、會議開始",
                "items": ["一、上次會議決議追蹤", "二、主席致詞"],
            },
            {
                "title": "貳、報告事項",
                "items": ["一、報告主題", "報告人", "內容"],
            },
            {
                "title": "參、討論事項",
                "items": ["案由一：{{title}}", "決議", "表決結果", "負責人", "執行期限", "備註"],
            },
            {
                "title": "肆、臨時動議",
                "items": ["案由一：{{motion_title}}", "提案人", "決議"],
            },
            {
                "title": "伍、散會",
                "items": ["散會時間", "下次會議時間", "備註"],
            },
        ],
        "tables": [
            {
                "title": "待辦事項",
                "headers": ["項次", "事項", "負責人", "期限", "備註"],
                "rows": [["1", "", "", "", ""], ["2", "", "", "", ""]],
            },
            {
                "title": "簽核欄位",
                "headers": ["製表人", "主席", "社團負責人", "指導老師"],
                "rows": [["", "", "", ""]],
            },
        ],
        "decor": {"page_footer": "第1頁　共1頁"},
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
        "header_lines": ["{{school_name}}「{{activity_name}}」活動企畫書"],
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


def _build_activity_application_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["臺北市立大學　社團活動申請表"],
        "meta_rows": [
            ("注意事項", "請於活動二週前完成申請並隨表附活動企畫書"),
            ("注意事項", "申請校內場地，請增附場地申請表"),
            ("活動名稱", "{{activity_name}}"),
            ("活動時間", "{{start_date}} {{start_time}} 起至 {{end_date}} {{end_time}} 止"),
            ("活動地點", "{{location}}"),
            ("申請日期", "{{application_date}}"),
            ("主辦社團", "{{club_name}}"),
            ("參加人數", "{{participant_count}} 人"),
        ],
        "sections": [
            {"title": "前年社團評鑑", "items": ["特優□　優等□　甲等□　乙等□"]},
            {
                "title": "活動性質",
                "items": [
                    "□ 幹訓或營隊",
                    "□ 學術活動",
                    "□ 刊物出版",
                    "□ 康樂活動",
                    "□ 社會服務活動",
                    "□ 發展社團特色活動",
                    "□ 其他符合社團宗旨之綜合性活動",
                    "□ 學校委辦或代表學校之活動",
                ],
            },
            {"title": "宗旨", "items": ["{{purpose_summary}}"]},
            {"title": "活動內容或講題", "items": ["{{content_summary}}"]},
            {"title": "使用種類與額度由課外活動組填寫", "items": []},
        ],
        "tables": [
            {
                "title": "申請人與經費區",
                "headers": ["活動申請人", "系別", "班別", "手機", "申請補助", "自籌經費", "合計"],
                "rows": [["{{applicant_name}}", "{{applicant_department}}", "{{applicant_class}}", "{{applicant_phone}}", "{{subsidy_amount}}", "{{self_funded_amount}}", "{{total_amount}}"]],
            },
            {
                "title": "行政簽核區",
                "headers": ["承辦人", "單位主管", "組長", "學務長", "會辦單位", "校長"],
                "rows": [["", "", "", "", "", ""]],
            },
        ],
        "decor": {"page_footer": "A4 橫式一頁預覽"},
        "footnote": "此為橫式行政表單預覽，實際格式以下載 ODT 為準。",
    }


def _build_activity_schedule_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["活動流程表"],
        "meta_rows": [
            ("社團名稱", "{{club_name}}"),
            ("活動名稱", "{{activity_name}}"),
            ("活動日期", "{{activity_date}}"),
            ("活動地點", "{{activity_location}}"),
            ("主辦單位", "{{club_name}}"),
            ("活動負責人", "{{activity_owner}}"),
        ],
        "sections": [
            {
                "title": "工作提醒",
                "items": ["場地布置時間", "報到時間", "活動開始時間", "活動結束時間", "場復時間", "重要注意事項"],
            },
            {
                "title": "確認與簽核區",
                "items": ["製表人", "活動負責人", "社團負責人", "指導老師"],
            },
        ],
        "tables": [
            {
                "title": "粗流",
                "headers": ["時間", "時長", "活動名稱", "場控／主持", "備註"],
                "rows": [
                    ["09:00-09:30", "30min", "報到", "王小明", ""],
                    ["09:30-10:00", "30min", "開場", "李小華", ""],
                ],
            },
            {
                "title": "細流",
                "headers": ["大活動時間", "大活動名稱", "細時間", "組別／區域", "事項", "備註", "器材", "負責人", "人員"],
                "rows": [
                    ["09:00-09:30", "報到", "09:00-09:15", "入口處", "簽到與發資料", "", "簽到表", "王小明", "志工甲"],
                    ["09:30-10:00", "開場", "09:30-09:40", "主舞台", "主持開場", "", "麥克風", "李小華", "主持組"],
                ],
            },
        ],
        "decor": {"page_footer": "粗流 / 細流 預覽"},
        "footnote": "此為 ODS 版型預覽，實際格式以下載 ODS 為準。",
    }


def _build_attendance_sheet_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["{{school_name}} {{club_name}}", "「{{event_name}}」簽到表"],
        "meta_rows": [
            ("日期與時間", "{{event_date}} {{start_time}} 至 {{end_time}}"),
            ("活動地點", "{{location}}"),
            ("活動名稱", "{{event_name}}"),
            ("主辦單位", "{{organizer}}"),
        ],
        "sections": [
            {
                "title": "統計與備註",
                "items": ["應到人數", "實到人數", "請假人數", "缺席人數", "備註"],
            },
            {
                "title": "簽核欄位",
                "items": ["製表人", "社團負責人", "指導老師"],
            },
        ],
        "tables": [
            {
                "title": "雙欄簽到表",
                "headers": ["系級／單位", "姓名", "系級／單位", "姓名"],
                "rows": [
                    ["", "", "", ""],
                    ["", "", "", ""],
                    ["", "", "", ""],
                ],
            }
        ],
        "decor": {
            "page_footer": "第1頁　共1頁",
        },
        "footnote": "此為版型預覽，實際格式以下載 ODT 為準。",
    }


def _build_activity_result_report_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["臺北市立大學", "社團活動成果報告"],
        "meta_rows": [],
        "sections": [
            {"title": "會議記錄", "items": ["會議性質", "開會日期", "開會地點", "主席", "出席人員", "討論內容", "臨時動議", "決議"]},
            {"title": "活動簡介與記錄", "items": ["活動實際辦理情形", "參與情況", "活動成果", "重要紀錄"]},
            {"title": "社員心得", "items": ["心得內容", "參與者回饋"]},
            {"title": "附件清單", "items": ["簽到表", "活動照片", "經費收支結算表", "核銷明細", "其他附件"]},
        ],
        "tables": [
            {
                "title": "工作人員列表",
                "headers": ["工作職稱", "學號", "姓名", "工作職稱", "學號", "姓名"],
                "rows": [["", "", "", "", "", ""], ["", "", "", "", "", ""]],
            },
            {
                "title": "活動照片區",
                "headers": ["照片一／照片二", "照片三／照片四"],
                "rows": [
                    ["照片黏貼處\n\n活動照片內容：", "照片黏貼處\n\n活動照片內容："],
                    ["照片黏貼處\n\n活動照片內容：", "照片黏貼處\n\n活動照片內容："],
                ],
            },
            {
                "title": "經費使用摘要",
                "headers": ["預算金額", "實際支出", "補助金額", "自籌金額", "備註"],
                "rows": [["", "", "", "", "經費收支結算表另附。"]],
            },
            {
                "title": "簽核區",
                "headers": ["製表人", "社團負責人", "指導老師", "審核單位"],
                "rows": [["", "", "", ""]],
            },
        ],
        "decor": {},
        "footnote": "此為版型預覽，實際格式以下載 ODT 為準。",
    }


def _build_expense_budget_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["臺北市立大學", "「活動名稱」經費預算表"],
        "meta_rows": [
            ("活動名稱", "＿＿＿＿＿＿＿＿"),
            ("活動日期", "＿＿＿＿"),
            ("主辦社團", "＿＿＿＿＿＿＿＿"),
            ("活動負責人", "＿＿＿＿"),
            ("財務負責人", "＿＿＿＿"),
            ("製表日期", "＿＿＿＿"),
            ("備註", "＿＿＿＿＿＿＿＿"),
        ],
        "sections": [
            {"title": "預算摘要", "items": ["活動總預算", "申請補助總額", "自籌總額", "自籌比例", "待確認補助項目數"]},
            {"title": "簽核區", "items": ["製表人", "社團負責人", "指導老師", "審核單位"]},
        ],
        "tables": [
            {
                "title": "經費預算表格區",
                "headers": ["序號", "項目類別", "項目", "說明", "數量", "單位", "單價", "金額", "經費來源", "是否申請補助"],
                "rows": [
                    ["1", "材料費", "活動材料", "工作坊材料包", "10", "份", "120", "自動計算", "學校補助", "是"],
                    ["2", "餐費", "工作人員餐費", "工作人員 20 人", "20", "份", "100", "自動計算", "自籌", "否"],
                ],
            }
        ],
        "decor": {},
        "footnote": "此為版型預覽，實際格式以下載 ODS 為準。",
    }


def _build_income_expense_statement_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["臺北市立大學 社團經費收支表"],
        "meta_rows": [
            ("學年度", "＿＿＿＿"),
            ("學期", "＿＿＿＿"),
            ("社團名稱", "＿＿＿＿＿＿＿＿"),
            ("記帳期間", "＿＿＿＿ 至 ＿＿＿＿"),
            ("期初餘額", "0"),
            ("財務負責人", "＿＿＿＿"),
            ("製表日期", "＿＿＿＿"),
            ("備註", "＿＿＿＿＿＿＿＿"),
        ],
        "sections": [
            {"title": "工作表", "items": ["收支明細", "活動彙總", "類別彙總"]},
        ],
        "tables": [
            {
                "title": "收支明細",
                "headers": ["序號", "日期", "類別", "品項", "支出", "收入", "餘額"],
                "rows": [["1", "", "", "", "", "", ""], ["2", "", "", "", "", "", ""]],
            },
            {
                "title": "狀態追蹤欄位",
                "headers": ["代墊人", "是否已撥款", "是否已列入活動結算", "對應活動"],
                "rows": [["", "是 / 否 / 不適用", "是 / 否 / 不適用", ""]],
            },
        ],
        "decor": {},
        "footnote": "此為版型預覽，實際格式以下載 ODS 為準。",
    }


def _build_expense_settlement_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["臺北市立大學", "社團活動經費收支結算表"],
        "meta_rows": [
            ("活動名稱", "＿＿＿＿＿＿＿＿"),
            ("活動日期", "＿＿＿＿"),
            ("活動地點", "＿＿＿＿＿＿＿＿"),
            ("參加人數", "＿＿＿"),
            ("記錄人", "＿＿＿＿"),
            ("結算日期", "＿＿＿＿"),
        ],
        "sections": [
            {"title": "結算重點", "items": ["預算通過金額", "實際支出金額", "學校補助核銷金額總計", "得補助金額上限"]},
        ],
        "tables": [
            {
                "title": "經費收支結算明細",
                "headers": ["項目", "預算通過金額", "實際支出金額", "備註"],
                "rows": [["場地費", "", "", "學校補助"], ["材料費", "", "", "自籌"]],
            },
            {
                "title": "結算公式區",
                "headers": ["項目", "預算通過金額", "實際支出金額", "備註"],
                "rows": [
                    ["支出金額總計", "自動加總", "自動加總", ""],
                    ["學校補助核銷金額總計", "MIN 公式", "", ""],
                    ["得補助金額上限：A × B / C", "自動計算", "", "應以申請金額為上限"],
                ],
            },
        ],
        "decor": {},
        "footnote": "此為版型預覽，實際格式以下載 ODS 為準。",
    }


def _build_reimbursement_detail_preview_data(definition: dict) -> dict:
    return {
        "template_name": definition["name"],
        "suggested_format": definition["suggested_format"],
        "header_lines": ["臺北市立大學", "社團活動核銷明細表"],
        "meta_rows": [
            ("活動名稱", "＿＿＿＿＿＿＿＿"),
            ("活動日期", "＿＿＿＿"),
            ("主辦社團", "＿＿＿＿＿＿＿＿"),
            ("活動負責人", "＿＿＿＿"),
            ("財務負責人", "＿＿＿＿"),
            ("製表日期", "＿＿＿＿"),
        ],
        "sections": [
            {"title": "統計摘要", "items": ["支出總金額", "各經費來源金額", "各憑證狀態筆數", "單據張數合計"]},
        ],
        "tables": [
            {
                "title": "核銷明細表格區",
                "headers": ["序號", "支出日期", "對應經費項目", "品名／用途", "單據類型", "經費來源", "支付方式", "金額", "憑證狀態"],
                "rows": [
                    ["1", "", "材料費", "活動材料", "發票", "學校補助", "現金", "", "已附"],
                    ["2", "", "餐費", "工作人員餐費", "收據", "自籌", "轉帳", "", "待補"],
                ],
            }
        ],
        "decor": {},
        "footnote": "此為版型預覽，實際格式以下載 ODS 為準。",
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

    if not meta_rows and not sections and not tables:
        sections.append(
            {
                "title": "文件用途",
                "items": [definition.get("usage_description", definition["name"])],
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
