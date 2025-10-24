# 실시간 자율주행 분석 모듈

ESP32-CAM을 사용한 실시간 차선 검출 및 조향 판단 시스템

---

## 📁 폴더 구조

```
realtime_analysis/
├── __init__.py              # 패키지 초기화
├── config.py                # 설정 파일 (ESP32 주소, FPS, 파라미터)
├── capture_client.py        # ESP32-CAM 캡처 클라이언트
├── image_processor.py       # 이미지 전처리 및 차선 마스크 생성
├── lane_detector.py         # 차선 검출 및 조향 판단
├── ui_components.py         # UI 컴포넌트 (트랙바, 오버레이)
├── analyzer.py              # 메인 분석기 클래스
└── README.md                # 이 파일
```

---

## 🚀 사용법

### 기본 실행

```bash
cd /Users/kimjongphil/Documents/GitHub/ESP_Cam_Free_car/free_car
python realtime_analysis_v2.py
```

### 프로그래밍 방식 사용

```python
from realtime_analysis import RealtimeAnalyzer

# 분석기 생성
analyzer = RealtimeAnalyzer()

# 초기 설정
analyzer.setup()

# 실행
analyzer.run()
```

---

## 📦 모듈 설명

### 1. `config.py` - 설정 파일

모든 설정값을 한 곳에서 관리합니다.

**주요 설정:**
- `ESP32_IP`: ESP32-CAM IP 주소
- `TARGET_FPS`: 목표 프레임률 (3 FPS)
- `DEFAULT_HSV_PARAMS`: 차선 검출 기본 파라미터
- `COLORS`: UI 색상 정의

**수정 방법:**
```python
# config.py에서 직접 수정
ESP32_IP = "192.168.0.65"  # 사용자 환경에 맞게 변경
TARGET_FPS = 3
```

---

### 2. `capture_client.py` - 캡처 클라이언트

ESP32-CAM의 `/capture` 엔드포인트에서 이미지를 가져옵니다.

**주요 기능:**
- HTTP Keep-Alive로 연결 재사용
- 청크 단위 데이터 수신
- 자동 오류 처리 및 재시도
- 통계 추적 (성공/실패)

**사용 예시:**
```python
from realtime_analysis import CaptureClient

client = CaptureClient()
image, capture_time = client.capture_frame()

if image is not None:
    print(f"캡처 성공! 시간: {capture_time:.1f}ms")

# 통계 확인
stats = client.get_statistics()
print(f"성공률: {stats['success_rate']:.1f}%")
```

---

### 3. `image_processor.py` - 이미지 처리

이미지 전처리 및 차선 마스크 생성을 담당합니다.

**주요 기능:**
- CLAHE 적용 (명암 향상)
- ROI 추출 (하단 25%)
- 흰색/빨간색 차선 검출
- 노이즈 제거 (모폴로지 연산)

**사용 예시:**
```python
from realtime_analysis import ImageProcessor

processor = ImageProcessor()

# 전처리
blurred = processor.preprocess_image(image)

# ROI 추출
roi, roi_y_start = processor.extract_roi(blurred)

# 차선 마스크 생성
mask = processor.create_lane_mask(roi, white_v_min=200, white_s_max=30)
```

---

### 4. `lane_detector.py` - 차선 검출 및 조향 판단

히스토그램 분석을 통한 조향 명령 생성을 담당합니다.

**주요 기능:**
- 히스토그램 계산 (좌/중/우 3등분)
- 조향 판단 (left, right, center, stop)
- 신뢰도 계산

**사용 예시:**
```python
from realtime_analysis import LaneDetector

detector = LaneDetector()

# 히스토그램 계산
histogram = detector.calculate_histogram(mask)
print(histogram)  # {'left': 1500, 'center': 3000, 'right': 500}

# 조향 판단
command, confidence = detector.judge_steering(histogram, min_pixels=200)
print(f"명령: {command}, 신뢰도: {confidence:.2f}")
```

---

### 5. `ui_components.py` - UI 컴포넌트

트랙바, 오버레이, 화면 표시를 담당합니다.

**주요 기능:**
- 트랙바 생성 (파라미터 실시간 조정)
- 분석 오버레이 그리기
- 시간 정보 표시 (캡처/분석/전체 시간)
- FPS 표시

**사용 예시:**
```python
from realtime_analysis import UIComponents

ui = UIComponents()

# 트랙바 생성
ui.create_trackbars(initial_values, callback)

# 현재 값 가져오기
params = ui.get_trackbar_values()

# 오버레이 그리기
overlay = ui.draw_analysis_overlay(
    image, mask, roi_y_start, histogram, command, confidence
)

# 화면 표시
ui.show_combined_view(original, overlay)
```

