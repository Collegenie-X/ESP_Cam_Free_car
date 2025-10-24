#!/usr/bin/env python3
"""
Autonomous Driving Main Script
완전 자율주행 실행 파일

실행 방법:
python3 autonomous_drive.py

키보드 컨트롤:
- 'A' 키: 자율주행 모드 ON/OFF
- 'O' 키: 장애물 모드 ON/OFF
- 'L' 키: LED ON/OFF
- 'Q' 또는 ESC: 종료
"""

import sys
import time
import cv2
import numpy as np

# 모듈 임포트
from realtime_analysis.config import ESP32_IP, AUTONOMOUS_DRIVING_ENABLED
from realtime_analysis.capture_client import CaptureClient
from realtime_analysis.image_processor import ImageProcessor
from realtime_analysis.lane_detector import LaneDetector
from realtime_analysis.autonomous_driver import AutonomousDriver
from realtime_analysis.ui_components import UIComponents


class AutonomousDrivingSystem:
    """Complete Autonomous Driving System"""

    def __init__(self):
        """Initialize all modules"""
        print("=" * 70)
        print("🚗 ESP32-CAM Autonomous Driving System")
        print("=" * 70)
        print(f"ESP32-CAM IP: {ESP32_IP}")
        print()

        # 모듈 초기화
        self.capture_client = CaptureClient()
        self.image_processor = ImageProcessor()
        self.lane_detector = LaneDetector()
        self.autonomous_driver = AutonomousDriver()
        self.ui = UIComponents()

        # 상태 변수
        self.autonomous_mode = AUTONOMOUS_DRIVING_ENABLED
        self.obstacle_mode = False
        self.led_state = False
        self.debug_mode = False  # 디버그 모드 (세그멘테이션 확인용)

        # HSV 파라미터 (트랙바에서 조정)
        self.hsv_params = {
            "white_v_min": 200,
            "white_s_max": 30,
            "min_pixels": 200,
        }

        # 카메라 컨트롤
        self.camera_controls = {
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
        }
        self.prev_camera_controls = self.camera_controls.copy()

        # FPS 계산
        self.fps_counter = 0
        self.fps_start = time.time()
        self.current_fps = 0

        # 프레임 카운터 (ESP32 업데이트용)
        self.frame_count = 0
        self.esp32_update_interval = 50  # 20 → 50 (트랙바 간섭 감소)

        # 트랙바 업데이트 카운터 (더 자주 읽기)
        self.trackbar_update_interval = 5  # 5프레임마다 트랙바 읽기

        print("✅ All modules initialized")
        print()
        print("⚡ Performance Optimizations:")
        print("  - Denoising: DISABLED (10x faster)")
        print("  - Sharpening: DISABLED (2x faster)")
        print("  - Highlight suppression: FAST mode (blur instead of inpaint)")
        print("  - ESP32 updates: Every 50 frames (reduce interference)")
        print("  - Trackbar updates: Every 5 frames")
        print("  - Expected FPS: 5-7 (vs 1-2 before)")
        self._print_controls()

    def _print_controls(self):
        """Print control instructions"""
        print()
        print("🎮 Controls:")
        print("  - Press 'A' to toggle AUTONOMOUS mode")
        print("  - Press 'O' to toggle OBSTACLE mode")
        print("  - Press 'D' to toggle DEBUG mode (show segmentation)")
        print("  - Press 'L' to toggle LED")
        print("  - Press 'Q' or ESC to quit")
        print()
        print("📊 Trackbars:")
        print("  - White V Min, White S Max, Min Pixels (lane detection)")
        print("  - Brightness, Contrast, Saturation (ESP32 camera)")
        print()
        print("=" * 70)
        print()

    def setup(self):
        """Setup UI"""
        self.ui.create_trackbars(self.hsv_params)

    def run(self):
        """Main loop"""
        print(
            f"🚀 Starting autonomous driving... (Mode: {'ON' if self.autonomous_mode else 'OFF'})"
        )
        print()

        frame_interval = 1.0 / 5  # 5 FPS 목표 (최적화 완료)
        last_frame_time = 0

        try:
            while True:
                current_time = time.time()

                # FPS 제한
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.01)
                    continue

                last_frame_time = current_time

                # 키보드 입력 처리
                quit_flag = self._handle_inputs()
                if quit_flag:
                    break

                # 프레임 처리
                self._process_frame()

                # FPS 계산
                self._update_fps()

        except KeyboardInterrupt:
            print("\n\n⚠️  User interrupted (Ctrl+C)")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self._cleanup()

    def _handle_inputs(self) -> bool:
        """Handle keyboard inputs and trackbars"""
        self.frame_count += 1

        # 트랙바 값 읽기 (5프레임마다)
        if self.frame_count % self.trackbar_update_interval == 0:
            self.hsv_params = self.ui.get_trackbar_values()

        # ESP32 카메라 컨트롤 (50프레임마다 - 간섭 최소화)
        if self.frame_count % self.esp32_update_interval == 0:
            new_controls = self.ui.get_camera_controls()
            if new_controls != self.camera_controls:
                self.camera_controls = new_controls
                self._update_esp32_controls()

        # 키보드 입력 (waitKey 시간 단축 - 반응성 향상)
        key = cv2.waitKey(10) & 0xFF  # 30ms → 10ms

        # 자율주행 모드 토글 ('A' 키)
        if key == ord("a") or key == ord("A"):
            self.autonomous_mode = not self.autonomous_mode
            mode_str = "ON" if self.autonomous_mode else "OFF"
            print(f"\n🚗 Autonomous Mode: {mode_str}")

        # 장애물 모드 토글 ('O' 키)
        if key == ord("o") or key == ord("O"):
            self.obstacle_mode = not self.obstacle_mode
            mode_str = "OBSTACLE" if self.obstacle_mode else "LANE"
            print(f"\n🚧 Detection Mode: {mode_str}")

        # 디버그 모드 토글 ('D' 키)
        if key == ord("d") or key == ord("D"):
            self.debug_mode = not self.debug_mode
            mode_str = "ON (Segmentation visible)" if self.debug_mode else "OFF"
            print(f"\n🔍 Debug Mode: {mode_str}")

        # LED 토글 ('L' 키)
        if key == ord("l") or key == ord("L"):
            self.led_state = not self.led_state
            led_value = 1 if self.led_state else 0
            if self.capture_client.toggle_led(led_value):
                print(f"💡 LED: {'ON' if self.led_state else 'OFF'}")

        # 종료 ('Q' 또는 ESC)
        if key == ord("q") or key == ord("Q") or key == 27:
            return True

        return False

    def _update_esp32_controls(self):
        """Update ESP32 camera controls"""
        # Brightness
        if (
            self.camera_controls["brightness"]
            != self.prev_camera_controls["brightness"]
        ):
            if self.capture_client.set_camera_brightness(
                self.camera_controls["brightness"]
            ):
                self.prev_camera_controls["brightness"] = self.camera_controls[
                    "brightness"
                ]

        # Contrast
        if self.camera_controls["contrast"] != self.prev_camera_controls["contrast"]:
            if self.capture_client.set_camera_contrast(
                self.camera_controls["contrast"]
            ):
                self.prev_camera_controls["contrast"] = self.camera_controls["contrast"]

        # Saturation
        if (
            self.camera_controls["saturation"]
            != self.prev_camera_controls["saturation"]
        ):
            if self.capture_client.set_camera_saturation(
                self.camera_controls["saturation"]
            ):
                self.prev_camera_controls["saturation"] = self.camera_controls[
                    "saturation"
                ]

    def _process_frame(self):
        """Process single frame"""
        capture_start = time.time()

        # 1. 이미지 캡처
        image, capture_time = self.capture_client.capture_frame()
        if image is None:
            return

        # 2. 이미지 전처리 (밝기 향상, 노이즈 제거, 햇빛 반사 제거!)
        enhanced = self.image_processor.preprocess_image(image)

        # 3. ROI 추출
        roi, roi_y_start = self.image_processor.extract_roi(enhanced)

        # 4. 세그멘테이션 (0=도로, 1=장애물, 2=도로선)
        seg_mask = self.image_processor.create_segmentation_mask(
            roi, self.hsv_params["white_v_min"], self.hsv_params["white_s_max"]
        )

        # 5. 히스토그램 계산 (다층 ROI 가중치, 도로선 x5)
        histogram = self.lane_detector.calculate_histogram(seg_mask)

        # 6. 방향 결정
        if self.autonomous_mode:
            # 하이브리드 자율주행 알고리즘
            command, confidence, method = (
                self.autonomous_driver.decide_direction_hybrid(seg_mask, histogram, 0.8)
            )
            # 모터 제어 명령 전송
            self.autonomous_driver.send_motor_command(command, confidence)
        else:
            # 수동 모드: 단순 히스토그램 방향만 표시
            command, confidence = self.lane_detector.judge_steering(
                histogram, self.hsv_params["min_pixels"], prefer_low=self.obstacle_mode
            )
            method = "manual"

        # 7. 처리 시간 계산
        total_time = (time.time() - capture_start) * 1000
        process_time = total_time - capture_time

        # 8. 디버그 모드: 세그멘테이션 결과 시각화
        if self.debug_mode:
            # 세그멘테이션 마스크를 컬러로 변환
            h, w = seg_mask.shape
            seg_colored = np.zeros((h, w, 3), dtype=np.uint8)
            seg_colored[seg_mask == 0] = [50, 50, 50]  # 검정(도로) → 회색
            seg_colored[seg_mask == 1] = [0, 255, 255]  # 장애물 → 노란색
            seg_colored[seg_mask == 2] = [0, 0, 255]  # 도로선 → 빨간색

            # 원본 크기로 복원
            debug_image = np.zeros_like(enhanced)
            debug_image[roi_y_start : roi_y_start + h, 0:w] = seg_colored

            # 통계 텍스트 추가
            black_pixels = np.sum(seg_mask == 0)
            obstacle_pixels = np.sum(seg_mask == 1)
            lane_pixels = np.sum(seg_mask == 2)
            total_pixels = seg_mask.size

            cv2.putText(
                debug_image,
                f"Black(road): {black_pixels} ({black_pixels/total_pixels*100:.1f}%)",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                debug_image,
                f"Obstacle: {obstacle_pixels} ({obstacle_pixels/total_pixels*100:.1f}%)",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                debug_image,
                f"Lane: {lane_pixels} ({lane_pixels/total_pixels*100:.1f}%)",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

            display_image = self.ui.draw_complete_display(
                debug_image,  # 디버그 이미지 사용
                seg_mask,
                roi_y_start,
                histogram,
                command,
                confidence,
                self.current_fps,
                self.obstacle_mode,
                capture_time,
                process_time,
                total_time,
            )
        else:
            # 일반 모드
            display_image = self.ui.draw_complete_display(
                enhanced,
                seg_mask,
                roi_y_start,
                histogram,
                command,
                confidence,
                self.current_fps,
                self.obstacle_mode,
                capture_time,
                process_time,
                total_time,
            )

        # 자율주행 모드 표시 추가
        if self.autonomous_mode:
            cv2.putText(
                display_image,
                "[AUTO]",
                (10, display_image.shape[0] - 120),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                (0, 255, 0),  # 녹색
                2,
            )
        else:
            cv2.putText(
                display_image,
                "[MANUAL]",
                (10, display_image.shape[0] - 120),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                (100, 100, 100),  # 회색
                2,
            )

        self.ui.show_display(display_image)

        self.fps_counter += 1

    def _update_fps(self):
        """Update FPS counter"""
        elapsed = time.time() - self.fps_start
        if elapsed > 1.0:
            self.current_fps = int(self.fps_counter / elapsed)
            self.fps_counter = 0
            self.fps_start = time.time()

    def _cleanup(self):
        """Cleanup and show statistics"""
        print("\n\n" + "=" * 70)
        print("🏁 Shutting down...")
        print("=" * 70)

        # 자율주행 통계
        if self.autonomous_mode:
            stats = self.autonomous_driver.get_statistics()
            print("\n📊 Autonomous Driving Statistics:")
            print(f"  Total commands: {stats['total_commands']}")
            print(
                f"  Left: {stats['command_history']['left']} ({stats['left_ratio']*100:.1f}%)"
            )
            print(
                f"  Center: {stats['command_history']['center']} ({stats['center_ratio']*100:.1f}%)"
            )
            print(
                f"  Right: {stats['command_history']['right']} ({stats['right_ratio']*100:.1f}%)"
            )
            print(f"  Stop: {stats['command_history']['stop']}")

        # 캡처 통계
        capture_stats = self.capture_client.get_statistics()
        print("\n📸 Capture Statistics:")
        print(f"  Success: {capture_stats['success_count']}")
        print(f"  Failed: {capture_stats['failed_count']}")
        if capture_stats["total_time"] > 0:
            print(
                f"  Average FPS: {capture_stats['success_count'] / capture_stats['total_time']:.2f}"
            )

        self.ui.close()
        print("\n✅ Clean shutdown complete")
        print("=" * 70)


def main():
    """Main entry point"""
    system = AutonomousDrivingSystem()
    system.setup()
    system.run()


if __name__ == "__main__":
    main()
