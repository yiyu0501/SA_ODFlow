from __future__ import annotations

import unittest

from core.ui_components import badge_html, card_html, category_badge_html, paper_preview_shell


class UiComponentsTestCase(unittest.TestCase):
    def test_category_badge_uses_expected_categories(self):
        for category in ["日常行政型", "專案活動型", "社團運作型", "財務與清冊型"]:
            html = category_badge_html(category)
            self.assertIn(category, html)

    def test_badge_html_and_card_html_return_renderable_markup(self):
        badge = badge_html("ODT", tone="primary")
        card = card_html("活動企劃書", "整理活動流程與預算。", badges=[badge])

        self.assertIn("ODT", badge)
        self.assertIn("活動企劃書", card)
        self.assertIn("整理活動流程與預算。", card)

    def test_paper_preview_shell_handles_missing_data(self):
        html = paper_preview_shell("<div>預覽內容</div>", note="此為版型預覽")

        self.assertIn("預覽內容", html)
        self.assertIn("此為版型預覽", html)
        self.assertIn("odf-paper", html)


if __name__ == "__main__":
    unittest.main()
