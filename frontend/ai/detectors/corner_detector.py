"""
코너 감지 모듈

90도 코너 감지 및 방향 판단
"""

import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CornerDetector:
    """코너 감지 클래스"""

    def __init__(
        self,
        threshold_corner_ratio: float = 0.78,
        threshold_corner_balance: float = 0.20,
        threshold_direction_ratio: float = 2.0,
    ):
        """
        코너 감지기 초기화

        Args:
            threshold_corner_ratio: 코너 감지 픽셀 비율 (78% 이상)
            threshold_corner_balance: 좌중우 균등 분포 편차 (20% 미만)
            threshold_direction_ratio: 방향 판단 비율 (2.0배 이상)
        """
        self.threshold_corner_ratio = threshold_corner_ratio
        self.threshold_corner_balance = threshold_corner_balance
        self.threshold_direction_ratio = threshold_direction_ratio

    def is_corner_detected(self, mask: np.ndarray, histogram: Dict[str, int]) -> bool:
        """
        90도 코너 감지

        Args:
            mask: 차선 마스크
            histogram: 히스토그램 {"left", "center", "right"}

        Returns:
            True: 90도 코너 감지됨
        """
        height, width = mask.shape
        total_pixels = width * height
        lane_pixels = np.sum(mask == 255)

        # 조건 1: 차선 픽셀이 78% 이상
        if lane_pixels < total_pixels * self.threshold_corner_ratio:
            return False

        # 조건 2: 좌중우 균등 분포 (가로선)
        left = histogram["left"]
        center = histogram["center"]
        right = histogram["right"]
        total = left + center + right

        if total == 0:
            return False

        # 각 영역 비율
        left_ratio = left / total
        center_ratio = center / total
        right_ratio = right / total

        # 편차 계산 (표준편차)
        mean_ratio = 1.0 / 3.0
        variance = (
            (left_ratio - mean_ratio) ** 2
            + (center_ratio - mean_ratio) ** 2
            + (right_ratio - mean_ratio) ** 2
        ) / 3
        std_dev = variance**0.5

        # 편차가 20% 미만이면 균등 = 가로선
        return std_dev < self.threshold_corner_balance

    def judge_corner_direction(self, lookahead_mask: np.ndarray) -> Optional[str]:
        """
        코너 방향 판단 (LookAhead ROI 분석)

        Args:
            lookahead_mask: 중앙 ROI 마스크

        Returns:
            "LEFT" | "RIGHT" | None (판단 불가)
        """
        # 좌우 분할 (중앙 기준)
        height, width = lookahead_mask.shape
        center_left = lookahead_mask[:, : width // 2]
        center_right = lookahead_mask[:, width // 2 :]

        # 픽셀 카운트
        left_pixels = np.sum(center_left == 255)
        right_pixels = np.sum(center_right == 255)

        # 방향 판단 (비율 2.0 이상 = 명확한 방향)
        if left_pixels > right_pixels * self.threshold_direction_ratio:
            return "LEFT"
        elif right_pixels > left_pixels * self.threshold_direction_ratio:
            return "RIGHT"
        else:
            return None  # TURN_ASSIST 필요 (제자리 회전)
