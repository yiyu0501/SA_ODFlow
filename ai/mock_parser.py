from __future__ import annotations


def parse_text_input(text: str) -> dict:
    return {
        "source_text": text,
        "document_type": "",
        "meeting_date": "",
        "meeting_name": "",
        "attendees": [],
        "chair": "",
        "recorder": "",
        "agenda_items": [],
        "decisions": [],
        "action_items": [],
        "project_name": "",
        "evaluation_category": "",
        "note": "Task 1 skeleton only. Mock parser behavior will be expanded in Task 2.",
    }
