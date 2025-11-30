"""
라인 트래킹 메인 실행기
ESP32-CAM에서 영상을 받아 라인을 추적하고 제어 명령 전송
"""

import cv2
import sys
import time
import logging
from pathlib import Path

# 부모 디렉토리를 sys.path에 추가 (services 모듈 import용)
sys.path.append(str(Path(__file__).parent.parent))

from line_detector_module import LineDetectorModule
from direction_judge_module import DirectionJudgeModule
from visualization_module import VisualizationModule
from services.esp32_communication import ESP32Communication
import config as cfg

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, cfg.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MainLineTracker:
    """메인 라인 트래킹 시스템"""

    def __init__(self):
        """시스템 초기화"""
        logger.info("=" * 60)
        logger.info("라인 트래킹 시스템 초기화 시작")
        logger.info("=" * 60)

        # 모듈 초기화
        self.line_detector = LineDetectorModule(
            canny_low=cfg.CANNY_LOW_THRESHOLD,
            canny_high=cfg.CANNY_HIGH_THRESHOLD,
            hough_threshold=cfg.HOUGH_THRESHOLD,
            min_line_length=cfg.MIN_LINE_LENGTH,
            max_line_gap=cfg.MAX_LINE_GAP,
            roi_bottom_ratio=cfg.ROI_BOTTOM_RATIO,
        )

        self.direction_judge = DirectionJudgeModule(
            deadzone_threshold=cfg.DEADZONE_THRESHOLD,
            strong_turn_threshold=cfg.STRONG_TURN_THRESHOLD,
        )

        self.visualizer = VisualizationModule()

        # ESP32 통신
        self.esp32_comm = ESP32Communication(
            base_url=cfg.ESP32_BASE_URL, timeout=cfg.COMMAND_TIMEOUT
        )

        # 통계 정보
        self.frame_count = 0
        self.last_command = None
        self.start_time = time.time()

        logger.info("✅ 시스템 초기화 완료")

    def check_connection(self) -> bool:
        """
        ESP32-CAM 연결 확인

        Returns:
            연결 성공 여부
        """
        logger.info("ESP32-CAM 연결 확인 중...")

        if not self.esp32_comm.check_connection():
            logger.error("❌ ESP32-CAM 연결 실패!")
            logger.error(f"URL: {cfg.ESP32_BASE_URL}/status 확인 필요")
            return False

        logger.info("✅ ESP32-CAM 연결 성공")
        return True

    def process_frame(self, frame) -> None:
        """
        프레임 처리 및 명령 전송

        Args:
            frame: 입력 프레임
        """
        # Early return: 빈 프레임
        if frame is None or frame.size == 0:
            logger.warning("⚠️ 빈 프레임 수신")
            return

        self.frame_count += 1
        height, width = frame.shape[:2]
        image_center_x = width // 2

        # 1. 라인 중심점 검출
        line_center_x, processed_image = self.line_detector.detect_line_center(frame)

        # 2. 방향 판단
        if line_center_x is not None:
            command, offset = self.direction_judge.judge_direction(
                line_center_x, image_center_x
            )
        else:
            # 라인을 찾지 못한 경우 정지
            command = "stop"
            offset = 0

        # 3. ESP32에 명령 전송
        if cfg.ENABLE_COMMAND_SEND:
            if command != self.last_command:
                success = self.esp32_comm.send_command(command)
                if success:
                    self.last_command = command

        # 4. 시각화
        if cfg.SHOW_DEBUG_WINDOW:
            roi_start_y = self.line_detector.get_roi_start_y(height)
            debug_frame = self.visualizer.draw_debug_info(
                frame, line_center_x, command, offset, roi_start_y
            )

            # 처리된 이미지도 함께 표시
            if cfg.SHOW_PROCESSED_IMAGE:
                combined = self.visualizer.create_side_by_side_view(
                    debug_frame, processed_image
                )
                cv2.imshow("Line Tracking (Original | Processed)", combined)
            else:
                cv2.imshow("Line Tracking", debug_frame)

        # 5. 통계 로깅 (10프레임마다)
        if self.frame_count % 10 == 0:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            logger.info(
                f"프레임: {self.frame_count} | "
                f"FPS: {fps:.1f} | "
                f"명령: {command.upper()} | "
                f"오프셋: {offset}px"
            )

    def run(self) -> None:
        """
        메인 실행 루프
        """
        # 연결 확인
        if not self.check_connection():
            return

        logger.info("=" * 60)
        logger.info("🚗 라인 트래킹 시작!")
        logger.info("=" * 60)
        logger.info("종료하려면 'q' 키를 누르세요")
        logger.info("")

        try:
            # 폴링 모드로 프레임 수신
            frame_generator = self.esp32_comm.polling_generator(fps=cfg.CAPTURE_FPS)

            for frame in frame_generator:
                # 프레임 처리
                self.process_frame(frame)

                # 'q' 키로 종료
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("사용자 종료 요청")
                    break

        except KeyboardInterrupt:
            logger.info("Ctrl+C 감지 - 종료 중...")

        except Exception as e:
            logger.error(f"⚠️ 오류 발생: {e}", exc_info=True)

        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """정리 작업"""
        logger.info("=" * 60)
        logger.info("시스템 종료 중...")

        # 마지막 정지 명령 전송
        if cfg.ENABLE_COMMAND_SEND:
            logger.info("정지 명령 전송")
            self.esp32_comm.send_command("stop")

        # OpenCV 윈도우 닫기
        cv2.destroyAllWindows()

        # 통계 출력
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0

        logger.info(f"총 프레임: {self.frame_count}")
        logger.info(f"실행 시간: {elapsed:.1f}초")
        logger.info(f"평균 FPS: {avg_fps:.1f}")
        logger.info("=" * 60)
        logger.info("✅ 시스템 종료 완료")
        logger.info("=" * 60)


def main():
    """메인 함수"""
    tracker = MainLineTracker()
    tracker.run()


if __name__ == "__main__":
    main()
