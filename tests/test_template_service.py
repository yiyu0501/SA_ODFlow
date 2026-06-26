from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

import core.template_service as template_service
from core.template_service import (
    TEMPLATE_LIBRARY_CATEGORIES,
    build_template_preview_data,
    generate_template_file,
    get_template_definition,
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

    def test_list_template_definitions_returns_expected_library_categories(self):
        definitions = list_template_definitions()
        categories = {definition["library_category"] for definition in definitions}

        self.assertEqual(categories, set(TEMPLATE_LIBRARY_CATEGORIES))
        self.assertEqual(
            categories,
            {"日常行政型", "專案活動型", "社團運作型", "財務與清冊型"},
        )
        self.assertNotIn("社團評鑑型", categories)
        self.assertNotIn("社團評鑑", categories)

    def test_template_count_is_at_least_twenty_two(self):
        definitions = list_template_definitions()
        self.assertGreaterEqual(len(definitions), 22)

    def test_get_template_definition_returns_specific_template(self):
        definition = get_template_definition("meeting_notice_odt")

        self.assertEqual(definition["name"], "開會通知單")
        self.assertEqual(definition["suggested_format"], "ODT")

    def test_core_odt_templates_can_link_to_generate_flow(self):
        proposal_definition = get_template_definition("activity_proposal_odt")
        notice_definition = get_template_definition("meeting_notice_odt")
        agenda_definition = get_template_definition("meeting_agenda_odt")

        self.assertEqual(proposal_definition["linked_document_type"], "活動企劃書")
        self.assertEqual(notice_definition["linked_document_type"], "開會通知單")
        self.assertEqual(agenda_definition["linked_document_type"], "會議議程")

    def test_generate_template_file_creates_odt(self):
        output_path = generate_template_file("meeting_notice_odt")

        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.suffix, ".odt")
        with zipfile.ZipFile(output_path) as archive:
            self.assertIn("content.xml", archive.namelist())
            self.assertEqual(
                archive.read("mimetype"),
                b"application/vnd.oasis.opendocument.text",
            )
            content_xml = archive.read("content.xml").decode("utf-8")
            self.assertIn("{{meeting_reason}}", content_xml)

    def test_legacy_meeting_notice_alias_uses_formal_template(self):
        definition = get_template_definition("會議通知")
        output_path = generate_template_file("會議通知")
        content_xml = self._read_content_xml(output_path)

        self.assertEqual(definition["id"], "meeting_notice_odt")
        self.assertEqual(definition["name"], "開會通知單")
        self.assertIn("開會通知單", content_xml)

    def test_generate_template_file_creates_ods(self):
        output_path = generate_template_file("attendance_sheet_ods")

        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.suffix, ".ods")
        with zipfile.ZipFile(output_path) as archive:
            self.assertIn("content.xml", archive.namelist())
            self.assertEqual(
                archive.read("mimetype"),
                b"application/vnd.oasis.opendocument.spreadsheet",
            )

    def test_generated_template_file_uses_templates_output_directory(self):
        output_path = generate_template_file("activity_budget_ods")

        self.assertEqual(output_path.parent, self.output_dir)
        self.assertTrue(output_path.parent.exists())

    def test_all_twenty_two_templates_remain_generatable(self):
        for definition in list_template_definitions():
            output_path = generate_template_file(definition["id"])
            self.assertTrue(output_path.exists(), definition["id"])
            self.assertEqual(
                output_path.parent,
                self.output_dir,
                definition["id"],
            )

    def test_unsupported_template_format_raises_clear_error(self):
        original_definition = template_service.TEMPLATE_DEFINITIONS_BY_ID["meeting_notice_odt"]
        broken_definition = {**original_definition, "suggested_format": "ODP"}
        template_service.TEMPLATE_DEFINITIONS_BY_ID["meeting_notice_odt"] = broken_definition

        try:
            with self.assertRaises(ValueError) as context:
                generate_template_file("meeting_notice_odt")
        finally:
            template_service.TEMPLATE_DEFINITIONS_BY_ID["meeting_notice_odt"] = original_definition

        self.assertIn("不支援的範本格式", str(context.exception))

    def test_generated_template_filename_excludes_unsafe_characters(self):
        original_definition = template_service.TEMPLATE_DEFINITIONS_BY_ID["meeting_notice_odt"]
        unsafe_definition = {**original_definition, "name": '會議:通知/測試?*'}
        template_service.TEMPLATE_DEFINITIONS_BY_ID["meeting_notice_odt"] = unsafe_definition

        try:
            output_path = generate_template_file("meeting_notice_odt")
        finally:
            template_service.TEMPLATE_DEFINITIONS_BY_ID["meeting_notice_odt"] = original_definition

        for char in '\\/:*?"<>|':
            self.assertNotIn(char, output_path.name)

    def test_core_blank_templates_do_not_include_metadata_labels(self):
        disallowed_labels = [
            "範本類型",
            "建議格式",
            "對應評鑑分類",
            "使用情境",
            "使用說明",
        ]

        for template_id in [
            "meeting_minutes_template_odt",
            "meeting_notice_odt",
            "activity_proposal_odt",
        ]:
            output_path = generate_template_file(template_id)
            content_xml = self._read_content_xml(output_path)
            for label in disallowed_labels:
                self.assertNotIn(label, content_xml, f"{template_id} contains {label}")

    def test_meeting_minutes_template_uses_meeting_minutes_wording(self):
        output_path = generate_template_file("meeting_minutes_template_odt")
        content_xml = self._read_content_xml(output_path)

        self.assertIn("會議紀錄", content_xml)
        self.assertNotIn("會議記錄", content_xml)

    def test_core_blank_templates_keep_required_formal_fields(self):
        expected_fields = {
            "meeting_minutes_template_odt": [
                "會議時間",
                "主席",
                "出席人員",
                "記錄人員",
                "報告事項",
                "討論事項",
            ],
            "meeting_notice_odt": [
                "受文者",
                "發文日期",
                "發文字號",
                "開會事由",
                "開會時間",
                "開會地點",
                "主持人",
            ],
            "activity_proposal_odt": [
                "活動主題",
                "活動宗旨",
                "活動時間流程表",
                "活動預算",
            ],
        }

        for template_id, required_fields in expected_fields.items():
            output_path = generate_template_file(template_id)
            content_xml = self._read_content_xml(output_path)
            for field_name in required_fields:
                self.assertIn(field_name, content_xml, f"{template_id} missing {field_name}")

    def test_core_template_preview_data_returns_document_layout_blocks(self):
        minutes_preview = build_template_preview_data("meeting_minutes_template_odt")
        notice_preview = build_template_preview_data("會議通知")
        proposal_preview = build_template_preview_data("activity_proposal_odt")

        self.assertIn("{{organization_name}}文件", minutes_preview["header_lines"])
        self.assertEqual(minutes_preview["meta_rows"][0][0], "會議時間")
        self.assertEqual(notice_preview["header_lines"][0], "{{organization_name}} 開會通知單")
        self.assertEqual(notice_preview["decor"]["page_footer"], "第1頁　共1頁")
        self.assertEqual(proposal_preview["header_lines"][0], "{{school_name}}「{{activity_name}}」活動企劃書")
        self.assertEqual(proposal_preview["tables"][0]["title"], "活動時間流程表")


if __name__ == "__main__":
    unittest.main()
