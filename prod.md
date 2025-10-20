# 자율주행차 프로젝트 (Free Car)

## 프로젝트 개요
ESP32-CAM 모듈을 사용한 WiFi 기반 자율주행차 시스템
- **중앙처리**: 컴퓨터(Python)에서 영상 분석 및 방향 결정
- **임베디드**: ESP32-CAM(C/C++)에서 영상 스트리밍 및 모터 제어
  - 아두이노 플랫폼 사용 (C/C++ 언어)
  - ESP32 전용 라이브러리 활용

---

## 시스템 아키텍처

### 전체 흐름도
```
[ESP32-CAM] ---(WiFi 영상 스트리밍)---> [컴퓨터]
     ↑                                      |
     |                                      | (영상 분석)
     |                                      ↓
     └------(방향 명령: 왼쪽/오른쪽/중앙)----┘
```

### 통신 프로토콜
1. **영상 스트리밍**: `http://[ESP32_IP]/stream` (MJPEG 스트림)
2. **명령 수신**: `http://[ESP32_IP]/control?cmd=[left|right|center|stop]`

---

## 하드웨어 구성

### ESP32-CAM 핀 구성
| 기능 | GPIO 핀 | 설명 |
|------|---------|------|
| 모터A-전진 | GPIO 12 | 왼쪽 모터 전진 |
| 모터A-후진 | GPIO 13 | 왼쪽 모터 후진 |
| 모터B-전진 | GPIO 14 | 오른쪽 모터 전진 |
| 모터B-후진 | GPIO 15 | 오른쪽 모터 후진 |
| 카메라 | 내장 | OV2640 카메라 모듈 |

### 필요 부품
- ESP32-CAM 모듈 x1
- L298N 모터 드라이버 x1
- DC 모터 x2
- 배터리 팩 (7.4V)
- 차량 섀시

---

## 소프트웨어 구조

### ESP32-CAM (Arduino C/C++)

**언어**: C/C++ (Arduino Framework)
**코드 규칙**: 함수명/변수명은 영어, 주석은 한글

#### 파일 구조
```
free_car/
├── free_car.ino                    # 메인 진입점
├── config/
│   └── wifi_config.h               # WiFi 설정
│   └── pin_config.h                # 핀 설정
├── camera/
│   └── camera_stream_handler.h     # 카메라 스트리밍 핸들러
│   └── camera_init.h               # 카메라 초기화
├── motor/
│   └── motor_controller.h          # 모터 제어 로직
│   └── motor_command.h             # 모터 명령 정의
├── led/
│   └── led_controller.h            # LED 제어 로직
└── server/
    └── http_server_handler.h       # HTTP 서버 핸들러
    └── command_receiver.h          # 명령 수신 핸들러
```

#### 주요 클래스 및 함수

**1. WiFiConfig (config/wifi_config.h)**
- `const char* WIFI_SSID`: WiFi 이름
- `const char* WIFI_PASSWORD`: WiFi 비밀번호
- `void initWiFiConnection()`: WiFi 연결 설정

**2. PinConfig (config/pin_config.h)**
- 모터 핀 번호 정의 (상수)
- 카메라 핀 번호 정의 (상수)

**3. CameraStreamHandler (camera/camera_stream_handler.h)**
- `esp_err_t streamHandler(httpd_req_t *req)`: MJPEG 스트리밍 핸들러
- `esp_err_t sendFrame(httpd_req_t *req, camera_fb_t *fb)`: 프레임 전송

**4. CameraInit (camera/camera_init.h)**
- `bool initCamera()`: 카메라 센서 초기화
- `camera_config_t getCameraConfig()`: 카메라 설정 반환

**5. MotorController (motor/motor_controller.h)**
- `void initMotor()`: 모터 핀 초기화
- `void moveForward()`: 전진 동작
- `void turnLeft()`: 좌회전 동작
- `void turnRight()`: 우회전 동작
- `void stopMotor()`: 정지 동작

**6. MotorCommand (motor/motor_command.h)**
- `enum CommandType { LEFT, RIGHT, CENTER, STOP }`: 명령 타입 정의
- `CommandType parseCommand(String cmd)`: 명령 파싱

**7. LEDController (led/led_controller.h)**
- `void initLED()`: LED 핀 초기화
- `void turnOnLED()`: LED 켜기
- `void turnOffLED()`: LED 끄기
- `void toggleLED()`: LED 토글 (켜짐 ↔ 꺼짐)
- `bool getLEDState()`: LED 상태 반환
- `void setLEDBrightness(int brightness)`: LED 밝기 조절 (PWM)

