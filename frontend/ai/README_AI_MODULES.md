# 🧩 AI 모듈 구조 설명

자율주행 차선 추적 시스템이 모듈화되어 유지보수가 쉬워졌습니다.

## 📁 모듈 구조

```
ai/
├── autonomous_lane_tracker.py      # 메인 클래스 (V2, 모듈화)
├── autonomous_lane_tracker_v1_backup.py  # 백업 (기존 단일 파일)
├── image_preprocessor.py           # 이미지 전처리
├── lane_mask_generator.py          # 차선 마스크 생성
├── noise_filter.py                 # 노이즈 필터링
├── steering_judge.py               # 조향 판단
├── corner_detector.py              # 코너 감지
├── visualization.py                # 시각화
├── yolo_detector.py                # YOLO 객체 감지
└── lane_detector.py                # 기본 차선 감지 (데모용)
```

## 🔧 각 모듈 설명

### 1. `image_preprocessor.py` - 이미지 전처리

**역할**: 이미지 품질 개선 및 ROI 추출

**주요 클래스**: `ImagePreprocessor`

**주요 메서드**:
- `apply_clahe(image)`: CLAHE 적용 (선명도 개선)
- `apply_gaussian_blur(image)`: 가우시안 블러 (노이즈 제거)
- `extract_roi(image, roi)`: ROI 영역 추출
- `get_average_brightness(image)`: 평균 밝기 계산

**사용 예시**:
```python
from ai.image_preprocessor import ImagePreprocessor

preprocessor = ImagePreprocessor()
enhanced = preprocessor.apply_clahe(image)
blurred = preprocessor.apply_gaussian_blur(enhanced)
roi = preprocessor.extract_roi(blurred, {"y_start": 180, "y_end": 240, ...})
```

---

### 2. `lane_mask_generator.py` - 차선 마스크 생성

**역할**: HSV 색상 기반 차선 검출 (흰색 + 빨간색)

**주요 클래스**: `LaneMaskGenerator`

**주요 메서드**:
- `create_lane_mask(hsv, is_dark)`: 차선 마스크 생성
- `create_adaptive_mask(hsv, original_bgr)`: 적응형 마스크 생성 (밝기 자동 판단)

**HSV 범위**:
- 흰색 (밝은 환경): H(0-180), S(0-30), V(200-255)
- 흰색 (어두운 환경): H(0-180), S(0-50), V(150-255)
- 빨간색: H(0-10, 170-180), S(100-255), V(100-255)

**사용 예시**:
```python
from ai.lane_mask_generator import LaneMaskGenerator

mask_gen = LaneMaskGenerator(brightness_threshold=80)
hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
mask = mask_gen.create_adaptive_mask(hsv, roi)
```

---

### 3. `noise_filter.py` - 노이즈 필터링

**역할**: 빛 반사 노이즈 제거 (원형 → 제거, 선형 → 유지)

**주요 클래스**: `NoiseFilter`

**주요 메서드**:
- `remove_noise(mask)`: 3단계 노이즈 제거
  - 1차: Opening (형태학적 변환)
  - 2차: 컨투어 면적 + 종횡비 필터링
- `apply_morphology(mask, operation)`: 형태학적 변환

**파라미터**:
- `min_area`: 최소 면적 (기본: 100 픽셀)
- `min_aspect_ratio`: 최소 종횡비 (기본: 2.0)

**사용 예시**:
```python
from ai.noise_filter import NoiseFilter

filter = NoiseFilter(min_area=100, min_aspect_ratio=2.0)
clean_mask = filter.remove_noise(mask)
```

---

### 4. `steering_judge.py` - 조향 판단

**역할**: 히스토그램 분석 및 조향 명령 결정

**주요 클래스**: `SteeringJudge`

**주요 메서드**:
- `judge_steering(mask)`: 조향 판단
  - 반환: (command, histogram, confidence)
  - command: "LEFT" | "RIGHT" | "CENTER" | "STOP"

**판단 로직**:
1. 총 픽셀 < 200 → STOP
2. 좌우 차이 < 15% → CENTER (데드존)
3. 좌우 모두 < 100 → CENTER
4. 좌 > 우*1.3 → LEFT
5. 우 > 좌*1.3 → RIGHT

**사용 예시**:
```python
from ai.steering_judge import SteeringJudge

judge = SteeringJudge(threshold_deadzone=0.15, threshold_ratio=1.3)
command, histogram, confidence = judge.judge_steering(clean_mask)
```

---

### 5. `corner_detector.py` - 코너 감지

**역할**: 90도 코너 감지 및 방향 판단

**주요 클래스**: `CornerDetector`

**주요 메서드**:
- `is_corner_detected(mask, histogram)`: 90도 코너 감지
- `judge_corner_direction(lookahead_mask)`: 방향 판단 (LookAhead ROI)

**감지 조건**:
- 픽셀 78% 이상
- 좌중우 균등 분포 (편차 < 20%)

**사용 예시**:
```python
from ai.corner_detector import CornerDetector

detector = CornerDetector()
if detector.is_corner_detected(mask, histogram):
    direction = detector.judge_corner_direction(lookahead_mask)
```

