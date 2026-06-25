from __future__ import annotations

import unittest

from core.document_schemas import (
    get_recommended_evaluation_category,
    list_document_schemas,
    list_supported_document_types,
)


class DocumentSchemasTestCase(unittest.TestCase):
    def test_list_supported_document_types_returns_seven_types(self):
        self.assertEqual(
            list_supported_document_types(),
            [
                "會議紀錄",
                "開會通知",
                "會議議程",
                "活動企劃書",
                "活動成果報告",
                "活動檢討會紀錄",
                "年度計畫",
            ],
        )

    def test_list_document_schemas_contains_all_supported_types(self):
        schemas = list_document_schemas()
        self.assertEqual(len(schemas), 7)
        self.assertEqual(
            {schema["document_type"] for schema in schemas},
            set(list_supported_document_types()),
        )

    def test_each_document_type_has_recommended_evaluation_category(self):
        for document_type in list_supported_document_types():
            self.assertTrue(get_recommended_evaluation_category(document_type))


if __name__ == "__main__":
    unittest.main()
