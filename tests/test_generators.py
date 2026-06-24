from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from core.document_service import (
    create_document,
    create_document_version,
    get_current_version,
    update_version_file_paths,
)
from core.filename import build_versioned_filename
from core.meeting_minutes import empty_meeting_minutes_content
from generators.odt_generator import generate_meeting_minutes_odt
from generators.pdf_generator import generate_meeting_minutes_pdf


class ExportGeneratorsTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "odflow.sqlite3"
        self.output_dir = Path(self.temp_dir.name) / "generated"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _sample_content(self) -> dict:
        content = empty_meeting_minutes_content()
        content["meeting_title"] = "第/3次:幹部會議"
        content["meeting_date"] = "2026-06-24"
        content["meeting_time"] = "18:30"
        content["location"] = "社辦"
        content["chair"] = "王小明"
        content["recorder"] = "李小華"
        content["attendees"] = ["王小明", "李小華"]
        content["absentees"] = ["張同學"]
        content["agenda_items"] = [
            {
                "title": "確認迎新活動",
                "discussion": "討論迎新流程與分工",
                "decision": "下週前完成場地借用",
            }
        ]
        content["action_items"] = [
            {
                "task": "整理活動清單",
                "owner": "王小明",
                "deadline": "2026-06-30",
                "note": "請於例會前完成",
            }
        ]
        content["next_meeting_time"] = "2026-07-01 19:00"
        content["notes"] = "測試匯出"
        return content

    def _create_document_with_version(self) -> tuple[dict, dict]:
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=self._sample_content(),
            db_path=self.db_path,
        )
        return document, version

    def test_odt_generator_creates_file(self):
        document, version = self._create_document_with_version()

        output_path = generate_meeting_minutes_odt(
            document=document,
            version=version,
            output_dir=self.output_dir,
        )

        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.suffix, ".odt")
        with zipfile.ZipFile(output_path) as archive:
            self.assertIn("content.xml", archive.namelist())

    def test_pdf_generator_creates_file(self):
        document, version = self._create_document_with_version()

        output_path = generate_meeting_minutes_pdf(
            document=document,
            version=version,
            output_dir=self.output_dir,
        )

        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.suffix, ".pdf")
        self.assertTrue(output_path.read_bytes().startswith(b"%PDF-"))

    def test_generated_file_paths_can_be_written_back(self):
        document, version = self._create_document_with_version()
        odt_path = generate_meeting_minutes_odt(document, version, output_dir=self.output_dir)
        pdf_path = generate_meeting_minutes_pdf(document, version, output_dir=self.output_dir)

        update_version_file_paths(
            document_id=document["id"],
            version_number=version["version_number"],
            odf_path=str(odt_path),
            pdf_path=str(pdf_path),
            db_path=self.db_path,
        )
        current_version = get_current_version(document["id"], db_path=self.db_path)

        self.assertEqual(current_version["odf_path"], str(odt_path))
        self.assertEqual(current_version["pdf_path"], str(pdf_path))

    def test_build_versioned_filename_removes_unsafe_characters(self):
        filename = build_versioned_filename(
            club_name="學生會/社團",
            document_type="會議:紀錄",
            subject='第?3次*會議',
            version=1,
            extension="pdf",
        )

        for char in '\\/:*?"<>|':
            self.assertNotIn(char, filename)

    def test_generator_rejects_incomplete_content_json(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        broken_version = {
            "document_id": document["id"],
            "version_number": 1,
            "content_json": {"meeting_title": "只有標題"},
        }

        with self.assertRaises(ValueError):
            generate_meeting_minutes_odt(
                document=document,
                version=broken_version,
                output_dir=self.output_dir,
            )


if __name__ == "__main__":
    unittest.main()
