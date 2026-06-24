from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClubSettings:
    club_name: str = ""
    campus: str = ""
    academic_year: str = ""
    club_type: str = ""
    president_name: str = ""
    advisor_name: str = ""


@dataclass(slots=True)
class EvaluationItem:
    category_code: str
    category_name: str
    weight: int


@dataclass(slots=True)
class DocumentRecord:
    title: str
    document_type: str
    evaluation_category: str
    status: str = "draft"
    current_version: int = 1


@dataclass(slots=True)
class ProjectRecord:
    project_name: str
    project_type: str = ""
    status: str = "draft"
