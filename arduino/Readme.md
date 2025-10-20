# Free Car - 자율주행차 (Arduino C/C++)

## 📋 프로젝트 개요

ESP32-CAM 모듈을 사용한 WiFi 기반 자율주행차 시스템
- **중앙처리**: 컴퓨터(Python)에서 영상 분석 및 방향 결정
- **임베디드**: ESP32-CAM(C/C++)에서 영상 스트리밍 및 모터/LED 제어
  - 아두이노 플랫폼 사용 (C/C++ 언어)
  - ESP32 전용 라이브러리 활용

---

## 📁 프로젝트 구조

```
free_car/arduino/
├── free_car.ino                          # 메인 파일 (C/C++)
├── config/                               # 설정 모듈
│   ├── wifi_config.h                     # WiFi 설정 및 연결 함수
│   └── pin_config.h                      # 핀 번호 정의
├── camera/                               # 카메라 모듈
│   ├── camera_init.h                     # 카메라 초기화
│   └── camera_stream_handler.h           # MJPEG 스트리밍
├── motor/                                # 모터 모듈
│   ├── motor_command.h                   # 명령 타입 정의 및 파싱
│   └── motor_controller.h                # 모터 제어 로직
├── led/                                  # LED 모듈
│   └── led_controller.h                  # LED 제어 로직
└── server/                               # HTTP 서버 모듈
    ├── http_server_handler.h             # 서버 시작 및 URI 등록
    └── command_receiver.h                # 명령 수신 및 상태 확인
```

---

## 🎯 주요 기능

### 1️⃣ **WiFi 연결** (config/wifi_config.h)
- `initWiFiConnection()`: WiFi 연결 및 타임아웃 처리
- `isWiFiConnected()`: 연결 상태 확인
- `reconnectWiFi()`: 자동 재연결

### 2️⃣ **카메라 스트리밍** (camera/)
- **초기화**: `initCamera()` - ESP32-CAM OV2640 센서 설정
- **스트리밍**: `streamHandler()` - MJPEG 실시간 스트리밍
- **캡처**: `captureHandler()` - 단일 이미지 캡처

### 3️⃣ **모터 제어** (motor/)
- **명령 타입**: `LEFT`, `RIGHT`, `CENTER`, `STOP`
- **제어 함수**:
  - `turnLeft()`: 좌회전 (왼쪽 모터 정지, 오른쪽 모터 전진)
  - `turnRight()`: 우회전 (왼쪽 모터 전진, 오른쪽 모터 정지)
  - `moveForward()`: 전진 (양쪽 모터 전진)
  - `stopMotor()`: 정지

### 4️⃣ **LED 제어** (led/)
- **제어 함수**:
  - `turnOnLED()`: LED 켜기
  - `turnOffLED()`: LED 끄기
  - `toggleLED()`: LED 토글 (켜짐 ↔ 꺼짐)
  - `setLEDBrightness(brightness)`: LED 밝기 조절 (0-255)
  - `getLEDState()`: 현재 LED 상태 반환

### 5️⃣ **HTTP 서버** (server/)
- **웹 인터페이스**: `/` - HTML 제어 페이지
- **스트리밍**: `/stream` - MJPEG 영상
- **모터 제어 API**: `/control?cmd=[left|right|center|stop]`
- **LED 제어 API**: `/led?state=[on|off|toggle]`
- **상태 확인**: `/status` - JSON 형식
- **이미지 캡처**: `/capture` - 단일 이미지

---

## 🔌 API 사용법

### 영상 스트리밍
```
GET http://192.168.1.100/stream
```

### 모터 제어
```
GET http://192.168.1.100/control?cmd=left     # 좌회전
GET http://192.168.1.100/control?cmd=right    # 우회전
GET http://192.168.1.100/control?cmd=center   # 전진
GET http://192.168.1.100/control?cmd=stop     # 정지
```

### LED 제어
```
GET http://192.168.1.100/led?state=on          # LED 켜기
GET http://192.168.1.100/led?state=off         # LED 끄기
GET http://192.168.1.100/led?state=toggle      # LED 토글
```

### 상태 확인
```
GET http://192.168.1.100/status
응답:
{
  "wifi_connected": true,
  "ip_address": "192.168.1.100",
  "camera_status": "ok",
  "motor_status": "ok",
  "current_command": "CENTER",
  "led_state": "on"
}
```

---

## 🚀 사용 방법

### 1. 아두이노 IDE 설정
1. **ESP32 보드 설치**: 
   - 파일 → 환경설정 → 추가 보드 관리자 URL에 추가:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
2. **라이브러리 설치**: 자동으로 포함됨 (ESP32 보드 패키지)