---

### 6. `analyzer.py` - 메인 분석기

모든 모듈을 통합하여 실시간 분석을 실행합니다.

**주요 기능:**
- 모듈 통합 및 조율
- FPS 제어 (3 FPS)
- 메인 루프 실행
- 통계 출력

**사용 예시:**
```python
from realtime_analysis import RealtimeAnalyzer

analyzer = RealtimeAnalyzer()
analyzer.setup()
analyzer.run()
```

---

## 🎯 조향 판단 로직

### 히스토그램 계산
화면을 좌/중/우 3등분하여 각 영역의 차선 픽셀 수를 계산합니다.

### 판단 기준

1. **STOP**: 전체 픽셀 수가 최소 임계값보다 적으면 정지
2. **CENTER**: 좌우 차이가 데드존(15%) 이내면 직진
3. **LEFT**: 왼쪽이 오른쪽의 1.3배 이상이면 좌회전
4. **RIGHT**: 오른쪽이 왼쪽의 1.3배 이상이면 우회전

### 신뢰도 계산
우세한 쪽의 비율을 신뢰도로 계산합니다.

---

## ⚙️ 설정 가이드

### ESP32-CAM IP 주소 변경

`config.py` 파일에서 수정:
```python
ESP32_IP = "192.168.0.65"  # 실제 ESP32 IP로 변경
```

### FPS 변경

`config.py` 파일에서 수정:
```python
TARGET_FPS = 5  # 3에서 5로 변경
```

### 차선 검출 파라미터 변경

**방법 1: 실시간 조정 (트랙바 사용)**
- 프로그램 실행 중 트랙바를 움직여서 조정

**방법 2: 기본값 변경**
`config.py` 파일에서 수정:
```python
DEFAULT_HSV_PARAMS = {
    "white_v_min": 180,  # 200에서 180으로 변경
    "white_s_max": 40,   # 30에서 40으로 변경
    "min_pixels": 150,   # 200에서 150으로 변경
}
```

---

## 🛠 확장 가이드

### 새로운 차선 색상 추가

`image_processor.py`의 `create_lane_mask()` 수정:

```python
def create_lane_mask(self, roi, white_v_min, white_s_max):
    # 기존 코드...
    
    # 노란색 차선 추가
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # 통합 마스크에 추가
    mask = cv2.bitwise_or(mask, mask_yellow)
    
    return mask
```

### 조향 판단 로직 수정

`lane_detector.py`의 `judge_steering()` 수정:

```python
def judge_steering(self, histogram, min_pixels):
    # 기존 코드...
    
    # 급회전 판단 추가
    if left_ratio > right_ratio * 2.0:
        return "sharp_left", confidence
    
    # 기존 로직...
```

---

## 📊 성능 최적화

### 현재 성능
- 캡처 속도: 평균 200-300ms
- 분석 속도: 평균 20-30ms
- 전체 속도: 평균 250-350ms (2.8-4 FPS)

### 최적화 팁

1. **해상도 낮추기** (Arduino 측)
   - QVGA (320x240) → QQVGA (160x120)

2. **JPEG 품질 조정** (Arduino 측)
   - 품질 10 → 15 (속도↑, 화질↓)

3. **ROI 영역 축소**
   - `config.py`에서 `ROI_BOTTOM_RATIO` 증가 (0.75 → 0.8)

4. **노이즈 제거 생략**
   - `image_processor.py`에서 `_remove_noise()` 호출 제거

---

## 🐛 문제 해결

### 이미지가 너무 어두워요
1. Arduino 측 카메라 설정 확인 (`camera_init.h`)
2. 트랙바에서 `White V Min` 낮추기 (200 → 150)

### 캡처 속도가 느려요
1. ESP32-CAM 네트워크 연결 확인
2. `capture_client.py`에서 `CAPTURE_TIMEOUT` 줄이기
3. Arduino 측 최적화 적용 확인

### 조향 판단이 불안정해요
1. 트랙바에서 `Min Pixels` 조정
2. `config.py`에서 `DEADZONE_RATIO` 증가 (0.15 → 0.2)

---

## 📝 라이선스

MIT License

---

## 👤 작성자

ESP_Cam_Free_car 프로젝트 팀

---

## 🔗 관련 문서

- [Arduino 최적화 가이드](../../arduino/free_car/QUICK_OPTIMIZATION_GUIDE.md)
- [프로젝트 README](../README.md)

