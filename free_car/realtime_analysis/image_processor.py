"""
이미지 처리 모듈

CLAHE, HSV 변환, 차선 마스크 생성
"""

import cv2
import numpy as np
from typing import Tuple

from .config import (
    ROI_BOTTOM_RATIO,
    BLACK_V_MIN,
    BLACK_V_MAX,
    BLACK_S_MAX,
    GRAY_V_MIN,
    GRAY_V_MAX,
    GRAY_S_MAX,
    RED_H_LOW_MIN,
    RED_H_LOW_MAX,
    RED_H_HIGH_MIN,
    RED_H_HIGH_MAX,
    RED_S_MIN,
    RED_V_MIN,
    ENABLE_IMAGE_ENHANCEMENT,
    BRIGHTNESS_BOOST,
    CONTRAST_BOOST,
    ENABLE_CLAHE,
    ENABLE_SHARPENING,
    ENABLE_DENOISING,
)


class ImageProcessor:
    """Image Processor with Advanced Preprocessing Pipeline"""

    def __init__(self):
        """Initialize image processor"""
        # CLAHE 초기화 (각 채널별 적응형 히스토그램 평활화)
        self.clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

        # 이전 프레임 저장 (시간 필터링용)
        self.prev_frame = None

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Advanced preprocessing pipeline for ESP32-CAM images

        Pipeline:
        1. Brightness enhancement
        2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        3. Specular reflection removal (햇빛 반사 제거)
        4. Noise reduction
        5. Sharpening (optional)

        Args:
            image: Input BGR image

        Returns:
            Enhanced image
        """
        if not ENABLE_IMAGE_ENHANCEMENT:
            return image

        enhanced = image.copy()

        # Step 1: 밝기 향상
        if BRIGHTNESS_BOOST > 0:
            enhanced = self._boost_brightness(enhanced, BRIGHTNESS_BOOST)

        # Step 2: CLAHE 적용 (대비 향상)
        if ENABLE_CLAHE:
            enhanced = self._apply_clahe_to_color(enhanced)

        # Step 3: 햇빛 반사 제거 (핵심!)
        enhanced = self._suppress_specular_highlights(enhanced)

        # Step 4: 노이즈 제거
        if ENABLE_DENOISING:
            enhanced = self._reduce_noise(enhanced)

        # Step 5: 샤프닝 (도로선 엣지 강조)
        if ENABLE_SHARPENING:
            enhanced = self._apply_sharpening(enhanced)

        # 현재 프레임을 이전 프레임으로 저장
        self.prev_frame = enhanced.copy()

        return enhanced

    def _boost_brightness(self, image: np.ndarray, boost_value: int) -> np.ndarray:
        """
        Boost image brightness

        Args:
            image: Input image
            boost_value: Brightness increase amount (0-100)

        Returns:
            Brightened image
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + boost_value, 0, 255)
        hsv = hsv.astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def _apply_clahe_to_color(self, image: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE to color image (preserve color information)

        Args:
            image: Input BGR image

        Returns:
            CLAHE enhanced image
        """
        # LAB 색공간 변환 (휘도와 색상 분리)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        # L 채널(휘도)에만 CLAHE 적용
        l_channel = self.clahe.apply(l_channel)

        # 대비 추가 조정
        if CONTRAST_BOOST != 1.0:
            l_channel = np.clip(l_channel * CONTRAST_BOOST, 0, 255).astype(np.uint8)

        # 채널 재결합
        enhanced_lab = cv2.merge([l_channel, a_channel, b_channel])
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    def _suppress_specular_highlights(self, image: np.ndarray) -> np.ndarray:
        """
        Remove specular reflection (햇빛 반사) - FAST version

        Strategy:
        1. Detect oversaturated bright regions (V > 250, S < 20)
        2. Simple blur instead of inpainting (훨씬 빠름!)

        Args:
            image: Input BGR image

        Returns:
            Image with suppressed highlights
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # 반사 영역 마스크 생성 (임계값을 더 엄격하게)
        # 조건: 매우 밝고(V>250), 채도 매우 낮음(S<20) = 햇빛 반사
        highlight_mask = ((v > 250) & (s < 20)).astype(np.uint8)

        # 반사 영역이 있으면 간단히 블러 처리 (inpaint보다 10배 빠름)
        if np.sum(highlight_mask) > 50:
            # 반사 영역만 추출
            result = image.copy()
            # 작은 블러로 반사 억제
            blurred = cv2.GaussianBlur(image, (5, 5), 0)
            # 마스크 영역만 블러 적용
            result[highlight_mask == 1] = blurred[highlight_mask == 1]
            return result

        return image

    def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Apply non-local means denoising

        Args:
            image: Input BGR image

        Returns:
            Denoised image
        """
        # Non-local Means Denoising: 고품질 노이즈 제거
        # h=10: 필터 강도 (높을수록 강력, 과하면 디테일 손실)
        # templateWindowSize=7, searchWindowSize=21
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

    def _apply_sharpening(self, image: np.ndarray) -> np.ndarray:
        """
        Apply unsharp masking to enhance edges

        Args:
            image: Input BGR image

        Returns:
            Sharpened image
        """
        # Unsharp Masking: 원본 - 블러 = 엣지 강조
        gaussian_blur = cv2.GaussianBlur(image, (0, 0), 2.0)
        sharpened = cv2.addWeighted(image, 1.5, gaussian_blur, -0.5, 0)
        return sharpened

    def extract_roi(self, image: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        ROI 추출 (하단 영역)

        Args:
            image: 입력 이미지

        Returns:
            (ROI 이미지, ROI 시작 Y 좌표)
        """
        height, width = image.shape[:2]
        roi_y_start = int(height * ROI_BOTTOM_RATIO)
        roi = image[roi_y_start:height, 0:width]

        return roi, roi_y_start

    def create_lane_mask(
        self, roi: np.ndarray, white_v_min: int, white_s_max: int
    ) -> np.ndarray:
        """
        차선 마스크 생성 (이진)

        Args:
            roi: ROI 이미지
            white_v_min: 흰색 V 최소값
            white_s_max: 흰색 S 최대값

        Returns:
            차선 마스크 (이진 이미지)
        """
        # HSV 변환
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 흰색 차선 검출
        lower_white = np.array([0, 0, white_v_min])
        upper_white = np.array([180, white_s_max, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)

        # 빨간색 차선 검출 (보너스)
        mask_red = self._detect_red_lanes(hsv)

        # 통합 마스크
        mask = cv2.bitwise_or(mask_white, mask_red)

        # 노이즈 제거
        mask = self._remove_noise(mask)

        return mask

    def create_segmentation_mask(
        self, roi: np.ndarray, white_v_min: int, white_s_max: int
    ) -> np.ndarray:
        """
        다층 세그멘테이션 마스크 생성 (확장된 범위)
        0 = 검정 (도로)
        1 = 기타 색깔 (장애물)
        2 = 흰색/회색/빨간색 (차선, 가중치 높음)

        Args:
            roi: ROI 이미지
            white_v_min: 흰색 V 최소값
            white_s_max: 흰색 S 최대값

        Returns:
            세그멘테이션 마스크 (0, 1, 2 값)
        """
        h, w = roi.shape[:2]
        seg_mask = np.zeros((h, w), dtype=np.uint8)

        # HSV 변환
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 1. 검정색 도로 검출 (BLACK_V_MIN ~ BLACK_V_MAX, 낮은 채도)
        black_mask = cv2.inRange(
            hsv,
            np.array([0, 0, BLACK_V_MIN]),
            np.array([180, BLACK_S_MAX, BLACK_V_MAX]),
        )
        seg_mask[black_mask == 255] = 0

        # 2. 차선 검출 (흰색 + 회색 + 빨간색, 확장된 범위)
        # 2-1. 밝은 흰색
        white_mask = cv2.inRange(
            hsv, np.array([0, 0, white_v_min]), np.array([180, white_s_max, 255])
        )

        # 2-2. 회색 도로선 (밝기 중간, 채도 낮음)
        gray_mask = cv2.inRange(
            hsv, np.array([0, 0, GRAY_V_MIN]), np.array([180, GRAY_S_MAX, GRAY_V_MAX])
        )

        # 2-3. 빨간색 (확장된 범위)
        red_mask = self._detect_red_lanes(hsv)

        # 차선 통합 (흰색 + 회색 + 빨간색)
        lane_mask = cv2.bitwise_or(white_mask, gray_mask)
        lane_mask = cv2.bitwise_or(lane_mask, red_mask)
        lane_mask = self._remove_noise(lane_mask)
        seg_mask[lane_mask == 255] = 2

        # 3. 나머지 (기타 색깔 = 장애물)
        seg_mask[(black_mask == 0) & (lane_mask == 0)] = 1

        return seg_mask

    def create_non_black_mask(self, roi: np.ndarray) -> np.ndarray:
        """
        비검정(장애물) 마스크 생성

        Args:
            roi: ROI 이미지

        Returns:
            검정 이외 영역 마스크 (이진)
        """
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # V가 낮으면 검정으로 간주 → 그 반대를 취함
        black_low = np.array([0, 0, 0])
        black_high = np.array([180, 255, BLACK_V_MAX])
        black_mask = cv2.inRange(hsv, black_low, black_high)

        non_black = cv2.bitwise_not(black_mask)

        # 노이즈 제거 재사용
        non_black = self._remove_noise(non_black)

        return non_black

    def _detect_red_lanes(self, hsv: np.ndarray) -> np.ndarray:
        """
        빨간색 차선 검출 (확장된 범위)

        Args:
            hsv: HSV 이미지

        Returns:
            빨간색 마스크
        """
        # 빨간색 범위 1 (0-15, config에서 조정 가능)
        lower_red1 = np.array([RED_H_LOW_MIN, RED_S_MIN, RED_V_MIN])
        upper_red1 = np.array([RED_H_LOW_MAX, 255, 255])
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)

        # 빨간색 범위 2 (155-180, config에서 조정 가능)
        lower_red2 = np.array([RED_H_HIGH_MIN, RED_S_MIN, RED_V_MIN])
        upper_red2 = np.array([RED_H_HIGH_MAX, 255, 255])
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

        # 통합
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        return mask_red

    def _remove_noise(self, mask: np.ndarray) -> np.ndarray:
        """
        노이즈 제거 (모폴로지 연산)

        Args:
            mask: 이진 마스크

        Returns:
            노이즈 제거된 마스크
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

        # Closing: 작은 구멍 제거
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Opening: 작은 점 제거
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        return mask
