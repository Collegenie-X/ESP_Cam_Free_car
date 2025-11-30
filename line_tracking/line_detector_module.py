"""
라인 검출 모듈
Canny Edge Detection + Hough Lines를 사용한 라인 검출
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class LineDetectorModule:
    """라인 검출기 클래스"""
    
    def __init__(
        self,
        canny_low: int = 85,
        canny_high: int = 85,
        hough_threshold: int = 10,
        min_line_length: int = 10,
        max_line_gap: int = 10,
        roi_bottom_ratio: float = 0.5,
    ):
        """
        라인 검출기 초기화
        
        Args:
            canny_low: Canny 하한값
            canny_high: Canny 상한값
            hough_threshold: Hough 변환 임계값
            min_line_length: 최소 라인 길이
            max_line_gap: 최대 라인 간격
            roi_bottom_ratio: ROI 하단 영역 비율 (0.0 ~ 1.0)
        """
        self.canny_low = canny_low
        self.canny_high = canny_high
        self.hough_threshold = hough_threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap
        self.roi_bottom_ratio = roi_bottom_ratio
        
        logger.info("라인 검출기 초기화 완료")
    
    def detect_line_center(self, frame: np.ndarray) -> Tuple[Optional[int], np.ndarray]:
        """
        프레임에서 라인의 중심점 X 좌표를 검출
        
        Args:
            frame: 입력 이미지 (BGR)
        
        Returns:
            (중심점_x, 처리된_이미지)
            - 중심점_x: 라인의 중심 X 좌표 (없으면 None)
            - 처리된_이미지: 전처리된 이미지 (디버깅용)
        """
        # Early return: 빈 프레임
        if frame is None or frame.size == 0:
            return None, frame
        
        height, width = frame.shape[:2]
        
        # 1. ROI 영역 추출 (하단 영역만)
        roi_start_y = int(height * self.roi_bottom_ratio)
        roi = frame[roi_start_y:height, 0:width]
        
        # 2. 그레이스케일 변환
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 3. 블러 처리 (노이즈 제거)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 4. Canny 엣지 검출
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        
        # 5. Hough Lines 검출
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=self.hough_threshold,
            minLineLength=self.min_line_length,
            maxLineGap=self.max_line_gap
        )
        
        # 6. 중심점 계산
        center_x = self._calculate_center_point(lines, width)
        
        return center_x, edges
    
    def _calculate_center_point(
        self, 
        lines: Optional[np.ndarray], 
        image_width: int
    ) -> Optional[int]:
        """
        검출된 라인들의 중심점 계산
        
        Args:
            lines: Hough Lines 결과
            image_width: 이미지 너비
        
        Returns:
            중심점 X 좌표 (없으면 None)
        """
        # Early return: 라인이 없으면 None
        if lines is None or len(lines) == 0:
            return None
        
        # 모든 라인의 중심점을 X 좌표 기준으로 계산
        x_positions = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 라인의 중심점 X 좌표
            center_x = (x1 + x2) // 2
            x_positions.append(center_x)
        
        # Early return: X 좌표가 없으면 None
        if not x_positions:
            return None
        
        # 전체 라인의 평균 중심점 계산
        final_center_x = int(np.mean(x_positions))
        
        return final_center_x
    
    def get_roi_start_y(self, height: int) -> int:
        """
        ROI 시작 Y 좌표 반환
        
        Args:
            height: 이미지 높이
        
        Returns:
            ROI 시작 Y 좌표
        """
        return int(height * self.roi_bottom_ratio)

