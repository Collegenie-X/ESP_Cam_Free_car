"""
카메라 라우트 핸들러
카메라 이미지 캡처 및 스트리밍을 담당하는 라우트들
"""

from flask import Blueprint, Response, current_app
import requests
import logging
import config

logger = logging.getLogger(__name__)

# 블루프린트 생성
camera_bp = Blueprint("camera", __name__)


@camera_bp.route("/capture")
def capture_image():
    """
    ESP32-CAM 단일 이미지 캡처 (폴링 방식)

    Returns:
        이미지 바이너리 데이터 또는 에러 응답
    """
    try:
        esp32_service = current_app.config.get("ESP32_SERVICE")
        capture_url = esp32_service.get_capture_url()

        response = requests.get(capture_url, timeout=config.REQUEST_TIMEOUT)

        if response.status_code != 200:
            logger.error(f"이미지 캡처 실패: {response.status_code}")
            return Response(status=503)

        return Response(response.content, mimetype="image/jpeg")

    except requests.exceptions.RequestException as e:
        logger.error(f"이미지 캡처 오류: {e}")
        return Response(status=503)


@camera_bp.route("/stream")
def stream_video():
    """
    ESP32-CAM 스트림 프록시 (비권장 - 다른 명령 처리 불가)

    주의: 이 엔드포인트는 연결을 계속 유지하므로
         다른 명령어 전송이 차단될 수 있습니다.

    Returns:
        MJPEG 스트림 응답
    """

    def generate_stream():
        """스트림 데이터를 생성하는 제너레이터 함수"""
        try:
            esp32_service = current_app.config.get("ESP32_SERVICE")
            stream_url = esp32_service.get_stream_url()

            # 스트림 연결 (계속 유지됨)
            response = requests.get(
                stream_url, stream=True, timeout=config.STREAM_TIMEOUT
            )

            # 청크 단위로 데이터 전달
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk

        except Exception as e:
            logger.error(f"스트림 오류: {e}")

    return Response(
        generate_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )
