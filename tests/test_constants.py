from __future__ import annotations

import unittest

from core.constants import (
    EVALUATION_CATEGORIES,
    EVALUATION_ITEMS,
    EVALUATION_REQUIRED_DOCUMENTS,
    WEIGHTS,
)


class EvaluationConstantsTestCase(unittest.TestCase):
    def test_category_count_is_seven(self):
        self.assertEqual(len(EVALUATION_CATEGORIES), 7)

    def test_weights_cover_all_categories(self):
        self.assertEqual(set(EVALUATION_CATEGORIES), set(WEIGHTS))

    def test_items_match_categories(self):
        self.assertEqual(len(EVALUATION_ITEMS), len(EVALUATION_CATEGORIES))

    def test_required_document_rules_cover_all_categories(self):
        self.assertEqual(set(EVALUATION_REQUIRED_DOCUMENTS), set(EVALUATION_CATEGORIES))


if __name__ == "__main__":
    unittest.main()
