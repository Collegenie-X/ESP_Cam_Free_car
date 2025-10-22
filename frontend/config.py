"""
ESP32-CAM 자율주행차 모니터링 시스템 설정 파일
모든 설정값과 상수를 중앙에서 관리
"""

# ==================== 네트워크 설정 ====================

# ESP32-CAM IP 주소 (환경변수로 덮어쓰기 가능)
DEFAULT_ESP32_IP = "192.168.0.65"

# Flask 서버 설정
DEFAULT_SERVER_PORT = 5000
SERVER_HOST = "0.0.0.0"
DEBUG_MODE = True

# 요청 타임아웃 (초)
REQUEST_TIMEOUT = 2
STREAM_TIMEOUT = 10


# ==================== API 엔드포인트 ====================

# ESP32-CAM API 엔드포인트
API_ENDPOINTS = {
    "stream": "/stream",  # 영상 스트리밍
    "capture": "/capture",  # 단일 이미지 캡처
    "control": "/control",  # 모터 제어
    "led": "/led",  # LED 제어
    "speed": "/speed",  # 속도 제어
    "camera": "/camera",  # 카메라 설정
    "status": "/status",  # 상태 확인
}


# ==================== 모터 제어 설정 ====================

# 모터 명령어
MOTOR_COMMANDS = {
    "left": "좌회전",
    "right": "우회전",
    "center": "전진",
    "stop": "정지",
}

# 속도 조절 설정
SPEED_MIN = 0
SPEED_MAX = 255
SPEED_DEFAULT_STEP = 10
SPEED_STEP_MIN = 1
SPEED_STEP_MAX = 100


# ==================== LED 설정 ====================

# LED 상태
LED_STATES = {
    "on": "켜기",
    "off": "끄기",
    "toggle": "토글",
}


# ==================== 카메라 설정 ====================

