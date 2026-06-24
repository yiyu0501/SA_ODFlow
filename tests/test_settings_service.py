from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.settings_service import (
    DEFAULT_ACADEMIC_YEAR,
    DEFAULT_CAMPUS,
    DEFAULT_CLUB_NAME,
    get_club_settings,
    get_evaluation_export_defaults,
    save_club_settings,
)


class SettingsServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "odflow.sqlite3"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_club_settings_returns_defaults_when_empty(self):
        settings = get_club_settings(db_path=self.db_path)

        self.assertEqual(settings["academic_year"], DEFAULT_ACADEMIC_YEAR)
        self.assertEqual(settings["campus"], DEFAULT_CAMPUS)
        self.assertEqual(settings["club_name"], DEFAULT_CLUB_NAME)

    def test_save_club_settings_persists_values(self):
        saved = save_club_settings(
            academic_year="115",
            campus="博愛校區",
            club_name="測試社團",
            club_type="自治性社團",
            president_name="王小明",
            advisor_name="李老師",
            db_path=self.db_path,
        )

        self.assertEqual(saved["academic_year"], "115")
        self.assertEqual(saved["campus"], "博愛校區")
        self.assertEqual(saved["club_name"], "測試社團")
        self.assertEqual(saved["club_type"], "自治性社團")
        self.assertEqual(saved["president_name"], "王小明")
        self.assertEqual(saved["advisor_name"], "李老師")

    def test_get_evaluation_export_defaults_reads_saved_settings(self):
        save_club_settings(
            academic_year="116",
            campus="博愛校區",
            club_name="展示用社團",
            db_path=self.db_path,
        )

        export_defaults = get_evaluation_export_defaults(db_path=self.db_path)

        self.assertEqual(
            export_defaults,
            {
                "academic_year": "116",
                "campus": "博愛校區",
                "club_name": "展示用社團",
            },
        )


if __name__ == "__main__":
    unittest.main()
