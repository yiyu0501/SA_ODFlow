from __future__ import annotations

import csv
import shutil
from pathlib import Path

from core.constants import EVALUATION_CATEGORIES
from core.database import DATA_DIR, DEFAULT_DB_PATH
from core.document_service import (
    get_current_version,
    list_documents,
    update_version_file_paths,
)
from core.filename import sanitize_filename_component
from generators.odt_generator import generate_meeting_minutes_odt
from generators.pdf_generator import generate_meeting_minutes_pdf
from generators.zip_generator import (
    copy_file_to_category,
    create_package_workspace,
    create_zip_archive,
    ensure_category_folders,
)


PDF_EXPORTABLE_STATUSES = {"正式版", "已歸檔"}
DEFAULT_ACADEMIC_YEAR = "114"
DEFAULT_CAMPUS = "天母校區"
DEFAULT_CLUB_NAME = "ODFlow示範社團"
EXPORTS_DIR = DATA_DIR / "generated" / "exports"


def build_evaluation_folder_name(
    academic_year: str,
    campus: str,
    club_name: str,
) -> str:
    safe_year = sanitize_filename_component(academic_year, fallback=DEFAULT_ACADEMIC_YEAR)
    safe_campus = sanitize_filename_component(campus, fallback=DEFAULT_CAMPUS)
    safe_club_name = sanitize_filename_component(club_name, fallback=DEFAULT_CLUB_NAME)
    return f"{safe_year}學年度臺北市立大學社團評鑑資料_{safe_campus}_{safe_club_name}"


def collect_exportable_documents(db_path: Path | str = DEFAULT_DB_PATH) -> list[dict]:
    records = []
    for document in list_documents(db_path=db_path):
        version = None
        version_error = None
        try:
            version = get_current_version(document["id"], db_path=db_path)
        except ValueError as exc:
            version_error = str(exc)

        records.append(
            {
                "document": document,
                "version": version,
                "document_id": document["id"],
                "title": document["title"],
                "document_type": document["document_type"],
                "evaluation_category": document["evaluation_category"],
                "status": document["status"],
                "current_version": document["current_version"],
                "current_version_label": document["current_version_label"],
                "content_json": version["content_json"] if version is not None else None,
                "pdf_path": version.get("pdf_path") if version is not None else None,
                "odf_path": version.get("odf_path") if version is not None else None,
                "version_error": version_error,
            }
        )

    return records


def build_document_index(
    package_root: Path,
    rows: list[dict],
    file_label: str = "PDF檔名",
) -> dict:
    headers = [
        "文件名稱",
        "文件類型",
        "評鑑分類",
        "狀態",
        "目前版本",
        file_label,
        "是否成功輸出",
        "備註",
    ]
    pdf_path = package_root / "文件索引表.pdf"
    csv_path = package_root / "文件索引表.csv"

    _build_table_pdf(
        output_path=pdf_path,
        title="文件索引表",
        headers=headers,
        rows=[
            [
                row["title"],
                row["document_type"],
                row["evaluation_category"],
                row["status"],
                row["current_version_label"],
                row["output_filename"],
                "是" if row["exported"] else "否",
                row["note"],
            ]
            for row in rows
        ],
        empty_message="目前沒有可列入索引的文件。",
        col_widths=[100, 72, 105, 48, 45, 120, 58, 170],
    )

    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(
                [
                    row["title"],
                    row["document_type"],
                    row["evaluation_category"],
                    row["status"],
                    row["current_version_label"],
                    row["output_filename"],
                    "是" if row["exported"] else "否",
                    row["note"],
                ]
            )

    return {"pdf_path": pdf_path, "csv_path": csv_path}


def build_failed_export_report(
    package_root: Path,
    rows: list[dict],
) -> Path:
    output_path = package_root / "未輸出文件清單.pdf"
    _build_table_pdf(
        output_path=output_path,
        title="未輸出文件清單",
        headers=["文件名稱", "文件類型", "評鑑分類", "狀態", "未輸出原因"],
        rows=[
            [
                row["title"],
                row["document_type"],
                row["evaluation_category"],
                row["status"],
                row["reason"],
            ]
            for row in rows
        ],
        empty_message="本次所有文件皆已成功輸出。",
        col_widths=[130, 80, 120, 55, 270],
    )
    return output_path


