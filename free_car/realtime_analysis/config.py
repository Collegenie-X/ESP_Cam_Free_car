"""
실시간 분석 설정 파일

ESP32-CAM 연결 및 분석 파라미터 설정

세그멘테이션 임계값 조정 가이드:
- BLACK_V_MAX: 검정(도로) 범위 확대 → 값 증가 (기본 60)
- GRAY_V_MIN, GRAY_V_MAX: 회색 도로선 밝기 범위 (기본 50-150)
- GRAY_S_MAX: 회색 채도 최대값, 높일수록 유색 포함 (기본 50)
- RED_H_LOW_MAX: 빨간색 범위1 확대 → 값 증가 (기본 15)
- RED_H_HIGH_MIN: 빨간색 범위2 확대 → 값 감소 (기본 155)
- RED_S_MIN, RED_V_MIN: 낮출수록 어둡거나 연한 빨강 포함 (기본 80)
"""

# ESP32-CAM 연결 설정
ESP32_IP = "192.168.0.65"
ESP32_PORT = 80
CAPTURE_URL = f"http://{ESP32_IP}/capture"

# 성능 설정
TARGET_FPS = 5  # 1초당 5 프레임 (전처리 최적화로 속도 향상)
CAPTURE_TIMEOUT = 2  # 캡처 타임아웃 (초)
CHUNK_SIZE = 8192  # 청크 크기 (bytes)

# UI Settings
WINDOW_NAME = "Autonomous Driving Analysis"

# Lane detection default parameters
DEFAULT_HSV_PARAMS = {
    "white_v_min": 200,  # White V minimum (0-255)
    "white_s_max": 30,  # White S maximum (0-255)
    "min_pixels": 200,  # Minimum pixels (0-5000)
}

# Trackbar ranges
TRACKBAR_RANGES = {
    "white_v_min": (0, 255),
    "white_s_max": (0, 255),
    "min_pixels": (0, 5000),
}

# ROI 설정
ROI_BOTTOM_RATIO = 0.75  # 하단 25% 사용

# 조향 판단 파라미터
DEADZONE_RATIO = 0.15  # 데드존 비율
BIAS_RATIO = 1.3  # 좌우 편향 판단 비율

# 색상 정의 (BGR)
COLORS = {
    "left": (0, 165, 255),  # 주황색
    "right": (255, 0, 255),  # 자홍색
    "center": (0, 255, 0),  # 초록색
    "stop": (0, 0, 255),  # 빨간색
    "white": (255, 255, 255),
    "yellow": (0, 255, 255),
    "gray": (100, 100, 100),
    "light_gray": (200, 200, 200),
}

# Obstacle (non-black) mode settings
# Road is black (dark), non-black is obstacle - choose side with fewer pixels
USE_OBSTACLE_MODE_DEFAULT = True

# Segmentation thresholds (adjustable)
BLACK_V_MIN = 0  # Black minimum V value (도로 검정색 최소값)
BLACK_V_MAX = 100  # Black maximum V value (60→100, 전처리로 밝아진 도로 포함)
BLACK_S_MAX = 120  # Black maximum saturation (80→120, 범위 확대)

GRAY_V_MIN = 50  # Gray road line minimum V value
GRAY_V_MAX = 150  # Gray road line maximum V value
GRAY_S_MAX = 50  # Gray saturation maximum (low saturation = gray)

# Red lane thresholds (wider range)
RED_H_LOW_MIN = 0  # Red hue range 1 minimum
RED_H_LOW_MAX = 15  # Red hue range 1 maximum (increased from 10)
RED_H_HIGH_MIN = 155  # Red hue range 2 minimum (decreased from 160)
RED_H_HIGH_MAX = 180  # Red hue range 2 maximum
RED_S_MIN = 80  # Red saturation minimum (decreased from 100)
RED_V_MIN = 80  # Red value minimum (decreased from 100)

# Keyboard control steps
STEP_WHITE_V = 5
STEP_WHITE_S = 5
STEP_MIN_PIXELS = 20

# Panel display settings
PANEL_MARGIN = 10
PANEL_LINE_HEIGHT = 20
PANEL_BG = (30, 30, 30)
PANEL_BG_ALPHA = 0.7  # 0.0~1.0

# Display settings
IMAGE_DISPLAY_WIDTH = 640  # Display width
IMAGE_DISPLAY_HEIGHT = 480  # Display height
STATUS_BAR_HEIGHT = 100  # Bottom status bar height

# ===== Autonomous Driving Settings =====
# Enable autonomous driving mode
AUTONOMOUS_DRIVING_ENABLED = False  # Toggle with 'A' key

# Motor control endpoint
MOTOR_CONTROL_URL = f"http://{ESP32_IP}/control"

# Steering decision thresholds
STEERING_CENTER_THRESHOLD = 500  # abs(left - right) must exceed this to turn
STEERING_MIN_CONFIDENCE = 0.3  # Minimum confidence to send command

# 90-degree road line detection (horizontal lines)
HORIZONTAL_LINE_THRESHOLD = (
    0.7  # Ratio of horizontal pixels to trigger special handling
)
HORIZONTAL_LINE_MIN_LENGTH = 50  # Minimum line length in pixels

# Image preprocessing for better quality
ENABLE_IMAGE_ENHANCEMENT = True
BRIGHTNESS_BOOST = 15  # Add brightness (20→15, 검정색 보존)
CONTRAST_BOOST = 1.2  # Contrast multiplier (1.3→1.2, 약하게)
ENABLE_CLAHE = True  # Adaptive histogram equalization
ENABLE_SHARPENING = False  # Edge sharpening filter (비활성화 - 속도 향상)
ENABLE_DENOISING = False  # Noise reduction (비활성화 - 가장 느림!)
