from __future__ import annotations

import runpy
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import core.template_service as template_service
from core.template_registry import (
    FORMAL_TEMPLATE_FORBIDDEN_BODY_TEXT,
    FORMAL_TEMPLATE_REGISTRY,
    TEMPLATE_LIBRARY_CATEGORIES,
)
from core.template_service import (
    build_template_preview_data,
    generate_template_file,
    get_template_definition,
    get_template_registry_entry,
    list_template_definitions,
)


class TemplateServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name) / "data" / "generated" / "templates"
        self.original_output_dir = template_service.DEFAULT_TEMPLATE_OUTPUT_DIR
        template_service.DEFAULT_TEMPLATE_OUTPUT_DIR = self.output_dir

    def tearDown(self):
        template_service.DEFAULT_TEMPLATE_OUTPUT_DIR = self.original_output_dir
        self.temp_dir.cleanup()

    def _read_content_xml(self, output_path: Path) -> str:
        with zipfile.ZipFile(output_path) as archive:
            return archive.read("content.xml").decode("utf-8")

    def _read_content_tree(self, output_path: Path) -> ET.Element:
        return ET.fromstring(self._read_content_xml(output_path))

    def test_registry_contains_twenty_two_formal_templates(self):
        definitions = list_template_definitions()
        self.assertEqual(len(FORMAL_TEMPLATE_REGISTRY), 22)
        self.assertEqual(len(definitions), 22)

    def test_all_template_keys_are_unique(self):
        definitions = list_template_definitions()
        template_keys = [definition["template_key"] for definition in definitions]
        self.assertEqual(len(template_keys), len(set(template_keys)))

    def test_all_categories_are_valid(self):
        definitions = list_template_definitions()
        categories = {definition["library_category"] for definition in definitions}
        self.assertEqual(categories, set(TEMPLATE_LIBRARY_CATEGORIES))
        self.assertNotIn("社團評鑑型", categories)

    def test_all_formats_are_odt_or_ods(self):
        definitions = list_template_definitions()
        formats = {definition["suggested_format"] for definition in definitions}
        self.assertEqual(formats, {"ODT", "ODS"})

    def test_all_spec_paths_exist(self):
        for definition in list_template_definitions():
            spec_path = Path(definition["spec_path"])
            self.assertTrue(spec_path.exists(), definition["spec_path"])

    def test_template_registry_can_be_read_by_template_page(self):
        runpy.run_path("pages/6_Templates.py")

    def test_unimplemented_templates_are_not_marked_downloadable(self):
        for definition in list_template_definitions():
            if definition["implementation_status"] in {"registered_only", "planned"}:
                self.assertFalse(definition["supports_blank_download"], definition["id"])

    def test_current_formal_templates_support_blank_download(self):
        downloadable = [
            definition["template_key"]
            for definition in list_template_definitions()
            if definition["supports_blank_download"]
        ]
        self.assertEqual(
            downloadable,
            [
                "meeting_minutes",
                "meeting_notice",
                "attendance_sheet",
                "activity_proposal",
                "activity_application",
                "activity_result_report",
                "expense_budget",
                "income_expense_statement",
                "expense_settlement",
                "reimbursement_detail",
            ],
        )

    def test_canonical_downloadable_templates_generate_files(self):
        for template_key in [
            "meeting_minutes",
            "meeting_notice",
            "attendance_sheet",
            "activity_proposal",
            "activity_application",
            "activity_result_report",
            "expense_budget",
            "income_expense_statement",
            "expense_settlement",
            "reimbursement_detail",
        ]:
            output_path = generate_template_file(template_key)
            self.assertTrue(output_path.exists(), template_key)

    def test_meeting_minutes_registry_entry_is_formal_odt(self):
        definition = get_template_definition("meeting_minutes")

        self.assertEqual(definition["template_key"], "meeting_minutes")
        self.assertEqual(definition["suggested_format"], "ODT")
        self.assertEqual(definition["implementation_status"], "implemented")
        self.assertTrue(definition["supports_blank_download"])
        self.assertTrue(definition["supports_generate_document"])

    def test_meeting_minutes_odt_contains_formal_sections(self):
        output_path = generate_template_file("meeting_minutes")
        content_xml = self._read_content_xml(output_path)

        for required_text in [
            "第{{meeting_number}}次{{meeting_type}}紀錄",
            "製作日期：{{document_date}}",
            "基本資料表",
            "會議名稱",
            "會議日期",
            "會議時間",
            "會議地點",
            "主席",
            "記錄人員",
            "出席人員",
            "列席人員",
            "請假人員",
            "缺席人員",
            "壹、會議開始",
            "一、上次會議決議追蹤",
            "二、主席致詞",
            "貳、報告事項",
            "報告人",
            "參、討論事項",
            "案由一：",
            "說明：",
            "討論：",
            "決議：",
            "表決結果：同意＿＿票，不同意＿＿票，棄權＿＿票。",
            "負責人：",
            "執行期限：",
            "待辦事項",
            "項次",
            "事項",
            "期限",
            "肆、臨時動議",
            "提案人：",
            "伍、散會",
            "散會時間：{{end_time}}",
            "下次會議時間：{{next_meeting_time}}",
            "簽核欄位",
            "製表人",
            "社團負責人",
            "指導老師",
        ]:
            self.assertIn(required_text, content_xml)

    def test_meeting_minutes_excludes_forbidden_metadata_text(self):
        output_path = generate_template_file("meeting_minutes")
        content_xml = self._read_content_xml(output_path)

        for forbidden_text in FORMAL_TEMPLATE_FORBIDDEN_BODY_TEXT:
            self.assertNotIn(forbidden_text, content_xml)

    def test_activity_result_report_registry_entry_is_formal_odt(self):
        definition = get_template_definition("activity_result_report")

        self.assertEqual(definition["template_key"], "activity_result_report")
        self.assertEqual(definition["suggested_format"], "ODT")
        self.assertEqual(definition["implementation_status"], "implemented")
        self.assertTrue(definition["supports_blank_download"])

    def test_activity_result_report_odt_contains_formal_sections(self):
        output_path = generate_template_file("activity_result_report")
        content_xml = self._read_content_xml(output_path)

        for required_text in [
            "臺北市立大學",
            "社團活動成果報告",
            "一、會議記錄",
            "會議性質",
            "開會日期",
            "開會地點",
            "主席",
            "記錄",
            "出席人員",
            "討論內容",
            "臨時動議",
            "決議",
            "二、活動簡介與記錄",
            "三、工作人員列表",
            "工作職稱",
            "學號",
            "姓名",
            "四、社員心得",
            "五、活動照片",
            "照片黏貼處",
            "活動照片內容：",
            "六、經費使用摘要",
            "預算金額",
            "實際支出",
            "補助金額",
            "自籌金額",
            "七、檢討與建議",
            "八、附件清單",
            "九、簽核區",
            "製表人",
            "社團負責人",
            "指導老師",
            "審核單位",
        ]:
            self.assertIn(required_text, content_xml)

    def test_activity_result_report_odt_excludes_ui_operation_text(self):
        output_path = generate_template_file("activity_result_report")
        content_xml = self._read_content_xml(output_path)

        for forbidden_text in [
            "新增會議記錄",
            "上傳照片",
            "新增工作人員",
            "專案自動化說明",
        ]:
            self.assertNotIn(forbidden_text, content_xml)

    def test_activity_application_registry_entry_is_formal_odt(self):
        definition = get_template_definition("activity_application")

        self.assertEqual(definition["template_key"], "activity_application")
        self.assertEqual(definition["suggested_format"], "ODT")
        self.assertEqual(definition["implementation_status"], "implemented")
        self.assertTrue(definition["supports_blank_download"])
        self.assertFalse(definition["supports_generate_document"])

    def test_activity_application_odt_contains_formal_sections(self):
        output_path = generate_template_file("activity_application")
        content_xml = self._read_content_xml(output_path)

        for required_text in [
            "臺北市立大學　社團活動申請表",
            "申請基本資料",
            "活動名稱",
            "申請日期",
            "活動時間，起",
            "活動時間，止",
            "活動地點",
            "主辦社團",
            "參加人數",
            "社長",
            "社長電話",
            "社團指導老師",
            "前年社團評鑑",
            "活動性質",
            "宗旨與活動內容區",
            "宗旨：",
            "活動內容或講題：",
            "申請人與經費區",
            "活動申請人",
            "活動費申請補助",
            "活動費自籌經費",
            "合計",
            "行政簽核保留區",
            "承辦人",
            "單位主管",
            "校長",
            "使用種類與額度由課外活動組填寫",
            "請於活動二週前完成申請並隨表附活動企畫書",
            "申請校內場地，請增附場地申請表",
            "□ 幹訓或營隊",
            "□ 學術活動",
            "□ 學校委辦或代表學校之活動",
        ]:
            self.assertIn(required_text, content_xml)

    def test_activity_application_excludes_forbidden_metadata_text(self):
        output_path = generate_template_file("activity_application")
        content_xml = self._read_content_xml(output_path)

        for forbidden_text in FORMAL_TEMPLATE_FORBIDDEN_BODY_TEXT:
            self.assertNotIn(forbidden_text, content_xml)

    def test_attendance_sheet_registry_entry_is_formal_odt(self):
        definition = get_template_definition("attendance_sheet")

        self.assertEqual(definition["template_key"], "attendance_sheet")
        self.assertEqual(definition["suggested_format"], "ODT")
        self.assertEqual(definition["implementation_status"], "implemented")
        self.assertTrue(definition["supports_blank_download"])
        self.assertFalse(definition["supports_generate_document"])

    def test_attendance_sheet_odt_contains_formal_sections(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        }
        output_path = generate_template_file("attendance_sheet")
        content_xml = self._read_content_xml(output_path)
        tree = self._read_content_tree(output_path)

        for required_text in [
            "簽到表",
            "日期與時間",
            "活動地點",
            "活動名稱",
            "主辦單位",
            "系級／單位",
            "姓名",
            "應到人數",
            "實到人數",
            "請假人數",
            "缺席人數",
            "備註",
            "製表人",
            "社團負責人",
            "指導老師",
        ]:
            self.assertIn(required_text, content_xml)

        sign_in_table = tree.find(".//table:table[@table:name='簽到明細']", namespaces)
        self.assertIsNotNone(sign_in_table)
        rows = sign_in_table.findall("./table:table-row", namespaces)
        self.assertGreaterEqual(len(rows), 16)

        header_text = [
            "".join(paragraph.itertext()).strip()
            for paragraph in rows[0].findall(".//text:p", namespaces)
        ]
        self.assertEqual(header_text, ["系級／單位", "姓名", "系級／單位", "姓名"])

    def test_attendance_sheet_excludes_signature_column_and_metadata_text(self):
        output_path = generate_template_file("attendance_sheet")
        content_xml = self._read_content_xml(output_path)

        self.assertNotIn("簽名", content_xml)
        for forbidden_text in FORMAL_TEMPLATE_FORBIDDEN_BODY_TEXT:
            self.assertNotIn(forbidden_text, content_xml)

    def test_expense_budget_registry_entry_is_formal_ods(self):
        definition = get_template_definition("expense_budget")

        self.assertEqual(definition["template_key"], "expense_budget")
        self.assertEqual(definition["suggested_format"], "ODS")
        self.assertEqual(definition["implementation_status"], "implemented")
        self.assertTrue(definition["supports_blank_download"])

    def test_expense_budget_ods_contains_formal_sheet_and_headers(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        }
        output_path = generate_template_file("expense_budget")
        tree = self._read_content_tree(output_path)
        budget_sheet = tree.find(".//table:table[@table:name='經費預算表']", namespaces)
        self.assertIsNotNone(budget_sheet)

        text_values = [
            "".join(paragraph.itertext()).strip()
            for paragraph in budget_sheet.findall(".//text:p", namespaces)
        ]
        for field_name in [
            "活動名稱",
            "活動日期",
            "主辦社團",
            "活動負責人",
            "財務負責人",
            "製表日期",
            "備註",
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
            "預算摘要",
            "簽核區",
        ]:
            self.assertIn(field_name, text_values)

    def test_expense_budget_ods_contains_expected_formulas(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        output_path = generate_template_file("expense_budget")
        tree = self._read_content_tree(output_path)
        budget_sheet = tree.find(".//table:table[@table:name='經費預算表']", namespaces)
        self.assertIsNotNone(budget_sheet)

        formulas = [
            cell.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula"]
            for cell in budget_sheet.findall(".//table:table-cell", namespaces)
            if "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula" in cell.attrib
        ]
        amount_formulas = [formula for formula in formulas if formula.startswith("=N([.E")]
        self.assertEqual(len(amount_formulas), 100)
        self.assertIn("=N([.E8])*N([.G8])", formulas)
        self.assertIn("=N([.E107])*N([.G107])", formulas)
        self.assertIn("=SUM([.H8:.H107])", formulas)
        self.assertIn('=SUMIF([.J8:.J107];"是";[.H8:.H107])', formulas)
        self.assertIn('=SUMIF([.I8:.I107];"學校補助";[.H8:.H107])', formulas)
        self.assertIn('=SUMIF([.I8:.I107];"社團會費";[.H8:.H107])', formulas)
        self.assertIn('=SUMIF([.I8:.I107];"校外補助";[.H8:.H107])', formulas)
        self.assertIn('=SUMIF([.I8:.I107];"自籌";[.H8:.H107])', formulas)
        self.assertIn('=SUMIF([.I8:.I107];"其他";[.H8:.H107])', formulas)
        self.assertIn(
            '=SUMIF([.I8:.I107];"社團會費";[.H8:.H107])+SUMIF([.I8:.I107];"自籌";[.H8:.H107])',
            formulas,
        )
        self.assertIn(
            '=IF(SUM([.H8:.H107])=0;0;(SUMIF([.I8:.I107];"社團會費";[.H8:.H107])+SUMIF([.I8:.I107];"自籌";[.H8:.H107]))/SUM([.H8:.H107]))',
            formulas,
        )
        self.assertIn('=COUNTIF([.J8:.J107];"待確認")', formulas)

    def test_expense_budget_contains_content_validations(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        output_path = generate_template_file("expense_budget")
        tree = self._read_content_tree(output_path)
        budget_sheet = tree.find(".//table:table[@table:name='經費預算表']", namespaces)
        self.assertIsNotNone(budget_sheet)

        validations = tree.findall(".//table:content-validation", namespaces)
        validations_by_name = {
            validation.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name"]: validation
            for validation in validations
        }

        self.assertIn("validation_budget_category", validations_by_name)
        self.assertIn("validation_budget_funding_source", validations_by_name)
        self.assertIn("validation_budget_subsidy", validations_by_name)

        category_condition = validations_by_name["validation_budget_category"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        funding_source_condition = validations_by_name["validation_budget_funding_source"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        subsidy_condition = validations_by_name["validation_budget_subsidy"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]

        for option in ['"場地費"', '"講師費"', '"交通費"', '"餐費"', '"材料費"', '"其他"']:
            self.assertIn(option, category_condition)
        for option in ['"學校補助"', '"社團會費"', '"校外補助"', '"自籌"', '"其他"']:
            self.assertIn(option, funding_source_condition)
        for option in ['"是"', '"否"', '"待確認"']:
            self.assertIn(option, subsidy_condition)

        validation_name_counts = {
            "validation_budget_category": 0,
            "validation_budget_funding_source": 0,
            "validation_budget_subsidy": 0,
        }
        for cell in budget_sheet.findall(".//table:table-cell", namespaces):
            validation_name = cell.attrib.get(
                "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}content-validation-name"
            )
            if validation_name in validation_name_counts:
                validation_name_counts[validation_name] += 1
        self.assertEqual(validation_name_counts["validation_budget_category"], 100)
        self.assertEqual(validation_name_counts["validation_budget_funding_source"], 100)
        self.assertEqual(validation_name_counts["validation_budget_subsidy"], 100)

    def test_income_expense_statement_registry_entry_is_formal_ods(self):
        definition = get_template_definition("income_expense_statement")

        self.assertEqual(definition["template_key"], "income_expense_statement")
        self.assertEqual(definition["suggested_format"], "ODS")
        self.assertEqual(definition["implementation_status"], "implemented")
        self.assertTrue(definition["supports_blank_download"])

    def test_income_expense_statement_ods_contains_required_sheets(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        output_path = generate_template_file("income_expense_statement")
        tree = self._read_content_tree(output_path)
        sheet_names = [
            table.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name"]
            for table in tree.findall(".//table:table", namespaces)
        ]

        self.assertIn("收支明細", sheet_names)
        self.assertIn("活動彙總", sheet_names)
        self.assertIn("類別彙總", sheet_names)

    def test_income_expense_statement_detail_sheet_headers_and_formula_exist(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        }
        output_path = generate_template_file("income_expense_statement")
        tree = self._read_content_tree(output_path)
        detail_sheet = tree.find(".//table:table[@table:name='收支明細']", namespaces)
        self.assertIsNotNone(detail_sheet)

        text_values = [
            "".join(paragraph.itertext()).strip()
            for paragraph in detail_sheet.findall(".//text:p", namespaces)
        ]
        for header in [
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
        ]:
            self.assertIn(header, text_values)

        formulas = [
            cell.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula"]
            for cell in detail_sheet.findall(".//table:table-cell", namespaces)
            if "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula" in cell.attrib
        ]
        self.assertEqual(len(formulas), 200)
        self.assertIn(
            "=[.$B$5]+N([.F8])-N([.E8])",
            formulas,
        )
        self.assertIn(
            "=[.G8]+N([.F9])-N([.E9])",
            formulas,
        )

    def test_income_expense_statement_contains_content_validations(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        output_path = generate_template_file("income_expense_statement")
        tree = self._read_content_tree(output_path)
        validations = tree.findall(".//table:content-validation", namespaces)
        validations_by_name = {
            validation.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name"]: validation
            for validation in validations
        }
        validation_names = set(validations_by_name)

        self.assertIn("validation_category", validation_names)
        self.assertIn("validation_paid_status", validation_names)
        self.assertIn("validation_settlement_status", validation_names)

        category_condition = validations_by_name["validation_category"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        self.assertIn('"補助收入"', category_condition)
        self.assertIn('"活動支出"', category_condition)

        paid_condition = validations_by_name["validation_paid_status"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        settlement_condition = validations_by_name["validation_settlement_status"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        for option in ['"是"', '"否"', '"不適用"']:
            self.assertIn(option, paid_condition)
            self.assertIn(option, settlement_condition)

    def test_expense_settlement_registry_entry_is_formal_ods(self):
        definition = get_template_definition("expense_settlement")

        self.assertEqual(definition["template_key"], "expense_settlement")
        self.assertEqual(definition["suggested_format"], "ODS")
        self.assertEqual(definition["implementation_status"], "implemented")
        self.assertTrue(definition["supports_blank_download"])

    def test_expense_settlement_ods_contains_formal_sheet_and_headers(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        }
        output_path = generate_template_file("expense_settlement")
        tree = self._read_content_tree(output_path)
        settlement_sheet = tree.find(".//table:table[@table:name='經費收支結算表']", namespaces)
        self.assertIsNotNone(settlement_sheet)

        text_values = [
            "".join(paragraph.itertext()).strip()
            for paragraph in settlement_sheet.findall(".//text:p", namespaces)
        ]
        for field_name in [
            "活動名稱",
            "活動日期",
            "活動地點",
            "參加人數",
            "記錄人",
            "結算日期",
            "項目",
            "預算通過金額",
            "實際支出金額",
            "備註",
            "支出金額總計",
            "學校補助核銷金額總計",
            "得補助金額上限：A × B / C",
            "活動承辦人",
            "課外組承辦人",
            "組長",
            "學務長",
        ]:
            self.assertIn(field_name, text_values)

    def test_expense_settlement_ods_contains_expected_formulas(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        output_path = generate_template_file("expense_settlement")
        tree = self._read_content_tree(output_path)
        settlement_sheet = tree.find(".//table:table[@table:name='經費收支結算表']", namespaces)
        self.assertIsNotNone(settlement_sheet)

        formulas = [
            cell.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula"]
            for cell in settlement_sheet.findall(".//table:table-cell", namespaces)
            if "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula" in cell.attrib
        ]
        self.assertIn("=SUM([.B8:.B17])", formulas)
        self.assertIn("=SUM([.C8:.C17])", formulas)
        self.assertIn('=SUMIF([.D8:.D17];"學校補助";[.B8:.B17])', formulas)
        self.assertIn('=SUMIF([.D8:.D17];"學校補助";[.C8:.C17])', formulas)
        self.assertIn("=IF(SUM([.B8:.B17])=0;0;SUM([.C8:.C17])/SUM([.B8:.B17]))", formulas)
        self.assertIn(
            '=IF(SUM([.B8:.B17])=0;0;MIN(SUMIF([.D8:.D17];"學校補助";[.B8:.B17]);SUMIF([.D8:.D17];"學校補助";[.C8:.C17]);SUMIF([.D8:.D17];"學校補助";[.B8:.B17])*(SUM([.C8:.C17])/SUM([.B8:.B17]))))',
            formulas,
        )

    def test_expense_settlement_contains_content_validation(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        output_path = generate_template_file("expense_settlement")
        tree = self._read_content_tree(output_path)
        settlement_sheet = tree.find(".//table:table[@table:name='經費收支結算表']", namespaces)
        self.assertIsNotNone(settlement_sheet)

        validations = tree.findall(".//table:content-validation", namespaces)
        validations_by_name = {
            validation.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name"]: validation
            for validation in validations
        }

        self.assertIn("validation_settlement_note", validations_by_name)
        note_condition = validations_by_name["validation_settlement_note"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        for option in ['"學校補助"', '"校外補助"', '"社團會費"', '"自籌"', '"其他"']:
            self.assertIn(option, note_condition)

        validated_note_cells = [
            cell
            for cell in settlement_sheet.findall(".//table:table-cell", namespaces)
            if cell.attrib.get("{urn:oasis:names:tc:opendocument:xmlns:table:1.0}content-validation-name")
            == "validation_settlement_note"
        ]
        self.assertEqual(len(validated_note_cells), 10)

    def test_reimbursement_detail_registry_entry_is_formal_ods(self):
        definition = get_template_definition("reimbursement_detail")

        self.assertEqual(definition["template_key"], "reimbursement_detail")
        self.assertEqual(definition["suggested_format"], "ODS")
        self.assertEqual(definition["implementation_status"], "implemented")
        self.assertTrue(definition["supports_blank_download"])

    def test_reimbursement_detail_ods_contains_formal_sheet_and_headers(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        }
        output_path = generate_template_file("reimbursement_detail")
        tree = self._read_content_tree(output_path)
        detail_sheet = tree.find(".//table:table[@table:name='核銷明細表']", namespaces)
        self.assertIsNotNone(detail_sheet)

        text_values = [
            "".join(paragraph.itertext()).strip()
            for paragraph in detail_sheet.findall(".//text:p", namespaces)
        ]
        for field_name in [
            "活動名稱",
            "活動日期",
            "主辦社團",
            "活動負責人",
            "財務負責人",
            "製表日期",
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
            "統計摘要區",
            "備註區",
        ]:
            self.assertIn(field_name, text_values)

    def test_reimbursement_detail_ods_contains_expected_formulas(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        output_path = generate_template_file("reimbursement_detail")
        tree = self._read_content_tree(output_path)
        detail_sheet = tree.find(".//table:table[@table:name='核銷明細表']", namespaces)
        self.assertIsNotNone(detail_sheet)

        formulas = [
            cell.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula"]
            for cell in detail_sheet.findall(".//table:table-cell", namespaces)
            if "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}formula" in cell.attrib
        ]
        self.assertIn("=SUM([.K8:.K107])", formulas)
        self.assertIn('=SUMIF([.H8:.H107];"學校補助";[.K8:.K107])', formulas)
        self.assertIn('=SUMIF([.H8:.H107];"校外補助";[.K8:.K107])', formulas)
        self.assertIn('=SUMIF([.H8:.H107];"社團會費";[.K8:.K107])', formulas)
        self.assertIn('=SUMIF([.H8:.H107];"自籌";[.K8:.K107])', formulas)
        self.assertIn('=SUMIF([.H8:.H107];"其他";[.K8:.K107])', formulas)
        self.assertIn('=COUNTIF([.L8:.L107];"已附")', formulas)
        self.assertIn('=COUNTIF([.L8:.L107];"待補")', formulas)
        self.assertIn('=COUNTIF([.L8:.L107];"遺失")', formulas)
        self.assertIn('=COUNTIF([.L8:.L107];"不核銷")', formulas)
        self.assertIn('=SUMPRODUCT(N(LEN([.G8:.G107])>0))', formulas)

    def test_reimbursement_detail_contains_content_validations(self):
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        output_path = generate_template_file("reimbursement_detail")
        tree = self._read_content_tree(output_path)
        detail_sheet = tree.find(".//table:table[@table:name='核銷明細表']", namespaces)
        self.assertIsNotNone(detail_sheet)

        validations = tree.findall(".//table:content-validation", namespaces)
        validations_by_name = {
            validation.attrib["{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name"]: validation
            for validation in validations
        }

        self.assertIn("validation_receipt_type", validations_by_name)
        self.assertIn("validation_funding_source", validations_by_name)
        self.assertIn("validation_payment_method", validations_by_name)
        self.assertIn("validation_receipt_status", validations_by_name)

        receipt_type_condition = validations_by_name["validation_receipt_type"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        funding_source_condition = validations_by_name["validation_funding_source"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        payment_method_condition = validations_by_name["validation_payment_method"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]
        receipt_status_condition = validations_by_name["validation_receipt_status"].attrib[
            "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}condition"
        ]

        for option in ['"發票"', '"電子發票證明聯"', '"收據"', '"匯款證明"', '"其他"']:
            self.assertIn(option, receipt_type_condition)
        for option in ['"學校補助"', '"校外補助"', '"社團會費"', '"自籌"', '"其他"']:
            self.assertIn(option, funding_source_condition)
        for option in ['"現金"', '"轉帳"', '"信用卡"', '"金融卡"', '"行動支付"', '"匯款"', '"其他"']:
            self.assertIn(option, payment_method_condition)
        for option in ['"已附"', '"待補"', '"遺失"', '"不核銷"', '"不適用"']:
            self.assertIn(option, receipt_status_condition)

        validation_name_counts = {
            "validation_receipt_type": 0,
            "validation_funding_source": 0,
            "validation_payment_method": 0,
            "validation_receipt_status": 0,
        }
        for cell in detail_sheet.findall(".//table:table-cell", namespaces):
            validation_name = cell.attrib.get(
                "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}content-validation-name"
            )
            if validation_name in validation_name_counts:
                validation_name_counts[validation_name] += 1
        self.assertEqual(validation_name_counts["validation_receipt_type"], 100)
        self.assertEqual(validation_name_counts["validation_funding_source"], 100)
        self.assertEqual(validation_name_counts["validation_payment_method"], 100)
        self.assertEqual(validation_name_counts["validation_receipt_status"], 100)

    def test_canonical_registered_only_template_does_not_fake_download(self):
        with self.assertRaises(ValueError) as context:
            generate_template_file("activity_schedule")

        self.assertIn("尚未提供正式空白範本下載", str(context.exception))

    def test_existing_legacy_downloads_still_work(self):
        for template_id in [
            "meeting_notice_odt",
            "meeting_minutes_template_odt",
            "activity_proposal_odt",
            "attendance_sheet_ods",
            "activity_budget_ods",
        ]:
            output_path = generate_template_file(template_id)
            self.assertTrue(output_path.exists(), template_id)

    def test_legacy_meeting_notice_alias_maps_to_canonical_registry_entry(self):
        definition = get_template_definition("會議通知")
        registry_entry = get_template_registry_entry("meeting_notice")

        self.assertEqual(definition["template_key"], "meeting_notice")
        self.assertEqual(definition["name"], "開會通知單")
        self.assertEqual(registry_entry["display_name"], "開會通知單")

    def test_generated_formal_templates_do_not_include_forbidden_metadata_body_text(self):
        for template_key in [
            "meeting_minutes",
            "meeting_notice",
            "attendance_sheet",
            "activity_proposal",
            "activity_application",
            "activity_result_report",
            "expense_budget",
            "income_expense_statement",
            "expense_settlement",
            "reimbursement_detail",
        ]:
            output_path = generate_template_file(template_key)
            content_xml = self._read_content_xml(output_path)
            for forbidden_text in FORMAL_TEMPLATE_FORBIDDEN_BODY_TEXT:
                self.assertNotIn(forbidden_text, content_xml, f"{template_key} contains {forbidden_text}")

    def test_core_blank_templates_keep_required_formal_fields(self):
        expected_fields = {
            "meeting_minutes": [
                "第{{meeting_number}}次{{meeting_type}}紀錄",
                "製作日期：{{document_date}}",
                "會議名稱",
                "會議日期",
                "會議時間",
                "會議地點",
                "主席",
                "列席人員",
                "缺席人員",
                "出席人員",
                "記錄人員",
                "壹、會議開始",
                "貳、報告事項",
                "參、討論事項",
                "表決結果",
                "待辦事項",
                "肆、臨時動議",
                "伍、散會",
                "簽核欄位",
            ],
            "meeting_notice": [
                "受文者",
                "發文日期",
                "發文字號",
                "開會事由",
                "開會時間",
                "開會地點",
                "主持人",
            ],
            "attendance_sheet": [
                "簽到表",
                "日期與時間",
                "活動地點",
                "活動名稱",
                "主辦單位",
                "系級／單位",
                "姓名",
                "應到人數",
                "實到人數",
                "請假人數",
                "缺席人數",
                "製表人",
                "社團負責人",
                "指導老師",
            ],
            "activity_proposal": [
                "活動主題",
                "活動宗旨",
                "活動時間流程表",
                "活動預算",
            ],
            "activity_application": [
                "臺北市立大學　社團活動申請表",
                "申請基本資料",
                "活動名稱",
                "申請日期",
                "活動時間，起",
                "活動時間，止",
                "活動地點",
                "主辦社團",
                "參加人數",
                "社長",
                "社團指導老師",
                "前年社團評鑑",
                "活動性質",
                "宗旨：",
                "活動內容或講題：",
                "活動申請人",
                "活動費申請補助",
                "活動費自籌經費",
                "合計",
                "承辦人",
                "單位主管",
                "校長",
                "使用種類與額度由課外活動組填寫",
            ],
            "activity_result_report": [
                "社團活動成果報告",
                "會議性質",
                "開會日期",
                "開會地點",
                "主席",
                "記錄",
                "出席人員",
                "討論內容",
                "臨時動議",
                "決議",
                "活動簡介與記錄",
                "工作人員列表",
                "工作職稱",
                "學號",
                "姓名",
                "社員心得",
                "活動照片",
                "照片黏貼處",
                "活動照片內容：",
                "經費使用摘要",
                "預算金額",
                "實際支出",
                "補助金額",
                "自籌金額",
                "附件清單",
                "簽核區",
            ],
            "income_expense_statement": [
                "學年度",
                "學期",
                "社團名稱",
                "期初餘額",
                "財務負責人",
                "收支明細",
                "活動彙總",
                "類別彙總",
                "是否已撥款",
                "是否已列入活動結算",
            ],
            "expense_settlement": [
                "社團活動經費收支結算表",
                "活動名稱",
                "活動日期",
                "活動地點",
                "參加人數",
                "記錄人",
                "預算通過金額",
                "實際支出金額",
                "學校補助核銷金額總計",
                "得補助金額上限：A × B / C",
            ],
            "expense_budget": [
                "經費預算表",
                "活動名稱",
                "活動日期",
                "主辦社團",
                "活動負責人",
                "財務負責人",
                "製表日期",
                "項目類別",
                "項目",
                "說明",
                "數量",
                "單位",
                "單價",
                "金額",
                "經費來源",
                "是否申請補助",
                "預算摘要",
                "活動總預算",
                "申請補助總額",
                "自籌總額",
                "自籌比例",
                "簽核區",
            ],
            "reimbursement_detail": [
                "社團活動核銷明細表",
                "活動名稱",
                "活動日期",
                "主辦社團",
                "活動負責人",
                "財務負責人",
                "製表日期",
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
                "統計摘要區",
            ],
        }

        for template_key, required_fields in expected_fields.items():
            output_path = generate_template_file(template_key)
            content_xml = self._read_content_xml(output_path)
            for field_name in required_fields:
                self.assertIn(field_name, content_xml, f"{template_key} missing {field_name}")

    def test_preview_data_supports_canonical_and_legacy_aliases(self):
        minutes_preview = build_template_preview_data("meeting_minutes")
        notice_preview = build_template_preview_data("會議通知")
        attendance_preview = build_template_preview_data("attendance_sheet")
        proposal_preview = build_template_preview_data("activity_proposal")
        application_preview = build_template_preview_data("activity_application")
        result_preview = build_template_preview_data("activity_result_report")
        budget_preview = build_template_preview_data("expense_budget")
        income_preview = build_template_preview_data("income_expense_statement")
        settlement_preview = build_template_preview_data("expense_settlement")
        reimbursement_preview = build_template_preview_data("reimbursement_detail")

        self.assertEqual(minutes_preview["header_lines"][0], "{{school_name}}{{club_name}}")
        self.assertEqual(minutes_preview["header_lines"][1], "第{{meeting_number}}次{{meeting_type}}紀錄")
        self.assertEqual(minutes_preview["tables"][0]["headers"], ["項次", "事項", "負責人", "期限", "備註"])
        self.assertEqual(notice_preview["header_lines"][0], "{{organization_name}} 開會通知單")
        self.assertEqual(attendance_preview["header_lines"][1], "「{{event_name}}」簽到表")
        self.assertEqual(
            attendance_preview["tables"][0]["headers"],
            ["系級／單位", "姓名", "系級／單位", "姓名"],
        )
        self.assertEqual(proposal_preview["header_lines"][0], "{{school_name}}「{{activity_name}}」活動企畫書")
        self.assertEqual(application_preview["header_lines"][0], "臺北市立大學　社團活動申請表")
        self.assertEqual(application_preview["tables"][0]["headers"][0], "活動申請人")
        self.assertEqual(result_preview["header_lines"][1], "社團活動成果報告")
        self.assertEqual(budget_preview["header_lines"][1], "「活動名稱」經費預算表")
        self.assertEqual(income_preview["header_lines"][0], "臺北市立大學 社團經費收支表")
        self.assertEqual(settlement_preview["header_lines"][1], "社團活動經費收支結算表")
        self.assertEqual(reimbursement_preview["header_lines"][1], "社團活動核銷明細表")


if __name__ == "__main__":
    unittest.main()
