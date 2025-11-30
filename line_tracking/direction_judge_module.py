"""
방향 판단 모듈
라인 중심점을 기반으로 조향 방향 결정
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class DirectionJudgeModule:
    """방향 판단기 클래스"""
    
    def __init__(
        self,
        deadzone_threshold: int = 30,
        strong_turn_threshold: int = 80,
    ):
        """
        방향 판단기 초기화
        
        Args:
            deadzone_threshold: 데드존 임계값 (픽셀) - 이 범위 내면 직진
            strong_turn_threshold: 강한 회전 임계값 (픽셀)
        """
        self.deadzone_threshold = deadzone_threshold
        self.strong_turn_threshold = strong_turn_threshold
        
        logger.info("방향 판단기 초기화 완료")
    
    def judge_direction(
        self, 
        line_center_x: int, 
        image_center_x: int
    ) -> Tuple[str, int]:
        """
        라인 중심점으로부터 방향 판단
        
        Args:
            line_center_x: 라인의 중심 X 좌표
            image_center_x: 이미지의 중심 X 좌표
        
        Returns:
            (명령, 오프셋)
            - 명령: "left", "right", "center"
            - 오프셋: 중심으로부터의 거리 (픽셀)
        """
        # 오프셋 계산 (양수: 오른쪽, 음수: 왼쪽)
        offset = line_center_x - image_center_x
        
        # 1. 데드존: 중심 근처는 직진
        if abs(offset) <= self.deadzone_threshold:
            return "center", offset
        
        # 2. 왼쪽으로 회전 (라인이 왼쪽에 있음)
        if offset < -self.deadzone_threshold:
            return "left", offset
        
        # 3. 오른쪽으로 회전 (라인이 오른쪽에 있음)
        if offset > self.deadzone_threshold:
            return "right", offset
        
        # 기본값: 직진
        return "center", offset
    
    def get_turn_intensity(self, offset: int) -> str:
        """
        회전 강도 판단
        
        Args:
            offset: 중심으로부터의 거리 (픽셀)
        
        Returns:
            "약함", "보통", "강함"
        """
        abs_offset = abs(offset)
        
        if abs_offset < self.deadzone_threshold:
            return "직진"
        elif abs_offset < self.strong_turn_threshold:
            return "보통"
        else:
            return "강함"

