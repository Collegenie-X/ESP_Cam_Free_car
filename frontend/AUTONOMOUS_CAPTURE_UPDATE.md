# 자율주행 시스템 업데이트 - /capture 폴링 방식 적용

## 📝 변경 사항 요약

ESP32-CAM의 `/capture` 엔드포인트를 사용하여 자율주행 시스템을 개선했습니다.

### 주요 변경 사항

1. **프론트엔드 스트림 방식 변경** (`templates/autonomous.html`)
   - 기존: `/api/autonomous/stream` (MJPEG 스트림)
   - 변경: ESP32-CAM의 `/capture` 직접 폴링 (200ms 간격, 5fps)
   - 장점: 더 안정적이고 ESP32 부하 감소

2. **백엔드 자율주행 처리 방식 변경** (`services/autonomous_driving_service.py`)
   - 자율주행 시작 시 백그라운드 스레드에서 `/capture` 폴링
   - 실시간으로 차선 추적 및 ESP32 명령 전송
   - 스레드 안전성 개선

## 🚀 사용 방법

### 1. ESP32-CAM 설정

ESP32-CAM이 다음 IP로 접근 가능해야 합니다:
```
http://192.168.0.65/capture
```

### 2. 서버 시작

```bash
cd frontend
python app.py
```

### 3. 자율주행 모니터링 페이지 접속

브라우저에서 다음 주소로 접속:
```
http://localhost:5000/autonomous
```

### 4. 자율주행 시작

1. 페이지 로드 시 자동으로 카메라 연결 확인
2. 실시간 스트림이 표시됨 (ESP32의 `/capture` 폴링)
3. "▶️ 자율주행 시작" 버튼 클릭
4. 백그라운드에서 차선 추적 시작
5. ESP32로 자동으로 명령 전송 (LEFT, RIGHT, CENTER, STOP)

## 📊 시스템 동작 방식

### 프론트엔드 (브라우저)
```
1. /capture를 200ms마다 폴링 (5fps)
2. 이미지를 <img> 태그에 표시
3. 사용자에게 실시간 스트림 제공
```

### 백엔드 (Flask 서버)
```
1. 자율주행 시작 시 백그라운드 스레드 생성
2. /capture를 200ms마다 가져옴
3. 차선 추적 알고리즘 실행
4. 결정된 명령을 ESP32로 전송
   - LEFT → /control?cmd=left
   - RIGHT → /control?cmd=right
   - CENTER → /control?cmd=center
   - STOP → /control?cmd=stop
```

## 🔍 주요 개선 사항

### 안정성 향상
- MJPEG 스트림 파싱 문제 해결
- 네트워크 일시적 오류에도 안정적으로 동작
- 스레드 안전한 구현

### 성능 최적화
- 프레임 레이트 제한 (5fps)
- ESP32 부하 감소
- 중복 명령 필터링

### 사용자 경험 개선
- 스트림 연결 상태 실시간 표시
- 자세한 로그 메시지
- 재시도 기능

## 🛠️ 문제 해결

### 카메라가 연결되지 않는 경우

1. ESP32-CAM IP 주소 확인:
   ```bash
   ping 192.168.0.65
   ```

2. 브라우저에서 직접 접근 테스트:
   ```
   http://192.168.0.65/capture
   ```
   → 이미지가 표시되어야 함

3. `frontend/config.py`에서 IP 주소 확인:
   ```python
   DEFAULT_ESP32_IP = "192.168.0.65"
   ```

### 자율주행이 시작되지 않는 경우

1. 브라우저 콘솔(F12) 확인
2. 서버 로그 확인:
   ```bash
   tail -f server.log
   ```
3. ESP32 상태 확인:
   ```
   http://192.168.0.65/status
   ```

### 명령이 전송되지 않는 경우

1. ESP32 `/control` 엔드포인트 테스트:
   ```
   http://192.168.0.65/control?cmd=center
   ```
2. 서버 로그에서 "명령 전송" 메시지 확인
3. 네트워크 연결 상태 확인

## 📁 수정된 파일 목록

### 1. `frontend/templates/autonomous.html`
- `initStream()`: 폴링 방식으로 변경
- `startStreamPolling()`: 추가
- `stopStreamPolling()`: 추가
- `retryStream()`: 폴링 재시작 로직 수정

### 2. `frontend/services/autonomous_driving_service.py`
- `__init__()`: 스레드 관련 변수 추가
- `start()`: 백그라운드 폴링 스레드 시작
- `stop()`: 스레드 안전한 종료
- `_polling_loop()`: 추가 - /capture 폴링 루프

## 🔧 설정 옵션

### FPS 조정

프론트엔드 (`autonomous.html`):
```javascript
const TARGET_FPS = 5; // 변경 가능 (1-10 권장)
```

백엔드 (`autonomous_driving_service.py`):
```python
TARGET_FPS = 5  # 변경 가능 (1-10 권장)
```

### IP 주소 변경

`frontend/config.py`:
```python
DEFAULT_ESP32_IP = "192.168.0.65"  # 실제 ESP32 IP로 변경
```

## 📈 성능 지표

- **프레임 레이트**: 5 FPS (안정적)
- **명령 지연 시간**: ~200ms
- **CPU 사용량**: 낮음 (단일 이미지 처리)
- **네트워크 부하**: 낮음 (작은 JPEG 이미지)

## 🎯 다음 단계

### 추천 개선 사항

1. **적응형 FPS**: 네트워크 상태에 따라 동적 조정
2. **명령 큐**: 명령 대기열 구현
3. **오류 복구**: 자동 재연결 기능
4. **성능 모니터링**: 실시간 FPS 표시

### 선택적 개선 사항

1. **WebSocket 사용**: 더 낮은 지연 시간
2. **이미지 압축**: 대역폭 절약
3. **다중 해상도**: 네트워크 상태에 따라 해상도 조정

## 📞 지원

문제가 발생하면:
1. `server.log` 확인
2. 브라우저 콘솔 확인
3. ESP32 시리얼 출력 확인

---

**업데이트 날짜**: 2025-10-22  
**버전**: 2.0.0  
**작성자**: ESP32-CAM Free Car Team

