"""
UI Components Module - Clean Separated Layout
Top: Trackbars | Middle: Image | Bottom: Status Panel
"""

import cv2
import numpy as np
from typing import Dict, Tuple

from .config import (
    WINDOW_NAME,
    COLORS,
    TRACKBAR_RANGES,
    IMAGE_DISPLAY_WIDTH,
    IMAGE_DISPLAY_HEIGHT,
    STATUS_BAR_HEIGHT,
)


class UIComponents:
    """UI Components Class with Separated Layout"""

    def __init__(self):
        """Initialize"""
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(
            WINDOW_NAME, IMAGE_DISPLAY_WIDTH, IMAGE_DISPLAY_HEIGHT + STATUS_BAR_HEIGHT
        )

    # ----- Trackbars (Top - handled by OpenCV) -----
    def create_trackbars(self, initial_values: Dict[str, int]):
        """Create trackbars at the top of window"""
        # Lane detection parameters
        cv2.createTrackbar(
            "White V Min",
            WINDOW_NAME,
            initial_values["white_v_min"],
            TRACKBAR_RANGES["white_v_min"][1],
            lambda x: None,
        )
        cv2.createTrackbar(
            "White S Max",
            WINDOW_NAME,
            initial_values["white_s_max"],
            TRACKBAR_RANGES["white_s_max"][1],
            lambda x: None,
        )
        cv2.createTrackbar(
            "Min Pixels",
            WINDOW_NAME,
            initial_values["min_pixels"],
            TRACKBAR_RANGES["min_pixels"][1],
            lambda x: None,
        )

        # Camera controls (-2 to 2 → 0 to 4 scale)
        cv2.createTrackbar(
            "Brightness   ",  # Extra spaces for right margin
            WINDOW_NAME,
            2,  # Default: 0 (middle)
            4,
            lambda x: None,
        )
        cv2.createTrackbar(
            "Contrast     ",  # Extra spaces for right margin
            WINDOW_NAME,
            2,  # Default: 0 (middle)
            4,
            lambda x: None,
        )
        cv2.createTrackbar(
            "Saturation   ",  # Extra spaces for right margin
            WINDOW_NAME,
            2,  # Default: 0 (middle)
            4,
            lambda x: None,
        )
        # LED control removed - use 'L' key to toggle

    def get_trackbar_values(self) -> Dict[str, int]:
        """Get current trackbar values"""
        return {
            "white_v_min": cv2.getTrackbarPos("White V Min", WINDOW_NAME),
            "white_s_max": cv2.getTrackbarPos("White S Max", WINDOW_NAME),
            "min_pixels": cv2.getTrackbarPos("Min Pixels", WINDOW_NAME),
        }

    def get_camera_controls(self) -> Dict[str, int]:
        """Get camera control values (LED controlled by 'L' key, not included here)"""
        return {
            "brightness": cv2.getTrackbarPos("Brightness   ", WINDOW_NAME)
            - 2,  # 0-4 → -2 to 2
            "contrast": cv2.getTrackbarPos("Contrast     ", WINDOW_NAME) - 2,
            "saturation": cv2.getTrackbarPos("Saturation   ", WINDOW_NAME) - 2,
        }

    # ----- Keyboard Input -----
    def handle_key(
        self, key: int, obstacle_mode: bool, led_state: bool
    ) -> Tuple[bool, bool, bool]:
        """
        Handle keyboard input

        Returns:
            (obstacle_mode, led_state, quit_flag)
        """
        quit_flag = False
        led_toggle = False

        if key == ord("q") or key == 27:  # 'q' or ESC
            quit_flag = True

        # Toggle obstacle mode
        if key == ord("o") or key == ord("O"):
            obstacle_mode = not obstacle_mode

        # Toggle LED
        if key == ord("l") or key == ord("L"):
            led_state = not led_state
            led_toggle = True

        return obstacle_mode, led_state, quit_flag

    # ----- Main Display Function -----
    def draw_complete_display(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        roi_y_start: int,
        histogram: Dict[str, int],
        command: str,
        confidence: float,
        fps: int,
        obstacle_mode: bool,
        capture_time: float,
        process_time: float,
        total_time: float,
    ) -> np.ndarray:
        """
        Create complete display with separated sections

        Layout:
        ┌─────────────────────────────┐
        │  TOP: Trackbars (OpenCV)    │ <- Handled by OpenCV
        ├─────────────────────────────┤
        │  MIDDLE: Image + Analysis   │ <- 640x480
        ├─────────────────────────────┤
        │  BOTTOM: Status Panel       │ <- 640x100
        └─────────────────────────────┘

        Returns:
            Complete display image (640x580)
        """
        # 1. Resize image to display size
        image_resized = cv2.resize(image, (IMAGE_DISPLAY_WIDTH, IMAGE_DISPLAY_HEIGHT))
        mask_resized = cv2.resize(
            mask,
            (IMAGE_DISPLAY_WIDTH, mask.shape[0] * IMAGE_DISPLAY_WIDTH // mask.shape[1]),
        )

        # Adjust ROI for resized image
        scale_y = IMAGE_DISPLAY_HEIGHT / image.shape[0]
        roi_y_resized = int(roi_y_start * scale_y)

        # 2. Draw analysis on image (MIDDLE section)
        middle_section = self._draw_image_analysis(
            image_resized,
            mask_resized,
            roi_y_resized,
            command,
            fps,
            obstacle_mode,
        )

        # 3. Create status panel (BOTTOM section)
        bottom_section = self._create_status_panel(
            histogram,
            confidence,
            capture_time,
            process_time,
            total_time,
        )

        # 4. Combine MIDDLE + BOTTOM
        complete_display = np.vstack([middle_section, bottom_section])

        return complete_display

    # ----- Middle Section: Image Analysis -----
    def _draw_image_analysis(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        roi_y: int,
        command: str,
        fps: int,
        obstacle_mode: bool,
    ) -> np.ndarray:
        """
        Draw analysis overlay on image (MIDDLE section)

        Returns:
            Image with overlays (640x480)
        """
        overlay = image.copy()
        h, w = overlay.shape[:2]

        # 1. Mask overlay in ROI
        if roi_y > 0 and roi_y < h:
            mask_h = min(mask.shape[0], h - roi_y)

            # 세그멘테이션 마스크인 경우 (0,1,2 값) → 3가지 색깔로 명확하게 구분
            if mask.max() <= 2:
                mask_colored = np.zeros((mask_h, w, 3), dtype=np.uint8)
                # 0=검정(도로) → 어두운 회색 (잘 보이도록)
                mask_colored[mask[:mask_h] == 0] = [50, 50, 50]
                # 1=기타(장애물) → 노란색 (경고색)
                mask_colored[mask[:mask_h] == 1] = [0, 255, 255]
                # 2=도로선(차선) → 빨간색 (강조)
                mask_colored[mask[:mask_h] == 2] = [0, 0, 255]
            else:
                # 이진 마스크 (기존 방식)
                mask_colored = cv2.cvtColor(mask[:mask_h], cv2.COLOR_GRAY2BGR)

            overlay[roi_y : roi_y + mask_h, 0:w] = cv2.addWeighted(
                overlay[roi_y : roi_y + mask_h, 0:w], 0.65, mask_colored, 0.35, 0
            )

        # 2. ROI boundary line
        if 0 < roi_y < h:
            cv2.line(overlay, (0, roi_y), (w, roi_y), COLORS["yellow"], 2)

            # 3. Division lines (left/center/right)
            third = w // 3
            cv2.line(overlay, (third, roi_y), (third, h), COLORS["gray"], 1)
            cv2.line(overlay, (third * 2, roi_y), (third * 2, h), COLORS["gray"], 1)

        # 4. Top-left: Command (large, clear)
        self._draw_command(overlay, command, 20, 50)

        # 5. Top-center: FPS (large)
        self._draw_fps(overlay, fps, w // 2, 50)

        # 6. Top-right: Mode
        self._draw_mode(overlay, obstacle_mode, w - 10, 50)

        return overlay

    def _draw_command(self, image: np.ndarray, command: str, x: int, y: int):
        """Draw steering command - LEFT SIDE"""
        text = f"{command.upper()}"
        color = COLORS.get(command, COLORS["white"])

        # Draw with shadow for better visibility
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_DUPLEX,
            1.5,
            (0, 0, 0),  # Shadow
            5,
        )
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_DUPLEX,
            1.5,
            color,
            2,
        )

    def _draw_fps(self, image: np.ndarray, fps: int, center_x: int, y: int):
        """Draw FPS centered - MIDDLE"""
        text = f"FPS: {fps}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 1.2, 2)[0]
        x = center_x - text_size[0] // 2

        # Draw with shadow
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            (0, 0, 0),  # Shadow
            4,
        )
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            COLORS["center"],
            2,
        )

    def _draw_mode(self, image: np.ndarray, obstacle_mode: bool, right_x: int, y: int):
        """Draw mode indicator - RIGHT SIDE"""
        text = "[OBST]" if obstacle_mode else "[LANE]"
        color = (0, 140, 255) if obstacle_mode else (0, 255, 100)

        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.9, 2)[0]
        x = right_x - text_size[0] - 10  # Add margin

        # Draw with shadow
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
            (0, 0, 0),  # Shadow
            4,
        )
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
            color,
            2,
        )

    # ----- Bottom Section: Status Panel -----
    def _create_status_panel(
        self,
        histogram: Dict[str, int],
        confidence: float,
        capture_time: float,
        process_time: float,
        total_time: float,
    ) -> np.ndarray:
        """
        Create status panel (BOTTOM section)

        Returns:
            Status panel image (640x100)
        """
        # Create dark background
        panel = np.zeros((STATUS_BAR_HEIGHT, IMAGE_DISPLAY_WIDTH, 3), dtype=np.uint8)
        panel[:] = (30, 30, 30)

        # Title bar
        cv2.rectangle(panel, (0, 0), (IMAGE_DISPLAY_WIDTH, 30), (50, 50, 50), -1)
        cv2.putText(
            panel,
            "=== STATUS ===",
            (IMAGE_DISPLAY_WIDTH // 2 - 80, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            COLORS["yellow"],
            2,
        )

        # Line 1: Histogram (large, clear with proper spacing)
        hist_text = f"L: {histogram['left']:6d}     C: {histogram['center']:6d}     R: {histogram['right']:6d}"
        cv2.putText(
            panel,
            hist_text,
            (15, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            COLORS["white"],
            2,
        )

        # Line 2: Confidence (left side)
        conf_text = f"Confidence: {confidence*100:5.1f}%"
        cv2.putText(
            panel,
            conf_text,
            (15, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            COLORS["white"],
            1,
        )

        # Timing (right side, separated)
        timing_text = f"Cap: {capture_time:4.0f}ms  |  Proc: {process_time:3.0f}ms  |  Tot: {total_time:4.0f}ms"
        cv2.putText(
            panel,
            timing_text,
            (IMAGE_DISPLAY_WIDTH - 450, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            COLORS["light_gray"],
            1,
        )

        return panel

    # ----- Window Management -----
    def show_display(self, image: np.ndarray):
        """Show complete display"""
        cv2.imshow(WINDOW_NAME, image)

    def close(self):
        """Close window"""
        cv2.destroyAllWindows()
