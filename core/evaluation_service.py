from __future__ import annotations

from core.constants import EVALUATION_ITEMS


def list_evaluation_items():
    return EVALUATION_ITEMS.copy()


def calculate_completion():
    raise NotImplementedError("Task 4 才會實作評鑑完整度計算。")
