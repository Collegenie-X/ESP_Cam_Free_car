#!/usr/bin/env python
"""
자율주행 시스템 테스트 스크립트 V2

모듈화된 구조에서 모든 컴포넌트가 정상적으로 로드되는지 확인합니다.
"""

import sys


def test_imports():
    """모듈 import 테스트"""
    print("=" * 50)
    print("🧪 자율주행 시스템 테스트 시작 (V2)")
    print("=" * 50)

    tests = []

    # 1. 필터 모듈
    try:
        from ai.filters import ImagePreprocessor, LaneMaskGenerator, NoiseFilter

        preprocessor = ImagePreprocessor()
        mask_gen = LaneMaskGenerator()
        noise_filter = NoiseFilter()
        tests.append(("✅ filters (전처리/마스크/노이즈)", True))
    except Exception as e:
        tests.append(("❌ filters", str(e)))

    # 2. 감지 모듈
    try:
        from ai.detectors import (
            SteeringJudge,
            CornerDetector,
            YOLODetector,
            LaneDetector,
        )

        judge = SteeringJudge()
        corner = CornerDetector()
        yolo = YOLODetector()
        lane = LaneDetector()
        tests.append(("✅ detectors (조향/코너/YOLO/차선)", True))
    except Exception as e:
        tests.append(("❌ detectors", str(e)))

    # 3. 시각화 모듈
    try:
        from ai.visualization import Visualization

        viz = Visualization()
        tests.append(("✅ visualization", True))
    except Exception as e:
        tests.append(("❌ visualization", str(e)))

    # 4. 메인 추적기
    try:
        from ai.core import AutonomousLaneTrackerV2

        tracker = AutonomousLaneTrackerV2()
        tests.append(("✅ core (AutonomousLaneTrackerV2)", True))
    except Exception as e:
        tests.append(("❌ core", str(e)))

    # 5. 서비스 모듈
    try:
        from services.autonomous_driving_service import AutonomousDrivingService
        from services.esp32_communication_service import ESP32CommunicationService

        esp32 = ESP32CommunicationService("http://192.168.0.65")
        service = AutonomousDrivingService(esp32)
        tests.append(("✅ services (자율주행/ESP32)", True))
    except Exception as e:
        tests.append(("❌ services", str(e)))

    # 6. Flask 앱
    try:
        from core.app_factory import create_app

        app = create_app()
        tests.append(("✅ Flask app", True))
    except Exception as e:
        tests.append(("❌ Flask app", str(e)))

    # 결과 출력
    print("\n" + "=" * 50)
    print("📊 테스트 결과")
    print("=" * 50)

    passed = 0
    failed = 0

    for test_name, result in tests:
        if result is True:
            print(f"{test_name}")
            passed += 1
        else:
            print(f"{test_name}")
            print(f"   오류: {result}")
            failed += 1

    print("=" * 50)
    print(f"통과: {passed}/{len(tests)}")
    print(f"실패: {failed}/{len(tests)}")
    print("=" * 50)

    if failed == 0:
        print("\n🎉 모든 테스트 통과!")
        print("\n다음 명령으로 서버를 시작하세요:")
        print("  python app.py")
        return 0
    else:
        print(f"\n⚠️  {failed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(test_imports())
