from __future__ import annotations

import runpy
import tempfile
import unittest
import zipfile
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

    def test_only_three_formal_templates_currently_support_blank_download(self):
        downloadable = [
            definition["template_key"]
            for definition in list_template_definitions()
            if definition["supports_blank_download"]
        ]
        self.assertEqual(
            downloadable,
            ["meeting_minutes", "meeting_notice", "activity_proposal"],
        )

    def test_canonical_downloadable_templates_generate_files(self):
        for template_key in ["meeting_minutes", "meeting_notice", "activity_proposal"]:
            output_path = generate_template_file(template_key)
            self.assertTrue(output_path.exists(), template_key)

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
        for template_key in ["meeting_minutes", "meeting_notice", "activity_proposal"]:
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

        self.assertIn("{{organization_name}}文件", minutes_preview["header_lines"])
        self.assertEqual(notice_preview["header_lines"][0], "{{organization_name}} 開會通知單")
        self.assertEqual(proposal_preview["header_lines"][0], "{{school_name}}「{{activity_name}}」活動企畫書")


if __name__ == "__main__":
    unittest.main()
