"""
실시간 분석기 메인 클래스

모든 모듈을 통합하여 실시간 분석 실행
"""

import time
import cv2
import numpy as np
from typing import Dict, Any

from .config import (
    TARGET_FPS,
    DEFAULT_HSV_PARAMS,
    ESP32_IP,
    USE_OBSTACLE_MODE_DEFAULT,
)
from .capture_client import CaptureClient
from .image_processor import ImageProcessor
from .lane_detector import LaneDetector
from .ui_components import UIComponents


class RealtimeAnalyzer:
    """실시간 분석기 클래스"""

    def __init__(self):
        """초기화"""
        # 모듈 초기화
        self.capture_client = CaptureClient()
        self.image_processor = ImageProcessor()
        self.lane_detector = LaneDetector()
        self.ui = UIComponents()

        # HSV parameters
        self.hsv_params = DEFAULT_HSV_PARAMS.copy()
        self.obstacle_mode = USE_OBSTACLE_MODE_DEFAULT

        # Camera controls (track previous values to avoid unnecessary ESP32 calls)
        self.camera_controls = {
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
        }
        self.prev_camera_controls = self.camera_controls.copy()

        # LED state (controlled by 'L' key)
        self.led_state = False

        # Statistics
        self.stats = {
            "frames": 0,
            "start_time": time.time(),
        }

        # FPS calculation
        self.fps_counter = 0
        self.fps_start = time.time()
        self.current_fps = 0

        # Frame skip for smoother trackbar (update ESP32 every N frames)
        self.frame_count = 0
        self.esp32_update_interval = 20  # Update ESP32 every 20 frames (~6-7 seconds)

        print("\n🎮 Controls initialized")
        print(f"   - ESP32 update interval: every {self.esp32_update_interval} frames")
        print(f"   - waitKey delay: 30ms for smooth trackbar")

    def setup(self):
        """초기 설정"""
        self._print_header()
        # 단일 창만 사용 (트랙바 제거)
        self._create_ui()

    def _print_header(self):
        """Print header"""
        from .config import (
            BLACK_V_MAX,
            GRAY_V_MIN,
            GRAY_V_MAX,
            RED_H_LOW_MAX,
            RED_H_HIGH_MIN,
        )

        print("=" * 70)
        print("Realtime Autonomous Driving Analysis with ESP32 Control")
        print("=" * 70)
        print(f"ESP32-CAM IP: {ESP32_IP}")
        print(f"Target FPS: {TARGET_FPS}")
        print()
        print("Segmentation Thresholds (adjustable in config.py):")
        print(f"  - Black (road): V < {BLACK_V_MAX}")
        print(f"  - Gray (road line): V={GRAY_V_MIN}-{GRAY_V_MAX}, low saturation")
        print(f"  - Red (lane): H=0-{RED_H_LOW_MAX} & {RED_H_HIGH_MIN}-180")
        print()
        print("Trackbars:")
        print("  Lane Detection:")
        print("    - White V Min, White S Max, Min Pixels")
        print("  Camera Control (ESP32):")
        print("    - Brightness, Contrast, Saturation (-2 to 2)")
        print()
        print("Keyboard:")
        print("  - Press 'o' to toggle Obstacle mode")
        print("  - Press 'L' to toggle LED ON/OFF")
        print("  - Press 'q' or ESC to quit")
        print("=" * 70)
        print()

    def _create_ui(self):
        """Create UI"""
        # Create trackbars
        self.ui.create_trackbars(self.hsv_params)

    def run(self):
        """메인 루프 실행"""
        # FPS 제어
        frame_interval = 1.0 / TARGET_FPS
        last_frame_time = 0

        try:
            while True:
                current_time = time.time()

                # FPS 제한
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.01)
                    continue

                last_frame_time = current_time

                # 키 입력으로 파라미터 업데이트 (ESP32 통신은 주기적으로만)
                self._handle_key_inputs()

                # 프레임 캡처 및 분석
                success = self._process_single_frame()

                # Early return: 캡처 실패
                if not success:
                    time.sleep(0.1)
                    continue

                # FPS 계산
                self._update_fps(current_time)

        except KeyboardInterrupt:
            print("\n\nUser interrupted (Ctrl+C or 'q' key)")

        except Exception as e:
            print(f"\nError occurred: {e}")
            import traceback

            traceback.print_exc()

        finally:
            self._cleanup()

    def _handle_key_inputs(self):
        """Handle keyboard input and update parameters"""
        # Get trackbar values (lane detection - always update, lightweight)
        self.hsv_params = self.ui.get_trackbar_values()

        # Get camera controls (only update ESP32 periodically to avoid lag)
        self.frame_count += 1
        if self.frame_count % self.esp32_update_interval == 0:
            new_camera_controls = self.ui.get_camera_controls()
            # Only update if changed
            if new_camera_controls != self.camera_controls:
                print(f"\n📊 Frame {self.frame_count}: Trackbar values changed")
                print(f"   Old: {self.camera_controls}")
                print(f"   New: {new_camera_controls}")
                self.camera_controls = new_camera_controls
                self._update_esp32_controls()
            else:
                print(f"\n📊 Frame {self.frame_count}: No changes in ESP32 controls")

        # Handle keyboard (use longer wait for smoother trackbar)
        key = cv2.waitKey(30) & 0xFF  # Increased to 30ms for very smooth trackbar
        prev_led = self.led_state
        self.obstacle_mode, self.led_state, quit_flag = self.ui.handle_key(
            key, self.obstacle_mode, self.led_state
        )

        # If LED was toggled, send command immediately
        if self.led_state != prev_led:
            led_value = 1 if self.led_state else 0
            print(f"\n💡 LED toggled: {'ON' if self.led_state else 'OFF'}")
            if self.capture_client.toggle_led(led_value):
                print(f"✅ LED command sent successfully")
            else:
                print(f"❌ Failed to send LED command")

        if quit_flag:
            raise KeyboardInterrupt

    def _update_esp32_controls(self):
        """Update ESP32 camera controls if changed"""
        print("\n🔧 Checking ESP32 controls...")

        # Only send commands if values changed
        if (
            self.camera_controls["brightness"]
            != self.prev_camera_controls["brightness"]
        ):
            print(f"📷 Setting brightness to {self.camera_controls['brightness']}...")
            if self.capture_client.set_camera_brightness(
                self.camera_controls["brightness"]
            ):
                self.prev_camera_controls["brightness"] = self.camera_controls[
                    "brightness"
                ]
                print(f"✅ Brightness → {self.camera_controls['brightness']}")
            else:
                print(f"❌ Failed to set brightness")

        if self.camera_controls["contrast"] != self.prev_camera_controls["contrast"]:
            print(f"📷 Setting contrast to {self.camera_controls['contrast']}...")
            if self.capture_client.set_camera_contrast(
                self.camera_controls["contrast"]
            ):
                self.prev_camera_controls["contrast"] = self.camera_controls["contrast"]
                print(f"✅ Contrast → {self.camera_controls['contrast']}")
            else:
                print(f"❌ Failed to set contrast")

        if (
            self.camera_controls["saturation"]
            != self.prev_camera_controls["saturation"]
        ):
            print(f"📷 Setting saturation to {self.camera_controls['saturation']}...")
            if self.capture_client.set_camera_saturation(
                self.camera_controls["saturation"]
            ):
                self.prev_camera_controls["saturation"] = self.camera_controls[
                    "saturation"
                ]
                print(f"✅ Saturation → {self.camera_controls['saturation']}")
            else:
                print(f"❌ Failed to set saturation")

        # LED is now controlled by 'L' key, not trackbar

    def _process_single_frame(self) -> bool:
        """
        단일 프레임 처리

        Returns:
            성공 여부
        """
        capture_start = time.time()

        # 1. 프레임 캡처
        image, capture_time = self.capture_client.capture_frame()

        # Early return: capture failed
        if image is None:
            print(f"⚠️  Frame {self.stats['frames']}: Capture failed - retrying...")
            return False

        self.stats["frames"] += 1
        self.fps_counter += 1

        # Log every 30 frames
        if self.stats["frames"] % 30 == 0:
            print(f"✅ Frame {self.stats['frames']}: Capture OK ({capture_time:.0f}ms)")

        # 2. 프레임 분석
        result = self._analyze_frame(image)

        # 3. 전체 처리 시간 계산
        total_time = (time.time() - capture_start) * 1000

        # 4. 화면 표시
        self._display_results(image, result, capture_time, total_time)

        return True

    def _analyze_frame(self, image) -> Dict[str, Any]:
        """
        프레임 분석

        Args:
            image: 입력 이미지

        Returns:
            분석 결과 딕셔너리
        """
        process_start = time.time()

        try:
            # 1. 전처리
            blurred = self.image_processor.preprocess_image(image)

            # 2. ROI 추출
            roi, roi_y_start = self.image_processor.extract_roi(blurred)

            # 3. 세그멘테이션 마스크 생성 (0=검정/도로, 1=기타/장애물, 2=차선)
            if self.obstacle_mode:
                # 장애물 모드: 기존 비검정 마스크 사용
                mask = self.image_processor.create_non_black_mask(roi)
            else:
                # 차선 모드: 다층 세그멘테이션 마스크 사용
                mask = self.image_processor.create_segmentation_mask(
                    roi,
                    self.hsv_params["white_v_min"],
                    self.hsv_params["white_s_max"],
                )

            # 4. 히스토그램 계산
            histogram = self.lane_detector.calculate_histogram(mask)

            # 5. 조향 판단
            command, confidence = self.lane_detector.judge_steering(
                histogram, self.hsv_params["min_pixels"], prefer_low=self.obstacle_mode
            )

            process_time = (time.time() - process_start) * 1000

            return {
                "analysis_image": image.copy(),
                "mask": mask,
                "roi_y_start": roi_y_start,
                "histogram": histogram,
                "command": command,
                "confidence": confidence,
                "process_time": process_time,
            }

        except Exception as e:
            print(f"Warning: Analysis failed: {e}")
            h = image.shape[0]
            return {
                "analysis_image": image.copy(),
                "mask": np.zeros((h // 4, image.shape[1]), dtype=np.uint8),
                "roi_y_start": int(h * 0.75),
                "histogram": {"left": 0, "center": 0, "right": 0},
                "command": "stop",
                "confidence": 0.0,
                "process_time": 0,
            }

    def _display_results(
        self,
        original_image,
        result: Dict[str, Any],
        capture_time: float,
        total_time: float,
    ):
        """
        Display results

        Args:
            original_image: Original image
            result: Analysis result
            capture_time: Capture time
            total_time: Total processing time
        """
        # Create complete display (image + status bar)
        complete_display = self.ui.draw_complete_display(
            result["analysis_image"],
            result["mask"],
            result["roi_y_start"],
            result["histogram"],
            result["command"],
            result["confidence"],
            self.current_fps,
            self.obstacle_mode,
            capture_time,
            result["process_time"],
            total_time,
        )

        self.ui.show_display(complete_display)

    def _update_fps(self, current_time: float):
        """FPS 업데이트"""
        if current_time - self.fps_start >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start = current_time

    def _check_exit_key(self) -> bool:
        """Check exit key (not used, handled in _handle_key_inputs)"""
        return False

    def _cleanup(self):
        """Cleanup"""
        # Print statistics
        self._print_statistics()

        # Close UI
        self.ui.close()

        print("\nExiting...")

    def _print_statistics(self):
        """Print statistics"""
        elapsed = time.time() - self.stats["start_time"]
        avg_fps = self.stats["frames"] / elapsed if elapsed > 0 else 0

        # Capture statistics
        capture_stats = self.capture_client.get_statistics()

        print("\n" + "=" * 60)
        print("Statistics")
        print("=" * 60)
        print(f"Processed frames: {self.stats['frames']}")
        print(f"Capture success: {capture_stats['total_captures']}")
        print(f"Capture failed: {capture_stats['failed_captures']}")
        print(f"Success rate: {capture_stats['success_rate']:.1f}%")
        print(f"Elapsed time: {elapsed:.1f}s")
        print(f"Average FPS: {avg_fps:.1f}")
        print("=" * 60)
