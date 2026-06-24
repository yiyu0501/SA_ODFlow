from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

import core.export_service as export_service
import generators.export_utils as export_utils
from core.constants import EVALUATION_CATEGORIES
from core.document_service import (
    create_document,
    create_document_version,
    get_current_version,
    update_version_file_paths,
)
from core.export_service import (
    build_evaluation_folder_name,
    build_odf_backup_package,
    build_pdf_evaluation_package,
)
from core.meeting_minutes import empty_meeting_minutes_content
from generators.odt_generator import generate_meeting_minutes_odt
from generators.pdf_generator import generate_meeting_minutes_pdf


class ExportServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "odflow.sqlite3"
        self.generated_dir = Path(self.temp_dir.name) / "generated"
        self.exports_dir = Path(self.temp_dir.name) / "exports"

        self.original_generated_dir = export_utils.DEFAULT_GENERATED_DIR
        self.original_exports_dir = export_service.EXPORTS_DIR
        export_utils.DEFAULT_GENERATED_DIR = self.generated_dir
        export_service.EXPORTS_DIR = self.exports_dir

    def tearDown(self):
        export_utils.DEFAULT_GENERATED_DIR = self.original_generated_dir
        export_service.EXPORTS_DIR = self.original_exports_dir
        self.temp_dir.cleanup()

    def _sample_content(self, title: str) -> dict:
        content = empty_meeting_minutes_content()
        content["meeting_title"] = title
        content["meeting_date"] = "2026-06-24"
        content["meeting_time"] = "18:30"
        content["location"] = "社辦"
        content["chair"] = "王小明"
        content["recorder"] = "李小華"
        content["attendees"] = ["王小明", "李小華"]
        content["agenda_items"] = [
            {
                "title": "確認迎新活動",
                "discussion": "討論流程",
                "decision": "下週完成場地借用",
            }
        ]
        content["action_items"] = [
            {
                "task": "整理活動清單",
                "owner": "王小明",
                "deadline": "2026-06-30",
                "note": "",
            }
        ]
        content["notes"] = "測試內容"
        return content

    def _create_document_with_version(
        self,
        *,
        title: str,
        category: str,
        status: str,
        with_pdf: bool = False,
        with_odf: bool = False,
    ) -> dict:
        document = create_document(
            title=title,
            document_type="會議紀錄",
            evaluation_category=category,
            status=status,
            db_path=self.db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=self._sample_content(title),
            db_path=self.db_path,
        )

        odf_path = None
        pdf_path = None
        if with_odf:
            odf_path = str(
                generate_meeting_minutes_odt(document, version, output_dir=self.generated_dir)
            )
        if with_pdf:
            pdf_path = str(
                generate_meeting_minutes_pdf(document, version, output_dir=self.generated_dir)
            )
        if odf_path or pdf_path:
            update_version_file_paths(
                document_id=document["id"],
                version_number=version["version_number"],
                odf_path=odf_path,
                pdf_path=pdf_path,
                db_path=self.db_path,
            )

        return document

    def _zip_names(self, zip_path: Path) -> list[str]:
        with zipfile.ZipFile(zip_path) as archive:
            return archive.namelist()

    def test_build_evaluation_folder_name_formats_root_name(self):
        folder_name = build_evaluation_folder_name("114", "天母校區", "ODFlow示範社團")
        self.assertEqual(
            folder_name,
            "114學年度臺北市立大學社團評鑑資料_天母校區_ODFlow示範社團",
        )

    def test_pdf_package_contains_seven_category_folders(self):
        result = build_pdf_evaluation_package(
            academic_year="114",
            campus="天母校區",
            club_name="ODFlow示範社團",
            db_path=self.db_path,
        )
        names = self._zip_names(result["zip_path"])

        for category in EVALUATION_CATEGORIES:
            prefix = f"{result['top_level_folder']}/{category}"
            self.assertTrue(any(name.startswith(prefix) for name in names))

    def test_formal_document_is_exported_to_its_category(self):
        self._create_document_with_version(
            title="幹部會議紀錄",
            category="2.社團行政_管理運作",
            status="正式版",
            with_pdf=True,
        )

        result = build_pdf_evaluation_package(db_path=self.db_path)
        names = self._zip_names(result["zip_path"])

        self.assertEqual(result["exported_count"], 1)
        self.assertTrue(
            any(
                name.endswith(".pdf")
                and "/2.社團行政_管理運作/" in name
                for name in names
            )
        )

    def test_draft_document_does_not_enter_formal_package(self):
        self._create_document_with_version(
            title="社員大會紀錄",
            category="2.社團行政_管理運作",
            status="草稿",
            with_pdf=True,
        )

        result = build_pdf_evaluation_package(db_path=self.db_path)
        names = self._zip_names(result["zip_path"])

        self.assertEqual(result["exported_count"], 0)
        self.assertEqual(result["failed_count"], 1)
        self.assertFalse(
            any(
                name.endswith(".pdf")
                and "/2.社團行政_管理運作/" in name
                for name in names
            )
        )
        self.assertEqual(result["failed_documents"][0]["reason"], "狀態不是正式版或已歸檔")

    def test_archived_document_enters_formal_package(self):
        self._create_document_with_version(
            title="年度計畫",
            category="4.社團行政_年度計畫",
            status="已歸檔",
            with_pdf=True,
        )

        result = build_pdf_evaluation_package(db_path=self.db_path)
        names = self._zip_names(result["zip_path"])

        self.assertEqual(result["exported_count"], 1)
        self.assertTrue(
            any(
                name.endswith(".pdf")
                and "/4.社團行政_年度計畫/" in name
                for name in names
            )
        )

    def test_document_index_and_failed_report_are_included(self):
        self._create_document_with_version(
            title="活動檢討會紀錄",
            category="6.社團活動_社團活動",
            status="草稿",
            with_pdf=True,
        )

        result = build_pdf_evaluation_package(db_path=self.db_path)
        names = self._zip_names(result["zip_path"])

        self.assertIn(f"{result['top_level_folder']}/文件索引表.pdf", names)
        self.assertIn(f"{result['top_level_folder']}/文件索引表.csv", names)
        self.assertIn(f"{result['top_level_folder']}/未輸出文件清單.pdf", names)

    def test_odf_backup_package_can_be_built(self):
        self._create_document_with_version(
            title="幹部會議紀錄",
            category="2.社團行政_管理運作",
            status="待審",
            with_odf=True,
        )

        result = build_odf_backup_package(
            academic_year="114",
            club_name="ODFlow示範社團",
            db_path=self.db_path,
        )
        names = self._zip_names(result["zip_path"])

        self.assertEqual(result["exported_count"], 1)
        self.assertTrue(any(name.endswith(".odt") for name in names))

    def test_missing_pdf_is_auto_generated_and_written_back(self):
        document = self._create_document_with_version(
            title="幹部會議紀錄",
            category="2.社團行政_管理運作",
            status="正式版",
        )

        result = build_pdf_evaluation_package(db_path=self.db_path)
        current_version = get_current_version(document["id"], db_path=self.db_path)

        self.assertEqual(result["exported_count"], 1)
        self.assertTrue(current_version["pdf_path"])
        self.assertTrue(Path(current_version["pdf_path"]).exists())

    def test_empty_database_still_builds_empty_package_with_index(self):
        result = build_pdf_evaluation_package(db_path=self.db_path)
        names = self._zip_names(result["zip_path"])

        self.assertEqual(result["exported_count"], 0)
        self.assertEqual(result["failed_count"], 0)
        self.assertIn(f"{result['top_level_folder']}/文件索引表.pdf", names)
        self.assertIn(f"{result['top_level_folder']}/文件索引表.csv", names)
        for category in EVALUATION_CATEGORIES:
            prefix = f"{result['top_level_folder']}/{category}"
            self.assertTrue(any(name.startswith(prefix) for name in names))


if __name__ == "__main__":
    unittest.main()
