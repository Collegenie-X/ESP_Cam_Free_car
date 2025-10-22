# ESP32-CAM 자율주행차 Flask 모니터링 시스템

Flask를 이용한 ESP32-CAM 자율주행차 웹 모니터링 인터페이스입니다.

## 🚀 주요 기능

- 📹 **실시간 영상 모니터링**: ESP32-CAM의 영상을 폴링 방식으로 모니터링 (ESP32 부하 최소화)
- 🎮 **모터 제어**: 웹 인터페이스를 통한 직관적인 모터 제어 (전진/후진/좌회전/우회전/정지)
- ⚡ **속도 제어**: 실시간 속도 증감 제어
- 💡 **LED 제어**: LED 토글 스위치로 직관적인 제어
- 📷 **카메라 설정**: 밝기, 대비, AGC 게인 등 실시간 조정
- 📊 **실시간 상태 모니터링**: 모터 상태, LED 상태, 속도, 카메라 설정 등
- 📝 **활동 로그**: 모든 제어 활동 실시간 로깅
- ⌨️ **키보드 제어**: 방향키와 단축키로 빠른 제어
- 🎨 **3열 레이아웃**: 카메라/상태, 제어, 설정을 효율적으로 배치

## ⚡ 최적화

### 폴링 방식 이미지 캡처
ESP32는 단일 스레드이므로 `/stream` 사용 시 다른 요청을 처리하지 못합니다.
이 문제를 해결하기 위해 **폴링 방식**으로 `/capture` 엔드포인트를 주기적으로 호출합니다.

**장점:**
- ✅ 모터 제어와 영상 모니터링 동시 가능
- ✅ ESP32 부하 최소화
- ✅ 안정적인 명령 처리
- ✅ 조정 가능한 FPS (config.py에서 설정)

**단점:**
- ❌ 연속 스트림보다 약간 낮은 FPS (하지만 실용적)
- ❌ 약간의 네트워크 오버헤드

## 📁 프로젝트 구조

```
frontend/
├── app.py                    # Flask 메인 애플리케이션
├── config.py                 # 설정 파일 (IP, 텍스트, 상수 등)
├── requirements.txt          # Python 패키지 의존성
├── templates/
│   └── index.html           # 메인 대시보드 HTML
├── static/
│   ├── css/
│   │   └── style.css        # 스타일시트
│   └── js/
│       └── main.js          # 프론트엔드 JavaScript
├── utils/
│   └── server_port_selector.py  # 포트 선택 유틸리티
└── README.md                # 이 파일
```

## 🔧 설치 및 실행

### 1. Python 가상환경 생성 (권장)

```bash
cd frontend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. ESP32-CAM IP 주소 설정

**방법 1: 환경 변수 사용 (권장)**
```bash
export ESP32_IP="192.168.0.65"  # Linux/Mac
set ESP32_IP=192.168.0.65       # Windows
```

**방법 2: config.py 수정**
```python
# config.py
DEFAULT_ESP32_IP = "192.168.0.65"  # 실제 ESP32-CAM IP로 변경
```

### 4. Flask 서버 실행

```bash
python app.py
```

### 5. 웹 브라우저에서 접속

```
http://localhost:5000
```

## 🎮 사용 방법

### 웹 인터페이스

1. **모터 제어**
   - 버튼 클릭: 전진, 좌회전, 우회전
   - 버튼을 누르고 있는 동안 동작, 놓으면 정지
   - 정지 버튼: 즉시 정지

2. **속도 제어**
   - ➕ 가속: 속도 10씩 증가
   - ➖ 감속: 속도 10씩 감소

3. **LED 제어**
   - 토글 스위치로 ON/OFF 전환
   - 현재 상태 실시간 표시

4. **카메라 설정**
   - 슬라이더로 실시간 조정
   - 밝기: -2 ~ 2
   - 대비: -2 ~ 2
   - AGC 게인: 0 ~ 30

### 키보드 단축키

| 키 | 동작 |
|----|------|
| `↑` 또는 `W` | 전진 |
| `←` 또는 `A` | 좌회전 |
| `→` 또는 `D` | 우회전 |
| `Space` 또는 `S` | 정지 |
| `+` | 가속 |
| `-` | 감속 |
| `L` | LED 토글 |

## 📡 API 엔드포인트

### Flask 서버 API

| 엔드포인트 | 메소드 | 설명 |
|-----------|--------|------|
| `/` | GET | 메인 대시보드 |
| `/api/status` | GET | ESP32 상태 조회 (프록시) |
| `/api/control/<command>` | GET | 모터 제어 (left/right/center/stop) |
| `/api/led/<state>` | GET | LED 제어 (on/off/toggle) |
| `/api/speed/<operation>` | GET | 속도 제어 (plus/minus) |
| `/api/camera/<param>?value=N` | GET | 카메라 센서 제어 |
| `/capture` | GET | 단일 이미지 캡처 (폴링 방식, **권장**) |
| `/stream` | GET | MJPEG 스트림 (비권장 - 다른 명령 처리 불가) |

### ESP32-CAM 직접 제어 (GET 방식)

Flask 서버를 거치지 않고 직접 제어도 가능:

```bash
# 모터 제어
curl "http://192.168.0.65/control?cmd=center"

# 속도 제어
curl "http://192.168.0.65/speed?op=plus&step=10"

# LED 제어
curl "http://192.168.0.65/led?state=on"

# 카메라 설정
curl "http://192.168.0.65/camera?param=brightness&value=2"

