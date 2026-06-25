from __future__ import annotations

from pathlib import Path

from core.document_schemas import build_document_preview_blocks, derive_document_title
from generators.export_utils import prepare_output_path, validate_export_payload


def _load_reportlab():
    try:
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfbase.pdfmetrics import registerFont
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:
        raise RuntimeError(
            "缺少 reportlab，請先執行 `pip install -r requirements.txt`。"
        ) from exc

    return {
        "TA_LEFT": TA_LEFT,
        "A4": A4,
        "ParagraphStyle": ParagraphStyle,
        "getSampleStyleSheet": getSampleStyleSheet,
        "UnicodeCIDFont": UnicodeCIDFont,
        "registerFont": registerFont,
        "Paragraph": Paragraph,
        "SimpleDocTemplate": SimpleDocTemplate,
        "Spacer": Spacer,
    }


def generate_document_pdf(
    document: dict,
    version: dict,
    output_dir: Path | str | None = None,
) -> Path:
    validated_document, validated_version = validate_export_payload(document, version)
    output_path = prepare_output_path(validated_document, validated_version, "pdf", output_dir)

    reportlab = _load_reportlab()
    reportlab["registerFont"](reportlab["UnicodeCIDFont"]("STSong-Light"))

    styles = reportlab["getSampleStyleSheet"]()
    base_style = reportlab["ParagraphStyle"](
        "DocumentBody",
        parent=styles["BodyText"],
        fontName="STSong-Light",
        fontSize=11,
        leading=17,
        alignment=reportlab["TA_LEFT"],
    )
    title_style = reportlab["ParagraphStyle"](
        "DocumentTitle",
        parent=styles["Title"],
        fontName="STSong-Light",
        fontSize=18,
        leading=24,
    )
    heading_style = reportlab["ParagraphStyle"](
        "DocumentHeading",
        parent=styles["Heading2"],
        fontName="STSong-Light",
        fontSize=13,
        leading=20,
    )

    blocks = build_document_preview_blocks(
        validated_document["document_type"],
        validated_version["content_json"],
        title_override=derive_document_title(
            validated_document["document_type"],
            validated_version["content_json"],
            fallback=validated_document.get("title"),
        ),
    )

    story = []
    for block in blocks:
        kind = block["kind"]
        if kind == "title":
            story.extend(
                [
                    reportlab["Paragraph"](block["text"], title_style),
                    reportlab["Spacer"](1, 12),
                ]
            )
        elif kind == "heading":
            story.extend(
                [
                    reportlab["Paragraph"](block["text"], heading_style),
                    reportlab["Spacer"](1, 6),
                ]
            )
        elif kind == "paragraph":
            story.append(reportlab["Paragraph"](block["text"], base_style))
        elif kind == "bullet_list":
            for item in block["items"]:
                story.append(reportlab["Paragraph"](f"• {item}", base_style))
            story.append(reportlab["Spacer"](1, 6))

    pdf = reportlab["SimpleDocTemplate"](
        str(output_path),
        pagesize=reportlab["A4"],
        leftMargin=48,
        rightMargin=48,
        topMargin=48,
        bottomMargin=48,
    )
    pdf.build(story)
    return output_path


def generate_meeting_minutes_pdf(
    document: dict,
    version: dict,
    output_dir: Path | str | None = None,
) -> Path:
    return generate_document_pdf(document=document, version=version, output_dir=output_dir)
