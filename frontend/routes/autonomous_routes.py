"""
자율주행 API 라우트

자율주행 시작/중지, 상태 조회, 단일 프레임 분석 등을 제공합니다.
"""

from flask import Blueprint, jsonify, current_app, request, Response
import logging
import requests
import cv2
import numpy as np
import base64

autonomous_bp = Blueprint("autonomous", __name__, url_prefix="/api/autonomous")
logger = logging.getLogger(__name__)


@autonomous_bp.route("/start", methods=["POST"])
def start_autonomous():
    """
    자율주행 시작

    Returns:
        {"success": bool, "message": str}
    """
    try:
        auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
        if not auto_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "자율주행 서비스가 초기화되지 않았습니다",
                    }
                ),
                500,
            )

        result = auto_service.start()
        return jsonify(result)

    except Exception as e:
        logger.error(f"자율주행 시작 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/stop", methods=["POST"])
def stop_autonomous():
    """
    자율주행 중지

    Returns:
        {"success": bool, "message": str, "stats": {...}}
    """
    try:
        auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
        if not auto_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "자율주행 서비스가 초기화되지 않았습니다",
                    }
                ),
                500,
            )

        result = auto_service.stop()
        return jsonify(result)

    except Exception as e:
        logger.error(f"자율주행 중지 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/status")
def get_autonomous_status():
    """
    자율주행 상태 조회

    Returns:
        {
            "is_running": bool,
            "last_command": str,
            "state": str,
            "command_history": [...],
            "stats": {...}
        }
    """
    try:
        auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
        if not auto_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "자율주행 서비스가 초기화되지 않았습니다",
                    }
                ),
                500,
            )

        status = auto_service.get_status()
        return jsonify({"success": True, **status})

    except Exception as e:
        logger.error(f"자율주행 상태 조회 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/analyze", methods=["POST"])
