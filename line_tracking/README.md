# 🚗 라인 트래킹 시스템

ESP32-CAM을 사용한 실시간 라인 추적 자율주행 시스템

## 📋 개요

이 시스템은 ESP32-CAM에서 실시간 영상을 받아 OpenCV로 라인을 검출하고, 
검출된 라인의 중심점을 기준으로 좌/우/중앙 방향을 판단하여 차량을 제어합니다.

### 주요 기능

- ✅ **실시간 라인 검출**: Canny Edge + Hough Lines
- ✅ **자동 방향 판단**: 중심점 기반 조향 결정
- ✅ **실시간 시각화**: 디버깅 정보 표시
- ✅ **ESP32 통신**: HTTP API를 통한 제어 명령 전송
- ✅ **모듈형 설계**: 유지보수 및 확장 용이

---

## 🏗️ 시스템 구조

```
line_tracking/
├── __init__.py                    # 패키지 초기화
├── config.py                      # 설정 파일
├── main_line_tracker.py           # 메인 실행기
├── line_detector_module.py        # 라인 검출 모듈
├── direction_judge_module.py      # 방향 판단 모듈
├── visualization_module.py        # 시각화 모듈
└── README.md                      # 이 문서
```

### 모듈 설명

#### 1. `line_detector_module.py` - 라인 검출기
- **역할**: 이미지에서 라인을 검출하고 중심점 계산
- **알고리즘**:
  1. ROI(관심 영역) 추출 (화면 하단)
  2. 그레이스케일 + 블러 전처리
  3. Canny Edge Detection
  4. Hough Lines로 직선 검출
  5. 중심점 계산 (평균)

#### 2. `direction_judge_module.py` - 방향 판단기
- **역할**: 라인 중심점과 화면 중심을 비교하여 방향 결정
- **로직**:
  - 오프셋 < 30px → `center` (직진)
  - 오프셋 < -30px → `left` (좌회전)
  - 오프셋 > 30px → `right` (우회전)

#### 3. `visualization_module.py` - 시각화 모듈
- **역할**: 실시간 디버깅 화면 표시
- **표시 요소**:
  - ROI 경계선 (빨간 수평선)
  - 화면 중심선 (파란 수직선)
  - 라인 중심점 (초록 원)
  - 명령 및 오프셋 텍스트

#### 4. `main_line_tracker.py` - 메인 실행기
- **역할**: 전체 시스템 통합 및 실행
- **흐름**:
  1. ESP32-CAM 연결 확인
  2. 프레임 수신 (폴링 모드)
  3. 라인 검출 → 방향 판단
  4. 명령 전송 → 시각화
  5. 반복

---

## 🚀 사용 방법

### 1. 환경 설정

```bash
# 필수 패키지 설치
pip install opencv-python numpy requests
```

### 2. 설정 파일 수정

`config.py` 파일에서 ESP32 IP 주소를 수정하세요:

```python
# ESP32-CAM IP 주소 (실제 주소로 변경)
ESP32_IP = "192.168.0.65"
```

### 3. 실행

```bash
cd /Users/kimjongphil/Documents/GitHub/ESP_Cam_Free_car/free_car/line_tracking
python main_line_tracker.py
```

### 4. 종료

- 키보드: `q` 키
- 터미널: `Ctrl+C`

---

## ⚙️ 설정 파라미터

### 라인 검출 설정

| 파라미터 | 기본값 | 설명 |
|---------|-------|------|
| `CANNY_LOW_THRESHOLD` | 85 | Canny 하한값 |
| `CANNY_HIGH_THRESHOLD` | 85 | Canny 상한값 |
| `HOUGH_THRESHOLD` | 10 | Hough 변환 임계값 |
| `MIN_LINE_LENGTH` | 10 | 최소 라인 길이 (픽셀) |
| `MAX_LINE_GAP` | 10 | 최대 라인 간격 (픽셀) |
| `ROI_BOTTOM_RATIO` | 0.5 | ROI 하단 비율 (0.0~1.0) |

### 방향 판단 설정

| 파라미터 | 기본값 | 설명 |
|---------|-------|------|
| `DEADZONE_THRESHOLD` | 30 | 데드존 임계값 (픽셀) |
| `STRONG_TURN_THRESHOLD` | 80 | 강한 회전 임계값 (픽셀) |

### 디버깅 설정

| 파라미터 | 기본값 | 설명 |
|---------|-------|------|
| `SHOW_DEBUG_WINDOW` | True | 디버그 창 표시 |
| `SHOW_PROCESSED_IMAGE` | True | 처리된 이미지 표시 |
| `LOG_LEVEL` | "INFO" | 로그 레벨 |
| `ENABLE_COMMAND_SEND` | True | 명령 전송 활성화 |

---

## 🔧 파라미터 튜닝 가이드

### 라인이 검출되지 않을 때

