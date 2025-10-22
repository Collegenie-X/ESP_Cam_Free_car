#!/usr/bin/env python3
"""
ESP32-CAM 자율주행차 메인 실행 파일

사용법:
    python main.py
"""

import sys
import os


# 가상환경 체크
def check_venv():
    """가상환경 활성화 확인"""
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  경고: 가상환경이 활성화되지 않았습니다.")
        print("\n다음 명령으로 가상환경을 생성하고 활성화하세요:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate  # Mac/Linux")
        print("  venv\\Scripts\\activate    # Windows")
        print("  pip install -r requirements.txt")
        print()
        response = input("계속 진행하시겠습니까? (y/N): ")
        if response.lower() != "y":
            sys.exit(0)


# 라이브러리 체크
def check_dependencies():
    """필수 라이브러리 확인"""
    required = ["cv2", "numpy", "requests", "dotenv"]
    missing = []

    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        print(f"❌ 필수 라이브러리가 없습니다: {', '.join(missing)}")
        print("\n다음 명령으로 설치하세요:")
        print("  pip install -r requirements.txt")
        sys.exit(1)


def main():
    """메인 함수"""
    print("=" * 60)
    print("🚗 ESP32-CAM 자율주행차 시스템")
    print("=" * 60)

    # 환경 체크
    check_venv()
    check_dependencies()

    # 모듈 import
    from config.settings import Settings
    from core.autonomous_driver import AutonomousDriver
    from utils.logger import setup_logger

    # 설정 로드
    settings = Settings()

    # 로거 설정
    setup_logger(debug_mode=settings.DEBUG_MODE)

    # 설정 출력
    settings.print_settings()

    # .env 파일 확인
    if not os.path.exists(".env"):
        print("\n⚠️  .env 파일이 없습니다.")
        print("  .env.example을 복사하여 .env 파일을 만들고 설정을 수정하세요.")
        print("  cp .env.example .env")
        print()

    # 자율주행 드라이버 생성
    driver = AutonomousDriver(settings)

    print("\n💡 팁:")
    print("  - 'q' 키를 누르면 종료됩니다 (미리보기 창 활성화 시)")
    print("  - Ctrl+C로도 종료할 수 있습니다")
    print()
    input("준비되면 Enter를 누르세요...")

    # 실행
    try:
        driver.start()
    except KeyboardInterrupt:
        print("\n\n프로그램 종료")
    finally:
        driver.stop()


if __name__ == "__main__":
    main()
