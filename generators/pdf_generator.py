from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from core.document_schemas import derive_document_title
from generators.document_layout import build_document_render_spec
from generators.document_style import (
    BODY_FONT_SIZE_PT,
    NOTE_FONT_SIZE_PT,
    SECTION_FONT_SIZE_PT,
    TABLE_FONT_SIZE_PT,
    TITLE_FONT_SIZE_PT,
    register_pdf_font,
)
from generators.export_utils import prepare_output_path, validate_export_payload


PAGE_MARGIN_PT = 56


def _load_reportlab():
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfbase.pdfmetrics import registerFont
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError(
            "缺少 reportlab，請先執行 `pip install -r requirements.txt`。"
        ) from exc

    return {
        "A4": A4,
        "TA_CENTER": TA_CENTER,
        "TA_LEFT": TA_LEFT,
        "colors": colors,
        "ParagraphStyle": ParagraphStyle,
        "Paragraph": Paragraph,
        "SimpleDocTemplate": SimpleDocTemplate,
        "Spacer": Spacer,
        "Table": Table,
        "TableStyle": TableStyle,
        "UnicodeCIDFont": UnicodeCIDFont,
        "getSampleStyleSheet": getSampleStyleSheet,
        "registerFont": registerFont,
    }


def _paragraph_markup(text: str) -> str:
    return escape(str(text or "")).replace("\n", "<br/>")