```python
# config.py 수정
CANNY_LOW_THRESHOLD = 50      # 더 낮춰서 더 많은 엣지 검출
CANNY_HIGH_THRESHOLD = 100
HOUGH_THRESHOLD = 5           # 더 낮춰서 더 많은 라인 검출
ROI_BOTTOM_RATIO = 0.3        # ROI 영역 확대
```

### 너무 민감하게 반응할 때

```python
# config.py 수정
DEADZONE_THRESHOLD = 50       # 데드존 확대
MIN_LINE_LENGTH = 20          # 최소 라인 길이 증가
```

### 어두운 환경에서

ESP32-CAM의 밝기를 조절하세요:

```bash
# LED 켜기
curl "http://192.168.0.65/led?state=on"

# 밝기 증가
curl "http://192.168.0.65/camera?param=brightness&value=2"

# AGC 게인 증가
curl "http://192.168.0.65/camera?param=agc_gain&value=10"
```

---

## 📊 디버깅 화면 설명

### 원본 화면 (왼쪽)

- **빨간 수평선**: ROI 경계선 (이 아래만 분석)
- **파란 수직선**: 화면 중심선
- **초록 원**: 검출된 라인의 중심점
- **노란 선**: 중심점과 화면 중심의 거리
- **명령 텍스트**: 현재 전송된 명령 (LEFT/RIGHT/CENTER)
- **오프셋 텍스트**: 중심으로부터의 거리

### 처리 화면 (오른쪽)

- Canny Edge Detection 결과
- 흰색: 검출된 엣지

---

## 🎯 알고리즘 흐름

```
1. ESP32-CAM에서 프레임 수신
   ↓
2. ROI 추출 (화면 하단 50%)
   ↓
3. 그레이스케일 → 블러 → Canny Edge
   ↓
4. Hough Lines로 직선 검출
   ↓
5. 모든 직선의 중심점 평균 계산
   ↓
6. 화면 중심과 비교하여 방향 판단
   - offset < -30px → LEFT
   - offset > +30px → RIGHT
   - -30px ~ +30px → CENTER
   ↓
7. ESP32에 명령 전송 (HTTP GET)
   ↓
8. 화면에 시각화 표시
   ↓
9. 반복
```

---

## 🐛 문제 해결

### Q1: ESP32-CAM 연결 실패

```bash
# 1. 핑 테스트
ping 192.168.0.65

# 2. 상태 확인
curl http://192.168.0.65/status

# 3. 브라우저에서 스트림 확인
http://192.168.0.65/stream
```

### Q2: 라인이 검출되지 않음

1. **밝기 확인**: LED를 켜거나 조명 개선
2. **ROI 확인**: `ROI_BOTTOM_RATIO` 조정
3. **Canny 임계값**: 낮춰서 더 많은 엣지 검출
4. **디버그 창**: 처리된 이미지에서 엣지 확인

### Q3: 차량이 잘못된 방향으로 회전

1. **카메라 방향**: 카메라가 바르게 장착되었는지 확인
2. **데드존 조정**: `DEADZONE_THRESHOLD` 증가
3. **로그 확인**: 오프셋 값이 올바른지 확인

### Q4: FPS가 너무 낮음

```python
# config.py 수정
CAPTURE_FPS = 5               # FPS 낮춤 (더 안정적)
SHOW_PROCESSED_IMAGE = False  # 처리 이미지 표시 끔
LOG_LEVEL = "WARNING"         # 로그 레벨 올림
```

---

## 📈 성능 최적화 팁

### 1. FPS 향상

- `SHOW_PROCESSED_IMAGE = False`
- `LOG_LEVEL = "WARNING"`
- ROI 영역 축소

### 2. 안정성 향상

- `DEADZONE_THRESHOLD` 증가
- `MIN_LINE_LENGTH` 증가
- FPS 낮춤 (5-10fps)

### 3. 정확도 향상

- 조명 개선
- 라인 대비 증가 (흰색 라인 + 검은 바닥)
- ROI 영역 최적화

---

## 📚 참고 자료

### ESP32-CAM API

- `/stream`: 영상 스트리밍 (MJPEG)
- `/capture`: 단일 이미지 캡처 (JPEG)
- `/control?cmd=left`: 좌회전
- `/control?cmd=right`: 우회전
- `/control?cmd=center`: 직진
- `/control?cmd=stop`: 정지
- `/led?state=on`: LED 켜기

자세한 API 문서: [../Readme.md](../Readme.md)

### OpenCV 함수

- `cv2.Canny()`: 엣지 검출
- `cv2.HoughLinesP()`: 직선 검출
- `cv2.GaussianBlur()`: 노이즈 제거

---

## 🔄 업데이트 로그

- **2025-11-30**: 초기 버전 작성
  - Canny + Hough Lines 기반 라인 검출
  - 중심점 계산 알고리즘
  - 실시간 시각화
  - ESP32 통신 통합

---

## 👥 기여

버그 리포트 및 개선 제안은 이슈로 등록해주세요.

---

## 📄 라이선스

MIT License

