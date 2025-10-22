"""
차선 추적 서비스

차선 분석 및 조향 판단을 수행합니다.
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class LaneTrackingService:
    """차선 추적 서비스 클래스"""

    def __init__(
        self,
        brightness_threshold: int = 80,
        min_lane_pixels: int = 200,
        deadzone_ratio: float = 0.15,
        bias_ratio: float = 1.3,
    ):
        """
        차선 추적 초기화

        Args:
            brightness_threshold: 밝기 임계값
            min_lane_pixels: 최소 차선 픽셀 수
            deadzone_ratio: 데드존 비율
            bias_ratio: 좌우 편향 판단 비율
        """
        self.brightness_threshold = brightness_threshold
        self.min_lane_pixels = min_lane_pixels
        self.deadzone_ratio = deadzone_ratio
        self.bias_ratio = bias_ratio

        # CLAHE 초기화
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        # HSV 범위
        self.HSV_WHITE_BRIGHT = {
            "lower": np.array([0, 0, 200]),
            "upper": np.array([180, 30, 255]),
        }
        self.HSV_RED_1 = {
            "lower": np.array([0, 100, 100]),
            "upper": np.array([10, 255, 255]),
        }
        self.HSV_RED_2 = {
            "lower": np.array([160, 100, 100]),
            "upper": np.array([180, 255, 255]),
        }

        logger.info("차선 추적 서비스 초기화 완료")

    def process_frame(self, image: np.ndarray, debug: bool = False) -> Dict[str, Any]:
        """
        프레임 처리 및 조향 판단

        Args:
            image: 입력 이미지 (BGR)
            debug: 디버그 모드

        Returns:
            {
                "command": str,  # left, right, center, stop
                "histogram": dict,  # {left: int, center: int, right: int}
                "confidence": float,  # 0.0 ~ 1.0
                "debug_image": np.ndarray  # debug=True일 때만
            }
        """
        try:
            # 1. CLAHE 전처리
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            enhanced = self.clahe.apply(gray)
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

            # 2. 가우시안 블러
            blurred = cv2.GaussianBlur(enhanced_bgr, (5, 5), 0)

            # 3. ROI 추출 (하단)
            height, width = blurred.shape[:2]
            roi_y_start = int(height * 0.75)  # 하단 25%
            roi = blurred[roi_y_start:height, 0:width]

            # 4. HSV 변환 및 차선 마스크 생성
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # 흰색 차선
            mask_white = cv2.inRange(
                hsv, self.HSV_WHITE_BRIGHT["lower"], self.HSV_WHITE_BRIGHT["upper"]
            )

            # 빨간색 차선
            mask_red1 = cv2.inRange(
                hsv, self.HSV_RED_1["lower"], self.HSV_RED_1["upper"]
            )
            mask_red2 = cv2.inRange(
                hsv, self.HSV_RED_2["lower"], self.HSV_RED_2["upper"]
            )
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)

            # 통합 마스크
            mask = cv2.bitwise_or(mask_white, mask_red)

            # 5. 노이즈 제거
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # 6. 히스토그램 계산
            histogram = self._calculate_histogram(mask)

            # 7. 조향 판단
            command, confidence = self._judge_steering(histogram)

            result = {
                "command": command,
                "histogram": histogram,
                "confidence": confidence,
            }

            # 8. 디버그 이미지 생성
            if debug:
                debug_image = self._draw_debug_overlay(
                    image.copy(), roi_y_start, histogram, command, confidence
                )
                result["debug_image"] = debug_image

            return result

        except Exception as e:
            logger.error(f"프레임 처리 실패: {e}")
            return {
                "command": "stop",
                "histogram": {"left": 0, "center": 0, "right": 0},
                "confidence": 0.0,
            }

    def _calculate_histogram(self, mask: np.ndarray) -> Dict[str, int]:
        """
        히스토그램 계산 (3등분)

        Args:
            mask: 이진 마스크

        Returns:
            {left: int, center: int, right: int}
        """
        height, width = mask.shape
        third = width // 3

        left_sum = np.sum(mask[:, 0:third] == 255)
        center_sum = np.sum(mask[:, third : third * 2] == 255)
        right_sum = np.sum(mask[:, third * 2 : width] == 255)

        return {
            "left": int(left_sum),
            "center": int(center_sum),
            "right": int(right_sum),
        }

    def _judge_steering(self, histogram: Dict[str, int]) -> Tuple[str, float]:
        """
        조향 판단

        Args:
            histogram: 히스토그램 데이터

        Returns:
            (command, confidence)
        """
        left = histogram["left"]
        center = histogram["center"]
        right = histogram["right"]
        total = left + center + right

        # 차선이 거의 없으면 정지
        if total < self.min_lane_pixels:
            return "stop", 0.0

        # 정규화
        width = total
        left_ratio = left / width if width > 0 else 0
        center_ratio = center / width if width > 0 else 0
        right_ratio = right / width if width > 0 else 0

        # 데드존 (좌우 차이가 적으면 center)
        deadzone = self.deadzone_ratio
        if abs(left_ratio - right_ratio) < deadzone:
            return "center", center_ratio

        # 좌우 편향 판단
        if left_ratio > right_ratio * self.bias_ratio:
            confidence = min(left_ratio / (left_ratio + right_ratio), 1.0)
            return "left", confidence
        elif right_ratio > left_ratio * self.bias_ratio:
            confidence = min(right_ratio / (left_ratio + right_ratio), 1.0)
            return "right", confidence
        else:
            return "center", center_ratio

    def _draw_debug_overlay(
        self,
        image: np.ndarray,
        roi_y_start: int,
        histogram: Dict[str, int],
        command: str,
        confidence: float,
    ) -> np.ndarray:
        """
        디버그 오버레이 그리기

        Args:
            image: 원본 이미지
            roi_y_start: ROI 시작 Y 좌표
            histogram: 히스토그램 데이터
            command: 명령
            confidence: 신뢰도

        Returns:
            오버레이가 그려진 이미지
        """
        height, width = image.shape[:2]

        # ROI 경계선
        cv2.line(image, (0, roi_y_start), (width, roi_y_start), (255, 255, 0), 2)

        # 명령 텍스트
        command_text = command.upper()
        color = {
            "left": (0, 165, 255),  # 주황색
            "right": (255, 0, 255),  # 자홍색
            "center": (0, 255, 0),  # 초록색
            "stop": (0, 0, 255),  # 빨간색
        }.get(command, (255, 255, 255))

        cv2.putText(
            image,
            f">>> {command_text} <<<",
            (10, 40),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            color,
            3,
        )

        # 히스토그램 표시
        left = histogram["left"]
        center = histogram["center"]
        right = histogram["right"]

        cv2.putText(
            image,
            f"L: {left}  C: {center}  R: {right}",
            (10, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # 신뢰도 표시
        cv2.putText(
            image,
            f"Confidence: {confidence*100:.1f}%",
            (10, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        return image
