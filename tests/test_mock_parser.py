from __future__ import annotations

import unittest

from ai.mock_parser import parse_meeting_minutes


class MockParserTestCase(unittest.TestCase):
    def test_parse_meeting_minutes_returns_expected_content_shape(self):
        content = parse_meeting_minutes(
            transcript_text="""
            出席人員：王小明、李小華
            討論事項：確認迎新活動流程
            決議：下週前完成場地借用
            待辦：王小明整理活動清單
            """,
            meeting_date="2026-06-24",
            meeting_name="第 3 次幹部會議",
            meeting_type="幹部會議",
            instruction="請整理成會議紀錄",
        )

        self.assertEqual(content["meeting_title"], "第 3 次幹部會議")
        self.assertEqual(content["meeting_date"], "2026-06-24")
        self.assertIn("agenda_items", content)
        self.assertIn("action_items", content)
        self.assertIsInstance(content["attendees"], list)
        self.assertGreaterEqual(len(content["agenda_items"]), 1)
        self.assertGreaterEqual(len(content["action_items"]), 1)


if __name__ == "__main__":
    unittest.main()
