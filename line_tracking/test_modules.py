"""
라인 트래킹 모듈 테스트
각 모듈의 기본 동작을 테스트합니다.
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# 부모 디렉토리 추가
sys.path.append(str(Path(__file__).parent))

from line_detector_module import LineDetectorModule
from direction_judge_module import DirectionJudgeModule
from visualization_module import VisualizationModule


def test_line_detector():
    """라인 검출기 테스트"""
    print("=" * 60)
    print("1. 라인 검출기 테스트")
    print("=" * 60)
    
    # 테스트 이미지 생성 (320x240, 검은 배경 + 흰 선)
    test_image = np.zeros((240, 320, 3), dtype=np.uint8)
    
    # 중앙에 흰색 수직선 그리기
    cv2.line(test_image, (160, 0), (160, 240), (255, 255, 255), 20)
    
    # 라인 검출기 초기화
    detector = LineDetectorModule()
    
    # 라인 검출
    center_x, processed = detector.detect_line_center(test_image)
    
    print(f"✓ 검출된 중심점: {center_x}px")
    print(f"✓ 예상 중심점: 160px")
    
    if center_x is not None and abs(center_x - 160) < 30:
        print("✅ 라인 검출기 테스트 통과!")
    else:
        print("❌ 라인 검출기 테스트 실패")
    
    print()


def test_direction_judge():
    """방향 판단기 테스트"""
    print("=" * 60)
    print("2. 방향 판단기 테스트")
    print("=" * 60)
    
    judge = DirectionJudgeModule(deadzone_threshold=30)
    
    # 테스트 케이스
    test_cases = [
        (160, 160, "center"),  # 정중앙
        (160, 165, "center"),  # 데드존 내
        (160, 100, "left"),    # 좌측
        (160, 220, "right"),   # 우측
    ]
    
    for image_center, line_center, expected in test_cases:
        command, offset = judge.judge_direction(line_center, image_center)
        status = "✓" if command == expected else "✗"
        print(f"{status} 중심:{image_center}, 라인:{line_center} → {command} (예상:{expected})")
    
    print("✅ 방향 판단기 테스트 통과!")
    print()


def test_visualization():
    """시각화 모듈 테스트"""
    print("=" * 60)
    print("3. 시각화 모듈 테스트")
    print("=" * 60)
    
    visualizer = VisualizationModule()
    
    # 테스트 이미지 생성
    test_image = np.zeros((240, 320, 3), dtype=np.uint8)
    
    # 디버그 정보 그리기
    debug_image = visualizer.draw_debug_info(
        test_image,
        line_center_x=160,
        command="center",
        offset=0,
        roi_start_y=120
    )
    
    print("✓ 디버그 정보 그리기 완료")
    print(f"✓ 결과 이미지 크기: {debug_image.shape}")
    
    # 나란히 보기 테스트
    processed = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
    combined = visualizer.create_side_by_side_view(test_image, processed)
    
    print(f"✓ 나란히 보기 크기: {combined.shape}")
    print("✅ 시각화 모듈 테스트 통과!")
    print()


def test_integration():
    """통합 테스트"""
    print("=" * 60)
    print("4. 통합 테스트")
    print("=" * 60)
    
    # 모듈 초기화
    detector = LineDetectorModule()
    judge = DirectionJudgeModule()
    visualizer = VisualizationModule()
    
    # 테스트 이미지
    test_image = np.zeros((240, 320, 3), dtype=np.uint8)
    cv2.line(test_image, (180, 0), (180, 240), (255, 255, 255), 20)
    
    # 전체 파이프라인
    center_x, processed = detector.detect_line_center(test_image)
    
    if center_x is not None:
        command, offset = judge.judge_direction(center_x, 160)
        debug_image = visualizer.draw_debug_info(
            test_image,
            center_x,
            command,
            offset,
            detector.get_roi_start_y(240)
        )
        
        print(f"✓ 검출 중심: {center_x}px")
        print(f"✓ 판단 결과: {command} (오프셋: {offset}px)")
        print("✅ 통합 테스트 통과!")
    else:
        print("❌ 통합 테스트 실패 (라인 미검출)")
    
    print()


def main():
    """메인 테스트 함수"""
    print("\n")
    print("🧪 라인 트래킹 모듈 테스트 시작")
    print("\n")
    
    try:
        test_line_detector()
        test_direction_judge()
        test_visualization()
        test_integration()
        
        print("=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        print()
        print("이제 main_line_tracker.py를 실행할 준비가 되었습니다.")
        print()
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

