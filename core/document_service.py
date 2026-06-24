from __future__ import annotations

import json
from contextlib import closing
from pathlib import Path

from core.constants import DOCUMENT_STATUSES, EVALUATION_CATEGORIES
from core.database import DEFAULT_DB_PATH, get_connection, initialize_database
from core.meeting_minutes import normalize_meeting_minutes_content


def validate_document_status(status: str) -> str:
    normalized_status = str(status).strip()
    if normalized_status not in DOCUMENT_STATUSES:
        raise ValueError(f"不支援的文件狀態: {status}")
    return normalized_status


def validate_evaluation_category(category: str) -> str:
    normalized_category = str(category).strip()
    if normalized_category not in EVALUATION_CATEGORIES:
        raise ValueError(f"不支援的評鑑分類: {category}")
    return normalized_category


def _row_to_dict(row):
    return dict(row) if row is not None else None


def _load_content_json(content_json: str) -> dict:
    return normalize_meeting_minutes_content(json.loads(content_json))


def _serialize_content_json(content_json: dict) -> str:
    normalized = normalize_meeting_minutes_content(content_json)
    return json.dumps(normalized, ensure_ascii=False)


def _version_label(version_number: int) -> str:
    return f"v{version_number}" if version_number > 0 else "-"


def _normalize_version_row(version_row: dict | None) -> dict | None:
    if version_row is None:
        return None

    version = _row_to_dict(version_row)
    version["content_json"] = _load_content_json(version["content_json"])
    version["version_label"] = _version_label(version["version_number"])
    return version


