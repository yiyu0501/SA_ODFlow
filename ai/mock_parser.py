from __future__ import annotations

import re

from core.meeting_minutes import normalize_meeting_minutes_content


def _extract_line_value(text: str, labels: list[str]) -> str:
    for label in labels:
        pattern = rf"{re.escape(label)}\s*[:：]?\s*([^\n]+)"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


def _extract_lines_by_keyword(text: str, keywords: list[str]) -> list[str]:
    matched_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip(" -\t")
        if line and any(keyword in line for keyword in keywords):
            matched_lines.append(line)
    return matched_lines


def _extract_date_from_text(text: str) -> str:
    patterns = [
        r"(\d{4}-\d{1,2}-\d{1,2})",
        r"(\d{4}/\d{1,2}/\d{1,2})",
        r"(\d{1,2}月\d{1,2}日)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""


def _build_fallback_title(meeting_type: str, meeting_date: str) -> str:
    if meeting_date and meeting_type:
        return f"{meeting_date}{meeting_type}會議紀錄"
    if meeting_type:
        return f"{meeting_type}會議紀錄"
    return "會議紀錄草稿"


def parse_meeting_minutes(
    transcript_text: str,
    meeting_date: str = "",
    meeting_name: str = "",
    meeting_type: str = "",
    instruction: str = "",
) -> dict:
    merged_text = "\n".join(filter(None, [instruction, transcript_text]))
    discussion_lines = _extract_lines_by_keyword(
        transcript_text,
        ["討論", "議題", "提案", "報告事項"],
    )
    decision_lines = _extract_lines_by_keyword(transcript_text, ["決議", "結論"])
    action_lines = _extract_lines_by_keyword(transcript_text, ["待辦", "追蹤", "TODO", "todo"])

    agenda_items = []
    max_items = max(len(discussion_lines), len(decision_lines), 1)

    for index in range(max_items):
        discussion = discussion_lines[index] if index < len(discussion_lines) else ""
        decision = decision_lines[index] if index < len(decision_lines) else ""
        title = discussion.split("：", 1)[0] if "：" in discussion else f"議題 {index + 1}"
        agenda_items.append(
            {
                "title": title.strip(),
                "discussion": discussion,
                "decision": decision,
            }
        )

    action_items = []
    for line in action_lines:
        action_items.append(
            {
                "task": re.split(r"[:：]", line, maxsplit=1)[-1].strip(),
                "owner": "",
                "deadline": "",
                "note": "",
            }
        )

    attendees = _extract_line_value(transcript_text, ["出席人員", "出席"])
    absentees = _extract_line_value(transcript_text, ["請假人員", "請假", "缺席"])

    draft = {
        "meeting_title": meeting_name.strip() or _build_fallback_title(
            meeting_type.strip(),
            meeting_date.strip() or _extract_date_from_text(merged_text),
        ),
        "meeting_date": meeting_date.strip() or _extract_date_from_text(merged_text),
        "meeting_time": _extract_line_value(transcript_text, ["會議時間", "時間"]),
        "location": _extract_line_value(transcript_text, ["會議地點", "地點"]),
        "chair": _extract_line_value(transcript_text, ["主席", "主持人"]),
        "recorder": _extract_line_value(transcript_text, ["紀錄", "記錄"]),
        "attendees": attendees,
        "absentees": absentees,
        "agenda_items": agenda_items,
        "action_items": action_items,
        "next_meeting_time": _extract_line_value(transcript_text, ["下次會議時間", "下次會議"]),
        "notes": instruction.strip() or "依輸入內容產生的 mock 會議紀錄草稿。",
    }
    return normalize_meeting_minutes_content(draft)


def parse_text_input(text: str) -> dict:
    return parse_meeting_minutes(transcript_text=text)
