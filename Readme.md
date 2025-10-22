
## 🔌 API 사용법

### 📹 영상 스트리밍
```bash
GET http://192.168.0.65/stream
# MJPEG 형식의 실시간 영상 스트리밍 (약 30 FPS)
```

### 🎮 모터 제어
```bash
GET http://192.168.0.65/control?cmd=left      # 좌회전
GET http://192.168.0.65/control?cmd=right     # 우회전
GET http://192.168.0.65/control?cmd=center    # 전진
GET http://192.168.0.65/control?cmd=stop      # 정지
```

### 💡 LED 제어
```bash
GET http://192.168.0.65/led?state=on          # LED 켜기
GET http://192.168.0.65/led?state=off         # LED 끄기
GET http://192.168.0.65/led?state=toggle      # LED 토글 (켜짐↔꺼짐)
```

### ⚡ 모터 속도 제어
```bash
# 속도 증가 (기본: +10)
GET http://192.168.0.65/speed?op=plus&step=10

# 속도 감소 (기본: -10)
GET http://192.168.0.65/speed?op=minus&step=10

# 속도 크게 증가
GET http://192.168.0.65/speed?op=plus&step=20

# 속도 조금 감소
GET http://192.168.0.65/speed?op=minus&step=5
```

**파라미터:**
- `op`: `plus` (증가) 또는 `minus` (감소)
- `step`: 증감량 (1~100, 기본값 10)

**응답 예시:**
```
speed=210
```

### 📷 카메라 센서 제어

#### 밝기 조절 (brightness: -2 ~ 2)
```bash
GET http://192.168.0.65/camera?param=brightness&value=3   # 최대 밝기
GET http://192.168.0.65/camera?param=brightness&value=1   # 밝게
GET http://192.168.0.65/camera?param=brightness&value=0   # 기본
GET http://192.168.0.65/camera?param=brightness&value=-1  # 어둡게
```

#### 대비 조절 (contrast: -2 ~ 2)
```bash
GET http://192.168.0.65/camera?param=contrast&value=1     # 대비 증가
GET http://192.168.0.65/camera?param=contrast&value=0     # 기본
```

#### 채도 조절 (saturation: -2 ~ 2)
```bash
GET http://192.168.0.65/camera?param=saturation&value=1   # 채도 증가
GET http://192.168.0.65/camera?param=saturation&value=0   # 기본
```

#### AGC 게인 조절 (agc_gain: 0 ~ 30)
```bash
GET http://192.168.0.65/camera?param=agc_gain&value=10    # 게인 증가 (더 밝게, 노이즈 증가)
GET http://192.168.0.65/camera?param=agc_gain&value=4     # 기본
GET http://192.168.0.65/camera?param=agc_gain&value=2     # 게인 감소 (노이즈 감소)
```

#### 게인 상한 설정 (gainceiling: 0 ~ 6)
```bash
GET http://192.168.0.65/camera?param=gainceiling&value=6  # 최대 게인 허용
GET http://192.168.0.65/camera?param=gainceiling&value=4  # 제한
GET http://192.168.0.65/camera?param=gainceiling&value=0  # 최소
```

#### 자동 노출 제어 (aec2: 0 또는 1)
```bash
GET http://192.168.0.65/camera?param=aec2&value=1         # AEC2 활성화 (노출 향상)
GET http://192.168.0.65/camera?param=aec2&value=0         # AEC2 비활성화
```

#### 영상 미러/플립 (hmirror, vflip: 0 또는 1)
```bash
GET http://192.168.0.65/camera?param=hmirror&value=1      # 수평 미러 켜기
GET http://192.168.0.65/camera?param=vflip&value=1        # 수직 플립 켜기
```

#### 현재 카메라 설정 조회
```bash
GET http://192.168.0.65/camera
GET http://192.168.0.65/camera?get=settings
```

