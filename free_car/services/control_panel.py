"""
Control Panel Service

Real-time ESP32 control using OpenCV trackbar
"""

import cv2
import logging
import requests
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


class ControlPanel:
    """Control Panel Class"""

    def __init__(self, esp32_communication, window_name: str = "Control Panel"):
        """
        Initialize control panel

        Args:
            esp32_communication: ESP32 communication service
            window_name: Control panel window name
        """
        self.esp32 = esp32_communication
        self.window_name = window_name

        # Current values
        self.current_values = {
            "brightness": 2,  # -2 ~ 2 → trackbar: 0~4 (default 0 → trackbar 2)
            "contrast": 2,
            "saturation": 2,
            "led": 0,  # 0: OFF, 1: ON
            "speed": 200,  # 100 ~ 255
        }

        # Button areas (x, y, width, height) - adjusted for new layout
        self.button_areas = {
            "led_toggle": (20, 170, 160, 40),  # y adjusted for panel position
        }

        self._create_panel()
        self._setup_mouse_callback()
        logger.info("Control panel initialized")

    def _create_panel(self):
        """Create control panel window"""
        # Create window
        cv2.namedWindow(self.window_name)

        # Initial panel display
        self._render_panel()

        # Camera settings trackbars
        cv2.createTrackbar(
            "Brightness (-2~2)",
            self.window_name,
            self.current_values["brightness"],  # 0~4
            4,
            self._on_brightness_change,
        )

        cv2.createTrackbar(
            "Contrast (-2~2)",
            self.window_name,
            self.current_values["contrast"],
            4,
            self._on_contrast_change,
        )

        cv2.createTrackbar(
            "Saturation (-2~2)",
            self.window_name,
            self.current_values["saturation"],
            4,
            self._on_saturation_change,
        )

        # Speed control
        cv2.createTrackbar(
            "Speed (100~255)",
            self.window_name,
            self.current_values["speed"],
            255,
            self._on_speed_change,
        )

    def _render_panel(self):
        """Render the panel image"""
        # Create panel image
        panel = np.zeros((250, 700, 3), dtype=np.uint8)

        # Title
        cv2.putText(
            panel,
            "ESP32-CAM Control Panel",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # LED Toggle Button
        bx, by, bw, bh = self.button_areas["led_toggle"]
        led_color = (0, 200, 0) if self.current_values["led"] == 1 else (100, 100, 100)
        cv2.rectangle(panel, (bx, by - 180), (bx + bw, by - 180 + bh), led_color, -1)
        cv2.rectangle(
            panel, (bx, by - 180), (bx + bw, by - 180 + bh), (255, 255, 255), 2
        )

        led_text = "LED: ON" if self.current_values["led"] == 1 else "LED: OFF"
        text_size = cv2.getTextSize(led_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = bx + (bw - text_size[0]) // 2
        text_y = by - 180 + (bh + text_size[1]) // 2
        cv2.putText(
            panel,
            led_text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # Instructions
        y = 220
        cv2.putText(
            panel,
            "Use trackbars above | Click LED button to toggle",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (150, 150, 150),
            1,
        )

        cv2.imshow(self.window_name, panel)

    def _setup_mouse_callback(self):
        """Setup mouse click callback for buttons"""
        cv2.setMouseCallback(self.window_name, self._on_mouse_click)

    def _on_mouse_click(self, event, x, y, flags, param):
        """Handle mouse click events"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check LED toggle button (coordinates match rendered button)
            bx, by, bw, bh = self.button_areas["led_toggle"]
            # Button is rendered at (bx, by-180) in _render_panel
            button_y = by - 180
            if bx <= x <= bx + bw and button_y <= y <= button_y + bh:
                self._toggle_led()

    def _on_brightness_change(self, value: int):
        """Brightness change callback"""
        actual_value = value - 2  # trackbar 0~4 → -2~2
        if self.current_values["brightness"] != value:
            self.current_values["brightness"] = value
            self._send_camera_param("brightness", actual_value)

    def _on_contrast_change(self, value: int):
        """Contrast change callback"""
        actual_value = value - 2
        if self.current_values["contrast"] != value:
            self.current_values["contrast"] = value
            self._send_camera_param("contrast", actual_value)

    def _on_saturation_change(self, value: int):
        """Saturation change callback"""
        actual_value = value - 2
        if self.current_values["saturation"] != value:
            self.current_values["saturation"] = value
            self._send_camera_param("saturation", actual_value)

    def _on_speed_change(self, value: int):
        """Speed change callback"""
        if value < 100:
            value = 100
        if self.current_values["speed"] != value:
            self.current_values["speed"] = value
            logger.info(f"Speed set to: {value}")

    def _toggle_led(self):
        """Toggle LED on/off"""
        self.current_values["led"] = 1 - self.current_values["led"]
        state = "on" if self.current_values["led"] == 1 else "off"
        self._send_led_command(state)
        logger.info(f"LED toggled: {state.upper()}")
        # Re-render panel to show new LED state
        self._render_panel()

    def _send_camera_param(self, param: str, value: int):
        """
        Send camera parameter to ESP32

        Args:
            param: Parameter name (brightness, contrast, saturation)
            value: Value
        """
        try:
            url = f"{self.esp32.base_url}/camera"
            params = {"param": param, "value": value}
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                logger.info(f"Camera {param}={value} OK")
            else:
                logger.warning(
                    f"Camera {param}={value} FAILED (code: {response.status_code})"
                )
        except Exception as e:
            logger.error(f"Camera param error: {e}")

    def _send_led_command(self, state: str):
        """
        Send LED command to ESP32

        Args:
            state: "on" or "off"
        """
        try:
            url = f"{self.esp32.base_url}/led"
            params = {"state": state}
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                logger.info(f"LED {state.upper()} OK")
            else:
                logger.warning(f"LED {state} FAILED (code: {response.status_code})")
        except Exception as e:
            logger.error(f"LED command error: {e}")

    def update_status_display(self, stats: Dict[str, Any]):
        """
        Update status (now just logs to terminal, panel is static)

        Args:
            stats: Statistics information
        """
        # Don't update panel to avoid interfering with trackbars
        # Just log stats periodically
        frames = stats.get("frames_processed", 0)
        if frames % 50 == 0 and frames > 0:
            logger.info(
                f"Stats - Frames: {frames}, Commands: {stats.get('commands_sent', 0)}"
            )

    def destroy(self):
        """Close panel window"""
        try:
            cv2.destroyWindow(self.window_name)
        except:
            pass
