"""
Autonomous Driving Control Service

Processes lane tracking results and converts them into ESP32-CAM motor commands.
"""

import logging
from typing import Dict, Any, Optional
import time
import threading
import requests
from services.esp32_communication_service import ESP32CommunicationService
from ai.core.autonomous_lane_tracker import AutonomousLaneTrackerV2
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class AutonomousDrivingService:
    """Autonomous driving control service class"""

    # Command mapping (Lane tracking → ESP32 commands)
    COMMAND_MAP = {
        "LEFT": "left",
        "RIGHT": "right",
        "CENTER": "center",
        "STOP": "center",  # Changed default stop to center for continuous movement
    }

    # Default command when no lane is detected
    DEFAULT_COMMAND = "CENTER"  # Default to moving forward

    def __init__(
        self,
        esp32_service: ESP32CommunicationService,
        lane_tracker: Optional[AutonomousLaneTrackerV2] = None,
    ):
        """
        Initialize autonomous driving service

        Args:
            esp32_service: ESP32 communication service
            lane_tracker: Lane tracker (creates default if None)
        """
        self.esp32_service = esp32_service
        self.lane_tracker = lane_tracker or AutonomousLaneTrackerV2()
        self.is_running = False
        self.last_command = None
        self.command_history = []  # Keep last 10 commands
        self.stats = {
            "frames_processed": 0,
            "commands_sent": 0,
            "errors": 0,
            "start_time": None,
            "last_frame_time": 0,  # Last frame processing time in ms
        }
        self._polling_thread = None
        self._stop_polling = False
        self.latest_processed_image = None  # Store latest processed image for display
        self.last_image_update_time = 0  # Track last update time
        logger.info("Autonomous driving service initialized")

    def start(self) -> Dict[str, Any]:
        """
        Start autonomous driving (background /capture polling)

        Returns:
            {"success": bool, "message": str}
        """
        if self.is_running:
            return {"success": False, "message": "Autonomous driving already running"}

        self.is_running = True
        self.stats["start_time"] = time.time()
        self.stats["frames_processed"] = 0
        self.stats["commands_sent"] = 0
        self.stats["errors"] = 0
        self.command_history = []
        self._stop_polling = False

        # Start background thread
        self._polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self._polling_thread.start()

        logger.info("Started autonomous driving (background /capture polling)")
        return {"success": True, "message": "Started autonomous driving"}

    def stop(self) -> Dict[str, Any]:
        """
        Stop autonomous driving

        Returns:
            {"success": bool, "message": str}
        """
        if not self.is_running:
            return {"success": False, "message": "Autonomous driving not running"}

        # Stop polling thread first
        self._stop_polling = True
        if self._polling_thread and self._polling_thread.is_alive():
            self._polling_thread.join(timeout=2.0)

        # Send stop command immediately
        try:
            logger.info("🛑 Sending STOP command to ESP32")

            # Send stop command directly
            stop_response = self.esp32_service.send_command("control", {"cmd": "stop"})
            if stop_response.get("success"):
                logger.info("✓ STOP command sent successfully")
                self.last_command = "STOP"
            else:
                logger.error(f"✗ Failed to send stop command: {stop_response}")

            # Verify the stop command
            time.sleep(0.1)  # Brief wait for command to take effect
            verify_response = self.esp32_service.send_command("status")
            if verify_response.get("success"):
                logger.info("✓ Stop command verified")
            else:
                logger.warning("⚠ Could not verify stop command")

        except Exception as e:
            logger.error(f"✗ Error during stop sequence: {e}")

        self.is_running = False
        elapsed = (
            time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        )

        logger.info(
            f"Stopped autonomous driving (frames: {self.stats['frames_processed']}, "
            f"commands: {self.stats['commands_sent']}, "
            f"time: {elapsed:.1f}s)"
        )

        return {
            "success": True,
            "message": "Stopped autonomous driving",
            "stats": self.get_stats(),
        }

    def _polling_loop(self):
        """
        Background loop for /capture polling and lane tracking
        Real-time processing: Skip old frames, process only latest
        """
        logger.info("Starting ULTRA-FAST real-time polling loop")
        base_capture_url = self.esp32_service.get_capture_url()
        TARGET_FPS = 15  # Increased to 15fps for faster response
        FRAME_INTERVAL = 1.0 / TARGET_FPS  # 0.067 seconds
        MIN_COMMAND_INTERVAL = 0.15  # Minimum 150ms between commands

        # Send initial forward command
        self._send_command_to_esp32(self.DEFAULT_COMMAND)

        frame_counter = 0
        last_command_time = 0

        while not self._stop_polling and self.is_running:
            try:
                loop_start = time.time()

                # CRITICAL: Add timestamp to prevent caching!
                capture_url = f"{base_capture_url}?t={int(time.time() * 1000)}"

                # TIMING: Image capture
                capture_start = time.time()
                response = requests.get(
                    capture_url,
                    timeout=1.5,
                    headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
                )
                capture_time = (time.time() - capture_start) * 1000

                if response.status_code != 200:
                    logger.warning(f"Failed to capture image: {response.status_code}")
                    self.stats["errors"] += 1
                    time.sleep(FRAME_INTERVAL)
                    continue

                # TIMING: Image decode
                decode_start = time.time()
                nparr = np.frombuffer(response.content, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                decode_time = (time.time() - decode_start) * 1000

                if image is None or image.size == 0:
                    logger.warning("Failed to decode image")
                    self.stats["errors"] += 1
                    time.sleep(FRAME_INTERVAL)
                    continue

                frame_counter += 1
                self.stats["frames_processed"] = frame_counter

                # TIMING: Lane analysis
                analysis_start = time.time()
                result = self.process_frame(image, send_command=False, debug=False)
                analysis_time = (time.time() - analysis_start) * 1000

                if result.get("success"):
                    # Send command IMMEDIATELY if interval passed
                    current_time = time.time()
                    time_since_last_command = current_time - last_command_time

                    if time_since_last_command >= MIN_COMMAND_INTERVAL:
                        # TIMING: Command send
                        command_start = time.time()
                        sent = self._send_command_to_esp32(result["command"])
                        command_time = (time.time() - command_start) * 1000

                        if sent:
                            last_command_time = current_time
                            self.stats["commands_sent"] += 1

                        # Always update frame time (even if command not sent)
                        total_time = (current_time - loop_start) * 1000
                        self.stats["last_frame_time"] = int(total_time)

                        logger.info(
                            f"[{frame_counter}] {result['command']} "
                            f"L:{result['histogram']['left']} "
                            f"C:{result['histogram']['center']} "
                            f"R:{result['histogram']['right']} "
                            f"| Cap:{capture_time:.0f}ms Dec:{decode_time:.0f}ms "
                            f"Ana:{analysis_time:.0f}ms Cmd:{command_time:.0f}ms "
                            f"TOT={total_time:.0f}ms"
                        )
                    else:
                        # Even if command not sent, update frame time
                        total_time = (time.time() - loop_start) * 1000
                        self.stats["last_frame_time"] = int(total_time)

                    # Debug image every 1 second (non-blocking)
                    if current_time - self.last_image_update_time >= 1.0:
                        try:
                            debug_result = self.lane_tracker.process_frame(
                                image, debug=True
                            )
                            if debug_result.get("debug_images"):
                                processed_image = debug_result["debug_images"].get(
                                    "7_final", image
                                )
                                _, buffer = cv2.imencode(
                                    ".jpg",
                                    processed_image,
                                    [cv2.IMWRITE_JPEG_QUALITY, 75],
                                )
                                self.latest_processed_image = buffer.tobytes()
                                self.last_image_update_time = current_time
                        except Exception as e:
                            logger.debug(f"Debug image failed: {e}")
                else:
                    logger.warning(f"Processing failed: {result.get('error')}")

                # Minimal sleep - prioritize speed
                elapsed = time.time() - loop_start
                if elapsed < FRAME_INTERVAL:
                    time.sleep(FRAME_INTERVAL - elapsed)
                else:
                    # No sleep if already slow - process next immediately
                    if elapsed > 0.15:
                        logger.warning(f"⚠ Slow: {elapsed*1000:.0f}ms")

            except Exception as e:
                logger.error(f"Polling loop error: {e}")
                self.stats["errors"] += 1
                time.sleep(FRAME_INTERVAL)

        logger.info("Polling loop ended")

    def process_frame(
        self, image: np.ndarray, send_command: bool = True, debug: bool = False
    ) -> Dict[str, Any]:
        """
        Process frame and control autonomous driving

        Args:
            image: Camera image (BGR)
            send_command: Whether to send command to ESP32
            debug: Debug mode

        Returns:
            {
                "success": bool,
                "command": str,
                "state": str,
                "histogram": {...},
                "confidence": float,
                "sent_to_esp32": bool,
                "debug_images": {...}  # Only in debug mode
            }
        """
        try:
            # Process lane tracking
            result = self.lane_tracker.process_frame(image, debug=debug)

            # If no command or low confidence, use default command (CENTER)
            if not result.get("command") or result.get("confidence", 0) < 0.3:
                result["command"] = self.DEFAULT_COMMAND
                result["confidence"] = (
                    0.5  # Set moderate confidence for default command
                )

            self.stats["frames_processed"] += 1

            # Send ESP32 command (only when autonomous driving)
            sent_to_esp32 = False
            if self.is_running and send_command and result["command"]:
                sent_to_esp32 = self._send_command_to_esp32(result["command"])

            # Save command history (last 10, without images to avoid JSON serialization issues)
            history_entry = {
                "command": result["command"],
                "confidence": result["confidence"],
                "histogram": result["histogram"],
                "state": result["state"],
                "timestamp": time.time(),
            }

            self.command_history.append(history_entry)
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
            logger.error(f"Frame processing failed: {e}")
            return {"success": False, "error": str(e)}

    def _send_command_to_esp32(self, command: str) -> bool:
        """
        Send command to ESP32 (with duplicate filtering)

        Args:
            command: "LEFT" | "RIGHT" | "CENTER" | "STOP"

        Returns:
            Success status
        """
        # Prevent duplicate commands
        if command == self.last_command:
            logger.debug(f"Ignoring duplicate command: {command}")
            return False

        # Convert to ESP32 command
        esp32_cmd = self.COMMAND_MAP.get(command)
        if not esp32_cmd:
            logger.warning(f"Unknown command: {command}")
            return False

        # Send command
        try:
            logger.info(f"🚗 Sending command to ESP32: {command} → {esp32_cmd}")
            response = self.esp32_service.send_command("control", {"cmd": esp32_cmd})
            if response.get("success"):
                self.last_command = command
                self.stats["commands_sent"] += 1
                logger.info(f"✓ Command sent successfully: {command} → {esp32_cmd}")
                return True
            else:
                logger.warning(f"✗ Command failed: {response}")
                return False

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"✗ ESP32 command error: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get autonomous driving status

        Returns:
            {
                "is_running": bool,
                "last_command": str,
                "state": str,
                "stats": {...},
                "latest_image": str (base64) or None
            }
        """
        import base64

        # Clean command history for JSON serialization (remove any bytes data)
        clean_history = []
        for entry in self.command_history[-5:]:
            clean_entry = {
                "command": entry.get("command"),
                "confidence": entry.get("confidence"),
                "histogram": entry.get("histogram"),
                "state": entry.get("state"),
                "timestamp": entry.get("timestamp"),
            }
            clean_history.append(clean_entry)

        status = {
            "is_running": self.is_running,
            "last_command": self.last_command,
            "state": self.lane_tracker.state,
            "command_history": clean_history,  # Cleaned history without bytes
            "stats": self.get_stats(),
        }

        # Add latest processed image if available
        if self.latest_processed_image:
            status["latest_image"] = base64.b64encode(
                self.latest_processed_image
            ).decode("utf-8")
        else:
            status["latest_image"] = None

        return status

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics

        Returns:
            Statistics dictionary
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
            "last_frame_time": self.stats["last_frame_time"],
        }

    def analyze_single_frame(
        self, image: np.ndarray, draw_overlay: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze single frame (without starting autonomous driving)

        Args:
            image: Camera image
            draw_overlay: Draw overlay

        Returns:
            Analysis result + processed image
        """
        try:
            # Process lane tracking
            result = self.lane_tracker.process_frame(image, debug=True)

            # Create overlay image
            if draw_overlay and "debug_images" in result:
                overlay_image = result["debug_images"].get("7_final", image)
            else:
                overlay_image = image

            # Encode as JPEG
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
            logger.error(f"Single frame analysis failed: {e}")
            return {"success": False, "error": str(e)}
