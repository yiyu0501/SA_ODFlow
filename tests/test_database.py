from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from core.constants import EVALUATION_CATEGORIES
from core.database import initialize_database


class DatabaseInitializationTestCase(unittest.TestCase):
    def test_initialize_database_creates_schema_and_seed_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "odflow.sqlite3"

            initialize_database(db_path)

            self.assertTrue(db_path.exists())

            with sqlite3.connect(db_path) as connection:
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


if __name__ == "__main__":
    unittest.main()
