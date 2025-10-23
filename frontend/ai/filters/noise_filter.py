"""
노이즈 필터링 모듈

형태학적 변환 및 컨투어 기반 노이즈 제거
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class NoiseFilter:
    """노이즈 필터 클래스"""

    def __init__(self, min_area: int = 100, min_aspect_ratio: float = 2.0):
        """
        노이즈 필터 초기화

        Args:
            min_area: 최소 면적 (픽셀)
            min_aspect_ratio: 최소 종횡비 (가로/세로)
        """
        self.min_area = min_area
        self.min_aspect_ratio = min_aspect_ratio
        # 커널을 미리 생성하여 재사용 (성능 향상)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    def remove_noise(self, mask: np.ndarray) -> np.ndarray:
        """
        노이즈 제거 (최적화 버전 - 단순 Opening만 사용)
        컨투어 필터링 생략으로 속도 향상

        Args:
            mask: 원본 마스크

        Returns:
            노이즈가 제거된 마스크
        """
        # Opening만 사용 (속도 우선)
        opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        return opened

    def _filter_by_contours(self, mask: np.ndarray) -> np.ndarray:
        """
        컨투어 기반 필터링 (면적 + 종횡비)

        Args:
            mask: 원본 마스크

        Returns:
            필터링된 마스크
        """
        # 컨투어 검출
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 새 마스크 생성
        clean_mask = np.zeros_like(mask)

        for contour in contours:
            # 면적 필터
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue

            # 종횡비 필터
            x, y, w, h = cv2.boundingRect(contour)
            if h == 0:
                continue

            aspect_ratio = w / h

            # 종횡비 2.0 이상 = 가로로 긴 선 (차선)
            # 종횡비 < 2.0 = 정사각형/원형 (노이즈)
            if aspect_ratio >= self.min_aspect_ratio:
                cv2.drawContours(clean_mask, [contour], -1, 255, -1)

        return clean_mask

    def apply_morphology(
        self, mask: np.ndarray, operation: str = "OPEN", kernel_size: int = 3
    ) -> np.ndarray:
        """
        형태학적 변환 적용

        Args:
            mask: 원본 마스크
            operation: 연산 종류 ("OPEN", "CLOSE", "ERODE", "DILATE")
            kernel_size: 커널 크기

        Returns:
            변환된 마스크
        """
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
        )

        operations = {
            "OPEN": cv2.MORPH_OPEN,
            "CLOSE": cv2.MORPH_CLOSE,
            "ERODE": cv2.MORPH_ERODE,
            "DILATE": cv2.MORPH_DILATE,
        }

        op = operations.get(operation, cv2.MORPH_OPEN)
        return cv2.morphologyEx(mask, op, kernel)
