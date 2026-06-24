from __future__ import annotations

EVALUATION_CATEGORIES = [
    "1.社團行政_組織章程",
    "2.社團行政_管理運作",
    "3.社團行政_社團資料保存",
    "4.社團行政_年度計畫",
    "5.社團行政_財務管理",
    "6.社團活動_社團活動",
    "7.社團活動_服務學習",
]

WEIGHTS = {
    "1.社團行政_組織章程": 5,
    "2.社團行政_管理運作": 10,
    "3.社團行政_社團資料保存": 10,
    "4.社團行政_年度計畫": 10,
    "5.社團行政_財務管理": 15,
    "6.社團活動_社團活動": 35,
    "7.社團活動_服務學習": 15,
}

EVALUATION_ITEMS = [
    {
        "category_code": category.split(".")[0],
        "category_name": category,
        "weight": WEIGHTS[category],
    }
    for category in EVALUATION_CATEGORIES
]