def create_document(
    title: str,
    document_type: str,
    evaluation_category: str,
    project_id: int | None = None,
    status: str = "草稿",
    current_version: int = 0,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    initialize_database(db_path)
    validated_status = validate_document_status(status)
    validated_category = validate_evaluation_category(evaluation_category)

    with closing(get_connection(db_path)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO documents (
                title,
                document_type,
                evaluation_category,
                project_id,
                status,
                current_version
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                document_type.strip(),
                validated_category,
                project_id,
                validated_status,
                current_version,
            ),
        )
        document_id = cursor.lastrowid
        connection.commit()

    return get_document(document_id, db_path=db_path)


def create_document_version(
    document_id: int,
    content_json: dict,
    note: str = "",
    odf_path: str | None = None,
    pdf_path: str | None = None,
    set_as_current: bool = True,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    initialize_database(db_path)

    with closing(get_connection(db_path)) as connection:
        cursor = connection.cursor()
        document_row = cursor.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if document_row is None:
            raise ValueError(f"找不到文件: {document_id}")

        next_version = cursor.execute(
            """
            SELECT COALESCE(MAX(version_number), 0) + 1
            FROM document_versions
            WHERE document_id = ?
            """,
            (document_id,),
        ).fetchone()[0]

        cursor.execute(
            """
            INSERT INTO document_versions (
                document_id,
                version_number,
                content_json,
                odf_path,
                pdf_path,
                note
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                next_version,
                _serialize_content_json(content_json),
                odf_path,
                pdf_path,
                note.strip() or None,
            ),
        )

        if set_as_current:
            cursor.execute(
                """
                UPDATE documents
                SET current_version = ?,
                    title = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    next_version,
                    normalize_meeting_minutes_content(content_json)["meeting_title"] or document_row["title"],
                    document_id,
                ),
            )

        connection.commit()

        version_row = cursor.execute(
            """
            SELECT *
            FROM document_versions
            WHERE document_id = ? AND version_number = ?
            """,
            (document_id, next_version),
        ).fetchone()

    return _normalize_version_row(version_row)


def list_documents(db_path: Path | str = DEFAULT_DB_PATH) -> list[dict]:
    initialize_database(db_path)

    with closing(get_connection(db_path)) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM documents
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()

    documents = []
    for row in rows:
        document = _row_to_dict(row)
        document["current_version_label"] = _version_label(document["current_version"])
        documents.append(document)

    return documents


def get_document(document_id: int, db_path: Path | str = DEFAULT_DB_PATH) -> dict | None:
    initialize_database(db_path)

    with closing(get_connection(db_path)) as connection:
        row = connection.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()

        if row is None:
            return None

        document = _row_to_dict(row)
        current_version_row = connection.execute(
            """
            SELECT *
            FROM document_versions
            WHERE document_id = ? AND version_number = ?
            """,
            (document_id, document["current_version"]),
        ).fetchone()

    document["current_version_label"] = _version_label(document["current_version"])
    document["current_version_content_json"] = (
        _load_content_json(current_version_row["content_json"])
        if current_version_row is not None
        else None
    )
    return document


def get_current_version(
    document_id: int,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict | None:
    initialize_database(db_path)

    with closing(get_connection(db_path)) as connection:
        document_row = connection.execute(
            "SELECT current_version FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if document_row is None:
            raise ValueError(f"找不到文件: {document_id}")

        version_number = document_row["current_version"]
        if version_number <= 0:
            return None

        version_row = connection.execute(
            """
            SELECT *
            FROM document_versions
            WHERE document_id = ? AND version_number = ?
            """,
            (document_id, version_number),
        ).fetchone()

    if version_row is None:
        raise ValueError(f"文件 {document_id} 的目前版本不存在")

    return _normalize_version_row(version_row)


def get_document_with_current_version(
    document_id: int,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    document = get_document(document_id, db_path=db_path)
    if document is None:
        raise ValueError(f"找不到文件: {document_id}")

    document["current_version_data"] = get_current_version(document_id, db_path=db_path)
    return document


def get_document_versions(
    document_id: int,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict]:
    initialize_database(db_path)

    with closing(get_connection(db_path)) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM document_versions
            WHERE document_id = ?
            ORDER BY version_number DESC
            """,
            (document_id,),
        ).fetchall()

    versions = []
    for row in rows:
        versions.append(_normalize_version_row(row))

    return versions


def update_version_file_paths(
    document_id: int,
    version_number: int,
    odf_path: str | None = None,
    pdf_path: str | None = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    initialize_database(db_path)

    if odf_path is None and pdf_path is None:
        raise ValueError("至少要更新 odf_path 或 pdf_path 其中一項")

    with closing(get_connection(db_path)) as connection:
        cursor = connection.cursor()
        existing_row = cursor.execute(
            """
            SELECT *
            FROM document_versions
            WHERE document_id = ? AND version_number = ?
            """,
            (document_id, version_number),
        ).fetchone()
        if existing_row is None:
            raise ValueError(f"找不到文件 {document_id} 的版本 v{version_number}")

        next_odf_path = odf_path if odf_path is not None else existing_row["odf_path"]
        next_pdf_path = pdf_path if pdf_path is not None else existing_row["pdf_path"]

        cursor.execute(
            """
            UPDATE document_versions
            SET odf_path = ?,
                pdf_path = ?
            WHERE document_id = ? AND version_number = ?
            """,
            (next_odf_path, next_pdf_path, document_id, version_number),
        )
        connection.commit()

        updated_row = cursor.execute(
            """
            SELECT *
            FROM document_versions
            WHERE document_id = ? AND version_number = ?
            """,
            (document_id, version_number),
        ).fetchone()

    return _normalize_version_row(updated_row)


def update_document_status(
    document_id: int,
    status: str,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    initialize_database(db_path)
    validated_status = validate_document_status(status)

    with closing(get_connection(db_path)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE documents
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (validated_status, document_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"找不到文件: {document_id}")
        connection.commit()

    return get_document(document_id, db_path=db_path)


def set_current_version(
    document_id: int,
    version_number: int,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict:
    initialize_database(db_path)

    with closing(get_connection(db_path)) as connection:
        cursor = connection.cursor()
        version_row = cursor.execute(
            """
            SELECT *
            FROM document_versions
            WHERE document_id = ? AND version_number = ?
            """,
            (document_id, version_number),
        ).fetchone()
        if version_row is None:
            raise ValueError(
                f"找不到文件 {document_id} 的版本 v{version_number}"
            )

        content_json = _load_content_json(version_row["content_json"])
        cursor.execute(
            """
            UPDATE documents
            SET current_version = ?,
                title = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                version_number,
                content_json["meeting_title"],
                document_id,
            ),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"找不到文件: {document_id}")
        connection.commit()

    return get_document(document_id, db_path=db_path)
