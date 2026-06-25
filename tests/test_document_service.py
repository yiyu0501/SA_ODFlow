from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.document_schemas import get_default_document_content
from core.document_service import (
    create_document,
    create_document_version,
    get_current_version,
    get_document,
    get_document_versions,
    get_document_with_current_version,
    list_documents,
    set_current_version,
    update_document_status,
    update_version_file_paths,
    validate_document_status,
    validate_evaluation_category,
)


class DocumentServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "odflow.sqlite3"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _sample_meeting_content(self, title: str = "第 3 次幹部會議") -> dict:
        content = get_default_document_content("會議紀錄")
        content["meeting_title"] = title
        content["meeting_date"] = "2026-06-24"
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
                "note": "",
            }
        ]
        return content

    def _sample_activity_proposal(self) -> dict:
        content = get_default_document_content("活動企劃書")
        content["activity_name"] = "迎新活動"
        content["organizer"] = "ODFlow示範社團"
        content["schedule_items"] = [
            {"time": "18:00", "item": "報到", "owner": "李宣傳", "note": ""}
        ]
        return content

    def _sample_activity_report(self) -> dict:
        content = get_default_document_content("活動成果報告")
        content["activity_name"] = "迎新活動"
        content["participant_count"] = "30"
        content["activity_summary"] = "活動順利完成"
        return content

    def _sample_activity_review(self) -> dict:
        content = get_default_document_content("活動檢討會紀錄")
        content["meeting_title"] = "迎新活動檢討會"
        content["activity_name"] = "迎新活動"
        content["improvement_actions"] = [
            {
                "issue": "報到塞車",
                "action": "增設第二桌",
                "owner": "王活動",
                "deadline": "下次活動前",
            }
        ]
        return content

    def _sample_annual_plan(self) -> dict:
        content = get_default_document_content("年度計畫")
        content["academic_year"] = "114"
        content["club_name"] = "ODFlow示範社團"
        content["annual_goal"] = "完成年度活動整理"
        content["semester_plans"] = [
            {
                "semester": "上學期",
                "plan": "招新與迎新",
                "expected_month": "9 月",
                "owner": "林會長",
            }
        ]
        return content

    def test_create_document_adds_document(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )

        self.assertEqual(document["title"], "第 3 次幹部會議")
        self.assertEqual(document["status"], "草稿")
        self.assertEqual(document["current_version"], 0)

    def test_create_document_version_adds_new_version(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )

        version_one = create_document_version(
            document_id=document["id"],
            content_json=self._sample_meeting_content(),
            db_path=self.db_path,
        )
        version_two = create_document_version(
            document_id=document["id"],
            content_json=self._sample_meeting_content(title="第 3 次幹部會議（修訂）"),
            db_path=self.db_path,
        )

        self.assertEqual(version_one["version_number"], 1)
        self.assertEqual(version_two["version_number"], 2)

        refreshed_document = get_document(document["id"], db_path=self.db_path)
        self.assertEqual(refreshed_document["current_version"], 2)

    def test_list_documents_returns_created_document(self):
        create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )

        documents = list_documents(db_path=self.db_path)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["title"], "第 3 次幹部會議")

    def test_get_document_versions_returns_versions(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        create_document_version(
            document_id=document["id"],
            content_json=self._sample_meeting_content(),
            db_path=self.db_path,
        )

        versions = get_document_versions(document["id"], db_path=self.db_path)

        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0]["content_json"]["meeting_title"], "第 3 次幹部會議")

    def test_update_document_status_rejects_invalid_status(self):
        with self.assertRaises(ValueError):
            validate_document_status("草稿中")

    def test_validate_evaluation_category_rejects_invalid_category(self):
        with self.assertRaises(ValueError):
            validate_evaluation_category("9.不存在分類")

    def test_set_current_version_can_switch_back_to_previous_version(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        create_document_version(
            document_id=document["id"],
            content_json=self._sample_meeting_content(title="版本一"),
            db_path=self.db_path,
        )
        create_document_version(
            document_id=document["id"],
            content_json=self._sample_meeting_content(title="版本二"),
            db_path=self.db_path,
        )

        updated_document = set_current_version(
            document_id=document["id"],
            version_number=1,
            db_path=self.db_path,
        )

        self.assertEqual(updated_document["current_version"], 1)
        self.assertEqual(updated_document["title"], "版本一")

    def test_update_document_status_accepts_valid_status(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )

        updated_document = update_document_status(
            document_id=document["id"],
            status="待審",
            db_path=self.db_path,
        )

        self.assertEqual(updated_document["status"], "待審")

    def test_get_current_version_returns_current_version_row(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        create_document_version(
            document_id=document["id"],
            content_json=self._sample_meeting_content(title="版本一"),
            db_path=self.db_path,
        )

        current_version = get_current_version(document["id"], db_path=self.db_path)

        self.assertEqual(current_version["version_number"], 1)
        self.assertEqual(current_version["content_json"]["meeting_title"], "版本一")

    def test_update_version_file_paths_persists_paths(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        create_document_version(
            document_id=document["id"],
            content_json=self._sample_meeting_content(),
            db_path=self.db_path,
        )

        updated_version = update_version_file_paths(
            document_id=document["id"],
            version_number=1,
            odf_path="/tmp/demo.odt",
            pdf_path="/tmp/demo.pdf",
            db_path=self.db_path,
        )

        self.assertEqual(updated_version["odf_path"], "/tmp/demo.odt")
        self.assertEqual(updated_version["pdf_path"], "/tmp/demo.pdf")

    def test_get_document_with_current_version_returns_current_version_data(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        create_document_version(
            document_id=document["id"],
            content_json=self._sample_meeting_content(title="版本一"),
            db_path=self.db_path,
        )

        document_with_version = get_document_with_current_version(
            document["id"],
            db_path=self.db_path,
        )

        self.assertEqual(
            document_with_version["current_version_data"]["content_json"]["meeting_title"],
            "版本一",
        )

    def test_activity_proposal_can_be_saved_to_files(self):
        document = create_document(
            title="迎新活動企劃書",
            document_type="活動企劃書",
            evaluation_category="6.社團活動_社團活動",
            db_path=self.db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=self._sample_activity_proposal(),
            db_path=self.db_path,
        )
        self.assertEqual(version["content_json"]["activity_name"], "迎新活動")

    def test_activity_report_can_be_saved_to_files(self):
        document = create_document(
            title="迎新活動成果報告",
            document_type="活動成果報告",
            evaluation_category="6.社團活動_社團活動",
            db_path=self.db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=self._sample_activity_report(),
            db_path=self.db_path,
        )
        self.assertEqual(version["content_json"]["participant_count"], "30")

    def test_activity_review_can_be_saved_to_files(self):
        document = create_document(
            title="迎新活動檢討會紀錄",
            document_type="活動檢討會紀錄",
            evaluation_category="6.社團活動_社團活動",
            db_path=self.db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=self._sample_activity_review(),
            db_path=self.db_path,
        )
        self.assertEqual(version["content_json"]["meeting_title"], "迎新活動檢討會")

    def test_annual_plan_can_be_saved_to_files(self):
        document = create_document(
            title="年度計畫",
            document_type="年度計畫",
            evaluation_category="4.社團行政_年度計畫",
            db_path=self.db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=self._sample_annual_plan(),
            db_path=self.db_path,
        )
        self.assertEqual(version["content_json"]["academic_year"], "114")


if __name__ == "__main__":
    unittest.main()
