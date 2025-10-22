# 🚀 빠른 시작 가이드

## 1️⃣ 설치 (1분)

```bash
cd free_car

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate    # Windows

# 라이브러리 설치
pip install -r requirements.txt
```

## 2️⃣ 설정 (30초)

```bash
# .env 파일이 이미 생성되어 있습니다
# ESP32-CAM IP 주소 확인 후 필요시 수정
cat .env
```

## 3️⃣ 실행 (즉시)

### 방법 1: 직접 실행
```bash
python main.py
```

### 방법 2: 스크립트 사용 (Mac/Linux)
```bash
./run.sh
```

## ⌨️ 조작법

- **종료**: 미리보기 창에서 `q` 키 또는 터미널에서 `Ctrl+C`
- **설정 변경**: `.env` 파일 수정 후 재실행

## 📊 출력 화면

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
```

- **L/C/R**: 왼쪽/중앙/오른쪽 차선 픽셀 수
- **명령**: ESP32로 전송되는 제어 명령 (LEFT/RIGHT/CENTER/STOP)
- **백분율**: 명령의 신뢰도

## 🔧 설정 조정

### FPS 변경
```env
TARGET_FPS=10  # 더 빠르게
TARGET_FPS=3   # 더 안정적으로
```

### 밝기 조정
```env
BRIGHTNESS_THRESHOLD=100  # 밝은 환경
BRIGHTNESS_THRESHOLD=60   # 어두운 환경
```

### 미리보기 끄기 (성능 향상)
```env
SHOW_PREVIEW=False
```

## ❓ 문제 해결

### ESP32-CAM 연결 안 됨
```bash
# 브라우저에서 테스트
open http://192.168.0.65/stream
```

### 차선이 감지 안 됨
- 조명 확인
- `BRIGHTNESS_THRESHOLD` 값 조정
- 카메라 각도 조정

### 라이브러리 오류
```bash
pip install --upgrade -r requirements.txt
```

## 📁 프로젝트 구조

```
free_car/
├── main.py              ← 여기서 시작!
├── requirements.txt
├── .env                 ← 설정 파일
├── config/              # 설정
├── core/                # 자율주행 드라이버
├── services/            # ESP32 통신 + 차선 추적
└── utils/               # 로깅
```

## 🎯 다음 단계

1. **알고리즘 이해**: `README.md` 읽기
2. **설정 최적화**: `.env` 파일 조정
3. **코드 수정**: `services/lane_tracking_service.py` 개선

---

**문제가 있나요?** → `autonomous_driver.log` 파일 확인

