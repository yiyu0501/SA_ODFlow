from __future__ import annotations

from pathlib import Path

from core.database import DEFAULT_DB_PATH
from core.document_schemas import derive_document_title, normalize_document_content
from core.document_service import (
    create_document,
    create_document_version,
    list_documents,
    update_version_file_paths,
)
from core.settings_service import get_club_settings
from generators.odt_generator import generate_document_odt
from generators.pdf_generator import generate_document_pdf


DEMO_TITLE_PREFIX = "示範資料_"


def _build_demo_specs(club_name: str) -> list[dict]:
    return [
        {
            "document_type": "會議紀錄",
            "title": f"{DEMO_TITLE_PREFIX}幹部會議紀錄",
            "evaluation_category": "2.社團行政_管理運作",
            "status": "正式版",
            "content_json": {
                "document_title": f"{DEMO_TITLE_PREFIX}幹部會議紀錄",
                "meeting_title": f"{DEMO_TITLE_PREFIX}幹部會議紀錄",
                "meeting_date": "2026-06-12",
                "meeting_time": "18:30",
                "location": "社辦會議區",
                "chair": "林會長",
                "recorder": "陳文書",
                "attendees": ["林會長", "陳文書", "王活動", "李總務"],
                "absentees": [],
                "agenda_items": [
                    {
                        "title": "暑期招生活動準備",
                        "discussion": "確認場地借用、宣傳素材與值班分工。",
                        "decision": "下週前完成報名表與值班表。",
                    }
                ],
                "action_items": [
                    {
                        "task": "整理招生活動工作分配",
                        "owner": "王活動",
                        "deadline": "2026-06-18",
                        "note": "完成後回報群組。",
                    }
                ],
                "next_meeting_time": "2026-06-19 19:00",
                "notes": "示範用幹部會議紀錄。",
            },
        },
        {
            "document_type": "活動企劃書",
            "title": f"{DEMO_TITLE_PREFIX}迎新活動企劃書",
            "evaluation_category": "6.社團活動_社團活動",
            "status": "正式版",
            "content_json": {
                "document_title": f"{DEMO_TITLE_PREFIX}迎新活動企劃書",
                "activity_name": "迎新活動",
                "activity_date": "2026-09-18",
                "activity_time": "18:00-21:00",
                "location": "活動中心 3F",
                "organizer": club_name,
                "target_audience": "新生與幹部",
                "purpose": "協助新生成員快速認識社團與核心幹部。",
                "activity_description": "安排破冰、小隊任務與社團介紹，建立參與感。",
                "schedule_items": [
                    {
                        "time": "18:00",
                        "item": "報到與破冰",
                        "owner": "李宣傳",
                        "note": "入口報到桌同步發放資料。",
                    },
                    {
                        "time": "19:00",
                        "item": "社團介紹",
                        "owner": "林會長",
                        "note": "說明本學期重點活動。",
                    },
                ],
                "staff_assignments": [
                    {
                        "role": "總召",
                        "name": "王活動",
                        "task": "總體統籌與流程確認",
                    },
                    {
                        "role": "宣傳",
                        "name": "李宣傳",
                        "task": "海報與報名資訊整理",
                    },
                ],
                "budget_items": [
                    {"item": "點心", "amount": "2500", "note": "依報名人數調整"},
                    {"item": "名牌與文具", "amount": "800", "note": "現場分組使用"},
                ],
                "expected_outcomes": "預計招募 20 位新成員，建立本學期主要名單。",
                "notes": "示範用迎新活動企劃書。",
            },
        },
        {
            "document_type": "活動成果報告",
            "title": f"{DEMO_TITLE_PREFIX}迎新活動成果報告",
            "evaluation_category": "6.社團活動_社團活動",
            "status": "已歸檔",
            "content_json": {
                "document_title": f"{DEMO_TITLE_PREFIX}迎新活動成果報告",
                "activity_name": "迎新活動",
                "activity_date": "2026-09-18",
                "location": "活動中心 3F",
                "participant_count": "46",
                "organizer": club_name,
                "activity_summary": "完成迎新活動、社團介紹與分組交流。",
                "outcomes": "活動後新增 18 位穩定參與名單，社群加入率提升。",
                "photos_or_links": "社團雲端/迎新活動/照片集",
                "feedback_summary": "參與者反映分組任務互動佳，但開場等待較久。",
                "expense_summary": "總支出 3,120 元，低於原預算 180 元。",
                "improvement_notes": "下次應縮短報到與暖場時間，提早完成音控測試。",
                "notes": "示範用迎新活動成果報告。",
            },
        },
        {
            "document_type": "活動檢討會紀錄",
            "title": f"{DEMO_TITLE_PREFIX}迎新活動檢討會紀錄",
            "evaluation_category": "6.社團活動_社團活動",
            "status": "草稿",
            "content_json": {
                "document_title": f"{DEMO_TITLE_PREFIX}迎新活動檢討會紀錄",
                "meeting_title": f"{DEMO_TITLE_PREFIX}迎新活動檢討會紀錄",
                "meeting_date": "2026-09-21",
                "activity_name": "迎新活動",
                "attendees": ["王活動", "李宣傳", "張器材"],
                "strengths": "小隊任務互動度高，社團介紹段落節奏順。",
                "problems": "報到動線壅塞，音控彩排時間不足。",
                "improvement_actions": [
                    {
                        "issue": "報到動線",
                        "action": "增設第二報到桌",
                        "owner": "李宣傳",
                        "deadline": "下次大型活動前",
                    },
                    {
                        "issue": "音控彩排不足",
                        "action": "活動前一天完成全段彩排",
                        "owner": "張器材",
                        "deadline": "下次活動前",
                    },
                ],
                "next_time_suggestions": "保留破冰機制，但需提前完成現場配置。",
                "notes": "示範用活動檢討會紀錄。",
            },
        },
        {
            "document_type": "年度計畫",
            "title": f"{DEMO_TITLE_PREFIX}年度計畫",
            "evaluation_category": "4.社團行政_年度計畫",
            "status": "正式版",
            "content_json": {
                "document_title": f"{DEMO_TITLE_PREFIX}年度計畫",
                "academic_year": "114",
                "club_name": club_name,
                "annual_goal": "穩定社課運作、完成招新與服務學習主題活動。",
                "semester_plans": [
                    {
                        "semester": "上學期",
                        "plan": "完成招新、基礎培訓與迎新活動",
                        "expected_month": "9-11 月",
                        "owner": "林會長",
                    },
                    {
                        "semester": "下學期",
                        "plan": "辦理成果展與服務學習活動",
                        "expected_month": "3-5 月",
                        "owner": "王活動",
                    },
                ],
                "key_activities": [
                    {"activity_name": "迎新活動", "month": "9 月", "purpose": "招募新成員"},
                    {"activity_name": "成果展", "month": "5 月", "purpose": "展示年度成果"},
                ],
                "expected_outcomes": "提升穩定出席率與年度活動資料完整度。",
                "resource_needs": "場地協調、器材借用與活動預算支援。",
                "notes": "示範用年度計畫。",
            },
        },
    ]


