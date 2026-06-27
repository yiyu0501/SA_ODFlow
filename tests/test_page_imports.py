from __future__ import annotations

import contextlib
import io
import runpy
import unittest


PAGE_PATHS = [
    "app.py",
    "pages/1_Dashboard.py",
    "pages/2_Generate.py",
    "pages/3_Files.py",
    "pages/5_Evaluation.py",
    "pages/6_Templates.py",
    "pages/7_Settings.py",
]


class PageImportTestCase(unittest.TestCase):
    def test_page_modules_import_without_crashing(self):
        for path in PAGE_PATHS:
            with self.subTest(path=path):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                    io.StringIO()
                ):
                    runpy.run_path(path)


if __name__ == "__main__":
    unittest.main()
