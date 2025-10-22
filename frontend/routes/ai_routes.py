"""
AI 분석 라우트 핸들러
YOLO 객체 감지 및 차선 인식 API
"""

from flask import Blueprint, jsonify, request, Response, current_app
import requests
import cv2
import numpy as np
import logging
import config

logger = logging.getLogger(__name__)

# 블루프린트 생성
ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.route("/detect")
def detect_objects():
    """
    ESP32-CAM 이미지에서 객체 감지 API

    Query Parameters:
        draw (optional): "true"면 Bounding Box가 그려진 이미지 반환

    Returns:
        JSON 응답 (감지된 객체 리스트) 또는 이미지 (draw=true인 경우)

    예시 응답:
    {
        "success": true,
        "objects": [
            {
                "label": "person",
                "confidence": 0.92,
                "bbox": {"x": 100, "y": 150, "width": 200, "height": 300},
                "rect": {"x1": 100, "y1": 150, "x2": 300, "y2": 450}
            }
        ],
        "summary": {
            "total_objects": 2,
            "classes": {"person": 1, "car": 1}
        }
    }
    """
    try:
        # YOLO 감지기 가져오기
        yolo_detector = current_app.config.get("YOLO_DETECTOR")

        if not yolo_detector or not yolo_detector.is_ready():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "YOLO 모델이 로드되지 않았습니다. 서버 로그를 확인하세요.",
                    }
                ),
                503,
            )

        # ESP32에서 이미지 가져오기
        esp32_service = current_app.config.get("ESP32_SERVICE")
        capture_url = esp32_service.get_capture_url()

        response = requests.get(capture_url, timeout=config.REQUEST_TIMEOUT)

        if response.status_code != 200:
            return (
                jsonify({"success": False, "error": "ESP32-CAM 이미지 캡처 실패"}),
                503,
            )

        # 이미지 바이트 데이터
        image_bytes = response.content

        # YOLO 객체 감지
        detections = yolo_detector.detect_from_bytes(image_bytes)

        # draw 파라미터 확인
        draw = request.args.get("draw", "false").lower() == "true"

        if draw:
            # 이미지에 Bounding Box 그리기
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            result_image = yolo_detector.draw_detections(image, detections)

            # JPEG로 인코딩
            _, img_encoded = cv2.imencode(".jpg", result_image)

            return Response(img_encoded.tobytes(), mimetype="image/jpeg")

        # JSON 응답
        summary = yolo_detector.get_detection_summary(detections)

        return jsonify({"success": True, "objects": detections, "summary": summary})

    except Exception as e:
        logger.error(f"객체 감지 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/lanes")
def detect_lanes():
    """
    ESP32-CAM 이미지에서 차선 감지 API

    Query Parameters:
        draw (optional): "true"면 차선이 그려진 이미지 반환

    Returns:
        JSON 응답 (감지된 차선 리스트) 또는 이미지 (draw=true인 경우)

    예시 응답:
    {
        "success": true,
        "lanes": [
            {
                "side": "left",
                "line": {"x1": 100, "y1": 400, "x2": 200, "y2": 300}
            },
            {
                "side": "right",
                "line": {"x1": 400, "y1": 400, "x2": 300, "y2": 300}
            }
        ],
        "center_offset": 15
    }
    """
    try:
        # 차선 감지기 가져오기
        lane_detector = current_app.config.get("LANE_DETECTOR")

        if not lane_detector:
            return (
                jsonify(
                    {"success": False, "error": "차선 감지기가 초기화되지 않았습니다."}
                ),
                503,
            )

        # ESP32에서 이미지 가져오기
        esp32_service = current_app.config.get("ESP32_SERVICE")
        capture_url = esp32_service.get_capture_url()

        response = requests.get(capture_url, timeout=config.REQUEST_TIMEOUT)

        if response.status_code != 200:
            return (
                jsonify({"success": False, "error": "ESP32-CAM 이미지 캡처 실패"}),
                503,
            )

        # 이미지 디코딩
        nparr = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"success": False, "error": "이미지 디코딩 실패"}), 500

        # 차선 감지
        lanes = lane_detector.detect_lanes(image)

        # draw 파라미터 확인
        draw = request.args.get("draw", "false").lower() == "true"

        if draw:
            # 이미지에 차선 그리기
            result_image = lane_detector.draw_lanes(image, lanes)

            # JPEG로 인코딩
            _, img_encoded = cv2.imencode(".jpg", result_image)

            return Response(img_encoded.tobytes(), mimetype="image/jpeg")

        # 중심 오프셋 계산
        height, width = image.shape[:2]
        center_offset = lane_detector.calculate_center_offset(lanes, width)

        # JSON 응답
        return jsonify(
            {"success": True, "lanes": lanes, "center_offset": center_offset}
        )

    except Exception as e:
        logger.error(f"차선 감지 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/analyze")
def analyze_full():
    """
    ESP32-CAM 이미지 종합 분석 (객체 감지 + 차선 감지)

    Query Parameters:
        draw (optional): "true"면 분석 결과가 그려진 이미지 반환

    Returns:
        JSON 응답 (객체 + 차선 정보) 또는 이미지 (draw=true인 경우)
    """
    try:
        yolo_detector = current_app.config.get("YOLO_DETECTOR")
        lane_detector = current_app.config.get("LANE_DETECTOR")
        esp32_service = current_app.config.get("ESP32_SERVICE")

        # 이미지 캡처
        capture_url = esp32_service.get_capture_url()
        response = requests.get(capture_url, timeout=config.REQUEST_TIMEOUT)

        if response.status_code != 200:
            return (
                jsonify({"success": False, "error": "ESP32-CAM 이미지 캡처 실패"}),
                503,
            )

        # 이미지 디코딩
        nparr = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"success": False, "error": "이미지 디코딩 실패"}), 500

        result_data = {"success": True}

        # YOLO 객체 감지 (모델이 로드된 경우만)
        if yolo_detector and yolo_detector.is_ready():
            detections = yolo_detector.detect_from_bytes(response.content)
            result_data["objects"] = detections
            result_data["object_summary"] = yolo_detector.get_detection_summary(
                detections
            )
        else:
            result_data["objects"] = []
            result_data["object_summary"] = {"total_objects": 0, "classes": {}}

        # 차선 감지
        if lane_detector:
            lanes = lane_detector.detect_lanes(image)
            height, width = image.shape[:2]
            center_offset = lane_detector.calculate_center_offset(lanes, width)

            result_data["lanes"] = lanes
            result_data["center_offset"] = center_offset
        else:
            result_data["lanes"] = []
            result_data["center_offset"] = None

        # draw 파라미터 확인
        draw = request.args.get("draw", "false").lower() == "true"

        if draw:
            result_image = image.copy()

            # 차선 그리기
            if lane_detector and result_data["lanes"]:
                result_image = lane_detector.draw_lanes(
                    result_image, result_data["lanes"]
                )

            # 객체 그리기
            if yolo_detector and yolo_detector.is_ready() and result_data["objects"]:
                result_image = yolo_detector.draw_detections(
                    result_image, result_data["objects"]
                )

            # JPEG로 인코딩
            _, img_encoded = cv2.imencode(".jpg", result_image)

            return Response(img_encoded.tobytes(), mimetype="image/jpeg")

        return jsonify(result_data)

    except Exception as e:
        logger.error(f"종합 분석 오류: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