# 카메라 파라미터 범위 (ESP32-CAM OV2640 기준)
# 주의: 범위를 넘어가는 값은 자동으로 제한됩니다
CAMERA_PARAMS = {
    "brightness": {
        "min": -2,  # ESP32-CAM 실제 지원 범위 확장
        "max": 2,  # -3 ~ 3
        "default": 2,  # 아두이노 초기값
        "name": "밝기",
        "step": 1,
        "description": "이미지 밝기 조절 (음수는 어둡게, 양수는 밝게)",
        "device_min": -2,  # 실제 펌웨어 수용 범위
        "device_max": 2,
    },
    "contrast": {
        "min": -2,  # 확장 범위
        "max": 2,
        "default": 2,  # 아두이노 초기값
        "name": "대비",
        "step": 1,
        "description": "명암 대비 조절 (높을수록 선명)",
        "device_min": -2,
        "device_max": 2,
    },
    "saturation": {
        "min": -2,  # 확장 범위
        "max": 2,
        "default": 1,  # 아두이노 초기값
        "name": "채도",
        "step": 1,
        "description": "색상 채도 조절 (높을수록 진한 색상)",
        "device_min": -2,
        "device_max": 2,
    },
    "agc_gain": {
        "min": 0,
        "max": 30,  # OV2640 최대값
        "default": 30,  # 아두이노 초기값 (최대)
        "name": "AGC 게인",
        "step": 1,
        "description": "자동 게인 제어 (높을수록 밝지만 노이즈 증가)",
        "device_min": 0,
        "device_max": 30,
    },
    "gainceiling": {
        "min": 0,
        "max": 6,  # 2x, 4x, 8x, 16x, 32x, 64x, 128x
        "default": 6,  # 128x (최대)
        "name": "게인 상한",
        "step": 1,
        "description": "게인 최대 한계 (0=2x, 6=128x)",
        "device_min": 0,
        "device_max": 6,
    },
    "aec_value": {
        "min": 0,
        "max": 2400,  # 확장 범위 (아두이노에서 2000 사용)
        "default": 2000,  # 아두이노 초기값
        "name": "노출 시간 (AEC)",
        "step": 100,  # 100 단위로 조절
        "description": "수동 노출 시간 (높을수록 밝지만 흔들림 증가)",
        "device_min": 0,
        "device_max": 2000,
    },
    "ae_level": {
        "min": -2,
        "max": 2,
        "default": 0,
        "name": "자동 노출 레벨",
        "step": 1,
        "description": "자동 노출 보정 레벨",
        "device_min": -2,
        "device_max": 2,
    },
    "aec2": {
        "min": 0,
        "max": 1,
        "default": 1,  # DSP 활성화
        "name": "자동 노출 (DSP)",
        "step": 1,
        "description": "0=끄기, 1=켜기 (DSP 자동 노출)",
        "device_min": 0,
        "device_max": 1,
    },
    "quality": {
        "min": 4,  # 최고 품질
        "max": 63,  # 최저 품질
        "default": 10,  # 고품질
        "name": "JPEG 품질",
        "step": 1,
        "description": "JPEG 압축 품질 (낮을수록 고품질, 4~63)",
        "device_min": 4,
        "device_max": 63,
    },
    "hmirror": {
        "min": 0,
        "max": 1,
        "default": 0,
        "name": "수평 미러",
        "step": 1,
        "description": "0=끄기, 1=켜기 (좌우 반전)",
        "device_min": 0,
        "device_max": 1,
    },
    "vflip": {
        "min": 0,
        "max": 1,
        "default": 0,
        "name": "수직 플립",
        "step": 1,
        "description": "0=끄기, 1=켜기 (상하 반전)",
        "device_min": 0,
        "device_max": 1,
    },
    "awb": {
        "min": 0,
        "max": 1,
        "default": 1,  # 자동 화이트밸런스 활성화
        "name": "자동 화이트밸런스",
        "step": 1,
        "description": "0=끄기, 1=켜기 (자동 색상 보정)",
        "device_min": 0,
        "device_max": 1,
    },
    "awb_gain": {
        "min": 0,
        "max": 1,
        "default": 1,  # AWB 게인 활성화
        "name": "AWB 게인",
        "step": 1,
        "description": "0=끄기, 1=켜기 (AWB 게인 제어)",
        "device_min": 0,
        "device_max": 1,
    },
    "sharpness": {
        "min": -3,  # 확장 범위
        "max": 3,
        "default": 0,
        "name": "선명도",
        "step": 1,
        "description": "이미지 선명도 (양수는 샤프, 음수는 부드럽게)",
        "device_min": -2,
        "device_max": 2,
    },
    "denoise": {
        "min": 0,
        "max": 8,  # OV2640 최대값
        "default": 0,
        "name": "노이즈 제거",
        "step": 1,
        "description": "노이즈 감소 강도 (높을수록 부드럽지만 디테일 손실)",
        "device_min": 0,
        "device_max": 8,
    },
    "special_effect": {
        "min": 0,
        "max": 6,  # 0=Normal, 1=Negative, 2=Grayscale, 3=Red, 4=Green, 5=Blue, 6=Sepia
        "default": 0,
        "name": "특수 효과",
        "step": 1,
        "description": "0=일반, 1=네거티브, 2=흑백, 3=적색, 4=녹색, 5=청색, 6=세피아",
    },
    "wb_mode": {
        "min": 0,
        "max": 4,  # 0=Auto, 1=Sunny, 2=Cloudy, 3=Office, 4=Home
        "default": 0,
        "name": "화이트밸런스 모드",
        "step": 1,
        "description": "0=자동, 1=맑음, 2=흐림, 3=사무실, 4=가정",
    },
    "exposure_ctrl": {
        "min": 0,
        "max": 1,
        "default": 1,
        "name": "노출 제어",
        "step": 1,
        "description": "0=수동, 1=자동",
    },
    "aec_dsp": {
        "min": 0,
        "max": 1,
        "default": 1,
        "name": "AEC DSP",
        "step": 1,
        "description": "0=끄기, 1=켜기",
    },
    "agc_ctrl": {
        "min": 0,
        "max": 1,
        "default": 1,
        "name": "AGC 제어",
        "step": 1,
        "description": "0=수동, 1=자동",
    },
    "bpc": {
        "min": 0,
        "max": 1,
        "default": 0,
        "name": "BPC (흑점 보정)",
        "step": 1,
        "description": "Black Pixel Correction",
    },
    "wpc": {
        "min": 0,
        "max": 1,
        "default": 1,
        "name": "WPC (백점 보정)",
        "step": 1,
        "description": "White Pixel Correction",
    },
    "raw_gma": {
        "min": 0,
        "max": 1,
        "default": 1,
        "name": "RAW 감마",
        "step": 1,
        "description": "RAW Gamma",
    },
    "lenc": {
        "min": 0,
        "max": 1,
        "default": 1,
        "name": "렌즈 보정",
        "step": 1,
        "description": "Lens Correction (비네팅 보정)",
    },
    "dcw": {
        "min": 0,
        "max": 1,
        "default": 1,
        "name": "다운사이즈",
        "step": 1,
        "description": "Downsize Enable",
    },
    "colorbar": {
        "min": 0,
        "max": 1,
        "default": 0,
        "name": "컬러바 테스트",
        "step": 1,
        "description": "0=끄기, 1=켜기 (테스트 패턴)",
    },
}

