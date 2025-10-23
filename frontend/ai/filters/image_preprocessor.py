"""
이미지 전처리 모듈

CLAHE, 가우시안 블러, ROI 추출 등 이미지 전처리 기능 제공
"""

import cv2
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """이미지 전처리 클래스"""

    def __init__(self):
        """전처리기 초기화 - CLAHE 객체를 미리 생성하여 재사용"""
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """
        CLAHE (대비 제한 적응 히스토그램 평활화) 적용 - 최적화 버전

        Args:
            image: 원본 BGR 이미지

        Returns:
            선명도가 개선된 이미지
        """
        # 그레이스케일로 변환하여 처리 속도 향상 (컬러 변환 생략)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        enhanced_gray = self.clahe.apply(gray)
        # 그레이스케일을 BGR로 변환
        enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
        return enhanced

    @staticmethod
    def apply_gaussian_blur(
        image: np.ndarray, kernel_size: tuple = (3, 3)
    ) -> np.ndarray:
        """
        가우시안 블러 적용 (노이즈 제거) - 최적화: 커널 크기 축소

        Args:
            image: 원본 이미지
            kernel_size: 커널 크기 (기본: 3x3, 속도 향상)

        Returns:
            블러 처리된 이미지
        """
        return cv2.GaussianBlur(image, kernel_size, 0)

    @staticmethod
    def extract_roi(image: np.ndarray, roi: Dict[str, int]) -> np.ndarray:
        """
        ROI (관심 영역) 추출

        Args:
            image: 원본 이미지
            roi: ROI 좌표 {"y_start", "y_end", "x_start", "x_end"}

        Returns:
            ROI 영역 이미지
        """
        return image[roi["y_start"] : roi["y_end"], roi["x_start"] : roi["x_end"]]

    @staticmethod
    def get_average_brightness(image: np.ndarray) -> float:
        """
        이미지 평균 밝기 계산

        Args:
            image: BGR 이미지

        Returns:
            평균 밝기값 (0-255)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return float(np.mean(gray))
