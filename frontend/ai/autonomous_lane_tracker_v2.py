"""
자율주행 차선 추적 모듈 V2 (리팩토링 버전)

모듈화된 컴포넌트를 조합하여 차선 추적 수행
"""

import cv2
import numpy as np
from typing import Dict, Any
import logging

from ai.image_preprocessor import ImagePreprocessor
from ai.lane_mask_generator import LaneMaskGenerator
from ai.noise_filter import NoiseFilter
from ai.steering_judge import SteeringJudge
from ai.corner_detector import CornerDetector
from ai.visualization import Visualization

logger = logging.getLogger(__name__)


class AutonomousLaneTrackerV2:
    """자율주행 차선 추적 클래스 V2 (모듈화)"""

    # ROI 설정 (320x240 기준)
    ROI_BOTTOM = {"y_start": 180, "y_end": 240, "x_start": 0, "x_end": 320}
    ROI_CENTER = {"y_start": 120, "y_end": 180, "x_start": 0, "x_end": 320}

    def __init__(
        self,
        brightness_threshold: int = 80,
        use_adaptive: bool = True,
        min_noise_area: int = 100,
        min_aspect_ratio: float = 2.0,
    ):
        """
        자율주행 차선 추적기 초기화

        Args:
            brightness_threshold: 밝기 임계값
            use_adaptive: 적응형 HSV 사용 여부
            min_noise_area: 최소 노이즈 면적
            min_aspect_ratio: 최소 종횡비
        """
        # 컴포넌트 초기화
        self.preprocessor = ImagePreprocessor()
        self.mask_generator = LaneMaskGenerator(brightness_threshold)
        self.noise_filter = NoiseFilter(min_noise_area, min_aspect_ratio)
        self.steering_judge = SteeringJudge()
        self.corner_detector = CornerDetector()
        self.visualizer = Visualization()

        self.use_adaptive = use_adaptive
        self.state = "NORMAL_DRIVING"  # NORMAL_DRIVING, CORNER_DETECTED, TURNING

        logger.info("자율주행 차선 추적기 V2 초기화 완료 (모듈화)")

    def process_frame(self, image: np.ndarray, debug: bool = False) -> Dict[str, Any]:
        """
        프레임 처리 및 조향 판단 (전체 파이프라인)

        Args:
            image: 원본 이미지 (BGR)
            debug: 디버그 모드

        Returns:
            {
                "command": str,
                "state": str,
                "histogram": dict,
                "confidence": float,
                "debug_images": dict  # debug=True일 때만
            }
        """
        try:
            debug_images = {}

            # 1단계: CLAHE 전처리
            enhanced = self.preprocessor.apply_clahe(image)
            if debug:
                debug_images["1_clahe"] = enhanced

            # 2단계: 가우시안 블러
            blurred = self.preprocessor.apply_gaussian_blur(enhanced)
            if debug:
                debug_images["2_blurred"] = blurred

            # 3단계: ROI 추출 (하단)
            roi_bottom = self.preprocessor.extract_roi(blurred, self.ROI_BOTTOM)
            if debug:
                debug_images["3_roi_bottom"] = roi_bottom

            # 4단계: HSV 변환
            hsv = cv2.cvtColor(roi_bottom, cv2.COLOR_BGR2HSV)

            # 5단계: 차선 마스크 생성
            if self.use_adaptive:
                mask = self.mask_generator.create_adaptive_mask(hsv, roi_bottom)
            else:
                mask = self.mask_generator.create_lane_mask(hsv, is_dark=False)

            if debug:
                debug_images["5_mask"] = mask

            # 6단계: 노이즈 제거
            clean_mask = self.noise_filter.remove_noise(mask)
            if debug:
                debug_images["6_clean_mask"] = clean_mask

            # 7단계: 조향 판단
            command, histogram, confidence = self.steering_judge.judge_steering(
                clean_mask
            )

            # 8단계: 90도 코너 감지
            if self.corner_detector.is_corner_detected(clean_mask, histogram):
                self.state = "CORNER_DETECTED"

                # LookAhead ROI로 방향 판단
                corner_command = self._judge_corner_direction(blurred)
                if corner_command:
                    command = corner_command
                    self.state = "TURNING"
            else:
                self.state = "NORMAL_DRIVING"

            # 결과 구성
            result = {
                "command": command,
                "state": self.state,
                "histogram": histogram,
                "confidence": confidence,
            }

            # 디버그: 시각화
            if debug:
                debug_images["7_final"] = self.visualizer.draw_analysis_overlay(
                    image, command, self.state, histogram
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

    def _judge_corner_direction(self, image: np.ndarray) -> str:
        """
        90도 코너 방향 판단 (내부 메서드)

        Args:
            image: 전처리된 이미지

        Returns:
            "LEFT" | "RIGHT" | None
        """
        try:
            # 중앙 ROI 추출
            roi_center = self.preprocessor.extract_roi(image, self.ROI_CENTER)

            # HSV 변환 및 마스크 생성
            hsv = cv2.cvtColor(roi_center, cv2.COLOR_BGR2HSV)
            mask = self.mask_generator.create_adaptive_mask(hsv, roi_center)
            clean_mask = self.noise_filter.remove_noise(mask)

            # 방향 판단
            return self.corner_detector.judge_corner_direction(clean_mask)

        except Exception as e:
            logger.error(f"코너 방향 판단 실패: {e}")
            return None
