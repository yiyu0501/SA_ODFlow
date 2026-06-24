from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.document_service import create_document
from core.evaluation_service import (
    get_category_completion,
    get_evaluation_summary,
    get_missing_requirements,
    get_recommendations,
)


class EvaluationServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "odflow.sqlite3"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_document(self, title: str, category: str, status: str) -> dict:
        return create_document(
            title=title,
            document_type="會議紀錄" if "紀錄" in title else title,
            evaluation_category=category,
            status=status,
            db_path=self.db_path,
        )

    def test_get_evaluation_summary_returns_seven_categories(self):
        summary = get_evaluation_summary(db_path=self.db_path)
        self.assertEqual(len(summary["category_summaries"]), 7)

    def test_overall_completion_is_zero_without_documents(self):
        summary = get_evaluation_summary(db_path=self.db_path)
        self.assertEqual(summary["overall_completion_percentage"], 0.0)

    def test_formal_document_increases_completion(self):
        self._create_document("幹部會議紀錄", "2.社團行政_管理運作", "正式版")
        category_summary = get_category_completion(
            "2.社團行政_管理運作",
            db_path=self.db_path,
        )
        self.assertGreater(category_summary["completion_percentage"], 0.0)
        self.assertEqual(category_summary["completed_count"], 1)

    def test_draft_document_does_not_count_as_completed(self):
        self._create_document("幹部會議紀錄", "2.社團行政_管理運作", "草稿")
        category_summary = get_category_completion(
            "2.社團行政_管理運作",
            db_path=self.db_path,
        )
        self.assertEqual(category_summary["completed_count"], 0)
        self.assertEqual(category_summary["in_progress_count"], 1)

    def test_pending_document_is_in_progress_not_completed(self):
        self._create_document("社員大會紀錄", "2.社團行政_管理運作", "待審")
        category_summary = get_category_completion(
            "2.社團行政_管理運作",
            db_path=self.db_path,
        )
        statuses = {
            item["requirement_name"]: item["status"]
            for item in category_summary["required_documents"]
        }
        self.assertEqual(statuses["社員大會紀錄"], "進行中")
        self.assertEqual(category_summary["completed_count"], 0)

    def test_archived_document_counts_as_completed(self):
        self._create_document("年度計畫", "4.社團行政_年度計畫", "已歸檔")
        category_summary = get_category_completion(
            "4.社團行政_年度計畫",
            db_path=self.db_path,
        )
        statuses = {
            item["requirement_name"]: item["status"]
            for item in category_summary["required_documents"]
        }
        self.assertEqual(statuses["年度計畫"], "已完成")

    def test_get_missing_requirements_lists_missing_documents(self):
        self._create_document("幹部會議紀錄", "2.社團行政_管理運作", "正式版")
        missing = get_missing_requirements(db_path=self.db_path)
        self.assertTrue(any(item["requirement_name"] == "社員大會紀錄" for item in missing))

    def test_get_recommendations_returns_messages_for_missing_categories(self):
        recommendations = get_recommendations(db_path=self.db_path)
        messages = [item["message"] for item in recommendations]
        self.assertTrue(any("年度計畫" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
