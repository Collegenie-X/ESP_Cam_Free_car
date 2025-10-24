# 🚗 ESP32-CAM 자율주행 시스템 완전 가이드

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [핵심 기능](#핵심-기능)
3. [빠른 시작](#빠른-시작)
4. [세부 설명](#세부-설명)
5. [파라미터 조정](#파라미터-조정)
6. [문제 해결](#문제-해결)

---

## 시스템 개요

ESP32-CAM의 저품질 이미지에서도 안정적으로 작동하는 **하이브리드 자율주행 시스템**입니다.

### 주요 특징
- ✅ **강력한 이미지 전처리** (햇빛 반사 제거!)
- ✅ **다층 세그멘테이션** (도로, 도로선, 장애물)
- ✅ **하이브리드 방향 결정** (상황별 최적 알고리즘)
- ✅ **90도 도로선 대응** (횡단보도, T자 교차로)
- ✅ **실시간 모터 제어** (GET 방식 통신)

---

## 핵심 기능

### 1. 이미지 전처리 파이프라인

```
원본 이미지 (320x240, 어둡고 노이즈 많음)
    ↓
CLAHE (대비 향상) → 어두운 부분 밝게, 밝은 부분 어둡게
    ↓
햇빛 반사 제거 ★ → 과포화 영역 주변 픽셀로 보간
    ↓
노이즈 제거 → Non-local Means Denoising
    ↓
샤프닝 → 도로선 엣지 강조
    ↓
선명한 이미지 → 세그멘테이션
```

### 2. 3진 세그멘테이션

| 값 | 의미 | 색상 | 가중치 |
|----|------|------|--------|
| 0 | 검정색 도로 | 어두운 회색 | x0 |
| 1 | 기타 색상 (장애물) | 노란색 | x1 |
| 2 | 도로선 (흰색/회색/빨간색) | 빨간색 | x5 ⭐ |

### 3. 다층 ROI 가중치

화면을 상/중/하로 나누어 가까운 곳에 더 큰 가중치:

```
┌─────────────────────┐
│   상단 40% (x1)     │ 멀고 노이즈 많음
├─────────────────────┤
│   중단 30% (x2)     │ 중간 거리
├─────────────────────┤
│   하단 30% (x3)     │ 가깝고 정확 ⭐
└─────────────────────┘
```

### 4. 하이브리드 방향 결정

```python
if 90도_도로선_감지:
    더_넓은_쪽으로_회전()
elif 차선_명확 (>5%):
    차선_위치_기반_방향()  # 곡선 대응 우수
elif 장애물_많음 (>30%):
    장애물_회피_모드()  # 빈 공간 찾기
elif 차선_있음 (>2%):
    가중_히스토그램_방향()  # 기본 모드
else:
    이전_명령_유지() or 정지()
```

---

## 빠른 시작

### 1. 환경 설정

```bash
cd /Users/kimjongphil/Documents/GitHub/ESP_Cam_Free_car/free_car
source venv/bin/activate
```

### 2. Config 확인 및 수정

`realtime_analysis/config.py` 파일에서 ESP32 IP 주소 확인:

```python
ESP32_IP = "192.168.0.65"  # 실제 IP로 변경
```

### 3. 자율주행 실행

```bash
python3 autonomous_drive.py
```

### 4. 키보드 컨트롤

| 키 | 기능 |
|----|------|
| **A** | 자율주행 모드 ON/OFF |
| **O** | 장애물 모드 ON/OFF |
| **L** | LED ON/OFF |
| **Q** 또는 ESC | 종료 |

---

## 세부 설명

### 이미지 전처리 옵션

`config.py`에서 조정 가능:

```python
# 전처리 활성화/비활성화
ENABLE_IMAGE_ENHANCEMENT = True  # False로 하면 원본 사용

# 각 단계 개별 제어
BRIGHTNESS_BOOST = 20        # 밝기 추가 (0-100)
CONTRAST_BOOST = 1.3         # 대비 배율 (1.0-2.0)
ENABLE_CLAHE = True          # 적응형 히스토그램 평활화
ENABLE_SHARPENING = True     # 엣지 샤프닝
ENABLE_DENOISING = True      # 노이즈 제거
```

### 세그멘테이션 임계값 조정

```python
# 검정색 도로 범위
BLACK_V_MIN = 0      # 최소 밝기
BLACK_V_MAX = 60     # 최대 밝기
BLACK_S_MAX = 80     # 최대 채도

# 회색 도로선 범위
GRAY_V_MIN = 50      # 최소 밝기
GRAY_V_MAX = 150     # 최대 밝기
GRAY_S_MAX = 50      # 최대 채도

# 빨간색 차선 범위
RED_H_LOW_MIN = 0    # 빨강 범위1 시작
RED_H_LOW_MAX = 15   # 빨강 범위1 끝
RED_H_HIGH_MIN = 155 # 빨강 범위2 시작
RED_H_HIGH_MAX = 180 # 빨강 범위2 끝
RED_S_MIN = 80       # 최소 채도
RED_V_MIN = 80       # 최소 밝기
```

**조정 가이드:**
- 검정색이 너무 많이 감지되면: `BLACK_V_MAX` 감소
- 도로선이 감지 안되면: `GRAY_V_MAX` 증가, `GRAY_S_MAX` 증가
- 빨간색 차선 감지 강화: `RED_S_MIN`, `RED_V_MIN` 감소

### 자율주행 파라미터

```python
# 방향 결정 임계값
STEERING_CENTER_THRESHOLD = 500   # abs(left-right) > 이 값일 때만 회전
STEERING_MIN_CONFIDENCE = 0.3     # 최소 신뢰도 (낮으면 명령 안 보냄)

# 90도 도로선 감지
HORIZONTAL_LINE_THRESHOLD = 0.7   # 수평선 비율
HORIZONTAL_LINE_MIN_LENGTH = 50   # 최소 선 길이 (픽셀)
```

---

## 파라미터 조정

### 트랙바 (실시간 조정 가능)

실행 중 화면 상단 트랙바로 조정:

1. **White V Min** (0-255)
   - 흰색 차선 감지 최소 밝기
   - 높일수록 더 밝은 것만 감지
   - 추천: 180-220

2. **White S Max** (0-100)
   - 흰색 차선 최대 채도
   - 낮을수록 순수한 흰색만
   - 추천: 20-40

3. **Min Pixels** (0-1000)
   - 최소 픽셀 수
   - 이보다 적으면 정지
   - 추천: 100-300

4. **Brightness** (-2 ~ +2)
   - ESP32 카메라 밝기
   - 어두우면 +1 또는 +2

5. **Contrast** (-2 ~ +2)
   - ESP32 카메라 대비
   - 추천: 0 또는 +1

6. **Saturation** (-2 ~ +2)
   - ESP32 카메라 채도
   - 추천: 0

---

## 문제 해결

### 1. 차선 감지가 안됨

**증상:** 히스토그램이 모두 0 또는 매우 작음

**해결:**
1. `White V Min` 낮추기 (200 → 180 → 150)
2. `White S Max` 높이기 (30 → 50 → 70)
3. `config.py`에서 `GRAY_V_MAX` 증가 (150 → 180)
4. ESP32 카메라 `Brightness` 증가

### 2. 햇빛 반사로 오작동

**증상:** 밝은 부분을 차선으로 오인

**해결:**
- 자동으로 처리됨 (inpainting)
- 효과가 약하면 `image_processor.py`의 `_suppress_specular_highlights` 함수에서:
  ```python
  reflection_mask = ((v > 245) & (s < 15))
  # → v 값을 낮추기 (245 → 240 → 235)
  ```

### 3. 방향이 너무 자주 바뀜

**증상:** 떨림, 불안정

**해결:**
1. `STEERING_CENTER_THRESHOLD` 증가 (500 → 800 → 1000)
2. `autonomous_driver.py`의 `buffer_size` 증가 (3 → 5 → 7)

### 4. 곡선 도로에서 이탈

**증상:** 직선은 괜찮지만 곡선에서 실패

**해결:**
- 자동으로 차선 위치 기반 모드로 전환됨
- 차선이 충분히 감지되는지 확인 (트랙바 조정)

### 5. 모터 제어 안됨

**증상:** 화면은 보이지만 차가 안 움직임

**체크리스트:**
1. ESP32 IP 주소 확인:
   ```python
   # config.py
   ESP32_IP = "192.168.0.65"  # 실제 IP
   ```

2. 모터 제어 URL 확인:
   ```python
   MOTOR_CONTROL_URL = f"http://{ESP32_IP}/control"
   ```

3. 자율주행 모드 ON 확인:
   - 화면 하단에 `[AUTO]` 표시되어야 함
   - 'A' 키를 눌러 활성화

4. 터미널 로그 확인:
   ```
   ✅ Motor: LEFT (conf: 0.85)
   ✅ Motor: CENTER (conf: 0.92)
   ```

5. 수동으로 테스트:
   ```bash
   curl "http://192.168.0.65/control?cmd=left"
   curl "http://192.168.0.65/control?cmd=center"
   curl "http://192.168.0.65/control?cmd=right"
   curl "http://192.168.0.65/control?cmd=stop"
   ```

---

## 성능 최적화

### 속도 향상

**목표 FPS 조정:**
```python
# config.py
TARGET_FPS = 3  # 안정성 우선
# 또는
TARGET_FPS = 5  # 속도 우선 (노이즈 제거 비활성화 추천)
```

**전처리 단계 비활성화:**
```python
ENABLE_DENOISING = False  # 가장 느린 단계
ENABLE_SHARPENING = False
```

### 정확도 향상

**전처리 강화:**
```python
BRIGHTNESS_BOOST = 30  # 더 밝게
CONTRAST_BOOST = 1.5   # 대비 강화
```

**가중치 증가:**
```python
# lane_detector.py 수정
LANE_WEIGHT = 10  # 5 → 10
```

---

## 📊 실행 결과 예시

```
🚗 ESP32-CAM Autonomous Driving System
======================================================================
ESP32-CAM IP: 192.168.0.65

✅ All modules initialized

🎮 Controls:
  - Press 'A' to toggle AUTONOMOUS mode
  - Press 'O' to toggle OBSTACLE mode
  - Press 'L' to toggle LED
  - Press 'Q' or ESC to quit

🚀 Starting autonomous driving... (Mode: ON)

✅ Frame 30: Capture OK (41ms)
✅ Motor: CENTER (conf: 0.92)
✅ Motor: LEFT (conf: 0.78)
✅ Motor: LEFT (conf: 0.85)
✅ Motor: CENTER (conf: 0.94)
```

---

## 🔬 알고리즘 상세

### 히스토그램 계산 예시

```
화면을 좌/중/우로 3등분:

Left    │ Center  │ Right
───────┼─────────┼───────
        │         │
   O    │    L    │   O
   O    │    L    │   O
   O    │    L    │
───────┼─────────┼───────

O = 장애물 (1점)
L = 도로선 (5점)

계산 (다층 ROI 적용):
하단 30%: (1*3 + 1*3 + 1*3) + (5*3) = 24점
중단 30%: (1*2 + 1*2 + 1*2) + (5*2) = 16점
상단 40%: (1 + 1 + 1) + (5) = 8점

Left = 7점
Center = 38점 ⭐
Right = 7점

→ 결정: CENTER
```

---

## 📝 파일 구조

```
free_car/
├── autonomous_drive.py          # 메인 실행 파일 ⭐
├── realtime_analysis/
│   ├── config.py                # 모든 설정
│   ├── capture_client.py        # ESP32 통신
│   ├── image_processor.py       # 전처리 + 세그멘테이션
│   ├── lane_detector.py         # 히스토그램 + 방향 판단
│   ├── autonomous_driver.py     # 하이브리드 자율주행
│   └── ui_components.py         # UI 표시
└── AUTONOMOUS_DRIVING_GUIDE.md  # 이 파일
```

---

## 🚀 다음 단계

### 개선 아이디어
1. **AI 모델 통합** (MobileNet-SSD)
2. **PID 제어** (부드러운 조향)
3. **장애물 거리 측정** (초음파 센서)
4. **주행 경로 기록** (로그 분석)

---

## 📞 문의 및 피드백

문제가 발생하거나 개선 아이디어가 있으시면 이슈로 남겨주세요!

---

**Made with ❤️ for ESP32-CAM Autonomous Driving**