def analyze_frame():
    """
    단일 프레임 분석 (테스트용)

    Request:
        - JSON: {"image_url": "http://..."} 또는
        - multipart/form-data: file upload

    Returns:
        {
            "success": bool,
            "command": str,
            "state": str,
            "histogram": {...},
            "confidence": float,
            "image_base64": str  # 처리된 이미지 (Base64)
        }
    """
    try:
        auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
        if not auto_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "자율주행 서비스가 초기화되지 않았습니다",
                    }
                ),
                500,
            )

        # 이미지 가져오기
        image = None

        # 방법 1: JSON으로 URL 전달
        if request.is_json:
            data = request.get_json()
            image_url = data.get("image_url")

            if image_url:
                # ESP32-CAM에서 이미지 가져오기
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    nparr = np.frombuffer(response.content, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 방법 2: 파일 업로드
        elif "file" in request.files:
            file = request.files["file"]
            nparr = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 방법 3: ESP32-CAM에서 직접 캡처
        else:
            esp32_service = current_app.config.get("ESP32_SERVICE")
            if esp32_service:
                capture_url = esp32_service.get_capture_url()
                response = requests.get(capture_url, timeout=5)
                if response.status_code == 200:
                    nparr = np.frombuffer(response.content, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return (
                jsonify({"success": False, "error": "이미지를 가져올 수 없습니다"}),
                400,
            )

        # 프레임 분석
        result = auto_service.analyze_single_frame(image, draw_overlay=True)

        if not result["success"]:
            return jsonify(result), 500

        # 이미지를 Base64로 인코딩
        image_base64 = base64.b64encode(result["image"]).decode("utf-8")

        return jsonify(
            {
                "success": True,
                "command": result["command"],
                "state": result["state"],
                "histogram": result["histogram"],
                "confidence": result["confidence"],
                "image_base64": image_base64,
            }
        )

    except Exception as e:
        logger.error(f"프레임 분석 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/stream")
def autonomous_stream():
    """
    자율주행 실시간 스트리밍
    ESP32-CAM 스트림을 받아서 차선 추적 처리 후 재전송

    Returns:
        MJPEG 스트림
    """

    def generate():
        """MJPEG 스트림 생성 (5fps 제한)"""
        import time
        from flask import current_app as app

        # Application context 내에서 서비스 가져오기
        with current_app.app_context():
            auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
            esp32_service = current_app.config.get("ESP32_SERVICE")

        if not auto_service or not esp32_service:
            logger.error("서비스가 초기화되지 않았습니다")
            return

        try:

            stream_url = esp32_service.get_stream_url()
            logger.info(f"스트림 연결 시도: {stream_url}")

            # ESP32-CAM 스트림에 연결 (타임아웃 증가)
            try:
                response = requests.get(stream_url, stream=True, timeout=30)
                if response.status_code != 200:
                    logger.error(f"ESP32-CAM 스트림 연결 실패: {response.status_code}")
                    message = "ESP32-CAM 스트림 연결 실패"
                    yield b"--frame\r\nContent-Type: text/plain\r\n\r\n" + message.encode(
                        "utf-8"
                    ) + b"\r\n"
                    return
                logger.info("ESP32-CAM 스트림 연결 성공")
            except requests.exceptions.RequestException as e:
                logger.error(f"ESP32-CAM 스트림 연결 오류: {e}")
                message = "ESP32-CAM 연결 오류"
                yield b"--frame\r\nContent-Type: text/plain\r\n\r\n" + message.encode(
                    "utf-8"
                ) + b"\r\n"
                return

            # 프레임레이트 제한 (5fps = 0.2초 간격)
            TARGET_FPS = 5
            FRAME_INTERVAL = 1.0 / TARGET_FPS  # 0.2초
            last_frame_time = 0
            frame_count = 0

            # MJPEG 스트림 파싱
            bytes_data = b""
            for chunk in response.iter_content(chunk_size=1024):
                bytes_data += chunk

                # JPEG 이미지 찾기
                a = bytes_data.find(b"\xff\xd8")  # JPEG 시작
                b = bytes_data.find(b"\xff\xd9")  # JPEG 끝

                if a != -1 and b != -1 and b > a:
                    jpg = bytes_data[a : b + 2]
                    bytes_data = bytes_data[b + 2 :]

                    if len(jpg) < 100:  # 너무 작은 JPEG는 무시
                        logger.warning(f"잘못된 JPEG 데이터 (크기: {len(jpg)} bytes)")
                        continue

                    logger.debug(f"JPEG 프레임 수신 (크기: {len(jpg)} bytes)")

                    # 프레임레이트 제한 (5fps)
                    current_time = time.time()
                    if current_time - last_frame_time < FRAME_INTERVAL:
                        continue  # 프레임 스킵

                    last_frame_time = current_time
                    frame_count += 1

                    # 이미지 디코딩
                    try:
                        nparr = np.frombuffer(jpg, np.uint8)
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if image is None or image.size == 0:
                            logger.warning("이미지 디코딩 실패")
                            continue
                        logger.debug(f"이미지 디코딩 성공 (크기: {image.shape})")
                    except Exception as e:
                        logger.error(f"이미지 디코딩 오류: {e}")
                        continue

                    if image is not None:
                        # 차선 추적 처리 (항상 처리하고 명령은 자율주행 중일 때만 전송)
                        result = auto_service.process_frame(
                            image, send_command=True, debug=True
                        )

                        # 오버레이 이미지 가져오기
                        if result.get("success") and "debug_images" in result:
                            processed_image = result["debug_images"].get(
                                "7_final", image
                            )
                        else:
                            processed_image = image

                        # JPEG로 인코딩 (품질 낮춤 - 부하 감소)
                        _, buffer = cv2.imencode(
                            ".jpg", processed_image, [cv2.IMWRITE_JPEG_QUALITY, 70]
                        )
                        frame = buffer.tobytes()

                        # MJPEG 형식으로 전송
                        yield (
                            b"--frame\r\n"
                            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                        )

                        # 로그 (10프레임마다)
                        if frame_count % 10 == 0:
                            status = (
                                "자율주행 중" if auto_service.is_running else "모니터링"
                            )
                            logger.info(
                                f"스트림 처리 중... 프레임: {frame_count}, "
                                f"상태: {status}, "
                                f"명령: {result.get('command', 'N/A')}"
                            )

        except Exception as e:
            logger.error(f"자율주행 스트리밍 오류: {e}")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@autonomous_bp.route("/check_camera")
def check_camera():
    """
    ESP32-CAM 연결 상태 확인
    """
    try:
        esp32_service = current_app.config.get("ESP32_SERVICE")
        if not esp32_service:
            return jsonify({"success": False, "error": "ESP32 서비스 없음"}), 500

        # 1. 기본 연결 확인
        base_url = esp32_service.base_url
        try:
            response = requests.get(f"{base_url}/status", timeout=5)
            if response.status_code != 200:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"ESP32-CAM 응답 없음 (코드: {response.status_code})",
                        }
                    ),
                    400,
                )
        except requests.exceptions.RequestException as e:
            return (
                jsonify({"success": False, "error": f"ESP32-CAM 연결 실패: {str(e)}"}),
                400,
            )

        # 2. 스트림 URL - 바로 성공으로 반환 (실제 스트림은 접속 시 확인)
        stream_url = esp32_service.get_stream_url()

        return jsonify(
            {
                "success": True,
                "message": "ESP32-CAM 정상",
                "base_url": base_url,
                "stream_url": stream_url,
            }
        )

    except Exception as e:
        logger.error(f"카메라 체크 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/test")
def test_autonomous():
    """
    자율주행 시스템 테스트

    Returns:
        {
            "success": bool,
            "components": {
                "lane_tracker": bool,
                "esp32_service": bool,
                "autonomous_service": bool
            }
        }
    """
    try:
        components = {
            "lane_tracker": current_app.config.get("LANE_TRACKER") is not None,
            "esp32_service": current_app.config.get("ESP32_SERVICE") is not None,
            "autonomous_service": current_app.config.get("AUTONOMOUS_SERVICE")
            is not None,
        }

        all_ok = all(components.values())

        return jsonify(
            {
                "success": all_ok,
                "components": components,
                "message": "모든 컴포넌트 정상" if all_ok else "일부 컴포넌트 누락",
            }
        )

    except Exception as e:
        logger.error(f"테스트 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
