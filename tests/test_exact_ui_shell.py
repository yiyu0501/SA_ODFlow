from __future__ import annotations

import unittest
from unittest.mock import patch

import core.exact_ui as exact_ui


class ExactUiShellTestCase(unittest.TestCase):
    def test_nav_href_preserves_workspace_and_can_clear_it(self):
        with patch.object(exact_ui.st, "query_params", {"workspace": "demo"}):
            self.assertEqual(exact_ui.nav_href("Files"), "/?page=Files&workspace=demo")
            self.assertEqual(exact_ui.nav_href("landing", workspace=""), "/?page=landing")

    def test_render_public_landing_contains_required_demo_entry_points(self):
        html = exact_ui.render_public_landing()

        self.assertIn("校園 ODF 文件工作流平台", html)
        self.assertIn("開始使用 Demo", html)
        self.assertIn("查看功能", html)
        self.assertIn("活動資料集中管理", html)

    def test_render_demo_login_contains_fields_and_demo_button(self):
        html = exact_ui.render_demo_login(target_page="files", error_message="請先登入")

        self.assertIn('name="email"', html)
        self.assertIn('name="password"', html)
        self.assertIn('name="next" value="files"', html)
        self.assertIn("使用 Demo 帳號進入", html)
        self.assertIn("請先登入", html)


if __name__ == "__main__":
    unittest.main()