# 상태 확인
curl "http://192.168.0.65/status"
```

## 🎨 주요 특징

### 1. 실시간 모니터링
- 1초마다 자동으로 ESP32 상태 업데이트
- FPS 카운터로 스트리밍 성능 확인
- 연결 상태 실시간 표시

### 2. 반응형 디자인
- 데스크톱, 태블릿, 모바일 지원
- 터치 이벤트 지원 (모바일 제어)

### 3. 직관적인 UI
- 모던한 디자인
- 색상 코딩 (성공/오류/경고)
- 실시간 로그 시스템

### 4. 프록시 기능
- Flask 서버가 ESP32와 브라우저 사이 프록시 역할
- CORS 문제 해결
- 에러 핸들링

## ⚙️ 커스터마이징

### config.py 설정 가이드

모든 설정은 `config.py` 파일에서 중앙 관리됩니다.

#### 네트워크 설정
```python
# config.py
DEFAULT_ESP32_IP = "192.168.0.65"        # ESP32-CAM IP 주소
DEFAULT_SERVER_PORT = 5000                # Flask 서버 포트
REQUEST_TIMEOUT = 2                       # 요청 타임아웃 (초)
```

#### UI 텍스트 커스터마이징
```python
# config.py
UI_TEXT = {
    "app_title": "🚗 ESP32-CAM 자율주행차 모니터링",
    "motor_forward": "⬆️ 전진",
    "motor_left": "⬅️ 좌회전",
    # ... 등등
}
```

#### 카메라 파라미터 범위 설정
```python
# config.py
CAMERA_PARAMS = {
    "brightness": {
        "min": -2,
        "max": 2,
        "default": 0,
        "name": "밝기",
    },
    # ... 등등
}
```

#### 속도 제어 설정
```python
# config.py
SPEED_MIN = 0
SPEED_MAX = 255
SPEED_DEFAULT_STEP = 10        # 기본 증감량
```

#### 업데이트 주기 설정
```python
# config.py
STATUS_UPDATE_INTERVAL = 1000           # 상태 업데이트 주기 (밀리초)
FPS_UPDATE_INTERVAL = 1000              # FPS 카운터 주기 (밀리초)
CAMERA_UPDATE_DEBOUNCE = 300            # 카메라 설정 디바운싱 (밀리초)

# 이미지 캡처 주기 (중요!)
IMAGE_CAPTURE_INTERVAL = 100            # 100ms = 약 10 FPS
# 권장값:
# - 100ms (10 FPS): 부드러운 영상, 약간의 부하
# - 200ms (5 FPS): 균형잡힌 설정 (권장)
# - 500ms (2 FPS): 낮은 부하, 명령 우선
```

**중요**: `IMAGE_CAPTURE_INTERVAL`을 너무 낮게 설정하면 모터 제어 응답이 느려질 수 있습니다.

#### 키보드 단축키 커스터마이징
```python
# config.py
KEYBOARD_SHORTCUTS = {
    "forward": ["ArrowUp", "w", "W"],
    "left": ["ArrowLeft", "a", "A"],
    "right": ["ArrowRight", "d", "D"],
    "stop": [" ", "s", "S"],
    "speed_up": ["+", "="],
    "speed_down": ["-", "_"],
    "led_toggle": ["l", "L"],
}
```

### 환경 변수로 설정 덮어쓰기

```bash
# ESP32 IP 변경
export ESP32_IP="192.168.1.100"

# 서버 포트 변경
export PORT=8080

# 실행
python app.py
```

## 🐛 문제 해결

### ESP32-CAM 연결 실패
1. ESP32-CAM이 켜져있는지 확인
2. 같은 네트워크에 연결되어 있는지 확인
3. `config.py`의 `DEFAULT_ESP32_IP` 주소 확인 또는 환경변수 `ESP32_IP` 설정
4. 방화벽 설정 확인
5. 터미널에서 직접 테스트: `curl http://192.168.0.65/status`

### 영상이 표시되지 않음
1. ESP32-CAM 전원 확인
2. `/capture` 엔드포인트 직접 접속 테스트: `http://192.168.0.65/capture`
3. 브라우저 캐시 삭제
4. 브라우저 개발자 도구(F12)에서 네트워크 탭 확인

### 제어 명령이 동작하지 않음
1. 로그 패널에서 오류 확인
2. ESP32 상태 확인 (`/api/status`)
3. 네트워크 연결 확인
4. `IMAGE_CAPTURE_INTERVAL`이 너무 짧지 않은지 확인 (200ms 이상 권장)

### 영상은 나오지만 제어가 느림
1. `config.py`에서 `IMAGE_CAPTURE_INTERVAL`을 200ms 이상으로 증가
2. ESP32의 WiFi 신호 강도 확인
3. 너무 많은 탭을 열지 않았는지 확인

## 📝 개발 정보

- **Framework**: Flask 3.0.0
- **Frontend**: Vanilla JavaScript (jQuery 없음)
- **CSS**: 순수 CSS (프레임워크 없음)
- **통신 방식**: GET 요청 (RESTful API)

## 🔐 보안 고려사항

현재 버전은 개발/테스트 용도입니다. 프로덕션 환경에서 사용 시:

1. **인증 추가**: 로그인 시스템 구현
2. **HTTPS 사용**: SSL/TLS 인증서 적용
3. **CORS 제한**: 특정 도메인만 허용
4. **디버그 모드 비활성화**: `debug=False`

## 📄 라이선스

이 프로젝트는 Free Car 프로젝트의 일부입니다.




