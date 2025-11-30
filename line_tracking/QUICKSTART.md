# ⚡ 빠른 시작 가이드

## 1단계: IP 주소 확인

ESP32-CAM의 시리얼 모니터 또는 라우터 설정에서 IP 주소를 확인하세요.

예: `192.168.0.65`

## 2단계: 설정 파일 수정

`config.py` 파일을 열어 IP 주소를 수정하세요:

```python
ESP32_IP = "192.168.0.65"  # ← 여기를 실제 IP로 변경
```

## 3단계: ESP32 연결 테스트

브라우저에서 다음 주소로 접속하여 스트림이 보이는지 확인:

```
http://192.168.0.65/stream
```

또는 터미널에서:

```bash
curl http://192.168.0.65/status
```

## 4단계: 실행

### 방법 1: 스크립트 실행

```bash
chmod +x run_line_tracker.sh
./run_line_tracker.sh
```

### 방법 2: 직접 실행

```bash
python3 main_line_tracker.py
```

## 5단계: 확인

- 화면에 영상이 나타나는지 확인
- 라인이 검출되는지 확인 (초록 원)
- 명령이 표시되는지 확인 (LEFT/RIGHT/CENTER)

## 6단계: 종료

- 키보드 `q` 키 누르기
- 또는 `Ctrl+C`

---

## 🔧 문제 해결

### 연결이 안 될 때

```bash
# 1. 핑 테스트
ping 192.168.0.65

# 2. 같은 WiFi에 연결되어 있는지 확인
```

### 라인이 검출되지 않을 때

```python
# config.py에서 이 값들을 낮춰보세요
CANNY_LOW_THRESHOLD = 50
CANNY_HIGH_THRESHOLD = 100
HOUGH_THRESHOLD = 5
```

### 명령이 전송되지 않을 때

```python
# config.py에서 확인
ENABLE_COMMAND_SEND = True  # False면 True로 변경
```

---

## 💡 테스트 모드

명령 전송 없이 라인 검출만 테스트하려면:

```python
# config.py
ENABLE_COMMAND_SEND = False  # 명령 전송 비활성화
```

이렇게 하면 ESP32에 명령을 보내지 않고 화면만 확인할 수 있습니다.

---

## 📸 예상 화면

- **왼쪽**: 원본 영상 + 디버그 정보
- **오른쪽**: Canny Edge 결과 (흰색 선)
- **빨간 수평선**: ROI 경계
- **파란 수직선**: 화면 중심
- **초록 원**: 라인 중심점
- **명령 텍스트**: LEFT / RIGHT / CENTER

---

## 🚀 다음 단계

1. 파라미터 튜닝 (README.md 참조)
2. 실제 트랙에서 테스트
3. 속도 조절 API 추가 고려

즐거운 자율주행 되세요! 🚗💨

