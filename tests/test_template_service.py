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
                "activity_proposal",
                "income_expense_statement",
                "expense_settlement",
            ],
        )

    def test_canonical_downloadable_templates_generate_files(self):
        for template_key in [
            "meeting_minutes",
            "meeting_notice",
            "activity_proposal",
            "income_expense_statement",
            "expense_settlement",
        ]:
            output_path = generate_template_file(template_key)
            self.assertTrue(output_path.exists(), template_key)

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

    def test_canonical_registered_only_template_does_not_fake_download(self):
        with self.assertRaises(ValueError) as context:
            generate_template_file("activity_application")

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
            "activity_proposal",
            "income_expense_statement",
            "expense_settlement",
        ]:
            output_path = generate_template_file(template_key)
            content_xml = self._read_content_xml(output_path)
            for forbidden_text in FORMAL_TEMPLATE_FORBIDDEN_BODY_TEXT:
                self.assertNotIn(forbidden_text, content_xml, f"{template_key} contains {forbidden_text}")

    def test_core_blank_templates_keep_required_formal_fields(self):
        expected_fields = {
            "meeting_minutes": [
                "會議時間",
                "主席",
                "出席人員",
                "記錄人員",
                "報告事項",
                "討論事項",
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
            "activity_proposal": [
                "活動主題",
                "活動宗旨",
                "活動時間流程表",
                "活動預算",
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
        }

        for template_key, required_fields in expected_fields.items():
            output_path = generate_template_file(template_key)
            content_xml = self._read_content_xml(output_path)
            for field_name in required_fields:
                self.assertIn(field_name, content_xml, f"{template_key} missing {field_name}")

    def test_preview_data_supports_canonical_and_legacy_aliases(self):
        minutes_preview = build_template_preview_data("meeting_minutes")
        notice_preview = build_template_preview_data("會議通知")
        proposal_preview = build_template_preview_data("activity_proposal")
        income_preview = build_template_preview_data("income_expense_statement")
        settlement_preview = build_template_preview_data("expense_settlement")

        self.assertIn("{{organization_name}}文件", minutes_preview["header_lines"])
        self.assertEqual(notice_preview["header_lines"][0], "{{organization_name}} 開會通知單")
        self.assertEqual(proposal_preview["header_lines"][0], "{{school_name}}「{{activity_name}}」活動企畫書")
        self.assertEqual(income_preview["header_lines"][0], "臺北市立大學 社團經費收支表")
        self.assertEqual(settlement_preview["header_lines"][1], "社團活動經費收支結算表")


if __name__ == "__main__":
    unittest.main()