---

### 6. `visualization.py` - 시각화

**역할**: 분석 결과를 이미지에 오버레이

**주요 클래스**: `Visualization`

**주요 메서드**:
- `draw_analysis_overlay(image, command, state, histogram)`: 통합 오버레이
  - 상단 정보 패널 (명령, 상태)
  - 하단 히스토그램 바
  - ROI 경계선
  - 방향 화살표

**사용 예시**:
```python
from ai.visualization import Visualization

viz = Visualization()
result_image = viz.draw_analysis_overlay(image, "LEFT", "NORMAL_DRIVING", histogram)
```

---

### 7. `autonomous_lane_tracker.py` - 메인 클래스 (V2)

**역할**: 모든 모듈을 조합하여 전체 파이프라인 실행

**주요 클래스**: `AutonomousLaneTrackerV2`

**처리 파이프라인**:
```
이미지 입력
  ↓ ImagePreprocessor
1. CLAHE 전처리
  ↓ ImagePreprocessor
2. 가우시안 블러
  ↓ ImagePreprocessor
3. ROI 추출
  ↓ LaneMaskGenerator
5. 차선 마스크 생성
  ↓ NoiseFilter
6. 노이즈 제거
  ↓ SteeringJudge
7. 조향 판단
  ↓ CornerDetector (선택적)
8. 90도 코너 감지
  ↓ Visualization (debug=True)
9. 시각화
  ↓
결과 출력
```

**사용 예시**:
```python
from ai.autonomous_lane_tracker import AutonomousLaneTrackerV2

tracker = AutonomousLaneTrackerV2(
    brightness_threshold=80,
    use_adaptive=True,
    min_noise_area=100,
    min_aspect_ratio=2.0
)

result = tracker.process_frame(image, debug=True)
print(f"명령: {result['command']}")
print(f"히스토그램: {result['histogram']}")
```

---

## 🎯 모듈화의 장점

### 1. 유지보수성 향상
- 각 기능이 독립적인 파일로 분리
- 특정 기능 수정 시 해당 파일만 수정
- 코드 재사용 용이

### 2. 테스트 용이
- 각 모듈을 독립적으로 테스트 가능
- 단위 테스트 작성 쉬움

### 3. 확장성
- 새로운 필터 추가 쉬움
- 다른 프로젝트에서 모듈 재사용 가능

### 4. 가독성
- 각 파일이 단일 책임 원칙 준수
- 파일명만 보고도 역할 파악 가능

---

## 📊 모듈 크기 비교

| 파일 | 라인 수 | 역할 |
|------|--------|------|
| **V1 (단일 파일)** | 594줄 | 전체 기능 |
| **V2 (모듈화)** | | |
| ├── image_preprocessor.py | 68줄 | 전처리 |
| ├── lane_mask_generator.py | 82줄 | 마스크 생성 |
| ├── noise_filter.py | 109줄 | 노이즈 제거 |
| ├── steering_judge.py | 101줄 | 조향 판단 |
| ├── corner_detector.py | 95줄 | 코너 감지 |
| ├── visualization.py | 219줄 | 시각화 |
| └── autonomous_lane_tracker.py | 153줄 | 메인 통합 |
| **합계** | **827줄** | **(+233줄)** |

*추가된 233줄은 문서화 주석 및 개선된 인터페이스*

---

## 🔄 V1에서 V2로 마이그레이션

기존 코드는 그대로 동작합니다. 이미 `app_factory.py`에서 자동으로 V2를 사용합니다.

```python
# 기존 (V1)
from ai.autonomous_lane_tracker import AutonomousLaneTracker
tracker = AutonomousLaneTracker()

# 새로운 (V2) - 인터페이스 동일
from ai.autonomous_lane_tracker import AutonomousLaneTrackerV2
tracker = AutonomousLaneTrackerV2()
```

---

## 🛠️ 커스터마이징

### 파라미터 조정

```python
tracker = AutonomousLaneTrackerV2(
    brightness_threshold=100,  # 밝기 임계값 (기본: 80)
    use_adaptive=True,         # 적응형 HSV (기본: True)
    min_noise_area=150,        # 노이즈 최소 면적 (기본: 100)
    min_aspect_ratio=2.5,      # 종횡비 임계값 (기본: 2.0)
)
```

### 개별 모듈 사용

```python
# 전처리만 사용
from ai.image_preprocessor import ImagePreprocessor
preprocessor = ImagePreprocessor()
enhanced = preprocessor.apply_clahe(image)

# 노이즈 필터만 사용
from ai.noise_filter import NoiseFilter
filter = NoiseFilter(min_area=200)
clean = filter.remove_noise(mask)
```

---

## 📚 참고 문서

- `AUTONOMOUS_GUIDE.md`: 전체 시스템 가이드
- `prod.md`: 알고리즘 설계 문서
- 각 모듈 소스 코드의 docstring

---

**작성일**: 2025-10-22  
**버전**: 2.0  
**작성자**: AI Assistant