**8. HttpServerHandler (server/http_server_handler.h)**
- `void startHttpServer()`: HTTP 서버 초기화 및 시작
- `void registerUriHandlers()`: 각 엔드포인트 등록

**9. CommandReceiver (server/command_receiver.h)**
- `esp_err_t controlCommandHandler(httpd_req_t *req)`: 제어 명령 수신
- `esp_err_t ledControlHandler(httpd_req_t *req)`: LED 제어 명령 수신
- `void executeCommand(String cmd)`: 명령에 따른 모터 제어

---

### 컴퓨터 (Python)

#### 파일 구조
```
computer_control/
├── main.py                         # 메인 실행 파일
├── config/
│   └── esp32_config.py             # ESP32 연결 설정
├── vision/
│   └── stream_receiver.py          # 영상 스트림 수신
│   └── lane_detector.py            # 차선 인식 알고리즘
│   └── direction_analyzer.py       # 방향 분석 로직
└── control/
    └── command_sender.py           # 명령 전송 모듈
    └── control_logic.py            # 제어 로직
```

#### 주요 클래스 및 함수

**1. ESP32Config (config/esp32_config.py)**
- `ESP32_IP`: ESP32 IP 주소
- `STREAM_URL`: 스트림 URL
- `CONTROL_URL`: 제어 URL

**2. StreamReceiver (vision/stream_receiver.py)**
- `class 스트림수신기`: 영상 스트림 수신 클래스
- `프레임가져오기()`: 현재 프레임 반환

**3. LaneDetector (vision/lane_detector.py)**
- `class 차선검출기`: 차선 검출 알고리즘
- `차선찾기(frame)`: 차선 검출
- `중심점계산(lanes)`: 차선 중심점 계산

**4. DirectionAnalyzer (vision/direction_analyzer.py)**
- `class 방향분석기`: 방향 결정 로직
- `방향결정(center_point)`: 왼쪽/오른쪽/중앙 결정

**5. CommandSender (control/command_sender.py)**
- `class 명령전송기`: 명령 전송 클래스
- `명령전송(direction)`: HTTP 요청으로 명령 전송

**6. ControlLogic (control/control_logic.py)**
- `class 제어로직`: 전체 제어 흐름
- `실행()`: 메인 제어 루프

---

## 알고리즘 설계

### 차선 검출 알고리즘 (컴퓨터)
```
1. 프레임 수신
   ↓
2. 그레이스케일 변환
   ↓
3. 가우시안 블러 (노이즈 제거)
   ↓
4. Canny 엣지 검출
   ↓
5. ROI (관심 영역) 설정
   ↓
6. Hough 변환으로 직선 검출
   ↓
7. 차선 중심점 계산
   ↓
8. 방향 결정 (왼쪽/오른쪽/중앙)
```

### 방향 결정 로직
```python
if 중심점_X < 화면중앙 - 임계값:
    return "왼쪽"
elif 중심점_X > 화면중앙 + 임계값:
    return "오른쪽"
else:
    return "중앙"
```

### 모터 제어 로직 (ESP32)
```
- 왼쪽 명령: 왼쪽 모터 감속, 오른쪽 모터 가속
- 오른쪽 명령: 왼쪽 모터 가속, 오른쪽 모터 감속
- 중앙 명령: 양쪽 모터 동일 속도 전진
- 정지 명령: 양쪽 모터 정지
```

---

## API 엔드포인트

### ESP32-CAM 제공 API

#### 1. 영상 스트리밍
- **URL**: `GET http://[ESP32_IP]/stream`
- **응답**: MJPEG 스트림
- **Content-Type**: `multipart/x-mixed-replace`

#### 2. 모터 제어 명령
- **URL**: `GET http://[ESP32_IP]/control`
- **파라미터**:
  - `cmd`: 명령어 (left, right, center, stop)
- **예시**: 
  - `http://192.168.1.100/control?cmd=left`
  - `http://192.168.1.100/control?cmd=right`
  - `http://192.168.1.100/control?cmd=center`
  - `http://192.168.1.100/control?cmd=stop`
- **응답**: `200 OK` 또는 `400 Bad Request`

