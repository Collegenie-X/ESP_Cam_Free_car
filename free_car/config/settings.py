"""
자율주행 시스템 설정 관리
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Settings:
    """시스템 설정 클래스"""

    # ESP32-CAM 설정
    ESP32_IP = os.getenv("ESP32_IP", "192.168.0.65")
    ESP32_PORT = int(os.getenv("ESP32_PORT", "80"))
    ESP32_BASE_URL = f"http://{ESP32_IP}:{ESP32_PORT}"

    # 스트림 설정
    TARGET_FPS = int(os.getenv("TARGET_FPS", "5"))
    STREAM_TIMEOUT = 30
    USE_POLLING_MODE = (
        os.getenv("USE_POLLING_MODE", "True").lower() == "true"
    )  # True: /capture 폴링, False: /stream

    # 차선 추적 설정
    BRIGHTNESS_THRESHOLD = int(os.getenv("BRIGHTNESS_THRESHOLD", "80"))
    MIN_LANE_PIXELS = int(os.getenv("MIN_LANE_PIXELS", "200"))
    MIN_NOISE_AREA = 100
    MIN_ASPECT_RATIO = 2.0
    DEADZONE_RATIO = 0.15
    BIAS_RATIO = 1.3

    # 코너 감지 설정
    CORNER_PIXEL_THRESHOLD_RATIO = 0.78
    CORNER_DEVIATION_THRESHOLD = 0.2

    # ROI 설정 (320x240 기준)
    ROI_BOTTOM = {"y_start": 180, "y_end": 240, "x_start": 0, "x_end": 320}
    ROI_CENTER = {"y_start": 120, "y_end": 180, "x_start": 0, "x_end": 320}

    # 디버그 설정
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
    SHOW_PREVIEW = os.getenv("SHOW_PREVIEW", "True").lower() == "true"

    @classmethod
    def print_settings(cls):
        """현재 설정 출력"""
        print("=" * 60)
        print("🚗 자율주행 시스템 설정")
        print("=" * 60)
        print(f"ESP32-CAM 주소: {cls.ESP32_BASE_URL}")
        print(f"목표 FPS: {cls.TARGET_FPS}")
        print(
            f"영상 모드: {'폴링 (/capture)' if cls.USE_POLLING_MODE else '스트림 (/stream)'}"
        )
        print(f"디버그 모드: {cls.DEBUG_MODE}")
        print(f"화면 미리보기: {cls.SHOW_PREVIEW}")
        print("=" * 60)
