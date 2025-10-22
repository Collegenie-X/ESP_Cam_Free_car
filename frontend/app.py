"""
ESP32-CAM 자율주행차 모니터링 Flask 애플리케이션
ESP32-CAM과 GET 방식으로 통신하여 실시간 모니터링 및 제어

[리팩토링 완료]
기존의 단일 파일 구조를 모듈화하여 분리:
- services/: 비즈니스 로직 (ESP32 통신)
- routes/: 라우트 핸들러 (메인, API, 카메라)
- core/: 핵심 설정 (앱 팩토리, 로거)
"""

from core.app_factory import create_app
from utils.server_port_selector import get_port_from_env, select_server_port
import config


# ==================== 메인 실행 ====================

if __name__ == "__main__":
    # Flask 앱 생성 (팩토리 패턴)
    app = create_app()

    # 선호 포트 결정: 환경변수 PORT → config의 기본값
    preferred_port = get_port_from_env(default_port=config.DEFAULT_SERVER_PORT)
    selected_port = select_server_port(preferred_port)

    # ESP32 IP 정보 가져오기
    esp32_ip = app.config.get("ESP32_IP")

    # 시작 메시지 출력
    print("=" * 50)
    print("ESP32-CAM 자율주행차 모니터링 시스템 시작")
    print(f"ESP32-CAM IP: {esp32_ip}")
    print(f"웹 인터페이스: http://localhost:{selected_port}")
    print("=" * 50)

    # Flask 서버 실행
    app.run(host=config.SERVER_HOST, port=selected_port, debug=config.DEBUG_MODE)
