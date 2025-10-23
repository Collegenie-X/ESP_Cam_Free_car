"""
ESP32-CAM Communication Service
Handles HTTP communication with ESP32-CAM
"""

import requests
import logging
from typing import Dict, Optional, Any
import time

logger = logging.getLogger(__name__)


class ESP32CommunicationService:
    """Service class for ESP32-CAM communication"""

    def __init__(self, base_url: str, timeout: int = 2):
        """
        Initialize ESP32 communication service

        Args:
            base_url: ESP32-CAM base URL (e.g., http://192.168.0.65)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.last_command_time = 0
        self.command_interval = (
            0.05  # 50ms minimum interval between commands for smoother control
        )

    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get ESP32-CAM status information

        Returns:
            Status dictionary or None (if failed)
        """
        try:
            response = requests.get(f"{self.base_url}/status", timeout=self.timeout)

            if response.status_code != 200:
                logger.error(f"Status check failed: HTTP {response.status_code}")
                return None

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Status check error: {e}")
            return None

    def send_command(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send command to ESP32-CAM

        Args:
            endpoint: API endpoint path (e.g., /control)
            params: Query parameter dictionary

        Returns:
            Response dictionary (success, data, status_code)
        """
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_command_time
            if time_since_last < self.command_interval:
                sleep_time = self.command_interval - time_since_last
                time.sleep(sleep_time)

            # Ensure endpoint starts with /
            if not endpoint.startswith("/"):
                endpoint = f"/{endpoint}"

            url = f"{self.base_url}{endpoint}"

            # Special handling for stop command
            if params and params.get("cmd") == "stop":
                # Send stop command multiple times to ensure it's received
                for _ in range(3):
                    response = requests.get(url, params=params, timeout=self.timeout)
                    if response.status_code != 200:
                        logger.warning(
                            f"Stop command failed: HTTP {response.status_code}"
                        )
                    time.sleep(0.1)  # 100ms between retries

                # Verify motor status
                status_response = requests.get(
                    f"{self.base_url}/status", timeout=self.timeout
                )
                if status_response.status_code == 200:
                    try:
                        status_data = status_response.json()
                        if status_data.get("motor_status") != "stopped":
                            logger.warning("Motor may not be fully stopped")
                    except:
                        logger.warning("Could not verify motor status")
            else:
                # Normal command handling
                response = requests.get(url, params=params, timeout=self.timeout)

            self.last_command_time = time.time()

            return {
                "success": response.status_code == 200,
                "data": response.text,
                "status_code": response.status_code,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Command failed ({endpoint}): {e}")
            return {"success": False, "error": str(e), "status_code": 0}

    def get_stream_url(self) -> str:
        """
        Get stream URL

        Returns:
            Stream URL string
        """
        return f"{self.base_url}/stream"

    def get_capture_url(self) -> str:
        """
        Get capture URL

        Returns:
            Capture URL string
        """
        return f"{self.base_url}/capture"

    def verify_connection(self) -> bool:
        """
        Verify ESP32-CAM connection

        Returns:
            Connection status
        """
        try:
            response = requests.get(f"{self.base_url}/status", timeout=self.timeout)
            return response.status_code == 200
        except:
            return False

    def verify_motor_stopped(self) -> bool:
        """
        Verify that motors are actually stopped

        Returns:
            True if motors are confirmed stopped
        """
        try:
            response = requests.get(f"{self.base_url}/status", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return data.get("motor_status") == "stopped"
        except:
            pass
        return False

    def emergency_stop(self) -> bool:
        """
        Emergency stop - sends multiple stop commands

        Returns:
            Success status
        """
        success = True
        try:
            # Send stop command multiple times
            for _ in range(3):
                response = self.send_command("control", {"cmd": "stop"})
                if not response.get("success"):
                    success = False
                time.sleep(0.1)  # 100ms between commands

            # Verify stop
            if not self.verify_motor_stopped():
                logger.warning("Could not verify motor stop status")
                success = False

        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            success = False

        return success
