from __future__ import annotations

from pathlib import Path

from generators.export_utils import prepare_output_path, validate_export_payload


def generate_meeting_minutes_pdf(
    document: dict,
    version: dict,
    output_dir: Path | str | None = None,
) -> Path:
    validated_document, validated_version = validate_export_payload(document, version)
    output_path = prepare_output_path(validated_document, validated_version, "pdf", output_dir)

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

    registerFont(UnicodeCIDFont("STSong-Light"))

    styles = getSampleStyleSheet()
    base_style = ParagraphStyle(
        "MeetingBody",
        parent=styles["BodyText"],
        fontName="STSong-Light",
        fontSize=11,
        leading=17,
        alignment=TA_LEFT,
    )
    title_style = ParagraphStyle(
        "MeetingTitle",
        parent=styles["Title"],
        fontName="STSong-Light",
        fontSize=18,
        leading=24,
    )
    heading_style = ParagraphStyle(
        "MeetingHeading",
        parent=styles["Heading2"],
        fontName="STSong-Light",
        fontSize=13,
        leading=20,
    )

    content_json = validated_version["content_json"]
    story = [
        Paragraph("會議紀錄", title_style),
        Spacer(1, 12),
        Paragraph(f"會議名稱：{content_json['meeting_title']}", base_style),
        Paragraph(f"會議日期：{content_json['meeting_date']}", base_style),
        Paragraph(f"會議時間：{content_json['meeting_time']}", base_style),
        Paragraph(f"會議地點：{content_json['location']}", base_style),
        Paragraph(f"主席：{content_json['chair']}", base_style),
        Paragraph(f"紀錄：{content_json['recorder']}", base_style),
        Paragraph(f"出席人員：{'、'.join(content_json['attendees'])}", base_style),
        Paragraph(f"請假人員：{'、'.join(content_json['absentees'])}", base_style),
        Spacer(1, 10),
        Paragraph("討論事項與決議", heading_style),
    ]

    for index, item in enumerate(content_json["agenda_items"], start=1):
        story.extend(
            [
                Paragraph(f"{index}. 議題：{item['title']}", base_style),
                Paragraph(f"討論：{item['discussion']}", base_style),
                Paragraph(f"決議：{item['decision']}", base_style),
                Spacer(1, 6),
            ]
        )

    story.append(Paragraph("待辦事項", heading_style))
    for index, item in enumerate(content_json["action_items"], start=1):
        story.append(
            Paragraph(
                f"{index}. 待辦：{item['task']} / 負責人：{item['owner']} / "
                f"期限：{item['deadline']} / 備註：{item['note']}",
                base_style,
            )
        )

    story.extend(
        [
            Spacer(1, 10),
            Paragraph(f"下次會議時間：{content_json['next_meeting_time']}", base_style),
            Paragraph(f"備註：{content_json['notes']}", base_style),
        ]
    )

    pdf = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=48,
        rightMargin=48,
        topMargin=48,
        bottomMargin=48,
    )
    pdf.build(story)
    return output_path
