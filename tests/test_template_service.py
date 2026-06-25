from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

import core.template_service as template_service
from core.template_service import (
    TEMPLATE_LIBRARY_CATEGORIES,
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

    def test_list_template_definitions_returns_expected_library_categories(self):
        definitions = list_template_definitions()
        categories = {definition["library_category"] for definition in definitions}

        self.assertEqual(categories, set(TEMPLATE_LIBRARY_CATEGORIES))
        self.assertEqual(
            categories,
            {"日常行政", "活動專案", "社團評鑑", "財務與清冊"},
        )

    def test_template_count_is_at_least_twenty_two(self):
        definitions = list_template_definitions()
        self.assertGreaterEqual(len(definitions), 22)

    def test_get_template_definition_returns_specific_template(self):
        definition = get_template_definition("meeting_notice_odt")

        self.assertEqual(definition["name"], "會議通知")
        self.assertEqual(definition["suggested_format"], "ODT")

    def test_core_odt_templates_can_link_to_generate_flow(self):
        definition = get_template_definition("activity_proposal_odt")

        self.assertEqual(definition["linked_document_type"], "活動企劃書")

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


if __name__ == "__main__":
    unittest.main()
