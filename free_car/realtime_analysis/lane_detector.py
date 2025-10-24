"""
Lane Detection and Steering Decision Module
차선 검출 및 조향 판단 모듈 (히스토그램 분석)
"""

import numpy as np
from typing import Dict, Tuple

from .config import DEADZONE_RATIO, BIAS_RATIO


class LaneDetector:
    """Lane Detector with Multi-layer ROI Weighting"""

    def calculate_histogram(self, mask: np.ndarray) -> Dict[str, int]:
        """
        Calculate histogram with multi-layer ROI weighting

        Weighting Strategy:
        - Bottom 30%: x3 (가까운 곳, 가장 중요)
        - Middle 30%: x2 (중간 거리)
        - Top 40%: x1 (먼 곳, 노이즈 많음)

        Segmentation Values:
        - 0 (black/road): weight x0
        - 1 (obstacles): weight x1
        - 2 (lane lines): weight x5 (도로선 강조!)

        Args:
            mask: Binary or segmentation mask (0,1,2)

        Returns:
            {left: int, center: int, right: int}
        """
        height, width = mask.shape
        third_width = width // 3

        # 다층 ROI 분할 (상/중/하)
        bottom_30 = int(height * 0.7)  # 하단 30% 시작점
        middle_30 = int(height * 0.4)  # 중단 30% 시작점

        # 세그멘테이션 마스크인 경우 (0,1,2 값)
        if mask.max() <= 2:
            # 도로선 가중치 = 5, 장애물 = 1, 도로 = 0
            LANE_WEIGHT = 5
            OBSTACLE_WEIGHT = 1

            # === LEFT 영역 계산 ===
            left_col = mask[:, 0:third_width]
            # 하단 30% (가중치 x3)
            left_bottom = left_col[bottom_30:, :]
            left_sum = (
                np.sum(left_bottom == 1) * OBSTACLE_WEIGHT * 3
                + np.sum(left_bottom == 2) * LANE_WEIGHT * 3
            )
            # 중단 30% (가중치 x2)
            left_middle = left_col[middle_30:bottom_30, :]
            left_sum += (
                np.sum(left_middle == 1) * OBSTACLE_WEIGHT * 2
                + np.sum(left_middle == 2) * LANE_WEIGHT * 2
            )
            # 상단 40% (가중치 x1)
            left_top = left_col[:middle_30, :]
            left_sum += (
                np.sum(left_top == 1) * OBSTACLE_WEIGHT
                + np.sum(left_top == 2) * LANE_WEIGHT
            )

            # === CENTER 영역 계산 ===
            center_col = mask[:, third_width : third_width * 2]
            # 하단 30%
            center_bottom = center_col[bottom_30:, :]
            center_sum = (
                np.sum(center_bottom == 1) * OBSTACLE_WEIGHT * 3
                + np.sum(center_bottom == 2) * LANE_WEIGHT * 3
            )
            # 중단 30%
            center_middle = center_col[middle_30:bottom_30, :]
            center_sum += (
                np.sum(center_middle == 1) * OBSTACLE_WEIGHT * 2
                + np.sum(center_middle == 2) * LANE_WEIGHT * 2
            )
            # 상단 40%
            center_top = center_col[:middle_30, :]
            center_sum += (
                np.sum(center_top == 1) * OBSTACLE_WEIGHT
                + np.sum(center_top == 2) * LANE_WEIGHT
            )

            # === RIGHT 영역 계산 ===
            right_col = mask[:, third_width * 2 : width]
            # 하단 30%
            right_bottom = right_col[bottom_30:, :]
            right_sum = (
                np.sum(right_bottom == 1) * OBSTACLE_WEIGHT * 3
                + np.sum(right_bottom == 2) * LANE_WEIGHT * 3
            )
            # 중단 30%
            right_middle = right_col[middle_30:bottom_30, :]
            right_sum += (
                np.sum(right_middle == 1) * OBSTACLE_WEIGHT * 2
                + np.sum(right_middle == 2) * LANE_WEIGHT * 2
            )
            # 상단 40%
            right_top = right_col[:middle_30, :]
            right_sum += (
                np.sum(right_top == 1) * OBSTACLE_WEIGHT
                + np.sum(right_top == 2) * LANE_WEIGHT
            )
        else:
            # 이진 마스크 (기존 방식)
            left_sum = np.sum(mask[:, 0:third_width] == 255)
            center_sum = np.sum(mask[:, third_width : third_width * 2] == 255)
            right_sum = np.sum(mask[:, third_width * 2 : width] == 255)

        return {
            "left": int(left_sum),
            "center": int(center_sum),
            "right": int(right_sum),
        }

    def judge_steering(
        self, histogram: Dict[str, int], min_pixels: int, prefer_low: bool = False
    ) -> Tuple[str, float]:
        """
        조향 판단

        Args:
            histogram: 히스토그램 데이터
            min_pixels: 최소 픽셀 수

        Returns:
            (조향 명령, 신뢰도)
        """
        left = histogram["left"]
        center = histogram["center"]
        right = histogram["right"]
        total = left + center + right

        # Early return: 차선이 거의 없으면 정지
        if total < min_pixels:
            return "stop", 0.0

        # 정규화
        left_ratio = left / total
        center_ratio = center / total
        right_ratio = right / total

        # 데드존: 좌우 차이가 적으면 center
        if abs(left_ratio - right_ratio) < DEADZONE_RATIO:
            return "center", center_ratio

        # 장애물 모드: 더 빈쪽으로 회피 (prefer_low=True)
        if prefer_low:
            if left_ratio < right_ratio / BIAS_RATIO:
                confidence = self._calculate_confidence(right_ratio, left_ratio)
                return "right", confidence
            if right_ratio < left_ratio / BIAS_RATIO:
                confidence = self._calculate_confidence(left_ratio, right_ratio)
                return "left", confidence

        # 좌회전 판단
        if left_ratio > right_ratio * BIAS_RATIO:
            confidence = self._calculate_confidence(left_ratio, right_ratio)
            return "left", confidence

        # 우회전 판단
        if right_ratio > left_ratio * BIAS_RATIO:
            confidence = self._calculate_confidence(right_ratio, left_ratio)
            return "right", confidence

        # 기본값: center
        return "center", center_ratio

    def _calculate_confidence(self, dominant_ratio: float, other_ratio: float) -> float:
        """
        신뢰도 계산

        Args:
            dominant_ratio: 우세한 쪽 비율
            other_ratio: 다른 쪽 비율

        Returns:
            신뢰도 (0.0 ~ 1.0)
        """
        total = dominant_ratio + other_ratio

        # Early return: 0으로 나누기 방지
        if total == 0:
            return 0.0

        confidence = dominant_ratio / total
        return min(confidence, 1.0)  # 최대 1.0
