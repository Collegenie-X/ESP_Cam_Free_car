"""
조향 판단 모듈

히스토그램 분석 및 조향 명령 결정
"""

import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SteeringJudge:
    """조향 판단 클래스"""

    def __init__(
        self,
        threshold_deadzone: float = 0.15,
        threshold_ratio: float = 1.3,
        threshold_min_pixels: int = 200,
        threshold_min_side: int = 100,
    ):
        """
        조향 판단기 초기화

        Args:
            threshold_deadzone: 좌우 차이 임계값 (15% 미만 = 직진)
            threshold_ratio: 좌우 비율 임계값 (1.3배 이상 = 회전)
            threshold_min_pixels: 최소 차선 픽셀 (이하면 STOP)
            threshold_min_side: 좌우 각각 최소 픽셀
        """
        self.threshold_deadzone = threshold_deadzone
        self.threshold_ratio = threshold_ratio
        self.threshold_min_pixels = threshold_min_pixels
        self.threshold_min_side = threshold_min_side

    def judge_steering(self, mask: np.ndarray) -> Tuple[str, Dict[str, int], float]:
        """
        히스토그램 기반 조향 판단

        Args:
            mask: 차선 마스크

        Returns:
            (command, histogram, confidence)
            - command: "LEFT" | "RIGHT" | "CENTER" | "STOP"
            - histogram: {"left": int, "center": int, "right": int}
            - confidence: 0.0 ~ 1.0
        """
        # 히스토그램 계산
        histogram = self._calculate_histogram(mask)
        left_count = histogram["left"]
        center_count = histogram["center"]
        right_count = histogram["right"]
        total_count = left_count + center_count + right_count

        # 판단 로직
        # 1. 차선 거의 없음
        if total_count < self.threshold_min_pixels:
            return "STOP", histogram, 0.0

        # 2. 좌우 차이가 작음 (데드존)
        diff = abs(left_count - right_count)
        diff_ratio = diff / total_count if total_count > 0 else 0

        if diff_ratio < self.threshold_deadzone:
            confidence = 1.0 - diff_ratio / self.threshold_deadzone
            return "CENTER", histogram, confidence

        # 3. 좌우 모두 적음 (중앙에 몰림)
        if (
            left_count < self.threshold_min_side
            and right_count < self.threshold_min_side
        ):
            return "CENTER", histogram, 0.8

        # 4. 명확한 좌우 편향
        if left_count > right_count * self.threshold_ratio:
            confidence = min(left_count / (right_count + 1) / 3.0, 1.0)
            return "LEFT", histogram, confidence
        elif right_count > left_count * self.threshold_ratio:
            confidence = min(right_count / (left_count + 1) / 3.0, 1.0)
            return "RIGHT", histogram, confidence
        else:
            # 애매하면 직진
            return "CENTER", histogram, 0.5

    def _calculate_histogram(self, mask: np.ndarray) -> Dict[str, int]:
        """
        히스토그램 계산 (좌/중/우 3분할)

        Args:
            mask: 차선 마스크

        Returns:
            {"left": int, "center": int, "right": int}
        """
        height, width = mask.shape

        # 이미지 3분할
        third = width // 3
        left_region = mask[:, 0:third]
        center_region = mask[:, third : 2 * third]
        right_region = mask[:, 2 * third :]

        # 각 영역 픽셀 카운트
        left_count = int(np.sum(left_region == 255))
        center_count = int(np.sum(center_region == 255))
        right_count = int(np.sum(right_region == 255))

        return {
            "left": left_count,
            "center": center_count,
            "right": right_count,
        }
