"""
Autonomous Driving Module
자율주행 핵심 로직 - 하이브리드 방향 결정 알고리즘
"""

import numpy as np
import cv2
from typing import Dict, Tuple, Optional
import requests
import time

from .config import (
    MOTOR_CONTROL_URL,
    STEERING_CENTER_THRESHOLD,
    STEERING_MIN_CONFIDENCE,
    HORIZONTAL_LINE_THRESHOLD,
    HORIZONTAL_LINE_MIN_LENGTH,
)


class AutonomousDriver:
    """Autonomous Driving Controller with Hybrid Decision Algorithm"""

    def __init__(self):
        """Initialize autonomous driver"""
        # 이전 명령 저장 (연속성 유지)
        self.prev_command = "center"
        self.prev_command_count = 0

        # 이동평균 필터를 위한 히스토그램 버퍼
        self.histogram_buffer = []
        self.buffer_size = 3

        # 통계
        self.total_commands = 0
        self.command_history = {"left": 0, "right": 0, "center": 0, "stop": 0}

        print("🚗 Autonomous Driver initialized")

    def decide_direction_hybrid(
        self, seg_mask: np.ndarray, histogram: Dict[str, int], confidence: float
    ) -> Tuple[str, float, str]:
        """
        하이브리드 방향 결정 알고리즘

        Decision Strategy:
        1. 차선이 명확 → 차선 위치 기반
        2. 차선이 약함 → 가중 히스토그램
        3. 장애물 많음 → 장애물 회피
        4. 90도 도로선 → 특별 처리
        5. 불확실 → 이전 명령 유지

        Args:
            seg_mask: Segmentation mask (0=road, 1=obstacle, 2=lane)
            histogram: Histogram data {left, center, right}
            confidence: Current confidence value

        Returns:
            (command, confidence, method_used)
        """
        # 픽셀 카운트
        lane_pixels = np.sum(seg_mask == 2)
        obstacle_pixels = np.sum(seg_mask == 1)
        total_pixels = seg_mask.size

        # 차선 비율
        lane_ratio = lane_pixels / total_pixels
        obstacle_ratio = obstacle_pixels / total_pixels

        # === 상황 1: 90도 도로선 감지 ===
        if self._detect_horizontal_lane(seg_mask):
            command = self._handle_horizontal_lane(seg_mask)
            return command, 0.9, "horizontal_lane"

        # === 상황 2: 차선이 명확 (비율 > 5%) ===
        if lane_ratio > 0.05:
            command, conf = self._lane_position_method(seg_mask)
            if command != "unknown":
                return command, conf, "lane_position"

        # === 상황 3: 장애물 많음 (비율 > 30%) ===
        if obstacle_ratio > 0.3:
            command = self._obstacle_avoidance_method(histogram)
            return command, confidence, "obstacle_avoidance"

        # === 상황 4: 가중 히스토그램 (기본) ===
        if lane_ratio > 0.02:  # 최소한의 차선
            command = self._weighted_histogram_method(histogram)
            return command, confidence, "weighted_histogram"

        # === 상황 5: 불확실 → 이전 명령 유지 or 정지 ===
        if self.prev_command_count < 10:  # 10프레임까지 유지
            return self.prev_command, 0.1, "hold_previous"
        else:
            return "stop", 0.0, "uncertain_stop"

    def _lane_position_method(self, seg_mask: np.ndarray) -> Tuple[str, float]:
        """
        차선 위치 기반 방향 결정

        Args:
            seg_mask: Segmentation mask

        Returns:
            (command, confidence)
        """
        height, width = seg_mask.shape

        # 도로선만 추출 (값=2)
        lane_mask = (seg_mask == 2).astype(np.uint8)

        # 좌우로 나누기
        left_half = lane_mask[:, : width // 2]
        right_half = lane_mask[:, width // 2 :]

        # 각 절반의 무게중심 계산
        left_center = self._calculate_centroid_x(left_half)
        right_center = self._calculate_centroid_x(right_half) + width // 2

        # 두 차선이 모두 있을 때만 처리
        if left_center is not None and right_center is not None:
            # 차선 중심 계산
            lane_center = (left_center + right_center) / 2
            image_center = width / 2

            # 오프셋 계산 (양수=오른쪽, 음수=왼쪽)
            offset = lane_center - image_center
            offset_ratio = abs(offset) / (width / 2)

            # 임계값 적용
            if abs(offset) < 30:  # 중앙
                return "center", 1.0 - offset_ratio
            elif offset > 0:  # 차선이 오른쪽 → 왼쪽으로 이동
                return "left", min(offset_ratio, 1.0)
            else:  # 차선이 왼쪽 → 오른쪽으로 이동
                return "right", min(offset_ratio, 1.0)

        return "unknown", 0.0

    def _weighted_histogram_method(self, histogram: Dict[str, int]) -> str:
        """
        가중 히스토그램 기반 방향 결정 (이동평균 필터 적용)

        Args:
            histogram: Histogram data

        Returns:
            Command string
        """
        # 이동평균 필터: 현재 히스토그램 버퍼에 추가
        self.histogram_buffer.append(histogram.copy())
        if len(self.histogram_buffer) > self.buffer_size:
            self.histogram_buffer.pop(0)

        # 평균 계산
        avg_left = sum(h["left"] for h in self.histogram_buffer) / len(
            self.histogram_buffer
        )
        avg_center = sum(h["center"] for h in self.histogram_buffer) / len(
            self.histogram_buffer
        )
        avg_right = sum(h["right"] for h in self.histogram_buffer) / len(
            self.histogram_buffer
        )

        # 방향 결정
        diff = abs(avg_left - avg_right)

        # 임계값 체크
        if diff < STEERING_CENTER_THRESHOLD:
            return "center"
        elif avg_left > avg_right:
            return "left"
        else:
            return "right"

    def _obstacle_avoidance_method(self, histogram: Dict[str, int]) -> str:
        """
        장애물 회피 모드 (장애물이 적은 쪽으로)

        Args:
            histogram: Histogram data

        Returns:
            Command string
        """
        left = histogram["left"]
        center = histogram["center"]
        right = histogram["right"]

        # 가장 적은 곳으로 이동 (장애물 회피)
        min_val = min(left, center, right)

        if min_val == center:
            return "center"
        elif min_val == right:
            return "left"  # 오른쪽에 장애물 적음 → 왼쪽으로
        else:
            return "right"  # 왼쪽에 장애물 적음 → 오른쪽으로

    def _detect_horizontal_lane(self, seg_mask: np.ndarray) -> bool:
        """
        90도 도로선 감지 (횡단보도, T자 교차로)

        Args:
            seg_mask: Segmentation mask

        Returns:
            True if horizontal lane detected
        """
        # 도로선만 추출
        lane_mask = (seg_mask == 2).astype(np.uint8) * 255

        # Hough Line Transform으로 수평선 검출
        lines = cv2.HoughLinesP(
            lane_mask,
            rho=1,
            theta=np.pi / 180,
            threshold=50,
            minLineLength=HORIZONTAL_LINE_MIN_LENGTH,
            maxLineGap=10,
        )

        if lines is None:
            return False

        # 수평선 비율 계산
        horizontal_count = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # 각도 계산
            angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            # 수평에 가까우면 (0도 또는 180도)
            if angle < 15 or angle > 165:
                horizontal_count += 1

        horizontal_ratio = horizontal_count / len(lines) if len(lines) > 0 else 0

        return horizontal_ratio > HORIZONTAL_LINE_THRESHOLD

    def _handle_horizontal_lane(self, seg_mask: np.ndarray) -> str:
        """
        90도 도로선 특별 처리

        Args:
            seg_mask: Segmentation mask

        Returns:
            Command string
        """
        height, width = seg_mask.shape

        # 좌우 열린 공간 계산
        left_space = np.sum(seg_mask[:, : width // 3] == 0)
        right_space = np.sum(seg_mask[:, 2 * width // 3 :] == 0)

        # 더 넓은 쪽으로 회전
        if abs(left_space - right_space) < 1000:
            return "stop"  # 불확실하면 정지
        elif left_space > right_space:
            return "left"
        else:
            return "right"

    def _calculate_centroid_x(self, binary_mask: np.ndarray) -> Optional[int]:
        """
        이진 마스크의 X축 무게중심 계산

        Args:
            binary_mask: Binary mask

        Returns:
            X coordinate of centroid or None
        """
        moments = cv2.moments(binary_mask)
        if moments["m00"] > 0:
            cx = int(moments["m10"] / moments["m00"])
            return cx
        return None

    def send_motor_command(self, command: str, confidence: float) -> bool:
        """
        아두이노에 모터 제어 명령 전송

        Args:
            command: Command string (left/right/center/stop)
            confidence: Decision confidence (0.0-1.0)

        Returns:
            True if successful
        """
        # 신뢰도가 너무 낮으면 전송하지 않음
        if confidence < STEERING_MIN_CONFIDENCE and command != "stop":
            print(f"⚠️  Low confidence ({confidence:.2f}), skip command")
            return False

        # 이전 명령과 동일하면 카운트 증가
        if command == self.prev_command:
            self.prev_command_count += 1
        else:
            self.prev_command = command
            self.prev_command_count = 0

        # 통계 업데이트
        self.command_history[command] += 1
        self.total_commands += 1

        try:
            # GET 요청 전송
            url = f"{MOTOR_CONTROL_URL}?cmd={command}"
            response = requests.get(url, timeout=0.5)

            if response.status_code == 200:
                print(f"✅ Motor: {command.upper()} (conf: {confidence:.2f})")
                return True
            else:
                print(f"❌ Motor command failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Motor communication error: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        통계 정보 반환

        Returns:
            Statistics dictionary
        """
        return {
            "total_commands": self.total_commands,
            "command_history": self.command_history.copy(),
            "prev_command": self.prev_command,
            "left_ratio": self.command_history["left"] / max(self.total_commands, 1),
            "right_ratio": self.command_history["right"] / max(self.total_commands, 1),
            "center_ratio": self.command_history["center"]
            / max(self.total_commands, 1),
        }

