"""
자율주행 차선 추적 모듈 (prod.md 기반)

ESP32-CAM의 저품질 이미지에서 차선을 추적하고 조향 판단을 수행합니다.
- CLAHE: 저조도 이미지 개선
- HSV 이중 마스킹: 흰색(직진) + 빨간색(코너) 차선 검출
- 컨투어 필터링: 빛 반사 노이즈 제거
- 히스토그램: 좌/중/우 판단
- 90도 코너 감지: LookAhead ROI
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class AutonomousLaneTracker:
    """자율주행 차선 추적 클래스 (prod.md 사양 구현)"""

    # ROI 설정 (320x240 기준)
    ROI_BOTTOM = {"y_start": 180, "y_end": 240, "x_start": 0, "x_end": 320}
    ROI_CENTER = {"y_start": 120, "y_end": 180, "x_start": 0, "x_end": 320}

    # HSV 색상 범위
    HSV_WHITE_BRIGHT = {"lower": (0, 0, 200), "upper": (180, 30, 255)}
    HSV_WHITE_DARK = {"lower": (0, 0, 150), "upper": (180, 50, 255)}
    HSV_RED_1 = {"lower": (0, 100, 100), "upper": (10, 255, 255)}
    HSV_RED_2 = {"lower": (170, 100, 100), "upper": (180, 255, 255)}

    # 판단 임계값
    THRESHOLD_DEADZONE = 0.15  # 좌우 차이 15% 미만 = 직진
    THRESHOLD_RATIO = 1.3  # 좌 > 우*1.3 = 좌회전
    THRESHOLD_MIN_PIXELS = 200  # 최소 차선 픽셀 (이하면 STOP)
    THRESHOLD_MIN_SIDE = 100  # 좌우 각각 최소 픽셀

    # 90도 코너 감지
    THRESHOLD_CORNER_RATIO = 0.78  # 픽셀 78% 이상 = 코너
    THRESHOLD_CORNER_BALANCE = 0.20  # 좌중우 편차 20% 미만 = 가로선

    def __init__(self, brightness_threshold: int = 80, use_adaptive: bool = True):
        """
        자율주행 차선 추적기 초기화

        Args:
            brightness_threshold: 밝기 임계값 (이하면 어두운 환경)
            use_adaptive: 적응형 HSV 범위 사용 여부
        """
        self.brightness_threshold = brightness_threshold
        self.use_adaptive = use_adaptive
        self.state = "NORMAL_DRIVING"  # NORMAL_DRIVING, CORNER_DETECTED, TURNING
        logger.info("자율주행 차선 추적기 초기화 완료")

    def process_frame(self, image: np.ndarray, debug: bool = False) -> Dict[str, Any]:
        """
        프레임 처리 및 조향 판단 (전체 파이프라인)

        Args:
            image: 원본 이미지 (BGR)
            debug: 디버그 모드 (중간 결과 포함)

        Returns:
            {
                "command": "LEFT" | "RIGHT" | "CENTER" | "STOP",
                "state": "NORMAL_DRIVING" | "CORNER_DETECTED" | "TURNING",
                "histogram": {"left": int, "center": int, "right": int},
                "confidence": float,
                "debug_images": {...}  # debug=True일 때만
            }
        """
        try:
            debug_images = {}

            # 1단계: CLAHE 전처리 (선명도 개선)
            enhanced = self._apply_clahe(image)
            if debug:
                debug_images["1_clahe"] = enhanced

            # 2단계: 가우시안 블러 (노이즈 제거)
            blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
            if debug:
                debug_images["2_blurred"] = blurred

            # 3단계: ROI 추출 (하단)
            roi_bottom = self._extract_roi(blurred, self.ROI_BOTTOM)
            if debug:
                debug_images["3_roi_bottom"] = roi_bottom

            # 4단계: HSV 변환
            hsv = cv2.cvtColor(roi_bottom, cv2.COLOR_BGR2HSV)

            # 5단계: 차선 마스크 생성 (흰색 + 빨간색)
            mask = self._create_lane_mask(hsv, roi_bottom)
            if debug:
                debug_images["5_mask"] = mask

            # 6단계: 노이즈 제거 (컨투어 필터링)
            clean_mask = self._remove_noise(mask)
            if debug:
                debug_images["6_clean_mask"] = clean_mask

            # 7단계: 히스토그램 분석 및 조향 판단
            command, histogram, confidence = self._judge_steering(clean_mask)

            # 8단계: 90도 코너 감지 (선택적)
            if self._is_corner_detected(clean_mask, histogram):
                self.state = "CORNER_DETECTED"
                # LookAhead ROI로 방향 판단
                corner_command = self._judge_corner_direction(blurred)
                if corner_command:
                    command = corner_command
                    self.state = "TURNING"
            else:
                self.state = "NORMAL_DRIVING"

            result = {
                "command": command,
                "state": self.state,
                "histogram": histogram,
                "confidence": confidence,
            }

            if debug:
                debug_images["7_final"] = self._draw_histogram_overlay(
                    image, histogram, command
                )
                result["debug_images"] = debug_images

            return result

        except Exception as e:
            logger.error(f"프레임 처리 실패: {e}")
            return {
                "command": "STOP",
                "state": "ERROR",
                "histogram": {"left": 0, "center": 0, "right": 0},
                "confidence": 0.0,
            }

    def _apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """
        CLAHE (대비 제한 적응 히스토그램 평활화) 적용

        Args:
            image: 원본 BGR 이미지

        Returns:
            선명도가 개선된 이미지
        """
        # BGR을 LAB 색공간으로 변환 (L: 밝기, A: 녹색-빨강, B: 파랑-노랑)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # L 채널에만 CLAHE 적용
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l)

        # 다시 합치고 BGR로 변환
        lab_clahe = cv2.merge([l_clahe, a, b])
        enhanced = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

        return enhanced

    def _extract_roi(self, image: np.ndarray, roi: Dict[str, int]) -> np.ndarray:
        """
        ROI 영역 추출

        Args:
            image: 원본 이미지
            roi: ROI 좌표 {"y_start", "y_end", "x_start", "x_end"}

        Returns:
            ROI 영역 이미지
        """
        return image[roi["y_start"] : roi["y_end"], roi["x_start"] : roi["x_end"]]

    def _create_lane_mask(self, hsv: np.ndarray, original: np.ndarray) -> np.ndarray:
        """
        차선 마스크 생성 (흰색 + 빨간색 이중 마스킹)

        Args:
            hsv: HSV 이미지
            original: 원본 BGR 이미지 (밝기 판단용)

        Returns:
            이진 마스크 (255: 차선, 0: 도로)
        """
        # 밝기 판단 (적응형 HSV 범위)
        if self.use_adaptive:
            gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)
            is_dark = avg_brightness < self.brightness_threshold
        else:
            is_dark = False

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

    def _remove_noise(self, mask: np.ndarray) -> np.ndarray:
        """
        노이즈 제거 (3단계 필터링)
        1차: 형태학적 Opening
        2차: 컨투어 면적 + 종횡비 필터링
        3차: (선택) 연결성 검사

        Args:
            mask: 원본 마스크

        Returns:
            노이즈가 제거된 마스크
        """
        # 1차: Opening (작은 점 노이즈 제거)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # 2차: 컨투어 필터링 (면적 + 종횡비)
        contours, _ = cv2.findContours(
            opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # 새 마스크 생성
        clean_mask = np.zeros_like(mask)

        for contour in contours:
            area = cv2.contourArea(contour)

            # 면적 필터: 100픽셀 이상만 유지
            if area < 100:
                continue

            # 종횡비 필터: 가로로 긴 선(차선)만 유지
            x, y, w, h = cv2.boundingRect(contour)
            if h == 0:
                continue

            aspect_ratio = w / h

            # 종횡비 2.0 이상 = 가로로 긴 선 (차선)
            # 종횡비 < 2.0 = 정사각형/원형 (노이즈)
            if aspect_ratio >= 2.0:
                cv2.drawContours(clean_mask, [contour], -1, 255, -1)

        return clean_mask

    def _judge_steering(self, mask: np.ndarray) -> Tuple[str, Dict[str, int], float]:
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
        height, width = mask.shape

        # 이미지 3분할
        third = width // 3
        left_region = mask[:, 0:third]
        center_region = mask[:, third : 2 * third]
        right_region = mask[:, 2 * third :]

        # 각 영역 픽셀 카운트
        left_count = np.sum(left_region == 255)
        center_count = np.sum(center_region == 255)
        right_count = np.sum(right_region == 255)
        total_count = left_count + center_count + right_count

        histogram = {
            "left": int(left_count),
            "center": int(center_count),
            "right": int(right_count),
        }

        # 판단 로직
        # 1. 차선 거의 없음
        if total_count < self.THRESHOLD_MIN_PIXELS:
            return "STOP", histogram, 0.0

        # 2. 좌우 차이가 작음 (데드존)
        diff = abs(left_count - right_count)
        diff_ratio = diff / total_count if total_count > 0 else 0

        if diff_ratio < self.THRESHOLD_DEADZONE:
            confidence = 1.0 - diff_ratio / self.THRESHOLD_DEADZONE
            return "CENTER", histogram, confidence

        # 3. 좌우 모두 적음 (중앙에 몰림)
        if (
            left_count < self.THRESHOLD_MIN_SIDE
            and right_count < self.THRESHOLD_MIN_SIDE
        ):
            return "CENTER", histogram, 0.8

        # 4. 명확한 좌우 편향
        if left_count > right_count * self.THRESHOLD_RATIO:
            confidence = min(left_count / (right_count + 1) / 3.0, 1.0)
            return "LEFT", histogram, confidence
        elif right_count > left_count * self.THRESHOLD_RATIO:
            confidence = min(right_count / (left_count + 1) / 3.0, 1.0)
            return "RIGHT", histogram, confidence
        else:
            # 애매하면 직진
            return "CENTER", histogram, 0.5

    def _is_corner_detected(self, mask: np.ndarray, histogram: Dict[str, int]) -> bool:
        """
        90도 코너 감지

        Args:
            mask: 차선 마스크
            histogram: 히스토그램

        Returns:
            True: 90도 코너 감지됨
        """
        height, width = mask.shape
        total_pixels = width * height
        lane_pixels = np.sum(mask == 255)

        # 조건 1: 차선 픽셀이 78% 이상
        if lane_pixels < total_pixels * self.THRESHOLD_CORNER_RATIO:
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
        return std_dev < self.THRESHOLD_CORNER_BALANCE

    def _judge_corner_direction(self, image: np.ndarray) -> Optional[str]:
        """
        90도 코너 방향 판단 (LookAhead ROI)

        Args:
            image: 전처리된 이미지

        Returns:
            "LEFT" | "RIGHT" | None (판단 불가)
        """
        try:
            # 중앙 ROI 추출
            roi_center = self._extract_roi(image, self.ROI_CENTER)

            # HSV 변환 및 마스크 생성
            hsv = cv2.cvtColor(roi_center, cv2.COLOR_BGR2HSV)
            mask = self._create_lane_mask(hsv, roi_center)
            clean_mask = self._remove_noise(mask)

            # 좌우 분할 (중앙 기준)
            height, width = clean_mask.shape
            center_left = clean_mask[:, : width // 2]
            center_right = clean_mask[:, width // 2 :]

            # 픽셀 카운트
            left_pixels = np.sum(center_left == 255)
            right_pixels = np.sum(center_right == 255)

            # 방향 판단 (비율 2.0 이상 = 명확한 방향)
            if left_pixels > right_pixels * 2.0:
                return "LEFT"
            elif right_pixels > left_pixels * 2.0:
                return "RIGHT"
            else:
                return None  # TURN_ASSIST 필요 (제자리 회전)

        except Exception as e:
            logger.error(f"코너 방향 판단 실패: {e}")
            return None

    def _draw_histogram_overlay(
        self, image: np.ndarray, histogram: Dict[str, int], command: str
    ) -> np.ndarray:
        """
        히스토그램 및 판단 결과 오버레이 (분석 상황 시각화)

        Args:
            image: 원본 이미지
            histogram: 히스토그램
            command: 판단 결과

        Returns:
            오버레이가 그려진 이미지
        """
        result = image.copy()
        height, width = result.shape[:2]

        # ===== 1. 상단 정보 패널 =====
        panel_height = 100
        overlay = result.copy()
        cv2.rectangle(overlay, (0, 0), (width, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, result, 0.5, 0, result)

        # 명령 표시 (큰 글씨)
        command_color = {
            "LEFT": (0, 165, 255),    # 주황
            "RIGHT": (255, 0, 255),   # 마젠타
            "CENTER": (0, 255, 0),    # 초록
            "STOP": (0, 0, 255),      # 빨강
        }.get(command, (255, 255, 255))

        cv2.putText(
            result,
            f">>> {command} <<<",
            (10, 40),
            cv2.FONT_HERSHEY_DUPLEX,
            1.3,
            command_color,
            3,
        )

        # 상태 표시
        state_text = {
            "NORMAL_DRIVING": "일반 주행",
            "CORNER_DETECTED": "코너 감지",
            "TURNING": "회전 중",
        }.get(self.state, self.state)
        
        cv2.putText(
            result,
            f"상태: {state_text}",
            (10, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # ===== 2. 히스토그램 바 (하단) =====
        bar_height = 80
        bar_y = height - bar_height
        max_count = max(histogram.values()) or 1

        # 반투명 배경
        overlay = result.copy()
        cv2.rectangle(overlay, (0, bar_y), (width, height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, result, 0.4, 0, result)

        # 좌 (빨강)
        left_bar_h = int((histogram["left"] / max_count) * (bar_height - 20))
        if left_bar_h > 0:
            cv2.rectangle(
                result,
                (5, bar_y + (bar_height - left_bar_h - 5)),
                (width // 3 - 5, height - 5),
                (0, 0, 255),
                -1,
            )
        # 좌측 텍스트
        cv2.putText(
            result,
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
                result,
                (width // 3 + 5, bar_y + (bar_height - center_bar_h - 5)),
                (2 * width // 3 - 5, height - 5),
                (0, 255, 0),
                -1,
            )
        # 중앙 텍스트
        cv2.putText(
            result,
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
                result,
                (2 * width // 3 + 5, bar_y + (bar_height - right_bar_h - 5)),
                (width - 5, height - 5),
                (255, 0, 0),
                -1,
            )
        # 우측 텍스트
        cv2.putText(
            result,
            f"R: {histogram['right']}",
            (2 * width // 3 + 10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # ===== 3. ROI 영역 표시 =====
        # 하단 ROI 경계선
        roi_y = int(height * (self.ROI_BOTTOM["y_start"] / 240))
        cv2.line(result, (0, roi_y), (width, roi_y), (0, 255, 255), 2)
        cv2.putText(
            result,
            "ROI Bottom",
            (width - 120, roi_y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1,
        )

        # ===== 4. 방향 화살표 (큰 표시) =====
        arrow_y = height // 2
        arrow_size = 50
        
        if command == "LEFT":
            # 왼쪽 화살표
            cv2.arrowedLine(
                result,
                (width // 2 + arrow_size, arrow_y),
                (width // 2 - arrow_size, arrow_y),
                (0, 165, 255),
                8,
                tipLength=0.4,
            )
        elif command == "RIGHT":
            # 오른쪽 화살표
            cv2.arrowedLine(
                result,
                (width // 2 - arrow_size, arrow_y),
                (width // 2 + arrow_size, arrow_y),
                (255, 0, 255),
                8,
                tipLength=0.4,
            )
        elif command == "CENTER":
            # 위쪽 화살표
            cv2.arrowedLine(
                result,
                (width // 2, arrow_y + arrow_size),
                (width // 2, arrow_y - arrow_size),
                (0, 255, 0),
                8,
                tipLength=0.4,
            )

        return result
