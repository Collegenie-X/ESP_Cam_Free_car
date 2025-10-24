# 🚗 ESP32-CAM 자율주행차 (OpenCV 버전)

Flask 없이 OpenCV와 requests만 사용하는 간단하고 효율적인 자율주행 시스템입니다.

## 📁 프로젝트 구조

```
free_car/
├── main.py                        # 메인 실행 파일 (자율주행)
├── realtime_analysis.py           # ⭐ 실시간 분석 도구 (권장)
├── canny_ex.py                    # Canny Edge 분석 도구
├── requirements.txt               # 필수 라이브러리
├── .env.example                   # 환경 변수 예시
├── README.md                      # 이 파일
├── REALTIME_ANALYSIS_GUIDE.md     # 실시간 분석 가이드
├── config/                        # 설정 모듈
│   ├── __init__.py
│   └── settings.py               # 시스템 설정
├── core/                          # 핵심 모듈
│   ├── __init__.py
│   └── autonomous_driver.py      # 자율주행 드라이버
├── services/                      # 서비스 모듈
│   ├── __init__.py
│   ├── esp32_communication.py    # ESP32 통신
│   ├── lane_tracking_service.py  # 차선 추적
│   └── control_panel.py          # 제어 패널 (Tkinter)
└── utils/                         # 유틸리티
    ├── __init__.py
    └── logger.py                 # 로깅 설정
```

## 🚀 빠른 시작

### 1. 가상환경 생성 및 활성화

```bash
cd free_car
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate    # Windows
```

### 2. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 설정

```bash
cp .env.example .env
# .env 파일을 열어 ESP32-CAM IP 주소 수정
```

### 4. 실행

```bash
python main.py
```

## ⚙️ 설정 (.env)

```env
# ESP32-CAM 설정
ESP32_IP=192.168.0.65
ESP32_PORT=80

# 자율주행 설정
TARGET_FPS=5
BRIGHTNESS_THRESHOLD=80
MIN_LANE_PIXELS=200

# 디버그 모드
DEBUG_MODE=True
SHOW_PREVIEW=True
```

## 🎮 사용법

### 📸 실시간 분석 도구 (권장) ⭐

파라미터를 조정하며 실시간으로 차선 인식 결과를 확인할 수 있습니다.

```bash
# 1초당 3프레임 캡처 및 분석
python realtime_analysis.py
```

**특징:**
- 🖼️ 원본 이미지와 분석 결과 동시 표시
- 🎚️ 트랙바로 실시간 파라미터 조정 (White V Min, White S Max, Min Pixels)
- ⏱️ 캡처 시간, 분석 시간 표시
- 📊 조향 명령, 히스토그램, 신뢰도 표시

**자세한 사용법**: [REALTIME_ANALYSIS_GUIDE.md](REALTIME_ANALYSIS_GUIDE.md)

---

### 🚗 자율주행 실행

최적 파라미터를 찾은 후 실제 자율주행을 실행합니다.

1. **ESP32-CAM 연결 확인**
   - ESP32-CAM이 켜져 있고 네트워크에 연결되어 있는지 확인
   - 브라우저에서 `http://192.168.0.65/stream` 접속하여 스트림 확인

2. **프로그램 실행**
   ```bash
   python main.py
   ```

3. **종료 방법**
   - 미리보기 창에서 `q` 키 누르기
   - 터미널에서 `Ctrl+C` 누르기

---

### 🔬 Canny Edge 분석 도구

스트림 영상에서 Canny Edge 검출을 실시간으로 테스트합니다.

```bash
python canny_ex.py
```

## 📊 출력 예시

```
============================================================
🚗 ESP32-CAM 자율주행차 시스템
============================================================
ESP32-CAM 주소: http://192.168.0.65:80
목표 FPS: 5
디버그 모드: True
화면 미리보기: True
============================================================

✅ ESP32-CAM 연결 성공

[   2.1s] FPS:  5.0 | L: 120 C: 450 R:  80 | 명령: CENTER ( 62.5%)
[   4.2s] FPS:  5.1 | L: 200 C: 300 R:  50 | 명령: LEFT   ( 80.0%)
[   6.3s] FPS:  5.0 | L:  60 C: 280 R: 210 | 명령: RIGHT  ( 77.8%)
```

## 🔧 주요 기능

### 1. ESP32 통신 (`services/esp32_communication.py`)
- HTTP GET 방식으로 ESP32-CAM과 통신
- 스트림 수신 및 프레임 추출
- 모터 제어 명령 전송

### 2. 차선 추적 (`services/lane_tracking_service.py`)
- CLAHE 전처리
- HSV 색상 공간 기반 차선 검출
- 히스토그램 분석
- 조향 판단 (LEFT/RIGHT/CENTER/STOP)

### 3. 자율주행 드라이버 (`core/autonomous_driver.py`)
- 전체 시스템 통합
- FPS 제한 (기본 5fps)
- 실시간 통계 출력
- 디버그 미리보기

## 🎯 차선 추적 알고리즘

1. **CLAHE 전처리**: 명암 대비 향상
2. **가우시안 블러**: 노이즈 제거
3. **ROI 추출**: 하단 25% 영역만 사용
4. **HSV 변환**: 색상 기반 차선 검출
5. **노이즈 필터링**: 형태학적 연산
6. **히스토그램 계산**: 좌/중/우 3등분
7. **조향 판단**: 데드존 및 편향 비율 적용

## 📝 로그 파일

프로그램 실행 시 `autonomous_driver.log` 파일에 상세 로그가 기록됩니다.

```bash
tail -f autonomous_driver.log  # 실시간 로그 확인
```

## 🐛 문제 해결

### ESP32-CAM 연결 실패
```bash
# 연결 테스트
curl http://192.168.0.65/status
```

### 라이브러리 오류
```bash
# 라이브러리 재설치
pip install --upgrade -r requirements.txt
```

### 화면이 안 나옴
- `SHOW_PREVIEW=False`로 설정하면 미리보기 없이 실행됩니다

## 💡 팁

1. **FPS 조정**: `.env`에서 `TARGET_FPS` 값 변경
2. **밝기 조정**: `BRIGHTNESS_THRESHOLD` 값 조정 (0-255)
3. **디버그 끄기**: `DEBUG_MODE=False`로 성능 향상

## 🔄 업데이트 내역

### v1.1.0 (2025-10-24) ⭐
- ✅ **실시간 분석 도구 추가** (`realtime_analysis.py`)
  - 1초당 3프레임 캡처 및 분석
  - 원본 이미지와 분석 결과 동시 표시
  - 트랙바로 실시간 파라미터 조정
  - 캡처/분석 시간 측정 및 표시
- ✅ ESP32-CAM capture 속도 최적화
  - XCLK 20MHz, QVGA 320x240, Q=10
  - 평균 캡처 시간: 90-120ms
  - 프레임 버퍼 관리 개선
- ✅ HTTP Keep-Alive 연결 최적화
- ✅ 상세 사용 가이드 추가

### v1.0.0 (2025-10-22)
- ✅ 초기 버전 릴리스
- ✅ OpenCV 기반 차선 추적
- ✅ ESP32-CAM HTTP 통신
- ✅ 실시간 스트리밍 및 제어
- ✅ 모듈화된 구조

## 📚 참고

- ESP32-CAM API: `../Readme.md`
- 알고리즘 설계: `prod.md`

---

**작성일**: 2025-10-22  
**버전**: 1.0.0

