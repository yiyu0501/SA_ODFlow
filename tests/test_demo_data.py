from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import generators.export_utils as export_utils
from core.demo_data import DEMO_DOCUMENT_SPECS, create_demo_data
from core.document_service import get_current_version, list_documents
from core.evaluation_service import get_evaluation_summary


class DemoDataTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "odflow.sqlite3"
        self.generated_dir = Path(self.temp_dir.name) / "generated"
        self.original_generated_dir = export_utils.DEFAULT_GENERATED_DIR
        export_utils.DEFAULT_GENERATED_DIR = self.generated_dir

    def tearDown(self):
        export_utils.DEFAULT_GENERATED_DIR = self.original_generated_dir
        self.temp_dir.cleanup()

    def test_create_demo_data_creates_seed_documents(self):
        result = create_demo_data(db_path=self.db_path)
        documents = list_documents(db_path=self.db_path)

        self.assertEqual(result["created_count"], len(DEMO_DOCUMENT_SPECS))
        self.assertEqual(len(documents), len(DEMO_DOCUMENT_SPECS))

    def test_create_demo_data_does_not_duplicate_existing_seed_data(self):
        first_run = create_demo_data(db_path=self.db_path)
        second_run = create_demo_data(db_path=self.db_path)
        documents = list_documents(db_path=self.db_path)

        self.assertEqual(first_run["created_count"], len(DEMO_DOCUMENT_SPECS))
        self.assertEqual(second_run["created_count"], 0)
        self.assertEqual(second_run["skipped_count"], len(DEMO_DOCUMENT_SPECS))
        self.assertEqual(len(documents), len(DEMO_DOCUMENT_SPECS))

    def test_demo_data_provides_dashboard_completion_inputs(self):
        create_demo_data(db_path=self.db_path)
        summary = get_evaluation_summary(db_path=self.db_path)

        self.assertGreater(summary["total_completed_documents"], 0)
        self.assertGreater(summary["overall_completion_percentage"], 0.0)

    def test_demo_data_versions_have_exportable_files_or_content(self):
        create_demo_data(db_path=self.db_path)
        documents = list_documents(db_path=self.db_path)

        self.assertTrue(documents)
        for document in documents:
            version = get_current_version(document["id"], db_path=self.db_path)
            self.assertIsNotNone(version["content_json"])
            self.assertTrue(version["odf_path"])
            self.assertTrue(Path(version["odf_path"]).exists())

    def test_demo_data_contains_multiple_document_types(self):
        create_demo_data(db_path=self.db_path)
        document_types = {document["document_type"] for document in list_documents(db_path=self.db_path)}

        self.assertEqual(
            document_types,
            {
                "會議紀錄",
                "活動企劃書",
                "活動成果報告",
                "活動檢討會紀錄",
                "年度計畫",
            },
        )


if __name__ == "__main__":
    unittest.main()
