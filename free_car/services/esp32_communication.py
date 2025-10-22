"""
ESP32-CAM 통신 서비스

ESP32-CAM과 HTTP 통신을 담당합니다.
"""

import requests
import cv2
import numpy as np
from typing import Optional, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)


class ESP32Communication:
    """ESP32-CAM 통신 클래스"""

    def __init__(self, base_url: str, timeout: int = 5):
        """
        ESP32 통신 서비스 초기화

        Args:
            base_url: ESP32-CAM 베이스 URL (예: http://192.168.0.65)
            timeout: 요청 타임아웃 (초)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.last_command = None
        logger.info(f"ESP32 통신 초기화: {self.base_url}")

    def check_connection(self) -> bool:
        """
        ESP32-CAM 연결 확인

        Returns:
            연결 가능 여부
        """
        try:
            response = requests.get(f"{self.base_url}/status", timeout=self.timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"연결 확인 실패: {e}")
            return False

    def get_stream_url(self) -> str:
        """스트림 URL 반환"""
        return f"{self.base_url}/stream"

    def send_command(self, command: str) -> bool:
        """
        모터 제어 명령 전송

        Args:
            command: "left", "right", "center", "stop"

        Returns:
            전송 성공 여부
        """
        # 중복 명령 방지
        if command == self.last_command:
            return False

        url = f"{self.base_url}/control"
        params = {"cmd": command}

        # 네트워크 환경에 따라 타임아웃/재시도 강화
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.timeout + 2)

                if response.status_code == 200:
                    self.last_command = command
                    logger.info(f"✓ 명령 전송: {command.upper()}")
                    return True

                logger.warning(
                    f"✗ 명령 전송 실패 (코드: {response.status_code}) - 재시도 {attempt}/{max_retries}"
                )

            except requests.exceptions.RequestException as e:
                logger.error(f"✗ 명령 전송 오류: {e} - 재시도 {attempt}/{max_retries}")

        return False

    def get_frame(self) -> Optional[np.ndarray]:
        """
        단일 프레임 가져오기 (캡처)

        Returns:
            이미지 (BGR) 또는 None
        """
        try:
            response = requests.get(f"{self.base_url}/capture", timeout=self.timeout)
            if response.status_code == 200:
                nparr = np.frombuffer(response.content, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return image
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"프레임 가져오기 실패: {e}")
            return None

    def polling_generator(self, fps: int = 5):
        """
        폴링 모드 제너레이터 (/capture 주기적 호출)

        Args:
            fps: 초당 프레임 수

        Yields:
            이미지 (BGR)
        """
        interval = 1.0 / fps
        frame_count = 0

        logger.info(f"폴링 모드 시작: {fps}fps")

        while True:
            start_time = time.time()

            # 프레임 가져오기
            image = self.get_frame()
            if image is not None:
                frame_count += 1
                if frame_count % 10 == 0:
                    logger.info(f"폴링 프레임 수신: {frame_count}")
                yield image
            else:
                logger.warning("빈 프레임 수신")

            # FPS 유지
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stream_generator(self):
        """
        스트림 제너레이터

        Yields:
            이미지 (BGR)
        """
        stream_url = self.get_stream_url()
        logger.info(f"스트림 연결: {stream_url}")

        try:
            # 연결/읽기 타임아웃 분리 (연결 5초, 읽기 5초)
            response = requests.get(
                stream_url,
                stream=True,
                timeout=(5, 5),
                headers={"Accept": "multipart/x-mixed-replace"},
            )
            if response.status_code != 200:
                logger.error(f"스트림 연결 실패: {response.status_code}")
                return

            bytes_data = b""
            last_data_time = time.time()
            frame_counter = 0
            for chunk in response.iter_content(chunk_size=1024):
                if not chunk:
                    # 프레임 데이터가 일정 시간 이상 없으면 재연결
                    if time.time() - last_data_time > 30:
                        logger.warning("스트림 데이터 없음 - 재연결 시도")
                        break
                    continue

                last_data_time = time.time()
                bytes_data += chunk

                # JPEG 이미지 찾기
                a = bytes_data.find(b"\xff\xd8")  # JPEG 시작
                b = bytes_data.find(b"\xff\xd9")  # JPEG 끝

                if a != -1 and b != -1 and b > a:
                    jpg = bytes_data[a : b + 2]
                    bytes_data = bytes_data[b + 2 :]

                    if len(jpg) < 100:  # 너무 작은 JPEG 무시
                        continue

                    # 이미지 디코딩
                    nparr = np.frombuffer(jpg, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if image is not None and image.size > 0:
                        frame_counter += 1
                        if frame_counter % 10 == 0:
                            logger.info(f"스트림 프레임 수신: {frame_counter}")
                        yield image

        except requests.exceptions.RequestException as e:
            logger.error(f"스트림 오류: {e}")
        except Exception as e:
            logger.error(f"스트림 처리 오류: {e}")