# 아두이노 펌웨어가 현재 지원하는 파라미터 목록 (미지원은 501 반환)
# Readme.md 및 camera_init.h를 기준으로 함
SUPPORTED_CAMERA_PARAMS = {
    # 기본 설정
    "brightness",  # sensor->set_brightness
    "contrast",  # sensor->set_contrast
    "saturation",  # sensor->set_saturation
    # 노출/게인 설정
    "agc_gain",  # sensor->set_agc_gain
    "gainceiling",  # sensor->set_gainceiling
    "aec_value",  # sensor->set_aec_value (aruduino에서 2000 사용)
    "aec2",  # sensor->set_aec2
    # 품질/노이즈는 아두이노에서 미지원일 가능성 높음
    # "quality",       # 추가 확인 필요
    # "denoise",       # 추가 확인 필요
    # 영상 방향
    "hmirror",  # sensor->set_hmirror
    "vflip",  # sensor->set_vflip
}

# 카메라 설정 프리셋
CAMERA_PRESETS = {
    "default": {
        "name": "기본 설정",
        "description": "균형잡힌 설정 (아두이노 초기값 기반)",
        "icon": "🔄",
        "settings": {
            "brightness": 2,
            "contrast": 2,
            "saturation": 1,
            "sharpness": 0,
            "agc_gain": 30,
            "gainceiling": 6,
            "aec_value": 2000,
            "ae_level": 0,
            "awb": 1,
            "awb_gain": 1,
            "quality": 10,
            "denoise": 0,
        },
    },
    "night": {
        "name": "야간 모드",
        "description": "어두운 환경에 최적화 (모든 설정 최대)",
        "icon": "🌙",
        "settings": {
            "brightness": 2,  # 최대
            "contrast": 2,  # 최대
            "saturation": 2,  # 최대
            "agc_gain": 30,  # 최대
            "gainceiling": 6,  # 최대 (128x)
            "aec_value": 2400,  # 최대 노출
            "aec2": 1,  # DSP 켜기
        },
    },
    "day": {
        "name": "주간 모드",
        "description": "밝은 환경에 최적화",
        "icon": "☀️",
        "settings": {
            "brightness": 0,
            "contrast": 2,
            "saturation": 2,
            "sharpness": 1,
            "agc_gain": 10,
            "gainceiling": 3,
            "aec_value": 100,
            "ae_level": 0,
            "awb": 1,
            "awb_gain": 1,
            "quality": 10,
            "denoise": 0,
        },
    },
    "indoor": {
        "name": "실내 모드",
        "description": "실내 조명 환경",
        "icon": "🏠",
        "settings": {
            "brightness": 1,
            "contrast": 2,
            "saturation": 1,
            "sharpness": 0,
            "agc_gain": 20,
            "gainceiling": 5,
            "aec_value": 800,
            "ae_level": 1,
            "awb": 1,
            "wb_mode": 3,  # Office
            "quality": 10,
            "denoise": 2,
        },
    },
    "outdoor": {
        "name": "실외 모드",
        "description": "실외 자연광 환경",
        "icon": "🌳",
        "settings": {
            "brightness": 0,
            "contrast": 3,
            "saturation": 2,
            "sharpness": 2,
            "agc_gain": 8,
            "gainceiling": 2,
            "aec_value": 50,
            "ae_level": 0,
            "awb": 1,
            "wb_mode": 1,  # Sunny
            "quality": 8,
            "denoise": 0,
        },
    },
}

