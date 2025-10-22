"""
Flask 애플리케이션 팩토리
앱 생성 및 초기화를 담당하는 팩토리 함수
"""

from flask import Flask, jsonify
import os
import logging
import config
from services.esp32_communication_service import ESP32CommunicationService
from core.logger_config import setup_logger
from ai.detectors.yolo_detector import YOLODetector
from ai.detectors.lane_detector import LaneDetector
from ai.core.autonomous_lane_tracker import AutonomousLaneTrackerV2
from services.autonomous_driving_service import AutonomousDrivingService


def create_app():
    """
    Flask 애플리케이션 생성 및 설정

    팩토리 패턴을 사용하여 앱을 생성합니다.
    - 환경 설정
    - 서비스 초기화
    - 라우트 등록
    - 에러 핸들러 등록

    Returns:
        설정이 완료된 Flask 앱 인스턴스
    """
    # Flask 앱 생성 (템플릿/정적 파일 경로 명시)
    # app_factory.py가 core/ 폴더에 있으므로 상위 디렉토리 지정 필요
    import sys
    from pathlib import Path

    # frontend 폴더의 절대 경로 찾기
    base_dir = Path(__file__).parent.parent.absolute()

    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )

    # 로거 설정
    setup_logger()

    # ESP32-CAM IP 주소 설정 (환경변수 우선)
    esp32_ip = os.environ.get("ESP32_IP") or config.DEFAULT_ESP32_IP
    esp32_base_url = f"http://{esp32_ip}"

    # 앱 설정 저장
    app.config["ESP32_IP"] = esp32_ip
    app.config["ESP32_BASE_URL"] = esp32_base_url

    # ESP32 통신 서비스 초기화
    esp32_service = ESP32CommunicationService(
        base_url=esp32_base_url, timeout=config.REQUEST_TIMEOUT
    )
    app.config["ESP32_SERVICE"] = esp32_service

    # AI 서비스 초기화 (YOLO 객체 감지)
    try:
        yolo_detector = YOLODetector(confidence_threshold=0.5)
        app.config["YOLO_DETECTOR"] = yolo_detector
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"YOLO 모델 로드 실패 (선택적 기능): {e}")
        app.config["YOLO_DETECTOR"] = None

    # 차선 감지기 초기화 (기본, 데모용)
    lane_detector = LaneDetector()
    app.config["LANE_DETECTOR"] = lane_detector

    # 자율주행 차선 추적기 초기화 (prod.md 기반, 모듈화)
    autonomous_tracker = AutonomousLaneTrackerV2(
        brightness_threshold=80,
        use_adaptive=True,
        min_noise_area=100,
        min_aspect_ratio=2.0,
    )
    app.config["AUTONOMOUS_TRACKER"] = autonomous_tracker

    # 자율주행 서비스 초기화
    autonomous_service = AutonomousDrivingService(
        esp32_service=esp32_service, lane_tracker=autonomous_tracker
    )
    app.config["AUTONOMOUS_SERVICE"] = autonomous_service

    logger = logging.getLogger(__name__)
    logger.info("자율주행 시스템 초기화 완료")

    # 블루프린트 등록 (라우트 모듈 연결)
    register_blueprints(app)

    # 에러 핸들러 등록
    register_error_handlers(app)

    return app


def register_blueprints(app):
    """
    블루프린트 등록

    각 라우트 모듈을 앱에 연결합니다.

    Args:
        app: Flask 앱 인스턴스
    """
    from routes.main_routes import main_bp
    from routes.api_routes import api_bp
    from routes.camera_routes import camera_bp
    from routes.ai_routes import ai_bp
    from routes.autonomous_routes import autonomous_bp

    # 메인 페이지 라우트
    app.register_blueprint(main_bp)

    # API 라우트 (/api/* 경로)
    app.register_blueprint(api_bp)

    # 카메라 라우트
    app.register_blueprint(camera_bp)

    # AI 분석 라우트 (/api/ai/* 경로)
    app.register_blueprint(ai_bp)

    # 자율주행 라우트 (/api/autonomous/* 경로)
    app.register_blueprint(autonomous_bp)


def register_error_handlers(app):
    """
    에러 핸들러 등록

    HTTP 에러 발생 시 처리 로직을 정의합니다.

    Args:
        app: Flask 앱 인스턴스
    """

    @app.errorhandler(404)
    def not_found(error):
        """404 에러 핸들러"""
        return jsonify({"error": "페이지를 찾을 수 없습니다"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500 에러 핸들러"""
        return jsonify({"error": "서버 내부 오류"}), 500
