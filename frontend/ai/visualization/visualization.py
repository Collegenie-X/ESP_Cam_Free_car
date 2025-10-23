"""
시각화 모듈

분석 결과를 이미지에 오버레이하여 표시
"""

import cv2
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class Visualization:
    """시각화 클래스"""

    # ROI 설정 (320x240 기준)
    ROI_BOTTOM_Y = 180

    def __init__(self):
        """시각화 초기화"""
        pass

    def draw_analysis_overlay(
        self,
        image: np.ndarray,
        command: str,
        state: str,
        histogram: Dict[str, int],
    ) -> np.ndarray:
        """
        분석 결과 오버레이 (통합)

        Args:
            image: 원본 이미지
            command: 조향 명령
            state: 주행 상태
            histogram: 히스토그램

        Returns:
            오버레이가 그려진 이미지
        """
        result = image.copy()

        # 1. 상단 정보 패널
        result = self._draw_info_panel(result, command, state)

        # 2. 하단 히스토그램
        result = self._draw_histogram_bars(result, histogram)

        # 3. ROI 경계선
        result = self._draw_roi_boundary(result)

        # 4. 방향 화살표
        result = self._draw_direction_arrow(result, command)

        return result

    def _draw_info_panel(
        self, image: np.ndarray, command: str, state: str
    ) -> np.ndarray:
        """상단 정보 패널 그리기"""
        height, width = image.shape[:2]
        panel_height = 70  # 패널 높이 감소

        # 반투명 배경
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (width, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)

        # 명령 표시 (폰트 크기 감소)
        command_color = {
            "LEFT": (0, 165, 255),  # Orange
            "RIGHT": (255, 0, 255),  # Magenta
            "CENTER": (0, 255, 0),  # Green
            "STOP": (0, 0, 255),  # Red
        }.get(command, (255, 255, 255))

        cv2.putText(
            image,
            f">>> {command} <<<",
            (10, 30),  # y 위치 조정
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,  # 폰트 크기 감소: 1.3 -> 0.9
            command_color,
            2,  # 두께 감소: 3 -> 2
        )

        # 상태 표시 (영문으로 변경)
        state_text = {
            "NORMAL_DRIVING": "Normal",
            "CORNER_DETECTED": "Corner",
            "TURNING": "Turning",
        }.get(state, state)

        cv2.putText(
            image,
            f"State: {state_text}",
            (10, 55),  # y 위치 조정
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,  # 폰트 크기 감소: 0.7 -> 0.5
            (255, 255, 255),
            1,  # 두께 감소: 2 -> 1
        )

        return image

    def _draw_histogram_bars(
        self, image: np.ndarray, histogram: Dict[str, int]
    ) -> np.ndarray:
        """하단 히스토그램 바 그리기"""
        height, width = image.shape[:2]
        bar_height = 80
        bar_y = height - bar_height
        max_count = max(histogram.values()) or 1

        # 반투명 배경
        overlay = image.copy()
        cv2.rectangle(overlay, (0, bar_y), (width, height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)

        # 좌 (빨강)
        left_bar_h = int((histogram["left"] / max_count) * (bar_height - 20))
        if left_bar_h > 0:
            cv2.rectangle(
                image,
                (5, bar_y + (bar_height - left_bar_h - 5)),
                (width // 3 - 5, height - 5),
                (0, 0, 255),
                -1,
            )
        cv2.putText(
            image,
            f"L: {histogram['left']}",
            (10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # 중 (초록)
        center_bar_h = int((histogram["center"] / max_count) * (bar_height - 20))
        if center_bar_h > 0:
            cv2.rectangle(
                image,
                (width // 3 + 5, bar_y + (bar_height - center_bar_h - 5)),
                (2 * width // 3 - 5, height - 5),
                (0, 255, 0),
                -1,
            )
        cv2.putText(
            image,
            f"C: {histogram['center']}",
            (width // 3 + 10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # 우 (파랑)
        right_bar_h = int((histogram["right"] / max_count) * (bar_height - 20))
        if right_bar_h > 0:
            cv2.rectangle(
                image,
                (2 * width // 3 + 5, bar_y + (bar_height - right_bar_h - 5)),
                (width - 5, height - 5),
                (255, 0, 0),
                -1,
            )
        cv2.putText(
            image,
            f"R: {histogram['right']}",
            (2 * width // 3 + 10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        return image

    def _draw_roi_boundary(self, image: np.ndarray) -> np.ndarray:
        """ROI 경계선 그리기"""
        height, width = image.shape[:2]
        roi_y = int(height * (self.ROI_BOTTOM_Y / 240))

        cv2.line(image, (0, roi_y), (width, roi_y), (0, 255, 255), 2)
        cv2.putText(
            image,
            "ROI Bottom",
            (width - 120, roi_y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1,
        )

        return image

    def _draw_direction_arrow(self, image: np.ndarray, command: str) -> np.ndarray:
        """방향 화살표 그리기"""
        height, width = image.shape[:2]
        arrow_y = height // 2
        arrow_size = 50

        if command == "LEFT":
            # 왼쪽 화살표
            cv2.arrowedLine(
                image,
                (width // 2 + arrow_size, arrow_y),
                (width // 2 - arrow_size, arrow_y),
                (0, 165, 255),
                8,
                tipLength=0.4,
            )
        elif command == "RIGHT":
            # 오른쪽 화살표
            cv2.arrowedLine(
                image,
                (width // 2 - arrow_size, arrow_y),
                (width // 2 + arrow_size, arrow_y),
                (255, 0, 255),
                8,
                tipLength=0.4,
            )
        elif command == "CENTER":
            # 위쪽 화살표
            cv2.arrowedLine(
                image,
                (width // 2, arrow_y + arrow_size),
                (width // 2, arrow_y - arrow_size),
                (0, 255, 0),
                8,
                tipLength=0.4,
            )

        return image