def build_pdf_evaluation_package(
    academic_year: str = DEFAULT_ACADEMIC_YEAR,
    campus: str = DEFAULT_CAMPUS,
    club_name: str = DEFAULT_CLUB_NAME,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    folder_name = build_evaluation_folder_name(academic_year, campus, club_name)
    zip_name = f"{folder_name}.zip"
    workspace_dir, package_root = create_package_workspace(folder_name)

    try:
        ensure_category_folders(package_root, EVALUATION_CATEGORIES)
        records = collect_exportable_documents(db_path=db_path)
        index_rows = []
        failed_rows = []
        exported_categories: set[str] = set()

        for record in records:
            exported = False
            note = ""
            output_filename = ""

            if record["status"] not in PDF_EXPORTABLE_STATUSES:
                note = "狀態不是正式版或已歸檔"
            else:
                pdf_path, generation_note, failure_reason = _ensure_pdf_path(record, db_path=db_path)
                if pdf_path is not None:
                    copied_path = copy_file_to_category(
                        pdf_path,
                        package_root,
                        record["evaluation_category"],
                    )
                    output_filename = copied_path.name
                    exported = True
                    note = generation_note
                    exported_categories.add(record["evaluation_category"])
                else:
                    note = failure_reason

            row = _build_index_row(record, output_filename, exported, note)
            index_rows.append(row)
            if not exported:
                failed_rows.append(_build_failed_row(record, note))

        index_paths = build_document_index(package_root, index_rows, file_label="PDF檔名")
        failed_report_path = build_failed_export_report(package_root, failed_rows)
        zip_path = create_zip_archive(package_root, zip_name, output_dir=EXPORTS_DIR)

        return {
            "zip_path": zip_path,
            "zip_name": zip_path.name,
            "top_level_folder": folder_name,
            "exported_count": sum(1 for row in index_rows if row["exported"]),
            "failed_count": len(failed_rows),
            "exported_categories": _ordered_categories(exported_categories),
            "index_pdf_path": index_paths["pdf_path"],
            "index_csv_path": index_paths["csv_path"],
            "failed_report_path": failed_report_path,
            "documents": index_rows,
            "failed_documents": failed_rows,
        }
    finally:
        shutil.rmtree(workspace_dir, ignore_errors=True)


def build_odf_backup_package(
    academic_year: str = DEFAULT_ACADEMIC_YEAR,
    club_name: str = DEFAULT_CLUB_NAME,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    safe_year = sanitize_filename_component(academic_year, fallback=DEFAULT_ACADEMIC_YEAR)
    safe_club_name = sanitize_filename_component(club_name, fallback=DEFAULT_CLUB_NAME)
    folder_name = f"{safe_year}學年度_{safe_club_name}_ODF原始檔備份"
    zip_name = f"{folder_name}.zip"
    workspace_dir, package_root = create_package_workspace(folder_name)

    try:
        ensure_category_folders(package_root, EVALUATION_CATEGORIES)
        records = collect_exportable_documents(db_path=db_path)
        index_rows = []
        failed_rows = []
        exported_categories: set[str] = set()

        for record in records:
            odf_path, generation_note, failure_reason = _ensure_odf_path(record, db_path=db_path)
            exported = odf_path is not None
            output_filename = ""

            if odf_path is not None:
                copied_path = copy_file_to_category(
                    odf_path,
                    package_root,
                    record["evaluation_category"],
                )
                output_filename = copied_path.name
                exported_categories.add(record["evaluation_category"])
                note = generation_note
            else:
                note = failure_reason
                failed_rows.append(_build_failed_row(record, failure_reason))

            index_rows.append(_build_index_row(record, output_filename, exported, note))

        index_paths = build_document_index(package_root, index_rows, file_label="原始檔檔名")
        failed_report_path = build_failed_export_report(package_root, failed_rows)
        zip_path = create_zip_archive(package_root, zip_name, output_dir=EXPORTS_DIR)

        return {
            "zip_path": zip_path,
            "zip_name": zip_path.name,
            "top_level_folder": folder_name,
            "exported_count": sum(1 for row in index_rows if row["exported"]),
            "failed_count": len(failed_rows),
            "exported_categories": _ordered_categories(exported_categories),
            "index_pdf_path": index_paths["pdf_path"],
            "index_csv_path": index_paths["csv_path"],
            "failed_report_path": failed_report_path,
            "documents": index_rows,
            "failed_documents": failed_rows,
        }
    finally:
        shutil.rmtree(workspace_dir, ignore_errors=True)


def _ordered_categories(categories: set[str]) -> list[str]:
    return [category for category in EVALUATION_CATEGORIES if category in categories]


def _build_index_row(
    record: dict,
    output_filename: str,
    exported: bool,
    note: str,
) -> dict:
    return {
        "title": record["title"],
        "document_type": record["document_type"],
        "evaluation_category": record["evaluation_category"],
        "status": record["status"],
        "current_version_label": record["current_version_label"],
        "output_filename": output_filename or "-",
        "exported": exported,
        "note": note or "",
    }


def _build_failed_row(record: dict, reason: str) -> dict:
    return {
        "title": record["title"],
        "document_type": record["document_type"],
        "evaluation_category": record["evaluation_category"],
        "status": record["status"],
        "reason": reason or "未提供失敗原因",
    }


def _resolve_file(path_value: str | None) -> Path | None:
    if not path_value:
        return None

    path = Path(path_value)
    if path.exists() and path.is_file():
        return path
    return None


def _ensure_pdf_path(
    record: dict,
    db_path: Path | str,
) -> tuple[Path | None, str, str]:
    existing_path = _resolve_file(record.get("pdf_path"))
    if existing_path is not None:
        return existing_path, "", ""

    if record.get("version_error"):
        return None, "", record["version_error"]
    if record.get("version") is None:
        return None, "", "找不到目前版本"
    if record.get("content_json") is None:
        return None, "", "找不到 content_json"

    try:
        output_path = generate_meeting_minutes_pdf(record["document"], record["version"])
        updated_version = update_version_file_paths(
            document_id=record["document_id"],
            version_number=record["version"]["version_number"],
            pdf_path=str(output_path),
            db_path=db_path,
        )
    except (RuntimeError, ValueError) as exc:
        return None, "", f"沒有 PDF 且自動產生失敗：{exc}"

    record["version"] = updated_version
    record["content_json"] = updated_version["content_json"]
    record["pdf_path"] = updated_version["pdf_path"]
    return output_path, "無既有 PDF，已自動補產生。", ""


def _ensure_odf_path(
    record: dict,
    db_path: Path | str,
) -> tuple[Path | None, str, str]:
    existing_path = _resolve_file(record.get("odf_path"))
    if existing_path is not None:
        return existing_path, "", ""

    if record.get("version_error"):
        return None, "", record["version_error"]
    if record.get("version") is None:
        return None, "", "找不到目前版本"
    if record.get("content_json") is None:
        return None, "", "找不到 content_json"

    try:
        output_path = generate_meeting_minutes_odt(record["document"], record["version"])
        updated_version = update_version_file_paths(
            document_id=record["document_id"],
            version_number=record["version"]["version_number"],
            odf_path=str(output_path),
            db_path=db_path,
        )
    except ValueError as exc:
        return None, "", f"沒有 ODF 且自動產生失敗：{exc}"

    record["version"] = updated_version
    record["content_json"] = updated_version["content_json"]
    record["odf_path"] = updated_version["odf_path"]
    return output_path, "無既有 ODF，已自動補產生。", ""


def _build_table_pdf(
    output_path: Path,
    title: str,
    headers: list[str],
    rows: list[list[str]],
    empty_message: str,
    col_widths: list[int],
) -> None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfbase.pdfmetrics import registerFont
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError(
            "缺少 reportlab，請先執行 `pip install -r requirements.txt`。"
        ) from exc

    registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="STSong-Light",
        fontSize=16,
        leading=20,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="STSong-Light",
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
    )
    header_style = ParagraphStyle(
        "ReportHeader",
        parent=body_style,
        fontSize=9.5,
    )

    story = [Paragraph(title, title_style), Spacer(1, 12)]
    if rows:
        table_data = [
            [Paragraph(header, header_style) for header in headers],
            *[
                [Paragraph(str(cell or "-"), body_style) for cell in row]
                for row in rows
            ],
        ]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9eef7")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("LEADING", (0, 0), (-1, -1), 11),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
    else:
        story.append(Paragraph(empty_message, body_style))

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28,
    )
    document.build(story)
