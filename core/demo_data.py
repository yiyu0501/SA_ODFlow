from __future__ import annotations

from pathlib import Path

from core.database import DEFAULT_DB_PATH
from core.document_service import (
    create_document,
    create_document_version,
    list_documents,
    update_version_file_paths,
)
from core.meeting_minutes import empty_meeting_minutes_content
from core.settings_service import get_club_settings
from generators.odt_generator import generate_meeting_minutes_odt
from generators.pdf_generator import generate_meeting_minutes_pdf


DEMO_TITLE_PREFIX = "示範資料_"
DEMO_DOCUMENT_SPECS = [
    {
        "title": f"{DEMO_TITLE_PREFIX}幹部會議紀錄",
        "document_type": "會議紀錄",
        "evaluation_category": "2.社團行政_管理運作",
        "status": "正式版",
        "meeting_date": "2026-06-12",
        "meeting_time": "18:30",
        "location": "社辦會議區",
        "chair": "林會長",
        "recorder": "陳文書",
        "attendees": ["林會長", "陳文書", "王活動", "李總務"],
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
    {
        "title": f"{DEMO_TITLE_PREFIX}社員大會紀錄",
        "document_type": "會議紀錄",
        "evaluation_category": "2.社團行政_管理運作",
        "status": "已歸檔",
        "meeting_date": "2026-05-22",
        "meeting_time": "19:00",
        "location": "公誠樓 201",
        "chair": "林會長",
        "recorder": "陳文書",
        "attendees": ["林會長", "陳文書", "社員甲", "社員乙", "社員丙"],
        "agenda_items": [
            {
                "title": "期末社員大會",
                "discussion": "回顧本學期活動成果與下學期重點。",
                "decision": "通過下學期招新與成果展規劃方向。",
            }
        ],
        "action_items": [
            {
                "task": "整理社員大會簡報與簽到紀錄",
                "owner": "陳文書",
                "deadline": "2026-05-28",
                "note": "歸檔至社團雲端與 ODFlow。",
            }
        ],
        "next_meeting_time": "2026-09-10 18:30",
        "notes": "示範用社員大會紀錄。",
    },
    {
        "title": f"{DEMO_TITLE_PREFIX}活動檢討會紀錄",
        "document_type": "會議紀錄",
        "evaluation_category": "6.社團活動_社團活動",
        "status": "草稿",
        "meeting_date": "2026-04-18",
        "meeting_time": "20:00",
        "location": "線上會議",
        "chair": "王活動",
        "recorder": "李宣傳",
        "attendees": ["王活動", "李宣傳", "張器材"],
        "agenda_items": [
            {
                "title": "迎新工作坊檢討",
                "discussion": "檢討流程節奏、音控協調與報到動線。",
                "decision": "下次活動需提前一天完成音控彩排。",
            }
        ],
        "action_items": [
            {
                "task": "補上活動照片索引",
                "owner": "李宣傳",
                "deadline": "2026-04-22",
                "note": "草稿待確認後轉正式版。",
            }
        ],
        "next_meeting_time": "",
        "notes": "示範用活動檢討會紀錄。",
    },
    {
        "title": f"{DEMO_TITLE_PREFIX}年度計畫示範文件",
        "document_type": "年度計畫",
        "evaluation_category": "4.社團行政_年度計畫",
        "status": "正式版",
        "meeting_date": "2026-03-01",
        "meeting_time": "17:30",
        "location": "社團辦公室",
        "chair": "林會長",
        "recorder": "陳文書",
        "attendees": ["林會長", "陳文書", "王活動", "李總務"],
        "agenda_items": [
            {
                "title": "年度計畫主軸",
                "discussion": "訂定年度招新、社課與服務學習規劃節點。",
                "decision": "完成年度活動時程與執行對照項目。",
            }
        ],
        "action_items": [
            {
                "task": "整理年度行事曆初稿",
                "owner": "陳文書",
                "deadline": "2026-03-08",
                "note": "與老師確認後歸檔。",
            }
        ],
        "next_meeting_time": "2026-03-15 18:00",
        "notes": "示範用年度計畫文件。",
    },
    {
        "title": f"{DEMO_TITLE_PREFIX}活動成果報告示範文件",
        "document_type": "活動成果報告",
        "evaluation_category": "6.社團活動_社團活動",
        "status": "已歸檔",
        "meeting_date": "2026-04-25",
        "meeting_time": "16:00",
        "location": "活動中心 3F",
        "chair": "王活動",
        "recorder": "李宣傳",
        "attendees": ["王活動", "李宣傳", "張器材", "社員甲"],
        "agenda_items": [
            {
                "title": "成果整理",
                "discussion": "整理參與人數、滿意度與照片授權清單。",
                "decision": "成果報告完成後納入評鑑資料保存。",
            }
        ],
        "action_items": [
            {
                "task": "補上成果照片說明",
                "owner": "李宣傳",
                "deadline": "2026-04-28",
                "note": "完成後更新 PDF 與 ODT。",
            }
        ],
        "next_meeting_time": "",
        "notes": "示範用活動成果報告文件。",
    },
]


def create_demo_data(db_path: Path | str = DEFAULT_DB_PATH) -> dict:
    existing_titles = {document["title"] for document in list_documents(db_path=db_path)}
    club_settings = get_club_settings(db_path=db_path)
    created_documents = []
    skipped_titles = []

    for spec in DEMO_DOCUMENT_SPECS:
        if spec["title"] in existing_titles:
            skipped_titles.append(spec["title"])
            continue

        document = create_document(
            title=spec["title"],
            document_type=spec["document_type"],
            evaluation_category=spec["evaluation_category"],
            status=spec["status"],
            db_path=db_path,
        )
        version = create_document_version(
            document_id=document["id"],
            content_json=_build_demo_content(spec),
            note="Task 6 示範資料",
            db_path=db_path,
        )
        export_document = {**document, "club_name": club_settings["club_name"]}

        odf_path = None
        pdf_path = None
        generation_errors = []

        try:
            odf_path = str(generate_meeting_minutes_odt(export_document, version))
        except ValueError as exc:
            generation_errors.append(f"ODT 產生失敗：{exc}")

        try:
            pdf_path = str(generate_meeting_minutes_pdf(export_document, version))
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
        existing_titles.add(spec["title"])

    return {
        "created_count": len(created_documents),
        "skipped_count": len(skipped_titles),
        "created_titles": [item["document"]["title"] for item in created_documents],
        "skipped_titles": skipped_titles,
        "documents": created_documents,
    }


def _build_demo_content(spec: dict) -> dict:
    content = empty_meeting_minutes_content()
    content["meeting_title"] = spec["title"]
    content["meeting_date"] = spec["meeting_date"]
    content["meeting_time"] = spec["meeting_time"]
    content["location"] = spec["location"]
    content["chair"] = spec["chair"]
    content["recorder"] = spec["recorder"]
    content["attendees"] = spec["attendees"]
    content["agenda_items"] = spec["agenda_items"]
    content["action_items"] = spec["action_items"]
    content["next_meeting_time"] = spec["next_meeting_time"]
    content["notes"] = spec["notes"]
    return content
