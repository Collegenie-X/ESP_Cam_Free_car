"""
API 라우트 핸들러
ESP32-CAM 제어 API 엔드포인트들
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import config

# 블루프린트 생성
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/status")
def get_status():
    """
    ESP32 상태 조회 API (프록시)

    Returns:
        JSON 응답 (상태 정보 또는 에러)
    """
    # 현재 앱의 ESP32 통신 서비스 가져오기
    esp32_service = current_app.config.get("ESP32_SERVICE")

    status = esp32_service.get_status()

    if not status:
        return jsonify({"error": "ESP32-CAM 연결 실패", "connected": False}), 503

    # 현재 시간 추가
    status["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(status)


@api_bp.route("/control/<command>")
def control_motor(command):
    """
    모터 제어 API

    Args:
        command: 모터 명령어 (left, right, center, stop)

    Returns:
        JSON 응답 (성공 여부)
    """
    # 명령어 검증
    if command not in config.MOTOR_COMMANDS:
        return (
            jsonify(
                {"success": False, "error": config.UI_TEXT["error_invalid_command"]}
            ),
            400,
        )

    # ESP32에 명령 전송
    esp32_service = current_app.config.get("ESP32_SERVICE")
    result = esp32_service.send_command(
        config.API_ENDPOINTS["control"], {"cmd": command}
    )

    return jsonify(result)


@api_bp.route("/led/<state>")
def control_led(state):
    """
    LED 제어 API

    Args:
        state: LED 상태 (on, off, toggle)

    Returns:
        JSON 응답 (성공 여부)
    """
    # 상태 검증
    if state not in config.LED_STATES:
        return (
            jsonify({"success": False, "error": config.UI_TEXT["error_invalid_state"]}),
            400,
        )

    # ESP32에 명령 전송
    esp32_service = current_app.config.get("ESP32_SERVICE")
    result = esp32_service.send_command(config.API_ENDPOINTS["led"], {"state": state})

    return jsonify(result)


@api_bp.route("/speed/<operation>")
def control_speed(operation):
    """
    속도 제어 API

    Args:
        operation: 속도 연산 (plus, minus)

    Returns:
        JSON 응답 (성공 여부)
    """
    # 쿼리 파라미터에서 step 값 가져오기 (기본값: config에서)
    step = request.args.get("step", config.SPEED_DEFAULT_STEP, type=int)

    # 연산 검증
    if operation not in ["plus", "minus"]:
        return (
            jsonify(
                {"success": False, "error": config.UI_TEXT["error_invalid_operation"]}
            ),
            400,
        )

    # step 범위 검증 (최소~최대 사이로 제한)
    step = max(config.SPEED_STEP_MIN, min(step, config.SPEED_STEP_MAX))

    # ESP32에 명령 전송
    esp32_service = current_app.config.get("ESP32_SERVICE")
    result = esp32_service.send_command(
        config.API_ENDPOINTS["speed"], {"op": operation, "step": step}
    )

    return jsonify(result)


@api_bp.route("/camera/<param>")
def control_camera(param):
    """
    카메라 센서 제어 API

    Args:
        param: 카메라 파라미터명 (brightness, contrast 등)

    Returns:
        JSON 응답 (성공 여부)
    """
    # 쿼리 파라미터에서 value 가져오기
    value = request.args.get("value", type=int)

    # value 필수 검증
    if value is None:
        return (
            jsonify(
                {"success": False, "error": config.UI_TEXT["error_value_required"]}
            ),
            400,
        )

    # 아두이노 미지원 파라미터 처리
    if param not in config.SUPPORTED_CAMERA_PARAMS:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "파라미터 미지원 (Arduino)",
                    "param": param,
                    "supported": sorted(list(config.SUPPORTED_CAMERA_PARAMS)),
                }
            ),
            501,
        )

    # 파라미터 범위 검증 (디바이스 실수용 범위 우선 → UI 범위)
    if param in config.CAMERA_PARAMS:
        param_config = config.CAMERA_PARAMS[param]
        device_min = param_config.get("device_min", param_config["min"])
        device_max = param_config.get("device_max", param_config["max"])

        # 디바이스가 수용 가능한 범위로 클램프
        value = max(device_min, min(value, device_max))

    # ESP32에 명령 전송
    esp32_service = current_app.config.get("ESP32_SERVICE")
    result = esp32_service.send_command(
        config.API_ENDPOINTS["camera"], {"param": param, "value": value}
    )

    return jsonify(result)
