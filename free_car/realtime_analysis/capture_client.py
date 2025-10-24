"""
ESP32-CAM 캡처 클라이언트

/capture 엔드포인트를 사용한 이미지 캡처
"""

import time
import requests
import numpy as np
import cv2
from typing import Tuple, Optional

from .config import CAPTURE_URL, CAPTURE_TIMEOUT, CHUNK_SIZE, ESP32_IP


class CaptureClient:
    """ESP32-CAM capture client with control features"""

    def __init__(self):
        """Initialize"""
        # HTTP session (connection reuse)
        self.session = requests.Session()
        self.session.headers.update(
            {"Connection": "keep-alive", "Keep-Alive": "timeout=5, max=100"}
        )

        # Statistics
        self.total_captures = 0
        self.failed_captures = 0

        # ESP32 base URL
        self.base_url = f"http://{ESP32_IP}"

        print(f"\n📡 ESP32 Base URL: {self.base_url}")
        self._test_connection()

    def _test_connection(self):
        """Test ESP32 connection"""
        try:
            print(f"🔍 Testing ESP32 connection...")
            response = self.session.get(f"{self.base_url}/status", timeout=2)
            if response.status_code == 200:
                print(f"✅ ESP32 connected successfully!")
            else:
                print(f"⚠️ ESP32 responded with status {response.status_code}")
        except Exception as e:
            print(f"❌ ESP32 connection failed: {e}")
            print(f"   Make sure ESP32 is running at {self.base_url}")

    def capture_frame(self) -> Tuple[Optional[np.ndarray], float]:
        """
        단일 프레임 캡처

        Returns:
            (이미지 ndarray, 캡처 시간 ms)
            실패 시 (None, 0)
        """
        start_time = time.time()

        try:
            # HTTP 요청
            response = self.session.get(
                CAPTURE_URL, timeout=CAPTURE_TIMEOUT, stream=True
            )

            # Early return: 응답 실패
            if response.status_code != 200:
                self.failed_captures += 1
                return None, 0

            # 청크 단위로 데이터 수신
            content = self._read_response_chunks(response)

            # Early return: 빈 데이터
            if not content:
                self.failed_captures += 1
                return None, 0

            # 이미지 디코딩
            image = self._decode_image(content)

            # Early return: 디코딩 실패
            if image is None:
                self.failed_captures += 1
                return None, 0

            # 성공
            self.total_captures += 1
            capture_time = (time.time() - start_time) * 1000  # ms
            return image, capture_time

        except requests.exceptions.Timeout:
            print(f"⚠️ 캡처 타임아웃 (>{CAPTURE_TIMEOUT}초)")
            self.failed_captures += 1
            return None, 0

        except requests.exceptions.RequestException as e:
            print(f"⚠️ 캡처 실패: {e}")
            self.failed_captures += 1
            return None, 0

        except Exception as e:
            print(f"⚠️ 예상치 못한 오류: {e}")
            self.failed_captures += 1
            return None, 0

    def _read_response_chunks(self, response: requests.Response) -> bytes:
        """
        응답 청크 읽기

        Args:
            response: HTTP 응답 객체

        Returns:
            이미지 데이터 bytes
        """
        content = b""

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                content += chunk

        return content

    def _decode_image(self, content: bytes) -> Optional[np.ndarray]:
        """
        JPEG 데이터를 이미지로 디코딩

        Args:
            content: JPEG 바이트 데이터

        Returns:
            이미지 ndarray (BGR) 또는 None
        """
        try:
            nparr = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image

        except Exception as e:
            print(f"⚠️ 이미지 디코딩 실패: {e}")
            return None

    def reset_session(self):
        """세션 재설정 (연결 문제 시)"""
        self.session = requests.Session()
        self.session.headers.update(
            {"Connection": "keep-alive", "Keep-Alive": "timeout=5, max=100"}
        )
        print("🔄 HTTP 세션 재설정 완료")

    def get_statistics(self) -> dict:
        """
        Get statistics

        Returns:
            Statistics dictionary
        """
        total = self.total_captures + self.failed_captures
        success_rate = (self.total_captures / total * 100) if total > 0 else 0

        return {
            "total_captures": self.total_captures,
            "failed_captures": self.failed_captures,
            "success_rate": success_rate,
        }

    # ----- ESP32 Camera Control -----
    def set_camera_brightness(self, value: int) -> bool:
        """
        Set camera brightness (-2 to 2)

        Args:
            value: Brightness value (-2 to 2)

        Returns:
            Success status
        """
        try:
            url = f"{self.base_url}/camera?param=brightness&value={value}"
            print(f"  → GET {url}")
            response = self.session.get(url, timeout=1)
            print(f"  ← Status: {response.status_code}, Body: {response.text[:100]}")
            return response.status_code == 200
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return False

    def set_camera_contrast(self, value: int) -> bool:
        """
        Set camera contrast (-2 to 2)

        Args:
            value: Contrast value (-2 to 2)

        Returns:
            Success status
        """
        try:
            url = f"{self.base_url}/camera?param=contrast&value={value}"
            print(f"  → GET {url}")
            response = self.session.get(url, timeout=1)
            print(f"  ← Status: {response.status_code}, Body: {response.text[:100]}")
            return response.status_code == 200
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return False

    def set_camera_saturation(self, value: int) -> bool:
        """
        Set camera saturation (-2 to 2)

        Args:
            value: Saturation value (-2 to 2)

        Returns:
            Success status
        """
        try:
            url = f"{self.base_url}/camera?param=saturation&value={value}"
            print(f"  → GET {url}")
            response = self.session.get(url, timeout=1)
            print(f"  ← Status: {response.status_code}, Body: {response.text[:100]}")
            return response.status_code == 200
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return False

    def toggle_led(self, state: int) -> bool:
        """
        Toggle LED on/off

        Args:
            state: 0=OFF, 1=ON

        Returns:
            Success status
        """
        try:
            state_str = "on" if state == 1 else "off"
            url = f"{self.base_url}/led?state={state_str}"
            print(f"  → GET {url}")
            response = self.session.get(url, timeout=1)
            print(f"  ← Status: {response.status_code}, Body: {response.text[:100]}")
            success = response.status_code == 200
            if success:
                print(f"  ✅ LED {state_str.upper()}")
            return success
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return False
