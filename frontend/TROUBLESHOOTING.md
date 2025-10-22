# 트러블슈팅 가이드 🔧

## 문제 해결 방법

### 1. `TemplateNotFound: index.html` 에러

**증상:**
```
jinja2.exceptions.TemplateNotFound: index.html
```

**원인:**
- `app_factory.py`가 `core/` 폴더에 있어서 Flask가 템플릿 경로를 잘못 찾음
- 기본적으로 Flask는 `__name__`을 기준으로 경로를 설정

**해결:**
`core/app_factory.py`에서 템플릿/정적 파일 경로를 명시적으로 지정:

```python
from pathlib import Path

# frontend 폴더의 절대 경로 찾기
base_dir = Path(__file__).parent.parent.absolute()

app = Flask(
    __name__,
    template_folder=str(base_dir / 'templates'),
    static_folder=str(base_dir / 'static')
)
```

---

### 2. YOLO 모델 로드 실패

**증상:**
```
YOLO 모델이 로드되지 않았습니다. 서버 로그를 확인하세요.
```

**원인:**
- `ultralytics` 패키지 미설치
- PyTorch 미설치
- 인터넷 연결 문제 (모델 다운로드 실패)

**해결:**
```bash
# 1. 패키지 재설치
pip install --upgrade ultralytics torch torchvision

# 2. 수동으로 모델 다운로드
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# 3. 서버 재시작
python app.py
```

**참고:** YOLO는 선택적 기능이므로 로드 실패해도 서버는 정상 작동합니다.

---

### 3. OpenCV 이미지 디코딩 실패

**증상:**
```
이미지 디코딩 실패
```

**원인:**
- ESP32-CAM 연결 끊김
- 잘못된 이미지 형식
- OpenCV 설치 문제

**해결:**
```bash
# 1. ESP32-CAM 연결 확인
curl http://192.168.0.65/capture

# 2. OpenCV 재설치
pip uninstall opencv-python
pip install opencv-python==4.8.1.78

# 3. 이미지 형식 확인
curl -I http://192.168.0.65/capture
# Content-Type: image/jpeg 확인
```

---

### 4. ESP32-CAM 연결 실패

**증상:**
```
ESP32-CAM 연결 실패
```

**원인:**
- ESP32-CAM 전원 꺼짐
- WiFi 연결 끊김
- IP 주소 변경됨

**해결:**
```bash
# 1. IP 주소 확인
# Arduino 시리얼 모니터에서 IP 확인

# 2. 환경변수 설정
export ESP32_IP=192.168.0.65  # 실제 IP로 변경

# 3. config.py 수정
# DEFAULT_ESP32_IP = "실제_IP"

# 4. 연결 테스트
curl http://192.168.0.65/status
```

---

### 5. 포트 충돌 (Port Already in Use)

**증상:**
```
Address already in use
Port 5000 is in use
```

**원인:**
- 다른 프로세스가 5000번 포트 사용 중

**해결:**
```bash
# 1. 포트 사용 프로세스 찾기 (Mac/Linux)
lsof -i :5000

# 2. 프로세스 종료
kill -9 <PID>

# 3. 다른 포트로 실행
export PORT=5001
python app.py
```

---

### 6. 가상환경 활성화 안됨

**증상:**
```
ModuleNotFoundError: No module named 'flask'
```

**원인:**
- 가상환경 활성화 안됨

**해결:**
```bash
# Mac/Linux
cd frontend
source venv/bin/activate

# Windows
cd frontend
.\venv\Scripts\activate

# 확인
which python  # venv 경로 출력되어야 함
```

---

### 7. 패키지 설치 실패

**증상:**
```
ERROR: Could not find a version that satisfies the requirement
```

**원인:**
- Python 버전 호환성 문제
- 인터넷 연결 문제

**해결:**
```bash
# 1. Python 버전 확인 (3.8 이상 필요)
python3 --version

# 2. pip 업그레이드
pip install --upgrade pip

# 3. 패키지 개별 설치
pip install Flask==3.0.0
pip install requests==2.31.0
pip install ultralytics
pip install opencv-python
pip install torch torchvision

# 4. requirements.txt로 재설치
pip install -r requirements.txt
```

---

### 8. AI 분석이 느림

