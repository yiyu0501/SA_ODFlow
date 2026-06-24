from __future__ import annotations

from core.constants import (
    DOCUMENT_STATUSES,
    EVALUATION_CATEGORIES,
    EVALUATION_ITEMS,
    EVALUATION_RECOMMENDATIONS,
    EVALUATION_REQUIRED_DOCUMENTS,
)
from core.document_service import list_documents


COMPLETED_STATUSES = {"正式版", "已歸檔"}
IN_PROGRESS_STATUSES = {"草稿", "待審"}


def list_evaluation_items():
    return EVALUATION_ITEMS.copy()


def _get_weight(category_name: str) -> int:
    for item in EVALUATION_ITEMS:
        if item["category_name"] == category_name:
            return item["weight"]
    raise ValueError(f"找不到評鑑分類權重: {category_name}")


def _normalize_text(value: str | None) -> str:
    return str(value or "").strip().lower()


def _document_requirement_match(document: dict, requirement: dict) -> bool:
    search_area = " ".join(
        [
            _normalize_text(document.get("title")),
            _normalize_text(document.get("document_type")),
            _normalize_text(document.get("evaluation_category")),
        ]
    )
    return any(_normalize_text(term) in search_area for term in requirement["match_terms"])


def _completion_status_from_documents(matched_documents: list[dict]) -> str:
    statuses = {document["status"] for document in matched_documents}
    if statuses & COMPLETED_STATUSES:
        return "已完成"
    if statuses & IN_PROGRESS_STATUSES:
        return "進行中"
    return "缺漏"


def _filter_documents_by_category(documents: list[dict], category_name: str) -> list[dict]:
    return [
        document
        for document in documents
        if document.get("evaluation_category") == category_name
        and document.get("status") in DOCUMENT_STATUSES
    ]


def _build_requirement_statuses(category_name: str, documents: list[dict]) -> list[dict]:
    category_documents = _filter_documents_by_category(documents, category_name)
    requirement_statuses = []

    for requirement in EVALUATION_REQUIRED_DOCUMENTS[category_name]:
        matched_documents = [
            document
            for document in category_documents
            if _document_requirement_match(document, requirement)
        ]
        requirement_statuses.append(
            {
                "requirement_name": requirement["name"],
                "status": _completion_status_from_documents(matched_documents),
                "matched_documents": matched_documents,
            }
        )

    return requirement_statuses


def get_category_completion(
    category_name: str,
    documents: list[dict] | None = None,
    db_path=None,
) -> dict:
    if category_name not in EVALUATION_CATEGORIES:
        raise ValueError(f"不支援的評鑑分類: {category_name}")

    documents = documents if documents is not None else list_documents(db_path=db_path)
    requirement_statuses = _build_requirement_statuses(category_name, documents)

    required_count = len(requirement_statuses)
    completed_count = sum(1 for item in requirement_statuses if item["status"] == "已完成")
    in_progress_count = sum(1 for item in requirement_statuses if item["status"] == "進行中")
    missing_count = sum(1 for item in requirement_statuses if item["status"] == "缺漏")
    category_documents = _filter_documents_by_category(documents, category_name)
    draft_or_pending_count = sum(
        1 for document in category_documents if document["status"] in IN_PROGRESS_STATUSES
    )
    completion_rate = (completed_count / required_count) if required_count else 0.0

    return {
        "category_name": category_name,
        "weight": _get_weight(category_name),
        "required_count": required_count,
        "completed_count": completed_count,
        "in_progress_count": in_progress_count,
        "missing_count": missing_count,
        "draft_or_pending_count": draft_or_pending_count,
        "completion_rate": completion_rate,
        "completion_percentage": round(completion_rate * 100, 1),
        "weighted_completion_score": round(completion_rate * _get_weight(category_name), 2),
        "required_documents": requirement_statuses,
        "documents": category_documents,
    }


def get_missing_requirements(
    documents: list[dict] | None = None,
    db_path=None,
) -> list[dict]:
    documents = documents if documents is not None else list_documents(db_path=db_path)
    missing = []

    for category_name in EVALUATION_CATEGORIES:
        category_summary = get_category_completion(
            category_name,
            documents=documents,
        )
        for requirement in category_summary["required_documents"]:
            if requirement["status"] == "缺漏":
                missing.append(
                    {
                        "category_name": category_name,
                        "requirement_name": requirement["requirement_name"],
                    }
                )

    return missing


def get_recent_documents(
    limit: int = 5,
    documents: list[dict] | None = None,
    db_path=None,
) -> list[dict]:
    documents = documents if documents is not None else list_documents(db_path=db_path)
    recent_documents = []

    for document in documents[:limit]:
        recent_documents.append(
            {
                **document,
                "evaluation_progress_status": (
                    "已計入"
                    if document["status"] in COMPLETED_STATUSES
                    else "進行中"
                    if document["status"] in IN_PROGRESS_STATUSES
                    else "未計入"
                ),
            }
        )

    return recent_documents


def get_recommendations(
    missing_requirements: list[dict] | None = None,
    documents: list[dict] | None = None,
    db_path=None,
) -> list[dict]:
    if missing_requirements is None:
        missing_requirements = get_missing_requirements(documents=documents, db_path=db_path)

    missing_categories = []
    for item in missing_requirements:
        category_name = item["category_name"]
        if category_name not in missing_categories:
            missing_categories.append(category_name)

    recommendations = []
    for category_name in missing_categories:
        message = EVALUATION_RECOMMENDATIONS.get(category_name)
        if message:
            recommendations.append(
                {
                    "category_name": category_name,
                    "message": message,
                }
            )

    return recommendations


def get_evaluation_summary(db_path=None) -> dict:
    documents = list_documents(db_path=db_path)
    category_summaries = [
        get_category_completion(category_name, documents=documents)
        for category_name in EVALUATION_CATEGORIES
    ]
    total_required_documents = sum(item["required_count"] for item in category_summaries)
    total_completed_documents = sum(item["completed_count"] for item in category_summaries)
    draft_or_pending_documents = sum(
        1 for document in documents if document["status"] in IN_PROGRESS_STATUSES
    )
    overall_completion_rate = (
        sum(item["weighted_completion_score"] for item in category_summaries) / 100
    )
    missing_requirements = get_missing_requirements(documents=documents)
    recommendations = get_recommendations(missing_requirements=missing_requirements)

    return {
        "overall_completion_rate": overall_completion_rate,
        "overall_completion_percentage": round(overall_completion_rate * 100, 1),
        "category_summaries": category_summaries,
        "total_required_documents": total_required_documents,
        "total_completed_documents": total_completed_documents,
        "draft_or_pending_documents": draft_or_pending_documents,
        "recent_documents": get_recent_documents(documents=documents),
        "missing_requirements": missing_requirements,
        "recommendations": recommendations,
    }


def calculate_completion():
    return get_evaluation_summary()