# 카메라 이미지 크기
CAMERA_IMAGE_WIDTH = 320
CAMERA_IMAGE_HEIGHT = 240
CAMERA_FPS_TARGET = 30


# ==================== UI 텍스트 ====================

UI_TEXT = {
    # 헤더
    "app_title": "🚗 ESP32-CAM 자율주행차 모니터링",
    "connection_checking": "연결 확인 중...",
    "connection_connected": "연결됨",
    "connection_disconnected": "연결 끊김",
    # 섹션 타이틀
    "video_title": "📹 실시간 영상",
    "status_title": "📊 시스템 상태",
    "motor_title": "🎮 모터 제어",
    "speed_title": "⚡ 속도 제어",
    "led_title": "💡 LED 제어",
    "camera_title": "📷 카메라 설정",
    "log_title": "📝 활동 로그",
    # 버튼 텍스트
    "motor_forward": "⬆️ 전진",
    "motor_left": "⬅️ 좌회전",
    "motor_right": "➡️ 우회전",
    "motor_stop": "🛑 정지",
    "speed_up": "➕ 가속",
    "speed_down": "➖ 감속",
    "led_on": "💡 켜기",
    "led_off": "🌑 끄기",
    "led_toggle": "🔄 토글",
    "camera_reset": "🔄 기본 설정으로 리셋",
    "log_clear": "로그 지우기",
    # 상태 텍스트
    "motor_running": "🟢 동작 중",
    "motor_stopped": "🔴 정지",
    "led_on_status": "💡 켜짐",
    "led_off_status": "🌑 꺼짐",
    # 에러 메시지
    "error_connection": "ESP32-CAM 연결 실패",
    "error_invalid_command": "잘못된 명령",
    "error_invalid_state": "잘못된 상태",
    "error_invalid_operation": "잘못된 연산",
    "error_value_required": "값이 필요합니다",
    "error_stream": "카메라 스트림 연결 실패",
    # 로그 메시지
    "log_init": "시스템 초기화 완료",
    "log_motor_control": "모터 제어",
    "log_motor_control_failed": "모터 제어 실패",
    "log_speed_increase": "속도 증가",
    "log_speed_decrease": "속도 감소",
    "log_speed_control_failed": "속도 제어 실패",
    "log_led_control": "LED 제어",
    "log_led_control_failed": "LED 제어 실패",
    "log_camera_control": "카메라 설정",
    "log_camera_control_failed": "카메라 설정 실패",
    "log_camera_reset": "카메라 설정 리셋 완료",
    "log_clear": "로그 초기화",
    "log_stream_error": "카메라 스트림 오류",
}


# ==================== 로깅 설정 ====================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_ENTRIES = 50  # UI에 표시할 최대 로그 개수


# ==================== 업데이트 주기 ====================

# 상태 업데이트 주기 (밀리초)
STATUS_UPDATE_INTERVAL = 1000

# FPS 카운터 업데이트 주기 (밀리초)
FPS_UPDATE_INTERVAL = 1000

# 카메라 설정 디바운싱 시간 (밀리초)
CAMERA_UPDATE_DEBOUNCE = 300

# 이미지 캡처 주기 (밀리초) - ESP32 부하 고려
# 주의: 너무 빠르면 다른 명령 처리가 느려질 수 있음
IMAGE_CAPTURE_INTERVAL = 100  # 100ms = 약 10 FPS
# 권장값: 100ms (10 FPS), 200ms (5 FPS), 500ms (2 FPS)


# ==================== 키보드 단축키 ====================

KEYBOARD_SHORTCUTS = {
    "forward": ["ArrowUp", "w", "W"],
    "left": ["ArrowLeft", "a", "A"],
    "right": ["ArrowRight", "d", "D"],
    "stop": [" ", "s", "S"],
    "speed_up": ["+", "="],
    "speed_down": ["-", "_"],
    "led_toggle": ["l", "L"],
}


# ==================== 개발자 설정 ====================

# 디버그 출력
VERBOSE_LOGGING = False

# 개발 모드 설정
DEVELOPMENT_MODE = {
    "reload": True,
    "threaded": True,
}
