from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from core.constants import EVALUATION_CATEGORIES
import core.database as database_module
from core.database import get_default_db_path, initialize_database, resolve_db_path
from core.document_service import list_documents
from core.evaluation_service import get_evaluation_summary


class DatabaseInitializationTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_default_db_path = database_module.DEFAULT_DB_PATH

    def tearDown(self):
        database_module.DEFAULT_DB_PATH = self.original_default_db_path
        self.temp_dir.cleanup()

    def test_initialize_database_creates_schema_and_seed_data(self):
        db_path = Path(self.temp_dir.name) / "odflow.sqlite3"

        initialize_database(db_path)

        self.assertTrue(db_path.exists())

        with closing(sqlite3.connect(db_path)) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            expected_tables = {
                "clubs",
                "documents",
                "document_versions",
                "projects",
                "templates",
                "evaluation_items",
            }
            self.assertTrue(expected_tables.issubset(tables))

            item_count = connection.execute(
                "SELECT COUNT(*) FROM evaluation_items"
            ).fetchone()[0]
            self.assertEqual(item_count, len(EVALUATION_CATEGORIES))

    def test_initialize_database_none_uses_default_path_without_crash(self):
        database_module.DEFAULT_DB_PATH = Path(self.temp_dir.name) / "data" / "odflow.sqlite3"

        resolved_path = initialize_database(None)

        self.assertEqual(resolved_path, database_module.DEFAULT_DB_PATH)
        self.assertTrue(resolved_path.exists())

    def test_resolve_db_path_creates_parent_directory_when_missing(self):
        database_module.DEFAULT_DB_PATH = Path(self.temp_dir.name) / "nested" / "data" / "odflow.sqlite3"

        resolved_path = resolve_db_path(None)

        self.assertEqual(resolved_path, database_module.DEFAULT_DB_PATH)
        self.assertTrue(resolved_path.parent.exists())

    def test_list_documents_with_none_db_path_does_not_crash(self):
        database_module.DEFAULT_DB_PATH = Path(self.temp_dir.name) / "data" / "odflow.sqlite3"

        documents = list_documents(db_path=None)

        self.assertEqual(documents, [])
        self.assertTrue(database_module.DEFAULT_DB_PATH.exists())

    def test_get_evaluation_summary_with_none_db_path_does_not_crash(self):
        database_module.DEFAULT_DB_PATH = Path(self.temp_dir.name) / "data" / "odflow.sqlite3"

        summary = get_evaluation_summary(db_path=None)

        self.assertEqual(summary["overall_completion_percentage"], 0.0)
        self.assertEqual(summary["total_completed_documents"], 0)
        self.assertEqual(summary["draft_or_pending_documents"], 0)

    def test_get_default_db_path_returns_resolved_path(self):
        database_module.DEFAULT_DB_PATH = Path(self.temp_dir.name) / "data" / "odflow.sqlite3"

        resolved_path = get_default_db_path()

        self.assertEqual(resolved_path, database_module.DEFAULT_DB_PATH)
        self.assertTrue(resolved_path.parent.exists())


if __name__ == "__main__":
    unittest.main()