def create_demo_data(db_path: Path | str = DEFAULT_DB_PATH) -> dict:
    existing_titles = {document["title"] for document in list_documents(db_path=db_path)}
    club_settings = get_club_settings(db_path=db_path)
    club_name = club_settings["club_name"]
    created_documents = []
    skipped_titles = []

    for spec in _build_demo_specs(club_name):
        normalized_content = normalize_document_content(
            spec["document_type"],
            spec["content_json"],
        )
        derived_title = derive_document_title(
            spec["document_type"],
            normalized_content,
            fallback=spec["title"],
        )
        if spec["title"] in existing_titles or derived_title in existing_titles:
            skipped_titles.append(spec["title"])
            continue

        document = create_document(
            title=derived_title,
            document_type=spec["document_type"],
            evaluation_category=spec["evaluation_category"],
            status=spec["status"],
            db_path=db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=normalized_content,
            note="Task 9 示範資料",
            db_path=db_path,
        )
        export_document = {**document, "club_name": club_name}

        odf_path = None
        pdf_path = None
        generation_errors = []

        try:
            odf_path = str(generate_document_odt(export_document, version))
        except ValueError as exc:
            generation_errors.append(f"ODT 產生失敗：{exc}")

        try:
            pdf_path = str(generate_document_pdf(export_document, version))
        except (RuntimeError, ValueError) as exc:
            generation_errors.append(f"PDF 產生失敗：{exc}")

        if odf_path or pdf_path:
            version = update_version_file_paths(
                document_id=document["id"],
                version_number=version["version_number"],
                odf_path=odf_path,
                pdf_path=pdf_path,
                db_path=db_path,
            )

        created_documents.append(
            {
                "document": document,
                "version": version,
                "errors": generation_errors,
            }
        )
        existing_titles.update({spec["title"], derived_title})

    return {
        "created_count": len(created_documents),
        "skipped_count": len(skipped_titles),
        "created_titles": [item["document"]["title"] for item in created_documents],
        "skipped_titles": skipped_titles,
        "documents": created_documents,
    }


DEMO_DOCUMENT_SPECS = _build_demo_specs("ODFlow示範社團")