**응답 예시:**
```json
{
  "brightness": 1,
  "contrast": 1,
  "saturation": 0,
  "agc_gain": 4,
  "gainceiling": 6,
  "aec2": 1,
  "hmirror": 0,
  "vflip": 0
}
```

### 📊 상태 확인
```bash
GET http://192.168.0.65/status
```

**응답 예시:**
```json
{
  "wifi_connected": true,
  "ip_address": "192.168.0.65",
  "camera_status": "ok",
  "motor_status": "running",
  "current_command": "CENTER",
  "led_state": "on",
  "speed": 200,
  "camera_settings": {
    "brightness": 1,
    "contrast": 1,
    "saturation": 0,
    "agc_gain": 4,
    "gainceiling": 6,
    "aec2": 1,
    "hmirror": 0,
    "vflip": 0
  }
}
```

**응답 필드:**
- `wifi_connected`: WiFi 연결 상태
- `ip_address`: IP 주소
- `camera_status`: 카메라 상태
- `motor_status`: 모터 상태 (`running` 또는 `stopped`)
- `current_command`: 현재 명령 (`LEFT`, `RIGHT`, `CENTER`, `STOP`)
- `led_state`: LED 상태 (`on` 또는 `off`)
- `speed`: 현재 모터 속도 (0~255)
- `camera_settings`: 카메라 센서 설정값
  - `brightness`: 밝기 (-2 ~ 2)
  - `contrast`: 대비 (-2 ~ 2)
  - `saturation`: 채도 (-2 ~ 2)
  - `agc_gain`: AGC 게인 (0 ~ 30)
  - `gainceiling`: 게인 상한 (0 ~ 6)
  - `aec2`: 자동 노출 제어 (0 또는 1)
  - `hmirror`: 수평 미러 (0 또는 1)
  - `vflip`: 수직 플립 (0 또는 1)

### 📸 단일 이미지 캡처
```bash
GET http://192.168.0.65/capture
# JPEG 형식의 단일 이미지 반환
```

---

## 💡 사용 시나리오

### 어두운 환경에서 밝기 향상
```bash
# 1단계: 밝기 최대
GET http://192.168.0.65/camera?param=brightness&value=2

# 2단계: AGC 게인 증가
GET http://192.168.0.65/camera?param=agc_gain&value=8

# 3단계: 게인 상한 최대
GET http://192.168.0.65/camera?param=gainceiling&value=6

# 4단계: AEC2 활성화
GET http://192.168.0.65/camera?param=aec2&value=1

# 5단계: LED 켜기
GET http://192.168.0.65/led?state=on
```

### 빠르게 달리기
```bash
# 속도 증가
GET http://192.168.0.65/speed?op=plus&step=30

# 전진
GET http://192.168.0.65/control?cmd=center
```

### 부드럽게 회전
```bash
# 속도 감소
GET http://192.168.0.65/speed?op=minus&step=20

# 좌회전
GET http://192.168.0.65/control?cmd=left
```

### 정지 및 초기화
```bash
# 모터 정지
GET http://192.168.0.65/control?cmd=stop

# LED 끄기
GET http://192.168.0.65/led?state=off

# 카메라 기본 설정으로
GET http://192.168.0.65/camera?param=brightness&value=0
GET http://192.168.0.65/camera?param=agc_gain&value=4
```

---

## 🎯 전체 엔드포인트 요약

| 엔드포인트 | 메소드 | 설명 |
|-----------|--------|------|
| `/` | GET | 웹 인터페이스 (HTML) |
| `/stream` | GET | MJPEG 영상 스트리밍 |
| `/capture` | GET | 단일 이미지 캡처 (JPEG) |
| `/control` | GET | 모터 제어 (좌/우/전진/정지) |
| `/led` | GET | LED 제어 (켜기/끄기/토글) |
| `/speed` | GET | 모터 속도 증감 |
| `/camera` | GET | 카메라 센서 설정 제어 |
| `/status` | GET | 시스템 상태 확인 (JSON) |