#### 3. LED 제어 명령
- **URL**: `GET http://[ESP32_IP]/led`
- **파라미터**:
  - `state`: LED 상태 (on, off, toggle)
- **예시**: 
  - `http://192.168.1.100/led?state=on`
  - `http://192.168.1.100/led?state=off`
  - `http://192.168.1.100/led?state=toggle`
- **응답**: `LED state: ON` 또는 `LED state: OFF`

#### 4. 상태 확인
- **URL**: `GET http://[ESP32_IP]/status`
- **응답**: JSON 형식
```json
{
  "wifi_connected": true,
  "ip_address": "192.168.1.100",
  "camera_status": "ok",
  "motor_status": "ok",
  "current_command": "center",
  "led_state": "on"
}
```

---

## 개발 단계

### Phase 1: ESP32-CAM 기본 설정 (1일)
- [x] WiFi 연결 설정
- [ ] 카메라 초기화
- [ ] HTTP 서버 구동
- [ ] 영상 스트리밍 구현

### Phase 2: 모터 및 LED 제어 구현 (1일)
- [ ] 모터 핀 설정
- [ ] 기본 모터 제어 함수 구현
- [ ] LED 제어 함수 구현
- [ ] 명령 수신 API 구현
- [ ] 명령에 따른 모터/LED 동작 테스트

### Phase 3: 컴퓨터 제어 프로그램 (2일)
- [ ] 영상 스트림 수신 구현
- [ ] 차선 검출 알고리즘 구현
- [ ] 방향 결정 로직 구현
- [ ] 명령 전송 모듈 구현

### Phase 4: 통합 테스트 및 최적화 (1일)
- [ ] 전체 시스템 통합 테스트
- [ ] 지연 시간 최적화
- [ ] 알고리즘 튜닝
- [ ] 예외 처리 강화

---

## 코딩 규칙

### 1. 모듈형 구조
- 기능별로 헤더 파일 분리
- 각 모듈은 독립적으로 동작 가능
- 인터페이스와 구현 분리

### 2. 네이밍 규칙
- **파일명**: 기능_역할.확장자 (예: motor_controller.h)
- **함수명**: 동사_명사 형태 (예: 모터초기화, 프레임전송)
- **클래스명**: 명사 형태 (예: MotorController, CameraInit)
- **상수명**: 대문자_언더스코어 (예: WIFI_SSID, MOTOR_PIN_A1)

### 3. 코드 스타일
- Early return 패턴 사용
- 한 함수는 한 가지 역할만
- **코드(함수명/변수명)는 영어로 작성**
- **주석은 한글로 작성**
- 매직 넘버 사용 금지 (상수로 정의)

### 4. 예외 처리
```cpp
// Early return 패턴 예시
bool initCamera() {
    if (!checkCameraConfig()) {
        Serial.println("카메라 설정 실패");
        return false;
    }
    
    if (!initSensor()) {
        Serial.println("센서 초기화 실패");
        return false;
    }
    
    return true;
}
```

---

## 테스트 계획

### 단위 테스트
- [ ] WiFi 연결 테스트
- [ ] 카메라 스트리밍 테스트
- [ ] 모터 개별 동작 테스트
- [ ] API 엔드포인트 테스트

### 통합 테스트
- [ ] 영상 수신 → 분석 → 명령 전송 전체 흐름
- [ ] 네트워크 지연 시간 측정
- [ ] 실시간 성능 테스트

### 실제 주행 테스트
- [ ] 직선 주행
- [ ] 곡선 주행
- [ ] 장애물 회피 (추후)

---

## 성능 목표

- **프레임 레이트**: 최소 10 FPS
- **응답 지연**: 최대 200ms
- **WiFi 범위**: 최소 10m
- **배터리 구동 시간**: 최소 30분

---

## 추후 확장 기능

1. **장애물 감지**: 초음파 센서 추가
2. **속도 제어**: PWM을 이용한 가변 속도
3. **수동/자동 모드 전환**: 웹 인터페이스 추가
4. **배터리 모니터링**: 전압 센서 추가
5. **딥러닝 모델 적용**: YOLO 등의 객체 인식

---

## 참고 자료

- ESP32-CAM 공식 문서
- OpenCV 차선 검출 튜토리얼
- L298N 모터 드라이버 데이터시트
- MJPEG 스트리밍 프로토콜

---

## 버전 정보

- **작성일**: 2025-10-20
- **버전**: 1.0.0
- **작성자**: Free Car Project Team

