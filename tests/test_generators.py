from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from core.document_schemas import get_default_document_content
from core.template_service import generate_template_file
from core.document_service import (
    create_document,
    create_document_version,
    get_current_version,
    update_version_file_paths,
)
from core.filename import build_versioned_filename
from generators.odt_generator import generate_document_odt, generate_meeting_minutes_odt
from generators.pdf_generator import generate_document_pdf, generate_meeting_minutes_pdf


class ExportGeneratorsTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "odflow.sqlite3"
        self.output_dir = Path(self.temp_dir.name) / "generated"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _sample_content(self, document_type: str) -> dict:
        content = get_default_document_content(document_type)
        if document_type == "會議紀錄":
            content["meeting_title"] = "第/3次:幹部會議"
            content["meeting_date"] = "2026-06-24"
            content["meeting_time"] = "18:30"
            content["location"] = "社辦"
            content["chair"] = "王小明"
            content["recorder"] = "李小華"
            content["attendees"] = ["王小明", "李小華"]
            content["absentees"] = ["張同學"]
            content["opening_remarks"] = "請各組確認本週進度。"
            content["reports"] = "財務組報告迎新預算。"
            content["motions"] = "無。"
            content["adjournment_time"] = "20:10"
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
        elif document_type == "開會通知單":
            content["organization_name"] = "ODFlow示範社團"
            content["recipient"] = "全體幹部"
            content["document_date"] = "2026-06-20"
            content["document_number"] = "ODF字第001號"
            content["priority"] = "普通件"
            content["security_level"] = "普通"
            content["attachments"] = "無"
            content["meeting_reason"] = "確認迎新活動分工"
            content["meeting_datetime"] = "2026-06-24 18:30"
            content["meeting_location"] = "社辦"
            content["host"] = "王小明"
            content["contact_person"] = "李小華"
            content["contact_phone"] = "02-0000-0000"
            content["attendees"] = ["王小明", "李小華"]
            content["observers"] = ["張同學"]
            content["note"] = "請準時出席"
        elif document_type == "會議議程":
            content["meeting_title"] = "第 3 次幹部會議議程"
            content["meeting_date"] = "2026-06-24"
            content["meeting_time"] = "18:30"
            content["location"] = "社辦"
            content["chair"] = "王小明"
            content["recorder"] = "李小華"
            content["agenda_items"] = [
                {"time": "18:30", "item": "主席致詞", "owner": "王小明", "note": ""},
                {"time": "18:40", "item": "迎新進度報告", "owner": "李小華", "note": ""},
            ]
            content["proposal_items"] = [
                {
                    "title": "迎新活動場地",
                    "discussion": "確認活動中心 3F 是否可借用",
                    "decision": "由總務組提出申請",
                    "note": "",
                }
            ]
        elif document_type == "活動企劃書":
            content["activity_name"] = "迎新活動"
            content["activity_date"] = "2026-09-20"
            content["activity_time"] = "18:00-21:00"
            content["location"] = "活動中心 3F"
            content["activity_location"] = "活動中心 3F"
            content["school_name"] = "臺北市立大學"
            content["activity_theme"] = "新生交流"
            content["advisor_unit"] = "課外活動組"
            content["organizer"] = "ODFlow示範社團"
            content["co_organizer"] = "學生會"
            content["target_audience"] = "新生"
            content["expected_participants"] = "30"
            content["purpose"] = "協助新生快速認識社團。"
            content["activity_description"] = "安排破冰、社團介紹與小隊任務。"
            content["activity_content"] = "安排破冰、社團介紹與小隊任務。"
            content["schedule_items"] = [
                {"time": "18:00", "item": "報到", "owner": "李宣傳", "note": ""}
            ]
            content["staff_assignments"] = [
                {"role": "總召", "name": "王活動", "task": "整體統籌"}
            ]
            content["contact_items"] = [
                {"role": "總召", "name": "王活動", "phone": "0912-000-000", "email": "demo@example.com"}
            ]
            content["preparation_items"] = [
                {"task": "場地確認", "owner": "王活動", "deadline": "活動前一週", "note": ""}
            ]
            content["budget_items"] = [
                {
                    "item": "點心",
                    "description": "活動茶點",
                    "quantity": "30",
                    "unit_price": "70",
                    "amount": "2100",
                    "funding_source": "社費",
                    "note": "依人數調整",
                }
            ]
            content["expected_benefits"] = "提升參與率"
            content["expected_outcomes"] = "提升參與率"
            content["promotion_plan"] = "社群公告與班級宣傳"
            content["resource_needs"] = "場地、音響、投影設備"
            content["equipment_list"] = "投影機、麥克風"
            content["school_support"] = "協助借用場地"
            content["attachments"] = "無"
        elif document_type == "活動成果報告":
            content["activity_name"] = "迎新活動"
            content["activity_date"] = "2026-09-20"
            content["location"] = "活動中心 3F"
            content["participant_count"] = "30"
            content["organizer"] = "ODFlow示範社團"
            content["responsible_person"] = "王活動"
            content["activity_summary"] = "活動順利完成"
            content["outcomes"] = "招募 18 位新成員"
            content["feedback_summary"] = "互動良好"
            content["expense_summary"] = "低於預算"
            content["improvement_notes"] = "下次提早場佈"
            content["follow_up_items"] = [
                {"task": "寄送活動回顧", "owner": "李宣傳", "deadline": "2026-09-25", "note": ""}
            ]
        elif document_type == "活動檢討會紀錄":
            content["meeting_title"] = "迎新活動檢討會"
            content["meeting_date"] = "2026-09-21"
            content["activity_name"] = "迎新活動"
            content["location"] = "社辦"
            content["chair"] = "王活動"
            content["recorder"] = "李小華"
            content["attendees"] = ["王活動", "李小華"]
            content["improvement_actions"] = [
                {
                    "issue": "報到塞車",
                    "planned": "單一報到桌",
                    "actual": "尖峰時段排隊",
                    "problem": "動線不足",
                    "action": "增設第二桌",
                    "owner": "王活動",
                    "deadline": "下次活動前",
                }
            ]
            content["strengths"] = "小隊互動熱絡"
            content["problems"] = "音控測試不足"
            content["next_time_suggestions"] = "提前彩排"
        elif document_type == "年度計畫":
            content["academic_year"] = "114"
            content["club_name"] = "ODFlow示範社團"
            content["club_purpose"] = "推廣社團參與與文件整理"
            content["annual_goal"] = "完成年度活動整理"
            content["semester_plans"] = [
                {
                    "semester": "上學期",
                    "plan": "招新",
                    "expected_month": "9 月",
                    "owner": "林會長",
                }
            ]
            content["key_activities"] = [
                {
                    "month": "9 月",
                    "activity_name": "迎新活動",
                    "activity_type": "招新",
                    "target": "新生",
                    "expected_outcome": "建立穩定名單",
                    "purpose": "招募新成員",
                    "note": "",
                }
            ]
            content["cadre_assignments"] = [
                {"role": "會長", "name": "林會長", "task": "總體規劃"}
            ]
            content["expected_outcomes"] = "完成年度資料留存"
            content["resource_needs"] = "場地與器材"
        return content

    def _create_document_with_version(self, document_type: str) -> tuple[dict, dict]:
        document = create_document(
            title=f"{document_type}測試",
            document_type=document_type,
            evaluation_category="6.社團活動_社團活動"
            if document_type in {"活動企劃書", "活動成果報告", "活動檢討會紀錄"}
            else "4.社團行政_年度計畫"
            if document_type == "年度計畫"
            else "2.社團行政_管理運作",
            db_path=self.db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=self._sample_content(document_type),
            db_path=self.db_path,
        )
        return document, version

    def test_generate_document_odt_supports_seven_document_types(self):
        for document_type in [
            "會議紀錄",
            "開會通知單",
            "會議議程",
            "活動企劃書",
            "活動成果報告",
            "活動檢討會紀錄",
            "年度計畫",
        ]:
            document, version = self._create_document_with_version(document_type)
            output_path = generate_document_odt(
                document=document,
                version=version,
                output_dir=self.output_dir,
            )
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.suffix, ".odt")
            with zipfile.ZipFile(output_path) as archive:
                self.assertIn("content.xml", archive.namelist())
                content_xml = archive.read("content.xml").decode("utf-8")
                self.assertIn("office:document-content", content_xml)
                self.assertIn("text:h", content_xml)
                if document_type in {"會議紀錄", "開會通知單", "活動企劃書"}:
                    self.assertNotIn("{{", content_xml)
                    self.assertNotIn("}}", content_xml)

    def test_generate_document_pdf_supports_seven_document_types(self):
        for document_type in [
            "會議紀錄",
            "開會通知單",
            "會議議程",
            "活動企劃書",
            "活動成果報告",
            "活動檢討會紀錄",
            "年度計畫",
        ]:
            document, version = self._create_document_with_version(document_type)
            output_path = generate_document_pdf(
                document=document,
                version=version,
                output_dir=self.output_dir,
            )
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.suffix, ".pdf")
            self.assertTrue(output_path.read_bytes().startswith(b"%PDF-"))
            self.assertGreater(output_path.stat().st_size, 1000)

    def test_generate_attendance_sheet_ods_template(self):
        output_path = generate_template_file(
            "attendance_sheet_ods",
            output_dir=self.output_dir / "templates",
        )

        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.suffix, ".ods")
        with zipfile.ZipFile(output_path) as archive:
            self.assertIn("content.xml", archive.namelist())
            content_xml = archive.read("content.xml").decode("utf-8")
            self.assertIn("出席簽到表", content_xml)
            self.assertIn("編號", content_xml)
            self.assertIn("姓名", content_xml)

    def test_generated_file_paths_can_be_written_back(self):
        document, version = self._create_document_with_version("會議紀錄")
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

    def test_generator_accepts_partial_legacy_content_json(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        legacy_version = {
            "document_id": document["id"],
            "version_number": 1,
            "content_json": {"meeting_title": "只有標題"},
        }
        output_path = generate_meeting_minutes_odt(
            document=document,
            version=legacy_version,
            output_dir=self.output_dir,
        )

        self.assertTrue(output_path.exists())

    def test_generator_rejects_non_dict_content_json(self):
        document = create_document(
            title="第 3 次幹部會議",
            document_type="會議紀錄",
            evaluation_category="2.社團行政_管理運作",
            db_path=self.db_path,
        )
        broken_version = {
            "document_id": document["id"],
            "version_number": 1,
            "content_json": "not-a-dict",
        }

        with self.assertRaises(ValueError):
            generate_meeting_minutes_odt(
                document=document,
                version=broken_version,
                output_dir=self.output_dir,
            )

    def test_empty_values_do_not_crash_generators(self):
        for document_type in [
            "會議紀錄",
            "開會通知單",
            "會議議程",
            "活動企劃書",
            "活動成果報告",
            "活動檢討會紀錄",
            "年度計畫",
        ]:
            document, version = self._create_document_with_version(document_type)
            empty_version = {
                **version,
                "content_json": get_default_document_content(document_type),
            }
            odt_path = generate_document_odt(
                document=document,
                version=empty_version,
                output_dir=self.output_dir,
            )
            pdf_path = generate_document_pdf(
                document=document,
                version=empty_version,
                output_dir=self.output_dir,
            )
            self.assertTrue(odt_path.exists(), document_type)
            self.assertTrue(pdf_path.exists(), document_type)


if __name__ == "__main__":
    unittest.main()
