from __future__ import annotations

from contextlib import closing
from pathlib import Path

from core.database import DEFAULT_DB_PATH, get_connection, initialize_database


DEFAULT_ACADEMIC_YEAR = "114"
DEFAULT_CAMPUS = "天母校區"
DEFAULT_CLUB_NAME = "ODFlow示範社團"

DEFAULT_CLUB_SETTINGS = {
    "academic_year": DEFAULT_ACADEMIC_YEAR,
    "campus": DEFAULT_CAMPUS,
    "club_name": DEFAULT_CLUB_NAME,
    "club_type": "",
    "president_name": "",
    "advisor_name": "",
}


def get_club_settings(db_path: Path | str = DEFAULT_DB_PATH) -> dict:
    initialize_database(db_path)

    with closing(get_connection(db_path)) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM clubs
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
            """
        ).fetchone()

    if row is None:
        return {
            "id": None,
            **DEFAULT_CLUB_SETTINGS,
        }

    return {
        "id": row["id"],
        "academic_year": str(row["academic_year"] or DEFAULT_ACADEMIC_YEAR).strip()
        or DEFAULT_ACADEMIC_YEAR,
        "campus": str(row["campus"] or DEFAULT_CAMPUS).strip() or DEFAULT_CAMPUS,
        "club_name": str(row["club_name"] or DEFAULT_CLUB_NAME).strip() or DEFAULT_CLUB_NAME,
        "club_type": str(row["club_type"] or "").strip(),
        "president_name": str(row["president_name"] or "").strip(),
        "advisor_name": str(row["advisor_name"] or "").strip(),
    }


def save_club_settings(
    academic_year: str = DEFAULT_ACADEMIC_YEAR,
    campus: str = DEFAULT_CAMPUS,
    club_name: str = DEFAULT_CLUB_NAME,
    club_type: str = "",
    president_name: str = "",
    advisor_name: str = "",
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    initialize_database(db_path)

    payload = {
        "academic_year": str(academic_year or DEFAULT_ACADEMIC_YEAR).strip()
        or DEFAULT_ACADEMIC_YEAR,
        "campus": str(campus or DEFAULT_CAMPUS).strip() or DEFAULT_CAMPUS,
        "club_name": str(club_name or DEFAULT_CLUB_NAME).strip() or DEFAULT_CLUB_NAME,
        "club_type": str(club_type or "").strip(),
        "president_name": str(president_name or "").strip(),
        "advisor_name": str(advisor_name or "").strip(),
    }

    with closing(get_connection(db_path)) as connection:
        cursor = connection.cursor()
        row = cursor.execute(
            """
            SELECT id
            FROM clubs
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            cursor.execute(
                """
                INSERT INTO clubs (
                    club_name,
                    campus,
                    academic_year,
                    club_type,
                    president_name,
                    advisor_name
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["club_name"],
                    payload["campus"],
                    payload["academic_year"],
                    payload["club_type"],
                    payload["president_name"],
                    payload["advisor_name"],
                ),
            )
        else:
            cursor.execute(
                """
                UPDATE clubs
                SET club_name = ?,
                    campus = ?,
                    academic_year = ?,
                    club_type = ?,
                    president_name = ?,
                    advisor_name = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    payload["club_name"],
                    payload["campus"],
                    payload["academic_year"],
                    payload["club_type"],
                    payload["president_name"],
                    payload["advisor_name"],
                    row["id"],
                ),
            )

        connection.commit()

    return get_club_settings(db_path=db_path)


def get_evaluation_export_defaults(db_path: Path | str = DEFAULT_DB_PATH) -> dict:
    settings = get_club_settings(db_path=db_path)
    return {
        "academic_year": settings["academic_year"],
        "campus": settings["campus"],
        "club_name": settings["club_name"],
    }
