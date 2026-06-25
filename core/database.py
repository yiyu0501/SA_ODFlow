from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from core.constants import EVALUATION_ITEMS


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "odflow.sqlite3"

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_name TEXT,
        campus TEXT,
        academic_year TEXT,
        club_type TEXT,
        president_name TEXT,
        advisor_name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        document_type TEXT NOT NULL,
        evaluation_category TEXT NOT NULL,
        project_id INTEGER,
        status TEXT NOT NULL DEFAULT '草稿',
        current_version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS document_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        version_number INTEGER NOT NULL,
        content_json TEXT NOT NULL DEFAULT '{}',
        odf_path TEXT,
        pdf_path TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        note TEXT,
        FOREIGN KEY (document_id) REFERENCES documents (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        project_type TEXT,
        start_date TEXT,
        end_date TEXT,
        owner TEXT,
        status TEXT NOT NULL DEFAULT 'draft',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_name TEXT NOT NULL,
        template_type TEXT NOT NULL,
        file_format TEXT NOT NULL,
        template_path TEXT NOT NULL,
        evaluation_category TEXT,
        description TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS evaluation_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_code TEXT NOT NULL UNIQUE,
        category_name TEXT NOT NULL,
        weight INTEGER NOT NULL,
        required_documents_json TEXT NOT NULL DEFAULT '[]'
    )
    """,
]


def resolve_db_path(db_path: Path | str | None = None) -> Path:
    if db_path is None:
        resolved_path = DEFAULT_DB_PATH
    elif isinstance(db_path, Path):
        resolved_path = db_path
    else:
        resolved_path = Path(db_path)

    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def get_default_db_path() -> Path:
    return resolve_db_path()


def get_connection(db_path: Path | str | None = DEFAULT_DB_PATH) -> sqlite3.Connection:
    resolved_db_path = resolve_db_path(db_path)
    connection = sqlite3.connect(resolved_db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Path | str | None = DEFAULT_DB_PATH) -> Path:
    resolved_db_path = resolve_db_path(db_path)

    with closing(get_connection(resolved_db_path)) as connection:
        cursor = connection.cursor()

        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)

        for item in EVALUATION_ITEMS:
            cursor.execute(
                """
                INSERT INTO evaluation_items (
                    category_code,
                    category_name,
                    weight,
                    required_documents_json
                )
                VALUES (?, ?, ?, '[]')
                ON CONFLICT(category_code) DO UPDATE SET
                    category_name = excluded.category_name,
                    weight = excluded.weight
                """,
                (
                    item["category_code"],
                    item["category_name"],
                    item["weight"],
                ),
            )

        connection.commit()

    return resolved_db_path
