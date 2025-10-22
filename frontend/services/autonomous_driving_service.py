"""
자율주행 제어 서비스

차선 추적 결과를 ESP32-CAM 모터 명령으로 변환하고 실행합니다.
"""

import logging
from typing import Dict, Any, Optional
import time
from services.esp32_communication_service import ESP32CommunicationService
from ai.core.autonomous_lane_tracker import AutonomousLaneTrackerV2
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class AutonomousDrivingService:
    """자율주행 제어 서비스 클래스"""

    # 명령어 매핑 (차선 추적 → ESP32 명령)
    COMMAND_MAP = {
        "LEFT": "left",
        "RIGHT": "right",
        "CENTER": "center",
        "STOP": "stop",
    }

    def __init__(
        self,
        esp32_service: ESP32CommunicationService,
        lane_tracker: Optional[AutonomousLaneTrackerV2] = None,
    ):
        """
        자율주행 서비스 초기화

        Args:
            esp32_service: ESP32 통신 서비스
            lane_tracker: 차선 추적기 (None이면 기본 생성)
        """
        self.esp32_service = esp32_service
        self.lane_tracker = lane_tracker or AutonomousLaneTrackerV2()
        self.is_running = False
        self.last_command = None
        self.command_history = []  # 최근 10개 명령 저장
        self.stats = {
            "frames_processed": 0,
            "commands_sent": 0,
            "errors": 0,
            "start_time": None,
        }
        logger.info("자율주행 서비스 초기화 완료")

    def start(self) -> Dict[str, Any]:
        """
        자율주행 시작

        Returns:
            {"success": bool, "message": str}
        """
        if self.is_running:
            return {"success": False, "message": "이미 자율주행 중입니다"}

        self.is_running = True
        self.stats["start_time"] = time.time()
        self.stats["frames_processed"] = 0
        self.stats["commands_sent"] = 0
        self.stats["errors"] = 0
        self.command_history = []

        logger.info("자율주행 시작")
        return {"success": True, "message": "자율주행을 시작했습니다"}

    def stop(self) -> Dict[str, Any]:
        """
        자율주행 중지

        Returns:
            {"success": bool, "message": str}
        """
        if not self.is_running:
            return {"success": False, "message": "자율주행이 실행 중이 아닙니다"}

        # 모터 정지 명령 전송
        self.esp32_service.send_command("control", {"cmd": "stop"})

        self.is_running = False
        elapsed = (
            time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        )

        logger.info(
            f"자율주행 중지 (처리 프레임: {self.stats['frames_processed']}, "
            f"명령 전송: {self.stats['commands_sent']}, "
            f"경과 시간: {elapsed:.1f}초)"
        )

        return {
            "success": True,
            "message": "자율주행을 중지했습니다",
            "stats": self.get_stats(),
        }

    def process_frame(
        self, image: np.ndarray, send_command: bool = True, debug: bool = False
    ) -> Dict[str, Any]:
        """
        프레임 처리 및 자율주행 제어

        Args:
            image: 카메라 이미지 (BGR)
            send_command: ESP32에 명령 전송 여부
            debug: 디버그 모드

        Returns:
            {
                "success": bool,
                "command": str,
                "state": str,
                "histogram": {...},
                "confidence": float,
                "sent_to_esp32": bool,
                "debug_images": {...}  # debug=True일 때만
            }
        """
        try:
            # 차선 추적 처리
            result = self.lane_tracker.process_frame(image, debug=debug)

            self.stats["frames_processed"] += 1

            # ESP32 명령 전송 (자율주행 중일 때만)
            sent_to_esp32 = False
            if self.is_running and send_command and result["command"]:
                sent_to_esp32 = self._send_command_to_esp32(result["command"])

            # 명령 히스토리 저장 (최근 10개, 히스토그램 포함)
            self.command_history.append(
                {
                    "command": result["command"],
                    "confidence": result["confidence"],
                    "histogram": result["histogram"],
                    "state": result["state"],
                    "timestamp": time.time(),
                }
            )
            if len(self.command_history) > 10:
                self.command_history.pop(0)

            return {
                "success": True,
                "command": result["command"],
                "state": result["state"],
                "histogram": result["histogram"],
                "confidence": result["confidence"],
                "sent_to_esp32": sent_to_esp32,
                "debug_images": result.get("debug_images", {}),
            }

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"프레임 처리 실패: {e}")
            return {"success": False, "error": str(e)}

    def _send_command_to_esp32(self, command: str) -> bool:
        """
        ESP32에 명령 전송 (중복 명령 필터링)

        Args:
            command: "LEFT" | "RIGHT" | "CENTER" | "STOP"

        Returns:
            전송 성공 여부
        """
        # 동일 명령 중복 전송 방지
        if command == self.last_command:
            logger.debug(f"중복 명령 무시: {command}")
            return False

        # ESP32 명령으로 변환
        esp32_cmd = self.COMMAND_MAP.get(command)
        if not esp32_cmd:
            logger.warning(f"알 수 없는 명령: {command}")
            return False

        # 명령 전송
        try:
            logger.info(f"🚗 ESP32로 명령 전송 시도: {command} → {esp32_cmd}")
            response = self.esp32_service.send_command("/control", {"cmd": esp32_cmd})
            if response.get("success"):
                self.last_command = command
                self.stats["commands_sent"] += 1
                logger.info(f"✓ 명령 전송 성공: {command} → {esp32_cmd}")
                return True
            else:
                logger.warning(f"✗ 명령 전송 실패: {response}")
                return False

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"✗ ESP32 명령 전송 오류: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        자율주행 상태 조회

        Returns:
            {
                "is_running": bool,
                "last_command": str,
                "state": str,
                "stats": {...}
            }
        """
        return {
            "is_running": self.is_running,
            "last_command": self.last_command,
            "state": self.lane_tracker.state,
            "command_history": self.command_history[-5:],  # 최근 5개
            "stats": self.get_stats(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        통계 정보 조회

        Returns:
            통계 딕셔너리
        """
        elapsed = (
            time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        )
        fps = self.stats["frames_processed"] / elapsed if elapsed > 0 else 0

        return {
            "frames_processed": self.stats["frames_processed"],
            "commands_sent": self.stats["commands_sent"],
            "errors": self.stats["errors"],
            "elapsed_time": f"{elapsed:.1f}s",
            "fps": f"{fps:.1f}",
        }

    def analyze_single_frame(
        self, image: np.ndarray, draw_overlay: bool = True
    ) -> Dict[str, Any]:
        """
        단일 프레임 분석 (자율주행 시작 없이)

        Args:
            image: 카메라 이미지
            draw_overlay: 오버레이 그리기

        Returns:
            분석 결과 + 처리된 이미지
        """
        try:
            # 차선 추적
            result = self.lane_tracker.process_frame(image, debug=True)

            # 오버레이 이미지 생성
            if draw_overlay and "debug_images" in result:
                overlay_image = result["debug_images"].get("7_final", image)
            else:
                overlay_image = image

            # JPEG로 인코딩
            _, buffer = cv2.imencode(
                ".jpg", overlay_image, [cv2.IMWRITE_JPEG_QUALITY, 85]
            )
            image_base64 = buffer.tobytes()

            return {
                "success": True,
                "command": result["command"],
                "state": result["state"],
                "histogram": result["histogram"],
                "confidence": result["confidence"],
                "image": image_base64,
                "debug_images": result.get("debug_images", {}),
            }

        except Exception as e:
            logger.error(f"단일 프레임 분석 실패: {e}")
            return {"success": False, "error": str(e)}
