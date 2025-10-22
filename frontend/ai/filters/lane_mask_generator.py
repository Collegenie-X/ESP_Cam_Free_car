"""
차선 마스크 생성 모듈

HSV 색상 기반 차선 검출 (흰색 + 빨간색)
"""

import cv2
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class LaneMaskGenerator:
    """차선 마스크 생성 클래스"""

    # HSV 색상 범위 설정
    HSV_WHITE_BRIGHT = {
        "lower": np.array([0, 0, 200]),
        "upper": np.array([180, 30, 255]),
    }
    HSV_WHITE_DARK = {"lower": np.array([0, 0, 150]), "upper": np.array([180, 50, 255])}
    HSV_RED_1 = {"lower": np.array([0, 100, 100]), "upper": np.array([10, 255, 255])}
    HSV_RED_2 = {"lower": np.array([170, 100, 100]), "upper": np.array([180, 255, 255])}

    def __init__(self, brightness_threshold: int = 80):
        """
        차선 마스크 생성기 초기화

        Args:
            brightness_threshold: 밝기 임계값 (이하면 어두운 환경)
        """
        self.brightness_threshold = brightness_threshold

    def create_lane_mask(self, hsv: np.ndarray, is_dark: bool = False) -> np.ndarray:
        """
        차선 마스크 생성 (흰색 + 빨간색)

        Args:
            hsv: HSV 이미지
            is_dark: 어두운 환경 여부

        Returns:
            이진 마스크 (255: 차선, 0: 도로)
        """
        # 흰색 차선 마스크
        if is_dark:
            white_mask = cv2.inRange(
                hsv, self.HSV_WHITE_DARK["lower"], self.HSV_WHITE_DARK["upper"]
            )
        else:
            white_mask = cv2.inRange(
                hsv, self.HSV_WHITE_BRIGHT["lower"], self.HSV_WHITE_BRIGHT["upper"]
            )

        # 빨간색 차선 마스크 (두 범위 합침)
        red_mask1 = cv2.inRange(hsv, self.HSV_RED_1["lower"], self.HSV_RED_1["upper"])
        red_mask2 = cv2.inRange(hsv, self.HSV_RED_2["lower"], self.HSV_RED_2["upper"])
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)

        # 마스크 결합
        combined_mask = cv2.bitwise_or(white_mask, red_mask)

        return combined_mask

    def create_adaptive_mask(
        self, hsv: np.ndarray, original_bgr: np.ndarray
    ) -> np.ndarray:
        """
        적응형 차선 마스크 생성 (밝기 자동 판단)

        Args:
            hsv: HSV 이미지
            original_bgr: 원본 BGR 이미지

        Returns:
            이진 마스크
        """
        # 밝기 판단
        gray = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        is_dark = avg_brightness < self.brightness_threshold

        return self.create_lane_mask(hsv, is_dark)
