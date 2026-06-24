from __future__ import annotations

from copy import deepcopy


EMPTY_MEETING_MINUTES_CONTENT = {
    "meeting_title": "",
    "meeting_date": "",
    "meeting_time": "",
    "location": "",
    "chair": "",
    "recorder": "",
    "attendees": [],
    "absentees": [],
    "agenda_items": [
        {
            "title": "",
            "discussion": "",
            "decision": "",
        }
    ],
    "action_items": [
        {
            "task": "",
            "owner": "",
            "deadline": "",
            "note": "",
        }
    ],
    "next_meeting_time": "",
    "notes": "",
}


def empty_meeting_minutes_content() -> dict:
    return deepcopy(EMPTY_MEETING_MINUTES_CONTENT)


def split_people_text(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        items = [str(item).strip() for item in value]
        return [item for item in items if item]

    normalized = value.replace("、", "\n").replace("，", "\n").replace(",", "\n")
    items = [item.strip(" -\t") for item in normalized.splitlines()]
    return [item for item in items if item]


def people_list_to_text(value: str | list[str] | None) -> str:
    return "\n".join(split_people_text(value))


def normalize_agenda_items(items: list[dict] | None) -> list[dict]:
    normalized_items = []

    for item in items or []:
        normalized_item = {
            "title": str(item.get("title", "")).strip(),
            "discussion": str(item.get("discussion", "")).strip(),
            "decision": str(item.get("decision", "")).strip(),
        }

        if any(normalized_item.values()):
            normalized_items.append(normalized_item)

    return normalized_items or [deepcopy(EMPTY_MEETING_MINUTES_CONTENT["agenda_items"][0])]


def normalize_action_items(items: list[dict] | None) -> list[dict]:
    normalized_items = []

    for item in items or []:
        normalized_item = {
            "task": str(item.get("task", "")).strip(),
            "owner": str(item.get("owner", "")).strip(),
            "deadline": str(item.get("deadline", "")).strip(),
            "note": str(item.get("note", "")).strip(),
        }

        if any(normalized_item.values()):
            normalized_items.append(normalized_item)

    return normalized_items or [deepcopy(EMPTY_MEETING_MINUTES_CONTENT["action_items"][0])]


def normalize_meeting_minutes_content(content: dict | None) -> dict:
    normalized = empty_meeting_minutes_content()
    content = content or {}

    for field in (
        "meeting_title",
        "meeting_date",
        "meeting_time",
        "location",
        "chair",
        "recorder",
        "next_meeting_time",
        "notes",
    ):
        normalized[field] = str(content.get(field, "")).strip()

    normalized["attendees"] = split_people_text(content.get("attendees"))
    normalized["absentees"] = split_people_text(content.get("absentees"))
    normalized["agenda_items"] = normalize_agenda_items(content.get("agenda_items"))
    normalized["action_items"] = normalize_action_items(content.get("action_items"))

    return normalized