**증상:**
- `/api/ai/detect` 응답이 10초 이상 걸림

**원인:**
- YOLO 모델이 무거움
- CPU로 실행 중 (GPU 없음)

**해결:**
```python
# 1. 더 가벼운 모델 사용
# ai/yolo_detector.py 수정
detector = YOLODetector(model_path="yolov8n.pt")  # nano 버전

# 2. 신뢰도 임계값 높이기 (더 적은 객체 감지)
detector = YOLODetector(confidence_threshold=0.7)

# 3. 이미지 해상도 낮추기
# Arduino에서 카메라 해상도 QVGA (320x240)로 설정
```

---

### 9. 메모리 부족 (Out of Memory)

**증상:**
```
Killed
MemoryError
```

**원인:**
- YOLO 모델이 메모리를 많이 사용
- 라즈베리파이 등 저사양 기기

**해결:**
```bash
# 1. swap 메모리 늘리기 (Linux)
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. YOLO 사용 안함
# core/app_factory.py에서 YOLO 초기화 주석 처리
# app.config["YOLO_DETECTOR"] = None

# 3. 차선 감지만 사용
# 차선 감지는 OpenCV만 사용하여 가벼움
```

---

### 10. 차선 감지가 안됨

**증상:**
- `/api/ai/lanes` 응답에 `lanes: []`

**원인:**
- 카메라 각도 문제
- 조명 문제
- 차선이 명확하지 않음

**해결:**
```python
# ai/lane_detector.py 파라미터 조정
detector = LaneDetector(
    roi_top_ratio=0.5,    # ROI 영역 조정 (기본: 0.6)
    canny_low=30,         # 엣지 검출 민감도 (기본: 50)
    canny_high=100        # 엣지 검출 민감도 (기본: 150)
)
```

---

## 로그 확인 방법

### 서버 로그
```bash
# 터미널에서 실행 시 바로 표시됨
python app.py

# 로그 레벨 변경
# config.py 수정
LOG_LEVEL = "DEBUG"  # 상세 로그
```

### AI 분석 로그
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# ai/yolo_detector.py, ai/lane_detector.py에서
# logger.info(), logger.error() 확인
```

---

## 디버깅 팁

### 1. API 테스트
```bash
# 상태 확인
curl http://localhost:5000/api/status

# 객체 감지 (JSON)
curl http://localhost:5000/api/ai/detect

# 객체 감지 (이미지)
curl http://localhost:5000/api/ai/detect?draw=true > test.jpg
open test.jpg  # Mac
```

### 2. Python 코드로 테스트
```python
from ai.yolo_detector import YOLODetector
import cv2

detector = YOLODetector()
image = cv2.imread('test.jpg')
detections = detector.detect_objects(image)
print(detections)
```

### 3. 단계별 디버깅
```python
# 1. ESP32 연결 확인
import requests
r = requests.get('http://192.168.0.65/status')
print(r.json())

# 2. 이미지 캡처 확인
r = requests.get('http://192.168.0.65/capture')
with open('test.jpg', 'wb') as f:
    f.write(r.content)

# 3. YOLO 감지 확인
from ai.yolo_detector import YOLODetector
detector = YOLODetector()
detections = detector.detect_from_bytes(r.content)
print(detections)
```

---

## 자주 묻는 질문 (FAQ)

### Q1: YOLO 모델을 다른 버전으로 바꿀 수 있나요?
A: 네, `ai/yolo_detector.py`에서 모델 경로를 변경하세요:
```python
detector = YOLODetector(model_path="yolov8s.pt")  # small 버전
detector = YOLODetector(model_path="yolov8m.pt")  # medium 버전
```

### Q2: GPU를 사용할 수 있나요?
A: PyTorch가 GPU를 자동으로 감지합니다. CUDA가 설치되어 있으면 자동으로 GPU를 사용합니다.

### Q3: 다른 객체 감지 모델을 사용할 수 있나요?
A: 네, `YOLODetector` 클래스를 참고하여 새로운 클래스를 만들면 됩니다.

### Q4: 템플릿이 안 보이는 이유는?
A: `app_factory.py`에서 템플릿 경로가 올바르게 설정되었는지 확인하세요.

---

**문제가 해결되지 않으면 이슈로 등록해주세요!** 📮

