from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from core.document_schemas import get_default_document_content
from core.document_service import create_document, create_document_version
from generators.odt_generator import generate_document_odt
from generators.template_renderer import (
    DOCUMENT_TEMPLATE_PATHS,
    TemplateRenderError,
    render_odt_template,
)


class TemplateRendererTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "odflow.sqlite3"
        self.output_dir = Path(self.temp_dir.name) / "generated"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _content_xml(self, path: Path) -> str:
        with zipfile.ZipFile(path) as archive:
            return archive.read("content.xml").decode("utf-8")

    def _create_document_with_version(self, document_type: str, content: dict) -> tuple[dict, dict]:
        document = create_document(
            title=f"{document_type}測試",
            document_type=document_type,
            evaluation_category=(
                "6.社團活動_社團活動"
                if document_type == "活動企劃書"
                else "2.社團行政_管理運作"
            ),
            db_path=self.db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=content,
            db_path=self.db_path,
        )
        return document, version

    def test_three_placeholder_templates_exist(self):
        self.assertEqual(
            set(DOCUMENT_TEMPLATE_PATHS),
            {"會議紀錄", "開會通知單", "活動企劃書"},
        )
        for template_path in DOCUMENT_TEMPLATE_PATHS.values():
            self.assertTrue(template_path.exists(), template_path)
            self.assertGreater(template_path.stat().st_size, 0)

    def test_render_odt_template_replaces_scalar_placeholders(self):
        output_path = Path(self.temp_dir.name) / "rendered_notice.odt"
        render_odt_template(
            DOCUMENT_TEMPLATE_PATHS["開會通知單"],
            output_path,
            {
                "organization_name": "ODFlow測試社",
                "recipient": "全體幹部",
                "meeting_reason": "確認迎新活動",
            },
        )

        content_xml = self._content_xml(output_path)
        self.assertIn("ODFlow測試社", content_xml)
        self.assertIn("確認迎新活動", content_xml)
        self.assertNotIn("{{organization_name}}", content_xml)

    def test_meeting_minutes_template_generates_odt(self):
        content = get_default_document_content("會議紀錄")
        content["meeting_title"] = "第 3 次幹部會議"
        content["meeting_date"] = "2026-06-24"
        content["reports"] = "各組進度報告"
        content["agenda_items"] = [
            {"title": "迎新活動", "discussion": "確認流程", "decision": "下週定稿"}
        ]
        document, version = self._create_document_with_version("會議紀錄", content)

        output_path = generate_document_odt(document, version, output_dir=self.output_dir)
        content_xml = self._content_xml(output_path)

        self.assertIn("壹、會議議程", content_xml)
        self.assertIn("第 3 次幹部會議", content_xml)
        self.assertNotIn("{{", content_xml)

    def test_meeting_notice_template_generates_odt(self):
        content = get_default_document_content("開會通知單")
        content["organization_name"] = "ODFlow示範社團"
        content["recipient"] = "全體幹部"
        content["meeting_reason"] = "確認迎新活動分工"
        content["meeting_datetime"] = "2026-06-24 18:30"
        document, version = self._create_document_with_version("開會通知單", content)

        output_path = generate_document_odt(document, version, output_dir=self.output_dir)
        content_xml = self._content_xml(output_path)

        self.assertIn("開會通知單", content_xml)
        self.assertIn("用印處", content_xml)
        self.assertIn("確認迎新活動分工", content_xml)

    def test_activity_proposal_template_generates_odt(self):
        content = get_default_document_content("活動企劃書")
        content["activity_name"] = "迎新活動"
        content["activity_theme"] = "新生交流"
        content["purpose"] = "協助新生認識社團"
        content["budget_items"] = [
            {
                "item": "文宣費",
                "description": "海報印製",
                "quantity": "10",
                "unit_price": "50",
                "amount": "500",
                "funding_source": "社費",
                "note": "",
            }
        ]
        document, version = self._create_document_with_version("活動企劃書", content)

        output_path = generate_document_odt(document, version, output_dir=self.output_dir)
        content_xml = self._content_xml(output_path)

        self.assertIn("活動企劃書", content_xml)
        self.assertIn("1、活動主題", content_xml)
        self.assertIn("文宣費", content_xml)
        self.assertNotIn("{{budget_table}}", content_xml)

    def test_empty_values_do_not_render_python_repr(self):
        content = get_default_document_content("開會通知單")
        document, version = self._create_document_with_version("開會通知單", content)

        output_path = generate_document_odt(document, version, output_dir=self.output_dir)
        content_xml = self._content_xml(output_path)

        self.assertNotIn("None", content_xml)
        self.assertNotIn("[]", content_xml)
        self.assertNotIn("&quot;", content_xml)

    def test_fallback_generator_is_kept_when_template_rendering_fails(self):
        content = get_default_document_content("會議紀錄")
        content["meeting_title"] = "Fallback 測試會議"
        document, version = self._create_document_with_version("會議紀錄", content)

        with patch(
            "generators.odt_generator.render_document_odt_template",
            side_effect=TemplateRenderError("forced failure"),
        ):
            output_path = generate_document_odt(document, version, output_dir=self.output_dir)

        content_xml = self._content_xml(output_path)
        self.assertIn("Fallback 測試會議", content_xml)
        self.assertIn("text:h", content_xml)


if __name__ == "__main__":
    unittest.main()
