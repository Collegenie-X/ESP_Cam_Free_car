"""
ESP32-CAM 통신 서비스
ESP32-CAM과의 HTTP 통신을 담당하는 비즈니스 로직
"""

import requests
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class ESP32CommunicationService:
    """ESP32-CAM과의 통신을 담당하는 서비스 클래스"""

    def __init__(self, base_url: str, timeout: int = 2):
        """
        ESP32 통신 서비스 초기화

        Args:
            base_url: ESP32-CAM의 베이스 URL (예: http://192.168.0.65)
            timeout: 요청 타임아웃 (초)
        """
        self.base_url = base_url
        self.timeout = timeout

    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        ESP32-CAM 상태 정보 가져오기

        Returns:
            상태 정보 딕셔너리 또는 None (실패 시)
        """
        try:
            response = requests.get(f"{self.base_url}/status", timeout=self.timeout)

            if response.status_code != 200:
                return None

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"상태 조회 실패: {e}")
            return None

    def send_command(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        ESP32-CAM에 명령 전송

        Args:
            endpoint: API 엔드포인트 경로 (예: /control)
            params: 쿼리 파라미터 딕셔너리

        Returns:
            응답 결과 딕셔너리 (success, data, status_code)
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params, timeout=self.timeout)

            return {
                "success": response.status_code == 200,
                "data": response.text,
                "status_code": response.status_code,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"명령 전송 실패 ({endpoint}): {e}")
            return {"success": False, "error": str(e), "status_code": 0}

    def get_stream_url(self) -> str:
        """
        스트림 URL 반환

        Returns:
            스트림 URL 문자열
        """
        return f"{self.base_url}/stream"

    def get_capture_url(self) -> str:
        """
        캡처 URL 반환

        Returns:
            캡처 URL 문자열
        """
        return f"{self.base_url}/capture"
