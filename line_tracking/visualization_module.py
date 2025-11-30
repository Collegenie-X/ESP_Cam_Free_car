"""
시각화 모듈
실시간 디버깅 화면 표시
"""

import cv2
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class VisualizationModule:
    """시각화 모듈 클래스"""
    
    def __init__(self):
        """시각화 모듈 초기화"""
        self.colors = {
            "left": (0, 165, 255),    # 주황색
            "right": (255, 0, 255),    # 자홍색
            "center": (0, 255, 0),     # 초록색
            "stop": (0, 0, 255),       # 빨간색
        }
        
        logger.info("시각화 모듈 초기화 완료")
    
    def draw_debug_info(
        self,
        frame: np.ndarray,
        line_center_x: Optional[int],
        command: str,
        offset: int,
        roi_start_y: int,
    ) -> np.ndarray:
        """
        디버그 정보를 프레임에 그리기
        
        Args:
            frame: 원본 프레임
            line_center_x: 라인 중심점 X 좌표
            command: 명령 ("left", "right", "center")
            offset: 중심 오프셋
            roi_start_y: ROI 시작 Y 좌표
        
        Returns:
            디버그 정보가 그려진 프레임
        """
        result = frame.copy()
        height, width = result.shape[:2]
        image_center_x = width // 2
        
        # 1. ROI 경계선 (빨간색 수평선)
        cv2.line(
            result,
            (0, roi_start_y),
            (width, roi_start_y),
            (0, 0, 255),
            2
        )
        
        # 2. 화면 중심선 (파란색 수직선)
        cv2.line(
            result,
            (image_center_x, 0),
            (image_center_x, height),
            (255, 0, 0),
            2
        )
        
        # 3. 라인 중심점 표시 (초록색 원)
        if line_center_x is not None:
            # 중심점 좌표 (ROI 내에서의 Y 좌표)
            center_y = (roi_start_y + height) // 2
            
            # 초록색 원
            cv2.circle(
                result,
                (line_center_x, center_y),
                10,
                (0, 255, 0),
                -1
            )
            
            # 중심점에서 화면 중심까지 선
            cv2.line(
                result,
                (line_center_x, center_y),
                (image_center_x, center_y),
                (255, 255, 0),
                2
            )
        
        # 4. 명령 텍스트 (큰 글씨)
        command_color = self.colors.get(command, (255, 255, 255))
        command_text = command.upper()
        
        cv2.putText(
            result,
            f">>> {command_text} <<<",
            (10, 50),
            cv2.FONT_HERSHEY_DUPLEX,
            1.5,
            command_color,
            3
        )
        
        # 5. 오프셋 정보
        offset_text = f"Offset: {offset}px"
        offset_color = (255, 255, 255)
        
        cv2.putText(
            result,
            offset_text,
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            offset_color,
            2
        )
        
        # 6. 라인 검출 상태
        detection_text = "Line: FOUND" if line_center_x is not None else "Line: LOST"
        detection_color = (0, 255, 0) if line_center_x is not None else (0, 0, 255)
        
        cv2.putText(
            result,
            detection_text,
            (10, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            detection_color,
            2
        )
        
        return result
    
    def create_side_by_side_view(
        self,
        original: np.ndarray,
        processed: np.ndarray,
    ) -> np.ndarray:
        """
        원본 이미지와 처리된 이미지를 나란히 표시
        
        Args:
            original: 원본 이미지
            processed: 처리된 이미지 (Canny 결과 등)
        
        Returns:
            나란히 배치된 이미지
        """
        # 처리된 이미지를 3채널로 변환
        if len(processed.shape) == 2:
            processed_bgr = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        else:
            processed_bgr = processed
        
        # 크기 조정 (필요시)
        if original.shape != processed_bgr.shape:
            processed_bgr = cv2.resize(
                processed_bgr,
                (original.shape[1], original.shape[0])
            )
        
        # 좌우로 배치
        combined = np.hstack([original, processed_bgr])
        
        return combined

