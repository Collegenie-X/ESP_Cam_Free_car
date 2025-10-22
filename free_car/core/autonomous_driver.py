"""
자율주행 드라이버

전체 자율주행 로직을 통합하여 실행합니다.
"""

import cv2
import time
import logging
from typing import Optional
from services.esp32_communication import ESP32Communication
from services.lane_tracking_service import LaneTrackingService
from services.control_panel import ControlPanel
from config.settings import Settings

logger = logging.getLogger(__name__)


class AutonomousDriver:
    """자율주행 드라이버 클래스"""

    def __init__(self, settings: Settings):
        """
        자율주행 드라이버 초기화

        Args:
            settings: 설정 객체
        """
        self.settings = settings

        # 서비스 초기화
        self.esp32 = ESP32Communication(settings.ESP32_BASE_URL, timeout=5)
        self.lane_tracker = LaneTrackingService(
            brightness_threshold=settings.BRIGHTNESS_THRESHOLD,
            min_lane_pixels=settings.MIN_LANE_PIXELS,
            deadzone_ratio=settings.DEADZONE_RATIO,
            bias_ratio=settings.BIAS_RATIO,
        )

        # 제어 패널 (미리보기 모드일 때만)
        self.control_panel = None
        if settings.SHOW_PREVIEW:
            self.control_panel = ControlPanel(self.esp32)

        # 통계
        self.stats = {
            "frames_processed": 0,
            "commands_sent": 0,
            "start_time": None,
        }

        self.is_running = False
        logger.info("자율주행 드라이버 초기화 완료")

    def start(self):
        """자율주행 시작"""
        logger.info("=" * 60)
        logger.info("🚗 자율주행 시작")
        logger.info("=" * 60)

        # ESP32 연결 확인
        if not self.esp32.check_connection():
            logger.error("❌ ESP32-CAM 연결 실패")
            return

        logger.info("✅ ESP32-CAM 연결 성공")

        self.is_running = True
        self.stats["start_time"] = time.time()
        self.stats["frames_processed"] = 0
        self.stats["commands_sent"] = 0

        # 프레임레이트 제한
        target_fps = self.settings.TARGET_FPS
        frame_interval = 1.0 / target_fps
        last_frame_time = 0

        try:
            # 영상 소스 선택 (폴링 or 스트림)
            if self.settings.USE_POLLING_MODE:
                logger.info("📸 폴링 모드 (/capture) 사용")
                video_source = self.esp32.polling_generator(self.settings.TARGET_FPS)
            else:
                logger.info("📹 스트림 모드 (/stream) 사용")
                video_source = self.esp32.stream_generator()

            # 프레임 처리 루프
            frame_count = 0
            for image in video_source:
                frame_count += 1
                if not self.is_running:
                    break

                # FPS 제한
                current_time = time.time()
                if current_time - last_frame_time < frame_interval:
                    continue
                last_frame_time = current_time

                # 방어 코드: 이미지 유효성 체크
                if image is None:
                    logger.warning("빈 프레임 수신 - 건너뜀")
                    continue

                # 차선 추적
                result = self.lane_tracker.process_frame(
                    image, debug=self.settings.DEBUG_MODE
                )

                self.stats["frames_processed"] += 1

                # 명령 전송
                command = result["command"]
                if self.esp32.send_command(command):
                    self.stats["commands_sent"] += 1

                # 디버그 정보 출력
                if frame_count % 10 == 0:
                    self._print_status(result)

                # 화면 미리보기
                if self.settings.SHOW_PREVIEW and "debug_image" in result:
                    cv2.imshow("자율주행", result["debug_image"])

                # 제어 패널 업데이트
                if self.control_panel:
                    self.control_panel.update_status_display(self.stats)

                # 키 입력 처리
                if self.settings.SHOW_PREVIEW:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        logger.info("사용자가 종료 요청")
                        break

        except KeyboardInterrupt:
            logger.info("\n사용자가 중단 (Ctrl+C)")
        except Exception as e:
            logger.error(f"자율주행 오류: {e}", exc_info=True)
        finally:
            self.stop()

    def stop(self):
        """자율주행 중지"""
        if not self.is_running:
            return

        self.is_running = False

        # 정지 명령 전송
        self.esp32.send_command("stop")

        # 통계 출력
        elapsed = (
            time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        )
        fps = self.stats["frames_processed"] / elapsed if elapsed > 0 else 0

        logger.info("=" * 60)
        logger.info("🛑 자율주행 종료")
        logger.info(f"처리된 프레임: {self.stats['frames_processed']}")
        logger.info(f"전송된 명령: {self.stats['commands_sent']}")
        logger.info(f"경과 시간: {elapsed:.1f}초")
        logger.info(f"평균 FPS: {fps:.1f}")
        logger.info("=" * 60)

        # 제어 패널 닫기
        if self.control_panel:
            self.control_panel.destroy()

        # 창 닫기
        if self.settings.SHOW_PREVIEW:
            cv2.destroyAllWindows()

    def _print_status(self, result: dict):
        """
        상태 정보 출력

        Args:
            result: 차선 추적 결과
        """
        elapsed = time.time() - self.stats["start_time"]
        fps = self.stats["frames_processed"] / elapsed if elapsed > 0 else 0

        histogram = result["histogram"]
        command = result["command"]
        confidence = result["confidence"]

        logger.info(
            f"[{elapsed:6.1f}s] FPS: {fps:4.1f} | "
            f"L:{histogram['left']:4d} C:{histogram['center']:4d} R:{histogram['right']:4d} | "
            f"명령: {command.upper():6s} ({confidence*100:5.1f}%)"
        )