def _build_styles(reportlab, font_name: str) -> dict:
    styles = reportlab["getSampleStyleSheet"]()
    paragraph_style = reportlab["ParagraphStyle"]
    return {
        "title": paragraph_style(
            "DocumentTitle",
            parent=styles["Title"],
            fontName=font_name,
            fontSize=TITLE_FONT_SIZE_PT,
            leading=24,
            alignment=reportlab["TA_CENTER"],
            spaceAfter=16,
        ),
        "section": paragraph_style(
            "DocumentSection",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=SECTION_FONT_SIZE_PT,
            leading=20,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "body": paragraph_style(
            "DocumentBody",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=BODY_FONT_SIZE_PT,
            leading=18,
            alignment=reportlab["TA_LEFT"],
            wordWrap="CJK",
            spaceAfter=4,
        ),
        "table_header": paragraph_style(
            "TableHeader",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=TABLE_FONT_SIZE_PT,
            leading=15,
            alignment=reportlab["TA_CENTER"],
            wordWrap="CJK",
        ),
        "table_body": paragraph_style(
            "TableBody",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=TABLE_FONT_SIZE_PT,
            leading=15,
            alignment=reportlab["TA_LEFT"],
            wordWrap="CJK",
        ),
        "label": paragraph_style(
            "InfoLabel",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=TABLE_FONT_SIZE_PT,
            leading=15,
            alignment=reportlab["TA_LEFT"],
            wordWrap="CJK",
        ),
        "note": paragraph_style(
            "DocumentNote",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=NOTE_FONT_SIZE_PT,
            leading=14,
            alignment=reportlab["TA_LEFT"],
            wordWrap="CJK",
            textColor=reportlab["colors"].HexColor("#555555"),
            spaceAfter=4,
        ),
    }


def _paragraph(reportlab, style, text: str):
    return reportlab["Paragraph"](_paragraph_markup(text), style)


def _build_info_table(reportlab, styles: dict, section: dict, available_width: float):
    rows = section.get("rows", [])
    column_count = max((len(row) for row in rows), default=2)
    col_width = available_width / max(column_count, 1)
    table_data = []
    for row in rows:
        rendered_row = []
        for index, value in enumerate(row):
            cell_style = styles["label"] if index % 2 == 0 else styles["table_body"]
            rendered_row.append(_paragraph(reportlab, cell_style, value))
        table_data.append(rendered_row)

    table = reportlab["Table"](
        table_data,
        colWidths=[col_width] * column_count,
        repeatRows=0,
        hAlign="LEFT",
    )
    table.setStyle(
        reportlab["TableStyle"](
            [
                ("GRID", (0, 0), (-1, -1), 0.6, reportlab["colors"].HexColor("#555555")),
                ("BACKGROUND", (0, 0), (-1, -1), reportlab["colors"].white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
            + [
                ("BACKGROUND", (index, 0), (index, -1), reportlab["colors"].HexColor("#EFEFEF"))
                for index in range(0, column_count, 2)
            ]
        )
    )
    return table


def _build_data_table(reportlab, styles: dict, section: dict, available_width: float):
    headers = section.get("headers", [])
    rows = section.get("rows", [])
    column_count = max(len(headers), max((len(row) for row in rows), default=1))
    col_width = available_width / max(column_count, 1)

    table_data = []
    if headers:
        table_data.append(
            [_paragraph(reportlab, styles["table_header"], header) for header in headers]
        )
    for row in rows:
        table_data.append(
            [_paragraph(reportlab, styles["table_body"], value) for value in row]
        )

    table = reportlab["Table"](
        table_data,
        colWidths=[col_width] * column_count,
        repeatRows=1 if headers else 0,
        hAlign="LEFT",
    )
    table.setStyle(
        reportlab["TableStyle"](
            [
                ("GRID", (0, 0), (-1, -1), 0.6, reportlab["colors"].HexColor("#555555")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    if headers:
        table.setStyle(
            reportlab["TableStyle"](
                [
                    ("BACKGROUND", (0, 0), (-1, 0), reportlab["colors"].HexColor("#D9D9D9")),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ]
            )
        )
    return table


def _render_story(reportlab, spec: dict, available_width: float) -> list:
    styles = _CURRENT_STYLES
    story = [_paragraph(reportlab, styles["title"], spec["title"])]
    spacer = reportlab["Spacer"]

    for section in spec["sections"]:
        heading = section.get("heading")
        if heading:
            story.append(_paragraph(reportlab, styles["section"], heading))

        kind = section["kind"]
        if kind == "info_table":
            story.append(_build_info_table(reportlab, styles, section, available_width))
            story.append(spacer(1, 8))
        elif kind == "table":
            story.append(_build_data_table(reportlab, styles, section, available_width))
            story.append(spacer(1, 8))
        elif kind == "paragraph":
            for paragraph_text in section.get("paragraphs", []):
                story.append(_paragraph(reportlab, styles["body"], paragraph_text))
            story.append(spacer(1, 4))
        elif kind == "lines":
            for line in section.get("lines", []):
                story.append(_paragraph(reportlab, styles["body"], line))
            story.append(spacer(1, 4))
        elif kind == "bullet_list":
            for item in section.get("items", []):
                story.append(_paragraph(reportlab, styles["body"], f"• {item}"))
            story.append(spacer(1, 4))
        elif kind == "note":
            story.append(_paragraph(reportlab, styles["note"], section.get("text", "")))
            story.append(spacer(1, 4))

    return story


_CURRENT_STYLES: dict = {}


def generate_document_pdf(
    document: dict,
    version: dict,
    output_dir: Path | str | None = None,
) -> Path:
    validated_document, validated_version = validate_export_payload(document, version)
    output_path = prepare_output_path(validated_document, validated_version, "pdf", output_dir)

    reportlab = _load_reportlab()
    font_name = register_pdf_font(reportlab)
    global _CURRENT_STYLES
    _CURRENT_STYLES = _build_styles(reportlab, font_name)

    spec = build_document_render_spec(
        validated_document["document_type"],
        validated_version["content_json"],
        title_override=derive_document_title(
            validated_document["document_type"],
            validated_version["content_json"],
            fallback=validated_document.get("title"),
        ),
    )

    pdf = reportlab["SimpleDocTemplate"](
        str(output_path),
        pagesize=reportlab["A4"],
        leftMargin=PAGE_MARGIN_PT,
        rightMargin=PAGE_MARGIN_PT,
        topMargin=PAGE_MARGIN_PT,
        bottomMargin=PAGE_MARGIN_PT,
    )
    story = _render_story(reportlab, spec, pdf.width)
    pdf.build(story)
    return output_path


def generate_meeting_minutes_pdf(
    document: dict,
    version: dict,
    output_dir: Path | str | None = None,
) -> Path:
    return generate_document_pdf(document=document, version=version, output_dir=output_dir)
