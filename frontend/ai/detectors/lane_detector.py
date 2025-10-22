"""
차선 감지 모듈
OpenCV를 사용한 기본 차선 감지 알고리즘
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class LaneDetector:
    """차선 검출 클래스"""

    def __init__(
        self,
        roi_top_ratio: float = 0.6,
        canny_low: int = 50,
        canny_high: int = 150,
    ):
        """
        차선 감지기 초기화

        Args:
            roi_top_ratio: ROI(관심 영역) 상단 비율 (0.0 ~ 1.0)
            canny_low: Canny 엣지 검출 하한값
            canny_high: Canny 엣지 검출 상한값
        """
        self.roi_top_ratio = roi_top_ratio
        self.canny_low = canny_low
        self.canny_high = canny_high

    def detect_lanes(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        이미지에서 차선 감지

        Args:
            image: OpenCV 이미지 (numpy array)

        Returns:
            감지된 차선 리스트 (각 차선은 시작점과 끝점 정보 포함)
            예: [
                {
                    "side": "left",
                    "line": {"x1": 100, "y1": 400, "x2": 200, "y2": 300}
                }
            ]
        """
        try:
            # 1. 그레이스케일 변환
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 2. 가우시안 블러 (노이즈 제거)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)

            # 3. Canny 엣지 검출
            edges = cv2.Canny(blur, self.canny_low, self.canny_high)

            # 4. ROI(관심 영역) 설정
            height, width = image.shape[:2]
            roi_mask = self._create_roi_mask(height, width)
            masked_edges = cv2.bitwise_and(edges, roi_mask)

            # 5. Hough 변환으로 직선 검출
            lines = cv2.HoughLinesP(
                masked_edges,
                rho=1,
                theta=np.pi / 180,
                threshold=50,
                minLineLength=50,
                maxLineGap=150,
            )

            # 6. 차선 분류 (왼쪽/오른쪽)
            detected_lanes = self._classify_lanes(lines, width)

            return detected_lanes

        except Exception as e:
            logger.error(f"차선 감지 실패: {e}")
            return []

    def _create_roi_mask(self, height: int, width: int) -> np.ndarray:
        """
        ROI(관심 영역) 마스크 생성

        Args:
            height: 이미지 높이
            width: 이미지 너비

        Returns:
            ROI 마스크 (numpy array)
        """
        mask = np.zeros((height, width), dtype=np.uint8)

        # 사다리꼴 ROI 영역 정의
        roi_top = int(height * self.roi_top_ratio)
        roi_points = np.array(
            [
                [
                    (0, height),  # 좌하단
                    (width // 2 - 50, roi_top),  # 좌상단
                    (width // 2 + 50, roi_top),  # 우상단
                    (width, height),  # 우하단
                ]
            ],
            dtype=np.int32,
        )

        cv2.fillPoly(mask, roi_points, 255)
        return mask

    def _classify_lanes(
        self, lines: Optional[np.ndarray], image_width: int
    ) -> List[Dict[str, Any]]:
        """
        검출된 직선을 왼쪽/오른쪽 차선으로 분류

        Args:
            lines: Hough 변환 결과
            image_width: 이미지 너비

        Returns:
            분류된 차선 리스트
        """
        if lines is None:
            return []

        left_lines = []
        right_lines = []
        center_x = image_width // 2

        for line in lines:
            x1, y1, x2, y2 = line[0]

            # 기울기 계산
            if x2 == x1:
                continue
            slope = (y2 - y1) / (x2 - x1)

            # 너무 수평인 선 제외
            if abs(slope) < 0.5:
                continue

            # 왼쪽 차선 (음의 기울기)
            if slope < 0 and x1 < center_x and x2 < center_x:
                left_lines.append((x1, y1, x2, y2))
            # 오른쪽 차선 (양의 기울기)
            elif slope > 0 and x1 > center_x and x2 > center_x:
                right_lines.append((x1, y1, x2, y2))

        detected_lanes = []

        # 왼쪽 차선 대표선 계산
        if left_lines:
            left_line = self._average_line(left_lines)
            detected_lanes.append(
                {
                    "side": "left",
                    "line": {
                        "x1": left_line[0],
                        "y1": left_line[1],
                        "x2": left_line[2],
                        "y2": left_line[3],
                    },
                }
            )

        # 오른쪽 차선 대표선 계산
        if right_lines:
            right_line = self._average_line(right_lines)
            detected_lanes.append(
                {
                    "side": "right",
                    "line": {
                        "x1": right_line[0],
                        "y1": right_line[1],
                        "x2": right_line[2],
                        "y2": right_line[3],
                    },
                }
            )

        return detected_lanes

    def _average_line(
        self, lines: List[Tuple[int, int, int, int]]
    ) -> Tuple[int, int, int, int]:
        """
        여러 직선의 평균 직선 계산

        Args:
            lines: 직선 리스트

        Returns:
            평균 직선 (x1, y1, x2, y2)
        """
        x1_avg = int(np.mean([line[0] for line in lines]))
        y1_avg = int(np.mean([line[1] for line in lines]))
        x2_avg = int(np.mean([line[2] for line in lines]))
        y2_avg = int(np.mean([line[3] for line in lines]))

        return (x1_avg, y1_avg, x2_avg, y2_avg)

    def calculate_center_offset(
        self, lanes: List[Dict[str, Any]], image_width: int
    ) -> Optional[int]:
        """
        차선 중심과 이미지 중심의 오프셋 계산

        Args:
            lanes: detect_lanes() 결과
            image_width: 이미지 너비

        Returns:
            오프셋 (픽셀) - 양수: 오른쪽, 음수: 왼쪽, None: 계산 불가
        """
        if len(lanes) != 2:
            return None

        left_lane = next((lane for lane in lanes if lane["side"] == "left"), None)
        right_lane = next((lane for lane in lanes if lane["side"] == "right"), None)

        if not left_lane or not right_lane:
            return None

        # 차선 하단 중심점 계산
        left_x = left_lane["line"]["x1"]
        right_x = right_lane["line"]["x1"]
        lane_center = (left_x + right_x) // 2
        image_center = image_width // 2

        offset = lane_center - image_center
        return offset

    def draw_lanes(self, image: np.ndarray, lanes: List[Dict[str, Any]]) -> np.ndarray:
        """
        이미지에 차선 그리기 (Label 포함)

        Args:
            image: 원본 이미지
            lanes: detect_lanes() 결과

        Returns:
            차선이 그려진 이미지
        """
        result_image = image.copy()

        for lane in lanes:
            line = lane["line"]
            side = lane["side"]

            # 색상: 왼쪽 차선은 녹색, 오른쪽 차선은 빨간색
            color = (0, 255, 0) if side == "left" else (0, 0, 255)

            # 차선 그리기 (더 두껍게)
            cv2.line(
                result_image,
                (line["x1"], line["y1"]),
                (line["x2"], line["y2"]),
                color,
                4,  # 두께 증가 (3 -> 4)
            )

            # 레이블 추가
            label_text = "LEFT" if side == "left" else "RIGHT"

            # 레이블 위치: 차선 중간점
            label_x = (line["x1"] + line["x2"]) // 2
            label_y = (line["y1"] + line["y2"]) // 2

            # 텍스트 크기 계산
            font_scale = 0.7
            font_thickness = 2
            text_size = cv2.getTextSize(
                label_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
            )[0]

            # 텍스트 배경 (검은색)
            padding = 5
            cv2.rectangle(
                result_image,
                (label_x - padding, label_y - text_size[1] - padding),
                (label_x + text_size[0] + padding, label_y + padding),
                (0, 0, 0),
                -1,
            )

            # 텍스트 그리기 (흰색)
            cv2.putText(
                result_image,
                label_text,
                (label_x, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                font_thickness,
            )

        return result_image
