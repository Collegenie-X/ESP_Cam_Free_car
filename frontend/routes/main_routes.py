"""
메인 페이지 라우트 핸들러
웹 페이지 렌더링을 담당하는 라우트들
"""

from flask import Blueprint, render_template
import config

# 블루프린트 생성 (라우트 그룹화)
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    메인 대시보드 페이지 렌더링

    Returns:
        렌더링된 HTML 템플릿
    """
    # 환경변수에서 ESP32 IP 가져오기 (블루프린트에서는 current_app 사용)
    from flask import current_app

    esp32_ip = current_app.config.get("ESP32_IP")

    return render_template("index.html", esp32_ip=esp32_ip, config=config)


@main_bp.route("/settings")
def settings():
    """
    설정 페이지 렌더링

    Returns:
        렌더링된 HTML 템플릿
    """
    from flask import current_app

    esp32_ip = current_app.config.get("ESP32_IP")

    return render_template("settings.html", esp32_ip=esp32_ip)


@main_bp.route("/ai-demo")
def ai_demo():
    """
    AI 분석 데모 페이지 렌더링

    Returns:
        렌더링된 HTML 템플릿
    """
    return render_template("ai_demo.html")


@main_bp.route("/autonomous")
def autonomous():
    """
    자율주행 모니터링 페이지 렌더링

    Returns:
        렌더링된 HTML 템플릿
    """
    from flask import current_app

    esp32_ip = current_app.config.get("ESP32_IP")

    return render_template("autonomous.html", esp32_ip=esp32_ip)