### 2. 업로드
1. `free_car.ino` 파일 열기
2. **보드 선택**: 도구 → 보드 → ESP32 → AI Thinker ESP32-CAM
3. **포트 선택**: 도구 → 포트 → (ESP32-CAM 연결된 포트)
4. **업로드** 버튼 클릭

### 3. 실행
1. 시리얼 모니터 열기 (115200 baud)
2. IP 주소 확인
3. 웹 브라우저에서 `http://[IP주소]` 접속

---

## 🔧 하드웨어 연결

### ESP32-CAM 핀 구성
| 기능 | GPIO 핀 | 설명 |
|------|---------|------|
| 모터A-전진 | GPIO 12 | 왼쪽 모터 전진 |
| 모터A-후진 | GPIO 13 | 왼쪽 모터 후진 |
| 모터B-전진 | GPIO 14 | 오른쪽 모터 전진 |
| 모터B-후진 | GPIO 15 | 오른쪽 모터 후진 |
| LED | GPIO 4 | 내장 플래시 LED |
| 카메라 | 내장 | OV2640 카메라 모듈 |

---

## 💡 코드 규칙

✅ **코드(함수명/변수명)**: 영어로 작성  
✅ **주석**: 한글로 작성  
✅ **Early Return 패턴**: 에러 처리 우선  
✅ **모듈형 구조**: 기능별 파일 분리  
✅ **클린 코드**: 한 함수는 한 가지 역할

---

## 📝 웹 인터페이스

ESP32-CAM에 접속하면 다음과 같은 웹 인터페이스를 볼 수 있습니다:

### 기능
- 📹 **실시간 카메라 스트리밍**
- 🎮 **모터 제어 버튼** (좌회전 / 전진 / 우회전 / 정지)
- 💡 **LED 제어 버튼** (켜기 / 끄기 / 토글)
- ℹ️ **API 엔드포인트 정보**

---

## 🐛 문제 해결

### WiFi 연결 실패
- WiFi SSID와 비밀번호 확인
- 2.4GHz WiFi만 지원 (5GHz 미지원)
- 라우터와의 거리 확인

### 카메라 초기화 실패
- ESP32-CAM 전원 확인 (최소 5V 1A)
- 카메라 모듈 연결 확인

### 모터가 동작하지 않음
- L298N 모터 드라이버 전원 확인
- GPIO 핀 연결 확인
- 모터 전원 (7.4V) 별도 공급 확인

### LED가 작동하지 않음
- GPIO 4번 핀이 다른 용도로 사용되는지 확인
- LED는 ESP32-CAM 내장 플래시 LED 사용

---

## 📊 시스템 초기화 로그

시리얼 모니터에서 다음과 같은 로그를 확인할 수 있습니다:

```
============================================
  Free Car - 자율주행차 시스템 시작
============================================

[단계 1] WiFi 연결
WiFi 연결 시도...
WiFi 연결 성공!
IP 주소: 192.168.1.100
✅ WiFi 연결 완료

[단계 2] 카메라 초기화
카메라 초기화 중...
카메라 초기화 완료!
✅ 카메라 초기화 완료

[단계 3] 모터 초기화
모터 핀 초기화 중...
모터 핀 초기화 완료!
✅ 모터 초기화 완료

[단계 4] LED 초기화
LED 핀 초기화 중...
LED 핀 초기화 완료!
✅ LED 초기화 완료

[단계 5] HTTP 서버 시작
HTTP 서버 시작 중...
URI 등록: /
URI 등록: /stream
URI 등록: /capture
URI 등록: /control
URI 등록: /led
URI 등록: /status
HTTP 서버 시작 완료!
서버 주소: http://192.168.1.100
✅ HTTP 서버 시작 완료

============================================
  🚗 시스템 준비 완료!
============================================
📡 웹 인터페이스: http://192.168.1.100
📹 스트리밍: http://192.168.1.100/stream
🎮 모터 제어: http://192.168.1.100/control?cmd=[left|right|center|stop]
💡 LED 제어: http://192.168.1.100/led?state=[on|off|toggle]
📊 상태: http://192.168.1.100/status
============================================
```

---

## 📖 상세 문서

전체 프로젝트 설계 및 컴퓨터 제어 프로그램은 `../prod.md` 파일을 참고하세요.

---

## 🙏 기술 스택

- **언어**: C/C++ (Arduino Framework)
- **플랫폼**: ESP32-CAM
- **라이브러리**: 
  - WiFi.h (ESP32 WiFi)
  - esp_camera.h (카메라 제어)
  - esp_http_server.h (HTTP 서버)
